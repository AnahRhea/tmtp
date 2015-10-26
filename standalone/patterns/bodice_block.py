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
# This pattern is based on the Burda basic bodice block
# http://www.burdastyle.com/techniques/constructing-the-basic-bodice-block/technique_steps/1
# , which is adapted from Winifred Aldrich, Metric Pattern Cutting for
# Women's Wear, 5th ed., Blackwell Publishing: Oxford, 2008, 215 pp.
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
        part.label_x = base_pt.x + 1.5 * IN_TO_PX
        part.label_y = base_pt.y + 0.25 * IN_TO_PX
        return part

    def estimateNapeToWaist(self):
        return getattr(self.cd, 'nape_to_waist',
                       (0.4 * (self.cd.bust_circumference - 88 * CM_TO_PX) / 4) + 41 * CM_TO_PX)

    def estimateNeck(self): # TODO: Verify
        return getattr(self.cd, 'neck_circumference',
                       (1 * (self.cd.bust_circumference - 88 * CM_TO_PX)) + 37 * CM_TO_PX)

    def estimateShoulder(self):
        return getattr(self.cd, 'shoulder', 
                        12.25 * CM_TO_PX + 0.25 * (self.cd.bust_circumference - 88 * CM_TO_PX) / 4)

    def estimateBackBustWidth(self):
        return getattr(self.cd, 'back_bust_width',
                       34.4 * CM_TO_PX + (self.cd.bust_circumference - 88 * CM_TO_PX) / 4)

    def estimateChestMeasurement(self):
        return getattr(self.cd, 'front_underarm_width',
                       32.4 * CM_TO_PX + 1.2 * (self.cd.bust_circumference - 88 * CM_TO_PX) / 4)

    def estimateDartMeasurement(self):
        return 7 * CM_TO_PX + 0.6 * (self.cd.bust_circumference - 88 * CM_TO_PX) / 4

    def estimateArmscyeDepth(self):
        return getattr(self.cd, 'armscye_depth',
                       21 * CM_TO_PX + (self.cd.bust_circumference - 120 * CM_TO_PX) * 0.4 / 4)
            
    def makeFrontPart(self, base_pt):
        # Begin pattern piece
        part = PatternPiece('pattern', 'front', letter = 'A', fabric = 1, interfacing = 0, lining = 0)
        # set the label location. Someday this should be automatic
        part.label_x = base_pt.x + 0.5 * IN_TO_PX
        part.label_y = base_pt.y + 4 * IN_TO_PX

        path_svg = path()
        part.add(Path('pattern', 'path', 'Path for front', path_svg, 'seamline_style'))

        # Step 2
        pt_a = offsetPoint(base_pt, 0, 1.5 * CM_TO_PX)
        # Step 3
        pt_b = offsetPoint(pt_a, 0, self.estimateArmscyeDepth() + 0.5 * CM_TO_PX)
        # Step 4
        pt_c = offsetPoint(pt_b, self.cd.bust_circumference / 2 + 5 * CM_TO_PX, 0)
        # Step 5
        if (self.cd.bust_circumference > 92 * CM_TO_PX):         
            pt_d = pPoint(pt_c.x,
                           base_pt.y - (self.cd.bust_circumference - 92 * CM_TO_PX) / 8)
        else:
            pt_d = pPoint(pt_c.x, base_pt.y)
        # Step 6
        pt_e = offsetPoint(pt_a, 0, self.estimateNapeToWaist())
        # Step 7
        pt_f = pPoint(pt_c.x, pt_e.y)
        # Step 8
        pt_g = offsetPoint(base_pt, self.estimateNeck() / 5 - 0.2 * CM_TO_PX, 0)
        # Step 10
        pt_h = offsetPoint(pt_a, 0, self.cd.armscye_depth / 5 - 0.7 * CM_TO_PX)
        # Step 11
        pt_i = pntIntersectLineCircleP(pt_g, self.estimateShoulder() + 1 * CM_TO_PX, pt_h, pPoint(pt_d.x, pt_h.y)).p1
        # Step 12
        pt_j = pntMidPointP(pt_g, pt_i)
        pt_k = offsetPoint(pt_j, -1 * CM_TO_PX, 5 * CM_TO_PX)
        # Step 13: Make sure darts are same length
        min_diff = 100000
        for step in xrange(-20, 20):
            first_part = step * 0.1
            temp_pt_shoulder_1 = pntOnLineP(pt_j, pt_i, first_part * CM_TO_PX)
            temp_pt_shoulder_2 = pntOnLineP(pt_j, pt_g, (1 - first_part) * CM_TO_PX)
            temp_diff = abs(lineLengthP(pt_k, temp_pt_shoulder_1) - lineLengthP(pt_k, temp_pt_shoulder_2))
            if temp_diff < min_diff:
                pt_shoulder_1 = temp_pt_shoulder_1
                pt_shoulder_2 = temp_pt_shoulder_2
                min_diff = temp_diff
            elif temp_diff > min_diff:
                break
        # Step 14
        pt_l = offsetPoint(pt_b, self.estimateBackBustWidth() / 2 + 0.5 * CM_TO_PX, 0)
        # Step 15
        pt_m = pPoint(pt_l.x, pt_h.y)
        # Step 16
        pt_n = pntMidPointP(pt_l, pt_m)
        pt_p = pntMidPointP(pt_b, pt_l)
        pt_q = pPoint(pt_p.x, pt_e.y)
        # Step 17
        pt_r = pntOnLineP(pt_d, base_pt, self.estimateNeck() / 5 - 0.7 * CM_TO_PX)
        # Step 18
        pt_s = offsetPoint(pt_d, 0, self.estimateNeck() / 5 - 0.2 * CM_TO_PX)
        # Step 20
        pt_t = offsetPoint(pt_c, - self.estimateChestMeasurement() / 2 - self.estimateDartMeasurement() / 2, 0)
        # Step 21
        pt_u = pntOnLineP(pt_c, pt_t, getattr(self.cd, 'front_bust_points_distance', lineLengthP(pt_c, pt_t)) / 2)
        pt_v = pPoint(pt_u.x, pt_f.y)
        # Step 22
        pt_bp = offsetPoint(pt_u, 0, 2.5 * CM_TO_PX)
        # Step 23
        pt_w = pntOnLineP(pt_r, base_pt, self.estimateDartMeasurement())
        # Step 24
        tempPt1 = offsetPoint(pt_i, 0, 1.5 * CM_TO_PX)
        tempPt2 = pPoint(pt_w.x, tempPt1.y)
        # Step 25
        pt_x = pntIntersectLineCircleP(pt_w, self.estimateShoulder(), tempPt1, tempPt2).p2
        # Step 26
        pt_y = offsetPoint(pt_t, 0, -self.cd.armscye_depth / 3)
        pt_z = pntMidPointP(pt_l, pt_t)
        pt_aa = pPoint(pt_z.x, pt_f.y)
        # Step 27
        if self.cd.bust_circumference <= 82 * CM_TO_PX:
            distance_l = 2.25 * CM_TO_PX
            distance_t = 1.75 * CM_TO_PX
        elif self.cd.bust_circumference <= 94 * CM_TO_PX:
            distance_l = 2.5 * CM_TO_PX
            distance_t = 2 * CM_TO_PX
        elif self.cd.bust_circumference <= 104 * CM_TO_PX:
            distance_l = 3 * CM_TO_PX
            distance_t = 2.5 * CM_TO_PX
        else:
            distance_l = 3.5 * CM_TO_PX
            distance_t = 3 * CM_TO_PX

        pt_armscye_l = pntFromDistanceAndAngleP(pt_l, distance_l, -3.14159 / 4)
        pt_armscye_t = pntFromDistanceAndAngleP(pt_t, distance_t, -3.14159 * 3 / 4)
        # Step 29: Guess waistline adjustment
        if self.cd.bust_circumference <= 82 * CM_TO_PX:
            waist_adjustment = 0.5 * CM_TO_PX
        elif self.cd.bust_circumference <= 94 * CM_TO_PX:
            waist_adjustment = 1.0 * CM_TO_PX
        else:
            waist_adjustment = 1.5 * CM_TO_PX
        pt_ab = offsetPoint(pt_f, 0, waist_adjustment)
        # Step 30
        waist_removal = self.cd.bust_circumference + 3 * CM_TO_PX - self.cd.waist_circumference
        scaling_factor = 1
        if waist_removal / CM_TO_PX < 18:
            scaling_fator = (waist_removal / CM_TO_PX) / 18
        pt_q_ab = pntIntersectLinesP(pt_p, pPoint(pt_p.x, pt_ab.y), pt_e, pt_ab)
        pt_aa_ab = pntIntersectLinesP(pt_aa, pPoint(pt_aa.x, pt_ab.y), pt_e, pt_ab)
        pt_v_ab = pntIntersectLinesP(pt_v, pPoint(pt_v.x, pt_ab.y), pt_e, pt_ab)
        dart1_1 = pntOnLineP(pt_q_ab, pt_e, scaling_factor * 2.5 * CM_TO_PX / 2)
        dart1_2 = pntOnLineP(pt_q_ab, pt_ab, scaling_factor * 2.5 * CM_TO_PX / 2)
        dart2_1 = pntOnLineP(pt_aa_ab, pt_e, scaling_factor * 1 * CM_TO_PX)
        dart2_2 = pntOnLineP(pt_aa_ab, pt_ab, scaling_factor * 2 * CM_TO_PX)
        dart3_1 = pntOnLineP(pt_v_ab, pt_e, scaling_factor * 3.5 * CM_TO_PX / 2)
        dart3_2 = pntOnLineP(pt_v_ab, pt_ab, scaling_factor * 3.5 * CM_TO_PX / 2)

        rPointP(part, 'A', pt_a)
        rPointP(part, 'B', pt_b)
        rPointP(part, 'C', pt_c)
        rPointP(part, 'D', pt_d)
        rPointP(part, 'E', pt_e)
        rPointP(part, 'F', pt_f)
        rPointP(part, 'G', pt_g)
        rPointP(part, 'H', pt_h)
        rPointP(part, 'I', pt_i)
        rPointP(part, 'J', pt_j)
        rPointP(part, 'K', pt_k)
        rPointP(part, 'L', pt_l)
        rPointP(part, 'M', pt_m)
        rPointP(part, 'N', pt_n)
        rPointP(part, 'P', pt_p)
        rPointP(part, 'Q', pt_q)
        rPointP(part, 'R', pt_r)
        rPointP(part, 'S', pt_s)
        rPointP(part, 'T', pt_t)
        rPointP(part, 'U', pt_u)
        rPointP(part, 'V', pt_v)
        rPointP(part, 'BP', pt_bp)
        rPointP(part, 'W', pt_w)
        rPointP(part, 'X', pt_x)
        rPointP(part, 'Y', pt_y)
        rPointP(part, 'Z', pt_z)
        rPointP(part, 'AA', pt_aa)
        rPointP(part, 'AB', pt_ab)
        
        moveP(path_svg, base_pt)
        lineP(path_svg, pt_a)
        moveP(path_svg, pt_a)
        lineP(path_svg, pt_b)
        # lineP(path_svg, base_pt)

        moveP(path_svg, pt_b)
        lineP(path_svg, pt_c)

        moveP(path_svg, pt_c)
        lineP(path_svg, pt_d)

        moveP(path_svg, pt_b)
        lineP(path_svg, pt_e)

        moveP(path_svg, pt_e)
        lineP(path_svg, pt_f)
        lineP(path_svg, pt_c)


        # Step 9
        moveP(path_svg, pt_g)
        control1 = offsetPoint(pt_a, 2 * CM_TO_PX, 0)
        control2 = offsetPoint(pt_g, 0, 2 * CM_TO_PX)
        cubicCurveP(path_svg, control2, control1, pt_a)

        moveP(path_svg, pt_h)
        pt_half_b_c = offsetPoint(pt_h, (pt_c.x - pt_b.x) / 2, 0)
        lineP(path_svg, pt_half_b_c)
        
        moveP(path_svg, pt_g)
        lineP(path_svg, pt_i)

        # Draw dart
        moveP(path_svg, pt_shoulder_1)
        lineP(path_svg, pt_k)
        lineP(path_svg, pt_shoulder_2)

        moveP(path_svg, pt_l)
        lineP(path_svg, pt_m)

        moveP(path_svg, pt_p)
        lineP(path_svg, pt_q)

        moveP(path_svg, pt_d)
        lineP(path_svg, pt_r)

        # Step 19
        moveP(path_svg, pt_r)
        control1 = offsetPoint(pt_r, 0, (pt_s.y - pt_r.y) / 2)
        control2 = offsetPoint(pt_s, - (pt_s.x - pt_r.x) / 2, 0)
        cubicCurveP(path_svg, control1, control2, pt_s)

        moveP(path_svg, pt_t)
        lineP(path_svg, pPoint(pt_t.x, pt_h.y))
        
        moveP(path_svg, pt_u)
        lineP(path_svg, pt_v)

        # Optional bust line
        moveP(path_svg, pPoint(base_pt.x, pt_bp.y))
        lineP(path_svg, pPoint(pt_d.x, pt_bp.y))

        moveP(path_svg, pt_w)
        lineP(path_svg, pt_r)
        lineP(path_svg, pt_bp)
        lineP(path_svg, pt_w)
        print "Dart side 1: ", lineLengthP(pt_bp, pt_w)
        print "Dart side 2: ", lineLengthP(pt_bp, pt_r)


        # Construction lines
        #moveP(path_svg, tempPt1)
        #lineP(path_svg, tempPt2)

        moveP(path_svg, pt_w)
        lineP(path_svg, pt_x)
        
        moveP(path_svg, pt_z)
        lineP(path_svg, pt_aa)

        moveP(path_svg, pt_l)
        lineP(path_svg, pt_armscye_l)
        moveP(path_svg, pt_t)
        lineP(path_svg, pt_armscye_t)

        # Step 28
        control_distance = lineLengthP(pt_i, pt_n) / 3
        moveP(path_svg, pt_i)
        control = pntFromDistanceAndAngleP(pt_i, control_distance, 3.14159 / 2 + angleOfLineP(pt_g, pt_i))
        control2 = pntOnLineP(pt_n, pt_m, control_distance)
        cubicCurveP(path_svg, control, control2, pt_n)
        control = pntMidPointP(pt_n, pPoint(pt_n.x, pt_armscye_l.y))
        control2 = pntFromDistanceAndAngleP(pt_armscye_l, control_distance, -3.14159 * 3 / 4)
        cubicCurveP(path_svg, control, control2, pt_armscye_l)
        control_distance = lineLengthP(pt_armscye_l, pt_z) / 4
        control = pntFromDistanceAndAngleP(pt_armscye_l, control_distance, 3.14159 / 4)
        control2 = pntOnLineP(pt_z, pt_l, control_distance)
        cubicCurveP(path_svg, control, control2, pt_z)
        control_distance = lineLengthP(pt_armscye_t, pt_z) / 3
        control = pntOnLineP(pt_z, pt_t, control_distance)
        control2 = pntFromDistanceAndAngleP(pt_armscye_t, control_distance, 3.14159 * 3 / 4)
        cubicCurveP(path_svg, control, control2, pt_armscye_t)
        control_distance = lineLengthP(pt_armscye_t, pt_y) / 3
        control = pntFromDistanceAndAngleP(pt_armscye_t, control_distance, -3.14159 / 4)
        control2 = pntOnLineP(pt_y, pt_t, control_distance)
        cubicCurveP(path_svg, control, control2, pt_y)
        control_distance = lineLengthP(pt_y, pt_x) / 3
        control = pntOffLineP(pt_y, pt_t, control_distance)
        control2 = pntFromDistanceAndAngleP(pt_x, control_distance, angleOfLineP(pt_x, pt_w) + 3.14159 / 2)
        cubicCurveP(path_svg, control, control2, pt_x)

        moveP(path_svg, pt_f)
        lineP(path_svg, pt_ab)
        lineP(path_svg, pt_e)
        
        moveP(path_svg, dart1_1)
        lineP(path_svg, pt_p)
        lineP(path_svg, dart1_2)

        moveP(path_svg, dart2_1)
        lineP(path_svg, pt_z)
        lineP(path_svg, dart2_2)

        moveP(path_svg, dart3_1)
        lineP(path_svg, pt_bp)
        lineP(path_svg, dart3_2)

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

        # CHANGE THESE DEPENDING ON WHAT YOU WANT
        self.functional_ease = 4 * IN_TO_PX
        self.front_neck_drop = 3.5 * IN_TO_PX
        self.length = 26 * IN_TO_PX

        self.cfg['paper_width']  = ( 2 * IN_TO_PX + self.cd.bust_circumference / 2 )
        self.cfg['border']       = ( 5*CM_TO_PX )        # document borders

        self.seam_allowance = 0.5 * IN_TO_PX
        self.hem_allowance = 1 * IN_TO_PX
        border = self.cfg['border']

        # create the document info and fill it in
        # TODO - abstract these into configuration file(s)
        metainfo = {'companyName':'Test Company',      # mandatory
                    'designerName':'Test Designer',      # mandatory
                    'patternName':'Bodice Block - Burda',  # mandatory
                    'patternNumber':'1'         # mandatory
                    }
        self.cfg['metainfo'] = metainfo

        self.cfg['scale'] = 1/5.0
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
        tp.add(self.makeFrontPart(pPoint(0, 2 * IN_TO_PX)))
        
        # call draw once for the entire pattern
        doc.draw()
        return

# vi:set ts=4 sw=4 expandtab:

