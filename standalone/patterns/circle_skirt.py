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
# - length
# - waist_circumference
# - sweep (0.25 for quarter-circle, 0.5 for half-circle, etc.)
#   - if specifying sweep in a client measurement file, use type: string
# - optional:
#   - hem_allowance
#   - seam_allowance
#   - waist_seam_allowance
#   - fabric_width - determines whether you will need to cut multiple pieces
#   - pieces

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

    def prepareArcP(self, center, rx, ry, angle_start, angle_end):
        start_point = offsetPoint(center, rx * math.cos(angle_start), ry * math.sin(angle_start))
        end_point = offsetPoint(center, rx * math.cos(angle_end), ry * math.sin(angle_end))
        large = 0
        if abs(angle_end - angle_start) >  math.pi:
            large = 1
        (xmin, ymin, xmax, ymax) = boundingBoxForArc(
            start_point.x, start_point.y,
            rx, ry, 0, large, large, end_point.x, end_point.y)
        return (start_point, end_point, abs(xmax - xmin), abs(ymax - ymin))

    def makeSkirt(self, base_pt):
        # Begin pattern piece

        # Check if we need to split the pattern pieces
        # Assume no splitting of pattern pieces, for simplicity
        hem_allowance = getattr(self.cd, 'hem_allowance', 0)
        seam_allowance = getattr(self.cd, 'seam_allowance', 0)
        waist_seam_allowance = getattr(self.cd, 'waist_seam_allowance', 0)
        sweep = float(self.cd.sweep)
        pieces = max(getattr(self.cd, 'pieces', 1), math.ceil(sweep))
                
        fabric_width = getattr(self.cd, 'fabric_width', 0)
        center = base_pt
        angle = sweep * math.pi * 2 / pieces
        # Adjust for full circle, since we have to leave some room for the seam allowance
        done = False
        while not done:
            target_measure = self.cd.waist_circumference / pieces
            if angle > math.pi * 1.5:
                target_measure = target_measure + 2 * seam_allowance
            target_circumference = target_measure * 2 * math.pi / angle
            diameter = target_circumference / pi
            radius = diameter / 2 - waist_seam_allowance
            if angle > math.pi * 1.5:
                seam_angle = angle * seam_allowance / (2 * math.pi * radius * sweep / pieces)
            else:
                seam_angle = 0
            outer_radius = radius + waist_seam_allowance + self.cd.length
            hem_radius = outer_radius + hem_allowance
            (inner_start, inner_end, xdim, ydim) = self.prepareArcP(center, radius, radius, seam_angle, angle - seam_angle)
            (waist_start, waist_end, xdim, ydim) = self.prepareArcP(center, radius + waist_seam_allowance, radius + waist_seam_allowance, seam_angle, angle - seam_angle)
            (outer_start, outer_end, xdim, ydim) = self.prepareArcP(center, outer_radius, outer_radius, seam_angle, angle - seam_angle)
            (hem_start, hem_end, xdim, ydim) = self.prepareArcP(center, hem_radius, hem_radius, seam_angle, angle - seam_angle)
            dim = min(xdim, ydim)
            #print "Target measure %f Target circumference %f angle %f" % (target_measure / IN_TO_PX, target_circumference / IN_TO_PX, angle * 360 / (2 * math.pi))
            print "Radius: %.1f New waist %.1f Waist %.1f Pieces %d Dim %.1f" % (radius / IN_TO_PX, target_measure * pieces / IN_TO_PX, self.cd.waist_circumference / IN_TO_PX, pieces, dim / IN_TO_PX)
            if fabric_width == 0 or dim <= fabric_width or pieces > 100: # time to give up!
                done = True
            else:
                pieces = pieces * 2
                angle = angle / 2
                
        part = PatternPiece('pattern', 'skirt', letter = 'A', fabric = pieces, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + radius
        part.label_y = base_pt.y + radius
        
        path_svg = path()
        part.add(Path('pattern', 'outline', 'Path for skirt cut', path_svg, 'cuttingline_style'))
        rPointP(part, 'Center', center)

        large_arc = 0
        if angle > math.pi:
            large_arc = 1

        moveP(path_svg, inner_start)
        arcP(path_svg, radius, radius, inner_end, 0, large_arc)
        moveP(path_svg, hem_start)
        arcP(path_svg, hem_radius, hem_radius, hem_end, 0, large_arc)

        path_seam = path()
        part.add(Path('pattern', 'seam', 'Path for skirt seam', path_seam, 'seamline_style'))
            
        if waist_seam_allowance > 0:
            moveP(path_seam, waist_start)
            arcP(path_seam, radius + waist_seam_allowance, radius + waist_seam_allowance, waist_end, 0, large_arc)

        if seam_allowance > 0:
            # TODO Deal with different orientations
            angle1 = angleOfLineP(inner_start, hem_start)
            # Pick a point perpendicular to that angle
            seam_inner_start = pntFromDistanceAndAngleP(inner_start, seam_allowance, angle1 - math.pi / 2)
            seam_hem_start = pntFromDistanceAndAngleP(hem_start, seam_allowance, angle1 - math.pi / 2)
            angle2 = angleOfLineP(inner_end, hem_end)
            seam_inner_end = pntFromDistanceAndAngleP(inner_end, seam_allowance, angle2 + math.pi / 2)
            seam_hem_end = pntFromDistanceAndAngleP(hem_end, seam_allowance, angle2 + math.pi / 2)
            moveP(path_svg, inner_start)
            lineP(path_svg, seam_inner_start)
            lineP(path_svg, seam_hem_start)
            lineP(path_svg, hem_start)
            moveP(path_svg, inner_end)
            lineP(path_svg, seam_inner_end)
            lineP(path_svg, seam_hem_end)
            lineP(path_svg, hem_end)
        
        
        moveP(path_seam, inner_start)
        lineP(path_seam, hem_start)
        moveP(path_seam, inner_end)
        lineP(path_seam, hem_end)
        if hem_radius > outer_radius:
            path_hem = path()
            part.add(Path('pattern', 'hem', 'Path for skirt hem', path_hem, 'hemline_style'))
            moveP(path_hem, outer_start)
            arcP(path_hem, outer_radius, outer_radius, outer_end, 0, large_arc)
                
        # end of pattern piece
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
                    'patternName':'Circle skirt',  # mandatory
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
        tp.add(self.makeSkirt(pPoint(0, 0)))
        
        # call draw once for the entire pattern
        doc.draw()
        return

# vi:set ts=4 sw=4 expandtab:

