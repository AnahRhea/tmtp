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
# - one of the following:
#   - circumference
#   - diameter
#   - radius
# 
# No seam allowances added

from tmtpl.constants import *
from tmtpl.pattern   import *
from tmtpl.document   import *

from tmtpl.client   import Client
from tmtpl.curves    import GetCurveControlPoints, FudgeControlPoints, curveThroughPoints

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

    def makeBase(self, base_pt):
        # Begin pattern piece
        part = PatternPiece('pattern', 'circle', letter = 'A', fabric = 1, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + self.radius
        part.label_y = base_pt.y + self.radius
        path_svg = path()
        part.add(Path('pattern', 'circle', 'Path for base', path_svg, 'seamline_style'))
        moveP(path_svg, offsetPoint(base_pt, 0, self.radius))
        # TODO: Add support for SVG circles and ellipses someday
        arcP(path_svg, self.radius, self.radius, offsetPoint(base_pt, self.radius * 2, self.radius))
        arcP(path_svg, self.radius, self.radius, offsetPoint(base_pt, 0, self.radius))        
        # end of pattern piece
        return part

    def makeSide(self, base_pt):
        part = PatternPiece('pattern', 'side', letter = 'B', fabric = 1, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + 0.25 * IN_TO_PX
        part.label_y = base_pt.y + 0.25 * IN_TO_PX
        path_svg = path()
        part.add(Path('pattern', 'side', 'Path for side', path_svg, 'seamline_style'))
        moveP(path_svg, base_pt)
        lineP(path_svg, offsetPoint(base_pt, self.circumference, 0))
        lineP(path_svg, offsetPoint(base_pt, self.circumference, self.cd.height))
        lineP(path_svg, offsetPoint(base_pt, 0, self.cd.height))
        lineP(path_svg, base_pt)
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
        self.cfg['paper_width']  = ( self.circumference + (self.radius * 2) + 2 * IN_TO_PX )
        self.cfg['border']       = ( 0.5 * CM_TO_PX )        # document borders
        border = self.cfg['border']
        # create the document info and fill it in
        # TODO - abstract these into configuration file(s)
        metainfo = {'companyName':'Test Company',      # mandatory
                    'designerName':'Sacha Chua',      # mandatory
                    'patternName':'Cylinder',  # mandatory
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
        tp.add(self.makeSide(pPoint(0, 0)))
        tp.add(self.makeBase(pPoint(0, 0)))
        
        # call draw once for the entire pattern
        doc.draw()
        return

# vi:set ts=4 sw=4 expandtab:

