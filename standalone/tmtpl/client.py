#!/usr/bin/python
#
# Client data module
#
# This file is part of the tmtp (Tau Meta Tau Physica) project.
# For more information, see http://www.sew-brilliant.org/
#
# Copyright (C) 2010, 2011, 2012 Susan Spencer and Steve Conklin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. Attribution must be given in 
# all derived works.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import json

from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *

from constants import *

# Define globals

class ClientData(object):
    """
    Class used to build a heirarchical structure of client data
    """
    def __init__(self):
        return

class Client(object):
    """
    Class to hold client-specific data
    Does unit conversions for cm or inches and returns data in pts
    """
    def __init__(self, filename, filetype= 'json'):
        # This is set up to be extensible for XML or other formats

        self.filetypes = ['json']
        self.data = ClientData()
        if filetype not in self.filetypes:
            print 'Client: supported file types are ', self.filetypes
        if filetype == 'json':
            self.__readJson__(filename)

    def setMeasurement(self, key, val, conversion_factor=None):
        keyparts = key.split('.')
        if conversion_factor is None:
            conversion_factor = self.__conversion__
        # make sure the objects are created in the dotted 'path'
        parent = self.data
        for i in range (0, len(keyparts)-1):
            oname = keyparts[i]
            if oname not in dir(parent):
                # object does not exist, create a new ClientData object within the parent
                setattr(parent, oname, ClientData())
                # Now, set the parent to be the object we just created
                parent = getattr(parent, oname)
            else:
                # object exists - it better be a clientdata type and not something
                # else. This can be caused by errors in the variable naming in the json file
                parent = getattr(parent, oname)
                if not isinstance(parent, ClientData):
                    print "########################### ERROR: Malformed Client Data ###########################"
                    print "\nThe variable named <", oname, "> appears both as an attribute and as a parent"
                    print "Check the data file <", datafilename, ">"
                    print "\n####################################################################################"
                    raise ValueError

        # now, we have all the containing objects in place
        # get the rightmost part of the dotted variable, and add it
        attrname = keyparts[-1]
        # Create attribute based on the type in the json data
        ty = val['type']
        if ty == 'float':
            setattr(parent, attrname, float(val['value']) * conversion_factor)
        elif ty == 'string':
            setattr(parent, attrname, val['value'])
        elif ty == 'int':
            setattr(parent, attrname, int(val['value']))
        else:
            raise ValueError('Unknown type ' + ty + 'in client data')
                
    def __readJson__(self, datafilename):
        self.info={}

        # open the client file and read data
        f = open(datafilename, 'r')
        self.client = json.load(f)
        f.close()

        # Check to make sure we have units
        try:
            units = self.client['measureunit']['value']
            if units == 'cm':
                #self.__conversion__ = cm_to_pt
                self.__conversion__ = CM_TO_PX
            elif  units == 'in':
                #self.__conversion__ = in_to_pt
                self.__conversion__ = IN_TO_PX
        except KeyError:
            print 'Client Data measurement units not defined in client data file'
            raise

        #
        # read all these and then create a hierarchy of objects and
        # attributes, based on the 'dotted path' notation.
        #

        # read everything into attributes
        for key, val in self.client.items():
            self.setMeasurement(key, val)
        return

    def __dump__(self, obj, parent = '', parentstring = '', outtxt = []):
        objAttrs = dir(obj)

        # walk through the attributes in this object
        for oname in objAttrs:

            # we don't care about internal python stuff
            if oname.startswith('__'):
                continue

            # get the actual object we're looking at
            thisobj = getattr(obj, oname)

            # is it one of our own clientdata objects?
            if isinstance(thisobj, ClientData):
                # if so, then call dump on it
                if parentstring != '':
                    dot = '.'
                else:
                    dot = ''
                self.__dump__(thisobj, oname, (parentstring + dot + oname), outtxt)
            else:
                # if not, then it is an 'end item' bit of information
                # TODO convert back to the units used for input (not pts)
                if parent != '':
                    outtxt.append(parentstring + "." + oname + " " + str(thisobj) + "\n")
                else:
                    outtxt.append(oname + " " + str(thisobj) + "\n")
        return(outtxt)

    def dump(self):
        ot = ''
        output = sorted(self.__dump__(self.data))
        for line in output:
            ot = ot + line
        return ot

