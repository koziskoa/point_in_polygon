from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from math import *

class Algorithms:
    """
    A class to store algorithms for polygon generalization and other auxiliary methods.

    Methods for creating convex hull
    ----------
    jarvisScan(pol:QPolygonF)

    grahamScan(pol:QPolygonF)
    
    Methods for polygon generalization
    ----------
    minAreaEnclosingRectangle(pol: QPolygonF)

    wallAverage(pol:QPolygonF)

    longestEdge(pol:QPolygonF)

    weightedBisector(pol:QPolygonF)

    Auxiliary methods
    ----------
    get2LinesAngle(p1:QPointF,p2:QPointF,p3:QPointF,p4:QPointF):
        Computes angle between two given lines.

    getPolarAngle(p1:QPointF,p2:QPointF):
        Computes polar angle (slope) between two given points.

    vectorOrientation(p1:QPointF,p2:QPointF,p3:QPointF):
        Determines orientation given by two input vectors.

    findPivot(pol:QPolygonF):
        Returns point with minimum y coordinate.

    sortPoints(pol:QPolygonF, q:QPointF):
        Sorts dataset of points first by angle between a pivot and given point,
        then second by their Euclidean distance.

    rotate(pol:QPolygonF):
        Rotates polygon according to a given angle.

    minMaxBox(pol:QPolygonF):
        Creates min max box (bounding box) and computes its area.

    computeArea(pol:QPolygonF):
        Computes area of a given polygon.

    resizeRectangle(er:QPolygonF, pol:QPolygonF):
        Resizes polygon according to area of a given polygon.

    checkValidity(pol:QPolygonF):
        Checks if input polygon has at least three vertices for constructing
        convex hull or enclosing rectangle.

    euclidDistance(p1:QPointF, p2:QPointF):
        Computes Euclidean distance.

    findDiagonals(ch:QPolygonF)
        Returns list of all relevant diagonals of input convex hull (polygon).

    intersectionTest(p1:QPointF, p2:QPointF, pol:QPolygonF):
        Determines whether given diagonal (line) intersects with one of edges of input building.

    setDiagonals(diagonals:list, pol:QPolygonF):
        Returns two longest diagonals of input polygon (convex hull).
    """

    def __init__(self):
        pass

    def jarvisScan(pol: QPolygonF):
        """Creates convex hull by using Jarvis scan algorithm."""
        # Check for any lines or points
        if Algorithms.checkValidity(pol) == False:
            return False

        # Initialize convex hull
        ch = QPolygonF()

        # Find pivot
        q = min(pol, key=lambda k: k.y())

        # Initialize auxiliary point with the same y value as pivot
        pj_1 = QPointF(q.x() - 1, q.y())
        pj = q

        # Add pivot to convex hull
        ch.append(q)

        # Jarvis scan
        while True:
            # Initialize maximum
            phi_max = 0
            i_max = -1

            # Find suitable point for maximizing angle
            for i in range(len(pol)):
                # Proceed if points are not identical
                if pj != pol[i]:
                    # Measure angle
                    phi = Algorithms.get2LinesAngle(pj, pj_1, pj, pol[i])

                    # Update phi_max
                    if phi > phi_max:
                        phi_max = phi
                        i_max = i

            # Append point to convex hull
            ch.append(pol[i_max])

            # Update last two points
            pj_1 = pj
            pj = pol[i_max]

            # Stop condition
            if pj == q:
                break

        return ch

    def grahamScan(pol: QPolygonF):
        """Creates convex hull by using Graham scan algorithm."""
        # Check for any lines or points
        if Algorithms.checkValidity(pol) == False:
            return False

        # Find pivot
        q = Algorithms.findPivot(pol)
        # Initialize convex hull
        ch = QPolygonF()
        # Sort polygon points accordingly
        sorted_points = Algorithms.sortPoints(pol, q)
        # Initialize auxiliary list
        ch_list = []
        n = len(pol)

        # Graham Scan
        for i in range(n):
            # Append first two points
            while len(ch_list) >= 2:
                # Check for CW direction instead of CCW as the y axis is flipped
                if Algorithms.vectorOrientation(ch_list[-2], ch_list[-1], sorted_points[i]) == -1:
                    break
                # Pop unsuitable point
                else:
                    ch_list.pop()

            # Append point to auxiliary list
            ch_list.append(sorted_points[i])
        # Fit auxiliary list to convex hull polygon
        ch = QPolygonF(ch_list)

        return ch

    def minAreaEnclosingRectangle(pol: QPolygonF):
        """Creates minimum area enclosing rectangle."""
        # Create convex hull is possible
        ch = Algorithms.ch_alg(pol)
        if ch == False:
            return False
        # Get minmax box, its area and initialize minimum angle sigma
        mmb_min, area_min = Algorithms.minMaxBox(ch)
        sigma_min = 0

        # Process all segments of convex hull
        for i in range(len(ch)-1):
            # Compute slope of segment as angle sigma
            dx = ch[i+1].x() - ch[i].x()
            dy = ch[i+1].y() - ch[i].y()
            sigma = atan2(dy,dx)
            # Rotate convex hull
            ch_rot = Algorithms.rotate(ch, -sigma)
            # Find mmb and area over rotated convex hull
            mmb, area = Algorithms.minMaxBox(ch_rot)
            # Update minimum area, minmaxbox and slope angle sigma
            if area < area_min:
                area_min = area
                mmb_min = mmb
                sigma_min = sigma

        # Rotate minmax box back
        er = Algorithms.rotate(mmb_min, sigma_min)
        # Resize rectangle
        res = Algorithms.resizeRectangle(er, pol)

        return res

    def wallAverage(pol: QPolygonF):
        """Returns generalized polygon by using Wall average algorithm."""
        # Check for lines/points as no convex hull is created
        if Algorithms.checkValidity(pol) == False:
            return False

        # Compute slope angle sigma
        dx = pol[1].x() - pol[0].x()
        dy = pol[1].y() - pol[0].y()
        sigma = atan2(dy, dx)
        n = len(pol)
        # Initialize average remainder
        r_aver = 0

        # Process all edges
        for i in range(1, n):
            dx_i = pol[(i + 1) % n].x() - pol[i].x()
            dy_i = pol[(i + 1) % n].y() - pol[i].y()
            # Compute slope angle sigma for current segment
            sigma_i = atan2(dy_i, dx_i)
            # Direction difference
            delta_sigma_i = sigma_i - sigma
            # Adjust direction difference if less than 0
            if delta_sigma_i < 0:
                delta_sigma_i += 2 * pi
            # Fraction by pi/2
            k_i = round(2 * delta_sigma_i / pi)
            # Compute remainder for current segment
            r_i = delta_sigma_i - (k_i * (pi / 2))
            # Update average remainder
            r_aver += r_i

        # Compute average remainder (arithmetic)
        r_aver = r_aver / n
        # Set average_rotation
        sigma_aver = sigma + r_aver
        # Rotate building
        pol_rot = Algorithms.rotate(pol, -sigma_aver)
        # Find mmb and area of rotated building
        mmb, area = Algorithms.minMaxBox(pol_rot)
        # Rotate minmax box back
        er = Algorithms.rotate(mmb, sigma_aver)
        # Resize rectangle
        res = Algorithms.resizeRectangle(er, pol)

        return res

    def longestEdge(pol: QPolygonF):
        """Returns generalized polygon by using Longest Edge algorithm."""
        n = len(pol)
        # Initialize longest edge
        longest_edge = -1

        # Process all edges
        for i in range(n):
            current_edge_length = Algorithms.euclidDistance(pol[i], pol[(i + 1) % n])
            # Find longest edge of building
            if current_edge_length > longest_edge:
                longest_edge = current_edge_length
                dx = pol[(i + 1) % n].x() - pol[i].x()
                dy = pol[(i + 1) % n].y() - pol[i].y()

        # Find slope angle sigma of longest edge
        sigma = atan2(dy, dx)
        # Rotate building
        building_rot = Algorithms.rotate(pol, -sigma)
        # Find minmax box and area of rotated building
        mmb, area_l = Algorithms.minMaxBox(building_rot)
        # Rotate minmax box back
        er = Algorithms.rotate(mmb, sigma)
        # Resize rectangle
        res = Algorithms.resizeRectangle(er, pol)

        return res

    def weightedBisector(pol: QPolygonF):
        """Returns generalized polygon by using Weighted Bisector algorithm."""
        # Create convex hull if possible
        ch = Algorithms.ch_alg(pol)
        if ch == False:
            return False

        # If the building is triangular, return as no diagonals can be computed
        if len(ch) == 4: # GPolygonF 
            return ch

        # Get diagonals of convex hull
        diagonals = Algorithms.findDiagonals(ch)
        # Sort diagonals by their length
        diagonals.sort(key=lambda k: k[2], reverse=True)
        # Set two longest diagonals and their slope angles
        sigma1, dist1, sigma2, dist2 = Algorithms.setDiagonals(diagonals, pol)
        # Compute slope angle sigma as the main direction of the building
        sigma = (dist1 * sigma1 + dist2 * sigma2) / (dist1 + dist2)
        # Rotate building
        building_rot = Algorithms.rotate(pol, -sigma)
        # Find minmax box and area of rotated building
        mmb, area = Algorithms.minMaxBox(building_rot)
        # Rotate minmax box back
        er = Algorithms.rotate(mmb, sigma)
        # Resize rectangle
        res = Algorithms.resizeRectangle(er, pol)

        return res

    def get2LinesAngle(p1:QPointF,p2:QPointF,p3:QPointF,p4:QPointF):
        """
        Computes angle between two given lines.

            Parameters:
                p1, p2, p3, p4 (QPoint): Vertices of two lines.

            Returns:
               (float) Angle between input lines.
        """
        # Get vector components of the first line
        ux = p2.x()-p1.x()
        uy = p2.y()-p1.y()
        # Get vector components of the second line
        vx = p4.x()-p3.x()
        vy = p4.y()-p3.y()
        # Calculate dot product
        dp = ux*vx + uy*vy
        # Calculate norms for both vectors
        nu = sqrt(ux**2 + uy**2)
        nv = sqrt(vx**2 + vy**2)

        cos_angle = dp / (nu * nv)
        cos_angle = max(min(cos_angle,1), -1)

        return acos(cos_angle)
    

    def getPolarAngle(p1:QPointF, p2:QPointF):
        """
        Computes polar angle (slope) between two given points.

            Parameters:
                p1, p2 (QPoint): Vertices of a line.

            Returns:
               (float) Polar angle of input line.
        """
        dx = p2.x() -p1.x()
        dy = p2.y() - p1.y()

        return atan2(dy, dx)

    def vectorOrientation(p1:QPointF, p2:QPointF, p3:QPointF):
        """
        Determines orientation given by two input vectors.

            Parameters:
                p1, p3 (QPointF): Endpoints of input vectors.
                p2 (QPointF): Common vertex for both input vectors.

            Returns:
               1: counterclockwise orientation
               -1: clockwise orientation
               0: vectors are collinear
        """
        # Calculate cross product
        cross_prod = (p1.x() - p2.x()) * (p3.y() - p2.y()) - (p1.y() - p2.y()) * (p3.x() - p2.x())

        #Determine orientation
        if cross_prod > 0:
            return 1

        elif cross_prod < 0:
            return -1

        else:
            return 0

    def findPivot(pol:QPolygonF):
        """
        Returns point with minimum y coordinate.
        If there are multiple points with the min y-coord, returns the point with minimum x and y coordinates.

            Parameters:
                pol (QPolygonF): Input polygon.

            Returns:
               pivot (QPointF): Point with minimum y (or x and y) coordinate(s).
        """
        pivot = min(pol, key = lambda k : (k.y(), k.x()))
        return pivot

    def sortPoints(pol:QPolygonF, q:QPointF):
        """
        Sorts dataset of points first by angle between a pivot and given point,
        then second by their Euclidean distance.

            Parameters:
                pol (QPolygonF): Input polygon.
                q (QPointF): Pivot point.

            Returns:
               sorted_points (list): List of points in polygon sorted in ascending order.
        """
        sorted_points = []
        # Append each point
        for point in pol:
            sorted_points.append(point)
        # Sort by polar angle, then by Euclidean distance
        sorted_points.sort(key = lambda k: (Algorithms.getPolarAngle(q, k), Algorithms.euclidDistance(q, k)))

        return sorted_points

    def rotate(pol: QPolygonF, sig: float) -> QPolygonF:
        """Rotates polygon according to a given angle."""
        pol_rot = QPolygonF()

        # Process all polygon vertices
        for i in range(len(pol)):
            # Rotate point
            x_rot = pol[i].x()*cos(sig)-pol[i].y()*sin(sig)
            y_rot = pol[i].x()*sin(sig)+pol[i].y()*cos(sig)

            # Create QPointF object, set new coordinates
            q_point = QPointF(x_rot,y_rot)
            # Append new QPointF to polygon
            pol_rot.append(q_point)

        return pol_rot
    
    def minMaxBox(pol:QPolygonF):
        """
        Creates min max box (bounding box) and computes its area.

            Parameters:
                pol (QPolygonF): Input polygon.

            Returns:
               minmax_box (QPolygonF): Min max box (bounding box) of input polygon.
               area (float): Area of min max box.
        """
        # Find extreme coordinates
        x_min = min(pol, key = lambda k:k.x()).x()
        x_max = max(pol, key = lambda k:k.x()).x()
        y_min = min(pol, key = lambda k:k.y()).y()
        y_max = max(pol, key = lambda k:k.y()).y()
        
        # Create min max box vertices
        v1 = QPointF(x_min, y_min)
        v2 = QPointF(x_max, y_min)
        v3 = QPointF(x_max, y_max)
        v4 = QPointF(x_min, y_max)

        # Append vertices to minmax box
        minmax_box = QPolygonF([v1,v2,v3,v4])

        # Compute area of minmax box
        a = x_max - x_min
        b = y_max - y_min
        area = a*b

        return minmax_box, area
        
    def computeArea(pol: QPolygonF):
        """Computes area of a given polygon."""
        n = len(pol)
        area = 0
        # Process all vertices
        for i in range(n):
            # Area incrementation
            area += pol[i].x() * (pol[(i+1) % n].y()-pol[(i-1+n) % n].y())
        
        return 0.5 * abs(area)

    def resizeRectangle(er: QPolygonF, pol:QPolygonF):
        """
        Resizes polygon according to area of a given polygon.

            Parameters:
                er (QPolygonF): Polygon to be resized.
                pol (QPolygonF): Polygon to determine area of resized polygon.

            Returns:
               resized_polygon (QPolygonF): Resized polygon er.
        """
        # Initialize building area and enclosing rectangle area
        ab = abs(Algorithms.computeArea(pol))
        a = abs(Algorithms.computeArea(er))

        # Calculate size coefficient
        k = ab/a

        # Find centroid of enclosing rectangle
        x_t = (er[0].x() + er[1].x() + er[2].x() + er[3].x())/4
        y_t = (er[0].y() + er[1].y() + er[2].y() + er[3].y())/4
        T = QPointF(x_t, y_t)

        # Compute diagonal vectors of enclosing rectangle
        u1x = er[0].x() - x_t
        u1y = er[0].y() - y_t
        u2x = er[1].x() - x_t
        u2y = er[1].y() - y_t
        u3x = er[2].x() - x_t
        u3y = er[2].y() - y_t
        u4x = er[3].x() - x_t
        u4y = er[3].y() - y_t

        # Compute coordinates of vertices of resized polygon
        v1x = x_t + sqrt(k) * u1x
        v1y = y_t + sqrt(k) * u1y
        v2x = x_t + sqrt(k) * u2x
        v2y = y_t + sqrt(k) * u2y
        v3x = x_t + sqrt(k) * u3x
        v3y = y_t + sqrt(k) * u3y
        v4x = x_t + sqrt(k) * u4x
        v4y = y_t + sqrt(k) * u4y

        # Set new vertices
        v1 = QPointF(v1x, v1y)
        v2 = QPointF(v2x, v2y)
        v3 = QPointF(v3x, v3y)
        v4 = QPointF(v4x, v4y)

        # Create resized polygon
        resized_polygon = QPolygonF([v1, v2, v3, v4])

        return resized_polygon

    def checkValidity(pol: QPolygonF):
        """
        Checks if input polygon has at least three vertices for constructing
        convex hull or enclosing rectangle.

            Parameters:
                pol (QPolygonF): Input polygon.

            Returns:
               True (bool): polygon has at least three vertices
               False (bool): polygon has less than three vertices
        """
        if len(pol) < 3:
            # Inform user of invalid polygon
            dlg = QMessageBox()
            dlg.setWindowTitle("Invalid Polygon")
            dlg.setText("Input dataset contains lines or points")
            dlg.exec()
            return False

    def euclidDistance(p1:QPointF, p2: QPointF):
        """Computes Euclidean distance."""
        return sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)

    def findDiagonals(ch:QPolygonF):
        """
        Returns list of all relevant diagonals of input convex hull (polygon).

            Parameters:
                ch (QPolygonF): Input convex hull, can be any polygon.

            Returns:
               diagonals (list): List of diagonals of input convex hull.
        """
        diagonals = []
        # Iterate over each point of convex hull except the last (identical to first)
        n = len(ch)-1
        for i in range(n):
            for j in range(i+1, n):
                # Check for neighboring points, proceed if diagonal exists (avoid edges)
                if (j != (i-1+n)%n) and (j != (i+1)%n):
                    # Append vertices of diagonal and their Euclidean distance
                    diagonals.append([ch[i], ch[j], Algorithms.euclidDistance(ch[i], ch[j])])
        return diagonals

    def intersectionTest(p1:QPointF, p2:QPointF, pol:QPolygonF):
        """
        Determines whether given diagonal (line) intersects with one of edges of input building.

            Parameters:
                p1, p2 (QPointF): Vertices of diagonal.
                pol (QPolygonF): Input polygon (building).

            Returns:
                True (bool): the intersection exists
                False (bool): the intersection does not exist
        """
        n = len(pol)
        # Process all edges of input building
        for i in range(n):
            # Check if currently iterated edges of building share vertices with diagonal
            if (p1 == pol[i] or p1 == pol[(i+1)%n]) or (p2 == pol[i] or p2 == pol[(i+1)%n]):
                continue

            # Compute results of testing determinants
            t1 = (p2.x()-p1.x())*(pol[(i+1)%n].y()-p1.y())-(pol[(i+1)%n].x()-p1.x())*(p2.y()-p1.y())
            t2 = (p2.x()-p1.x())*(pol[i].y()-p1.y())-(pol[i].x()-p1.x())*(p2.y()-p1.y())
            t3 = (pol[(i+1)%n].x()-pol[i].x())*(p1.y()-pol[i].y())-(p1.x()-pol[i].x())*(pol[(i+1)%n].y()-pol[i].y())
            t4 = (pol[(i+1)%n].x()-pol[i].x())*(p2.y()-pol[i].y())-(p2.x()-pol[i].x())*(pol[(i+1)%n].y()-pol[i].y())

            # If at least one pair of results has the same sign, intersection does not exist
            if t1*t2 >= 0 or t3*t4 >=0:
                continue
            # Intersection exists
            else:
                return True
        return False

    def setDiagonals(diagonals, pol):
        """
        Returns two longest diagonals of input polygon (convex hull).

            Parameters:
                diagonals (list): List of diagonals of input polygon.
                pol (QPolygonF): Input polygon (convex hull).

            Returns:
                sigma1, sigma2 (float): Slope angles of longest diagonals.
                dist1, dist2 (float): Lengths of longest diagonals.
        """
        # Initialize necessary variables to None
        sigma1 = None
        dist1 = None
        sigma2 = None
        dist2 = None

        # Process each diagonal
        for i in range(len(diagonals)):
            p1, p2 = diagonals[i][0], diagonals[i][1]
            # Test currently iterated diagonal
            res = Algorithms.intersectionTest(p1, p2, pol)
            # If intersection exists, go to the next longest diagonal
            if res == True:
                continue
            # Intersection does not exist, diagonal is wholly inside of polygon
            else:
                # Increment slope angle and length of longest acceptable diagonal
                if dist1 is None:
                    dx = diagonals[i][0].x() - diagonals[i][1].x()
                    dy = diagonals[i][0].y() - diagonals[i][1].y()
                    sigma1 = atan2(dy, dx)
                    dist1 = diagonals[i][2]

                # Increment slope angle and length of second longest acceptable diagonal
                else:
                    dx = diagonals[i][0].x() - diagonals[i][1].x()
                    dy = diagonals[i][0].y() - diagonals[i][1].y()
                    sigma2 = atan2(dy, dx)
                    dist2 = diagonals[i][2]
                    # Two longest acceptable diagonals found, break cycle
                    break

        # FAILSAFE: If no acceptable diagonal(s) is(are) found,
        # force longest and second longest diagonal from diagonals list
        if sigma1 is None:
            dx = diagonals[0][0].x() - diagonals[0][1].x()
            dy = diagonals[0][0].y() - diagonals[0][1].y()
            sigma1 = atan2(dy, dx)
            dist1 = diagonals[0][2]

        if sigma2 is None:
            dx = diagonals[1][0].x() - diagonals[1][1].x()
            dy = diagonals[1][0].y() - diagonals[1][1].y()
            sigma2 = atan2(dy, dx)
            dist2 = diagonals[1][2]

        return sigma1, dist1, sigma2, dist2

    # Set default convex hull algorithm
    ch_alg = jarvisScan