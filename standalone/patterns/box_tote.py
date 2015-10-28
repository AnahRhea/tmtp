#!/usr/bin/env python
#!/usr/bin/python
#
# This file is part of the tmtp (Tau Meta Tau Physica) project.
# For more information, see http://www.sew-brilliant.org/
#
# Copyright (C) 2010, 2011, 2012  Susan Spencer and Steve Conklin
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
#
# This pattern was created by Sacha Chua.
# Specify the following measurements:
# - height
# - width
# - depth
# - optional:
#   - seam_allowance
#   - hem_allowance
#   - strap_width
#   - strap_length

from tmtpl.constants import *
from tmtpl.pattern   import *
from tmtpl.document   import *

from tmtpl.client   import Client

# Project specific
#from math import sin, cos, radians

from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *

class PatternDesign():

    def __init__(self):
        self.styledefs = {}
        return

    def makeReferenceSquare(self, base_pt):
        part = PatternPiece('pattern', '1"x1" reference', letter = 'R', fabric = 0, interfacing = 0, lining = 0)
        path_svg = path()
        part.add(Path('pattern', 'path', 'Path for reference square', path_svg, 'seamline_style'))
        moveP(path_svg, base_pt)
        path_svg.appendLineToPath(0, 1 * IN_TO_PX, relative = True);
        path_svg.appendLineToPath(1 * IN_TO_PX, 0, relative = True);
        path_svg.appendLineToPath(0, -1 * IN_TO_PX, relative = True);
        path_svg.appendLineToPath(-1 * IN_TO_PX, 0, relative = True);
        part.label_x = base_pt.x + 0.25 * IN_TO_PX
        part.label_y = base_pt.y + 0.25 * IN_TO_PX
        return part

    def makePart(self, base_pt):
        # Begin pattern piece
        part = PatternPiece('pattern', 'base', letter = 'A', fabric = 1, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + 0.25 * IN_TO_PX
        part.label_y = base_pt.y + 0.25 * IN_TO_PX
        path_svg = path()
        part.add(Path('pattern', 'base', 'Path for base', path_svg, 'seamline_style'))

        top_right = offsetPoint(base_pt, self.cd.width + self.cd.depth, 0)
        bottom_right = offsetPoint(top_right, 0, 2 * self.cd.height + self.cd.depth)
        bottom_left = pPoint(base_pt.x, bottom_right.y)

        moveP(path_svg, base_pt)
        lineP(path_svg, top_right)
        lineP(path_svg, bottom_right)
        lineP(path_svg, bottom_left)
        lineP(path_svg, base_pt)

        middle_left = pntMidPointP(base_pt, bottom_left)
        middle_right = pPoint(top_right.x, middle_left.y)
        moveP(path_svg, middle_left)
        lineP(path_svg, middle_right)

        moveP(path_svg, offsetPoint(base_pt, self.cd.depth / 2, 0))
        lineP(path_svg, offsetPoint(bottom_left, self.cd.depth / 2, 0))
        moveP(path_svg, offsetPoint(top_right, -self.cd.depth / 2, 0))
        lineP(path_svg, offsetPoint(bottom_right, -self.cd.depth / 2, 0))
        moveP(path_svg, offsetPoint(middle_left, self.cd.depth / 2, -self.cd.depth / 2))
        lineP(path_svg, middle_left)
        lineP(path_svg, offsetPoint(middle_left, self.cd.depth / 2, self.cd.depth / 2))
        lineP(path_svg, offsetPoint(middle_right, -self.cd.depth / 2, self.cd.depth / 2))
        lineP(path_svg, middle_right)
        lineP(path_svg, offsetPoint(middle_right, -self.cd.depth / 2, -self.cd.depth / 2))
        lineP(path_svg, offsetPoint(middle_left, self.cd.depth / 2, -self.cd.depth / 2))

        # Add seam allowances
        seam_allowance = getattr(self.cd, 'seam_allowance', 0)
        hem_allowance = getattr(self.cd, 'hem_allowance', seam_allowance)
        if seam_allowance > 0:
            path_cut = path()
            moveP(path_cut, offsetPoint(base_pt, -seam_allowance, -hem_allowance))
            lineP(path_cut, offsetPoint(bottom_left, -seam_allowance, hem_allowance))
            lineP(path_cut, offsetPoint(bottom_right, seam_allowance, hem_allowance))
            lineP(path_cut, offsetPoint(top_right, seam_allowance, -hem_allowance))
            lineP(path_cut, offsetPoint(base_pt, -seam_allowance, -hem_allowance))
            part.add(Path('pattern', 'cut', 'Path for cut', path_cut, 'cuttingline_style'))

        # end of pattern piece
        return part

    def makeStrap(self, base_pt):
        strap_length = getattr(self.cd, 'strap_length', 0)
        strap_width = getattr(self.cd, 'strap_width', 0)
        if strap_length == 0:
            return None
        part = PatternPiece('pattern', 'strap', letter = 'B', fabric = 1, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + 0.25 * IN_TO_PX
        part.label_y = base_pt.y + 0.25 * IN_TO_PX
        path_svg = path()
        part.add(Path('pattern', 'strap', 'Path for base', path_svg, 'seamline_style'))
        seam_allowance = getattr(self.cd, 'seam_allowance', 0)
        moveP(path_svg, base_pt)
        lineP(path_svg, offsetPoint(base_pt, 0, strap_width * 4))
        moveP(path_svg, offsetPoint(base_pt, strap_length, 0))
        lineP(path_svg, offsetPoint(base_pt, strap_length, strap_width * 4))
        
        for i in range(5):
            moveP(path_svg, offsetPoint(base_pt, 0, strap_width * i))
            lineP(path_svg, offsetPoint(base_pt, strap_length, strap_width * i))
        if seam_allowance > 0:
            path_cut = path()
            moveP(path_cut, base_pt)
            lineP(path_cut, offsetPoint(base_pt, -seam_allowance, 0))
            lineP(path_cut, offsetPoint(base_pt, -seam_allowance, strap_width * 4))
            lineP(path_cut, offsetPoint(base_pt, strap_length + seam_allowance, strap_width * 4))
            lineP(path_cut, offsetPoint(base_pt, strap_length + seam_allowance, 0))
            lineP(path_cut, base_pt)
            part.add(Path('pattern', 'cut', 'Path for cut', path_cut, 'cuttingline_style'))
            
        return part

    def pattern(self):
        """
        Method defining a pattern design. This is where the designer places
        all elements of the design definition
        """
        cd = self.cd

        self.radius = getattr(self.cd, 'radius',
                         getattr(self.cd, 'diameter',
                                 getattr(self.cd, 'circumference', 0) / (2 * math.pi)) / 2)
        self.circumference = 2 * math.pi * self.radius
        
        self.cfg['clientdata'] = cd
        self.cfg['paper_width']  = ( max(getattr(self.cd, 'strap_length', 0), self.cd.width + self.cd.depth) + 4 * getattr(self.cd, 'seam_allowance', 0) )
        self.cfg['border']       = ( 0.5 * CM_TO_PX )        # document borders
        border = self.cfg['border']
        # create the document info and fill it in
        # TODO - abstract these into configuration file(s)
        metainfo = {'companyName':'Test Company',      # mandatory
                    'designerName':'Sacha Chua',      # mandatory
                    'patternName':'Box tote',  # mandatory
                    'patternNumber':'1'         # mandatory
                    }
        self.cfg['metainfo'] = metainfo

        # attributes for the entire svg document
        docattrs = {'currentScale' : "0.05 : 1",
                    'fitBoxtoViewport' : "True",
                    'preserveAspectRatio' : "xMidYMid meet",
                    }

        doc = Document(self.cfg, name = 'document', attributes = docattrs)

        # Set up the title block
        tb = TitleBlock('pattern', 'titleblock', self.cfg['border'], self.cfg['border'], stylename = 'titleblock_text_style')
        doc.add(tb)
        
        # The whole pattern
        tp = Pattern('layout')
        doc.add(tp)

        # Set up styles dictionary in the pattern object
        tp.styledefs.update(self.styledefs)
        tp.add(self.makeReferenceSquare(pPoint(0, 0)))
        tp.add(self.makePart(pPoint(0, 0)))
        if getattr(self.cd, 'strap_length', 0) > 0:
            print "ADding strap"
            tp.add(self.makeStrap(pPoint(0, 0)))
        
        # call draw once for the entire pattern
        doc.draw()
        return

# vi:set ts=4 sw=4 expandtab:

