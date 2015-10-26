#!/usr/bin/env python
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
# This pattern is based on the Close Fitting Bodice Block
# from "Fabric Pattern Cutting" (Winifred Aldrich)
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
        part = PatternPiece('pattern', '2.5cm/1" reference', letter = 'R', fabric = 0, interfacing = 0, lining = 0)
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

# points: starting from shoulder top left (back), going counter clockwise
    # back neck, back shoulder, mid armscye back, bottom armscye back, mid armscye bottom, bottom armscye right, mid armscye front,
    # front shoulder, front neck
    def drawArmscye(self, path_svg, points, distance_back, distance_front):
        length = 0
        back_neck, back_shoulder, mid_armscye_back, bottom_armscye_back, bottom_armscye, bottom_armscye_front, mid_armscye_front, front_shoulder, front_neck = points
        pt_armscye_back = pntFromDistanceAndAngleP(bottom_armscye_back, distance_back, -3.14159 / 4)
        pt_armscye_front = pntFromDistanceAndAngleP(bottom_armscye_front, distance_front, -3.14159 * 3 / 4)
        moveP(path_svg, bottom_armscye_back)
        lineP(path_svg, pt_armscye_back)
        moveP(path_svg, bottom_armscye_front)
        lineP(path_svg, pt_armscye_front)

        control_distance = lineLengthP(front_shoulder, mid_armscye_front) / 3
        moveP(path_svg, front_shoulder)
        control = pntFromDistanceAndAngleP(front_shoulder, control_distance, 3.14159 / 2 + angleOfLineP(front_shoulder, front_neck))
        control2 = pntOffLineP(mid_armscye_front, bottom_armscye_front, control_distance)
        cubicCurveP(path_svg, control, control2, mid_armscye_front)
        length += curveLength([front_shoulder, control, control2, mid_armscye_front])
        
        control_distance = lineLengthP(mid_armscye_front, pt_armscye_front) / 3
        control = pntOnLineP(mid_armscye_front, bottom_armscye_front, control_distance)
        control2 = pntFromDistanceAndAngleP(pt_armscye_front, control_distance, -3.14159 / 4)
        cubicCurveP(path_svg, control, control2, pt_armscye_front)
        length += curveLength([mid_armscye_front, control, control2, pt_armscye_front])
        
        control_distance = lineLengthP(pt_armscye_front, bottom_armscye) / 4
        control = pntFromDistanceAndAngleP(pt_armscye_front, control_distance, 3.14159 * 3 / 4)
        control2 = pntOnLineP(bottom_armscye, bottom_armscye_front, control_distance)
        cubicCurveP(path_svg, control, control2, bottom_armscye)
        length += curveLength([pt_armscye_front, control, control2, bottom_armscye])
        
        control_distance = lineLengthP(pt_armscye_back, bottom_armscye) / 3
        control = pntOnLineP(bottom_armscye, bottom_armscye_back, control_distance)
        control2 = pntFromDistanceAndAngleP(pt_armscye_back, control_distance, 3.14159 / 4)
        cubicCurveP(path_svg, control, control2, pt_armscye_back)
        length += curveLength([bottom_armscye, control, control2, pt_armscye_back])
        
        control_distance = lineLengthP(pt_armscye_back, mid_armscye_back) / 3
        control = pntFromDistanceAndAngleP(pt_armscye_back, control_distance, -3.14159 * 3 / 4)
        control2 = pntOnLineP(mid_armscye_back, bottom_armscye_back, control_distance)
        cubicCurveP(path_svg, control, control2, mid_armscye_back)
        length += curveLength([pt_armscye_back, control, control2, mid_armscye_back])
        
        control_distance = lineLengthP(mid_armscye_back, back_shoulder) / 3
        control = pntOffLineP(mid_armscye_back, bottom_armscye_back, control_distance)
        control2 = pntFromDistanceAndAngleP(back_shoulder, control_distance, angleOfLineP(back_shoulder, back_neck) - 3.14159 / 2)
        cubicCurveP(path_svg, control, control2, back_shoulder)
        length += curveLength([mid_armscye_back, control, control2, back_shoulder])
        return length
        
    def makeBlock(self, base_pt):
        # Begin pattern piece
        part = PatternPiece('pattern', 'front', letter = 'A', fabric = 1, interfacing = 0, lining = 0)
        path_svg = path()
        part.add(Path('pattern', 'path', 'Path for block', path_svg, 'seamline_style'))
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + 0.5 * IN_TO_PX
        part.label_y = base_pt.y + 3 * CM_TO_PX
        
        pts = [None] * 35
        pts[0] = base_pt
        pts[1] = offsetPoint(pts[0], 0, 1.5 * CM_TO_PX)
        pts[2] = offsetPoint(pts[1], 0, self.cd.armscye_depth + 0.5 * CM_TO_PX)
        pts[3] = offsetPoint(pts[2], self.cd.bust_circumference / 2 + 5 * CM_TO_PX, 0)
        distance_3_4 = pts[2].y - pts[0].y
        size = 12 + (self.cd.bust_circumference / CM_TO_PX - 88) / 4
        if size >= 16:
            distance_3_4 += 0.3 * CM_TO_PX * (size - 14) / 2
        if size > 20:
            distance_3_4 += 0.5 * CM_TO_PX * (size - 18) / 2
        pts[4] = offsetPoint(pts[3], 0, -distance_3_4)
        pts[5] = offsetPoint(pts[1], 0, self.cd.nape_to_waist)
        pts[6] = pPoint(pts[3].x, pts[5].y)
        pts[7] = offsetPoint(pts[5], 0, self.cd.waist_to_hip)
        pts[8] = pPoint(pts[3].x, pts[7].y)
        pts[9] = offsetPoint(pts[0], self.cd.neck_circumference / 5 - 0.2 * CM_TO_PX, 0)
        pts[10] = offsetPoint(pts[1], 0, self.cd.armscye_depth / 5 - 0.7 * CM_TO_PX)
        pts[11] = pntIntersectLineCircleP(pts[9], self.cd.shoulder + 1 * CM_TO_PX, pts[10], pPoint(pts[4].x, pts[10].y)).p1
        
        pts[12] = pntMidPointP(pts[9], pts[11])
        pts[13] = offsetPoint(pts[12], -1 * CM_TO_PX, 5 * CM_TO_PX)
        # Step 13: Make sure darts are same length
        pt_shoulder_1 = pntOnLineP(pts[12], pts[9], 0.5 * CM_TO_PX)
        dart_length = lineLengthP(pt_shoulder_1, pts[13])
        # Define pt_shoulder_2 to be that length
        # Such that the chord between pt_shoulder_1 and pt_shoulder_2 is 1 cm
        pt_shoulder_2 = pntFromDistanceAndAngleP(pts[13], dart_length,
                                                 angleOfLineP(pts[13], pt_shoulder_1) + 2 * math.asin(0.5 * CM_TO_PX / dart_length))
        print "confirm distance between 1 and 2", lineLengthP(pt_shoulder_1, pt_shoulder_2) / CM_TO_PX
        print "confirm shoulder length", self.cd.shoulder, " =? ", lineLengthP(pts[9], pt_shoulder_1) + lineLengthP(pts[11], pt_shoulder_2)
        
        pts[14] = offsetPoint(pts[2], self.cd.back_width / 2 + 0.5 * CM_TO_PX, 0)
        pts[15] = pPoint(pts[14].x, pts[10].y)
        pts[16] = pntMidPointP(pts[14], pts[15])
        pts[17] = pntMidPointP(pts[2], pts[14])
        pts[18] = pPoint(pts[17].x, pts[5].y)
        pts[19] = pPoint(pts[17].x, pts[7].y)
        pts[20] = offsetPoint(pts[4], -self.cd.neck_circumference / 5 + 0.7 * CM_TO_PX, 0)
        pts[21] = offsetPoint(pts[4], 0, self.cd.neck_circumference / 5 - 0.2 * CM_TO_PX)
        pts[22] = offsetPoint(pts[3], -(self.cd.chest + self.cd.dart) / 2, 0)
        pts[23] = pntMidPointP(pts[22], pts[3])
        pts[24] = pPoint(pts[23].x, pts[5].y)
        pts[25] = pPoint(pts[23].x, pts[7].y)
        pts[26] = offsetPoint(pts[23], 0, 2.5 * CM_TO_PX)
        pts[27] = offsetPoint(pts[20], -self.cd.dart, 0)
        pts[28] = offsetPoint(pts[11], 0, 1.5 * CM_TO_PX)
        pts[29] = offsetPoint(pts[28], 10 * CM_TO_PX, 0)
        pts[30] = pntIntersectLineCircleP(pts[27], self.cd.shoulder, pts[28], pts[29]).p2
        pts[31] = offsetPoint(pts[22], 0, -(pts[3].y - pts[21].y) / 3)
        pts[32] = pntMidPointP(pts[14], pts[22])
        pts[33] = pPoint(pts[32].x, pts[5].y)
        pts[34] = pPoint(pts[32].x, pts[7].y)

        for i in range(len(pts)):
            rPointP(part, str(i), pts[i])

        moveP(path_svg, pts[1])
        lineP(path_svg, pts[7])
        lineP(path_svg, pts[8])
        lineP(path_svg, pts[21])
        
        control1 = offsetPoint(pts[21], (pts[20].x - pts[21].x) / 3, 0)
        control2 = offsetPoint(pts[20], 0, (pts[21].y - pts[20].y) / 3)
        cubicCurveP(path_svg, control1, control2, pts[20])

        lineP(path_svg, pts[26])
        lineP(path_svg, pts[27])
        lineP(path_svg, pts[30])

        # Draw armscye - complicated
        if self.cd.bust_circumference <= 92 * CM_TO_PX:
            distance_14 = 2.5 * CM_TO_PX
            distance_22 = 2 * CM_TO_PX
        elif self.cd.bust_circumference <= 104 * CM_TO_PX:
            distance_14 = 3 * CM_TO_PX
            distance_22 = 2.5 * CM_TO_PX
        else:
            distance_14 = 3.5 * CM_TO_PX
            distance_22 = 3 * CM_TO_PX
        
        armscye_length = self.drawArmscye(path_svg,
                                          [pts[12], pts[11], pts[16], pts[14], pts[32], pts[22], pts[31], pts[30], pts[27]],
                                          distance_14, distance_22)
        print "Armscye length: ", armscye_length / CM_TO_PX, "cm or ", armscye_length / IN_TO_PX, "in"
        lineP(path_svg, pt_shoulder_2)
        lineP(path_svg, pts[13])
        lineP(path_svg, pt_shoulder_1)
        lineP(path_svg, pts[9])
        
        control = offsetPoint(pts[9], 0, (pts[1].y - pts[9].y) / 3)
        control2 = offsetPoint(pts[1], (pts[9].x - pts[1].x) / 3, 0)
        cubicCurveP(path_svg, control, control2, pts[1])

        moveP(path_svg, pts[2])
        lineP(path_svg, pts[3])
        
        moveP(path_svg, pts[5])
        lineP(path_svg, pts[6])

        moveP(path_svg, pts[17])
        lineP(path_svg, pts[19])

        moveP(path_svg, pts[32])
        lineP(path_svg, pts[34])

        moveP(path_svg, pts[23])
        lineP(path_svg, pts[25])
        
        # end of pattern piece
        return part

    def pattern(self):
        """
        Method defining a pattern design. This is where the designer places
        all elements of the design definition
        """

        # The following attributes are set before calling this method:
        #
        # self.cd - Client Data, which has been loaded from the client data file
        #
        # self.styledefs - the style difinition dictionary, loaded from the styles file
        #
        # self.cfg - configuration settings from the main app framework
        #
        # TODO find a way to get this administrative cruft out of this pattern method

        cd = self.cd
        self.cfg['clientdata'] = cd

        self.functional_ease = 4 * IN_TO_PX
        self.front_neck_drop = 3.5 * IN_TO_PX
        
        self.cfg['paper_width']  = ( self.cd.hip_circumference + 5 * IN_TO_PX)
        self.cfg['border']       = ( 5*CM_TO_PT )        # document borders

        self.length = 26 * IN_TO_PX
        self.seam_allowance = 0.5 * IN_TO_PX
        self.hem_allowance = 1 * IN_TO_PX
        border = self.cfg['border']

        # create the document info and fill it in
        # TODO - abstract these into configuration file(s)
        metainfo = {'companyName':'Test Company',      # mandatory
                    'designerName':'Test Designer',      # mandatory
                    'patternName':'Bodice Block - Fabric Pattern Cutting (Winifred Aldrich)',  # mandatory
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
        tp.add(self.makeReferenceSquare(pPoint(0, 2 * IN_TO_PX)))
        tp.add(self.makeBlock(pPoint(0, 2 * IN_TO_PX)))
        
        # call draw once for the entire pattern
        doc.draw()
        return

# vi:set ts=4 sw=4 expandtab:

