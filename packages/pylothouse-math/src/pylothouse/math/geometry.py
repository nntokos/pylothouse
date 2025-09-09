from __future__ import annotations
from functools import singledispatch
import math
import _internal._helpers as _helpers

class GeometryObserver:
    def update_origin(self):
        pass


class GeometryConfig:
    _origin = 'topleft'
    _precision = 10
    _observers = []
    _verbose = False

    @classmethod
    def set_origin(cls, origin):
        if not isinstance(origin, str):
            raise TypeError("Origin must be a string. Either 'topleft' or 'bottomleft'")
        if not origin.lower() in ['topleft', 'bottomleft']:
            raise ValueError("Origin must be 'topleft' or 'bottomleft'")
        cls._origin = origin.lower()
        cls.notify_observers()

    @classmethod
    def get_origin(cls):
        return cls._origin

    @classmethod
    def set_precision(cls, precision):
        if not isinstance(precision, int):
            raise TypeError("Precision must be an integer")
        if precision < 0:
            raise ValueError("Precision must be greater than or equal to 0")
        cls._precision = precision

    @classmethod
    def get_precision(cls):
        return cls._precision

    @classmethod
    def set_verbose(cls, verbose):
        if not isinstance(verbose, bool):
            raise TypeError("Verbose must be a boolean")
        cls._verbose = verbose

    @classmethod
    def get_verbose(cls):
        return cls._verbose


    @classmethod
    def register_observer(cls, observer: GeometryObserver):
        if observer not in cls._observers:
            cls._observers.append(observer)

    @classmethod
    def unregister_observer(cls, observer: GeometryObserver):
        if observer in cls._observers:
            cls._observers.remove(observer)

    @classmethod
    def notify_observers(cls, ):
        for observer in cls._observers:
            observer.update_origin()



class GeometryUtils:

    @staticmethod
    def Vertex2D(vertex, func_ref) -> Vertex2D:
        """

        :param vertex: Tuple of 2 elements or Vertex2D object
        :return: Vertex2D object
        """
        func_name = func_ref.__name__
        if isinstance(vertex, Vertex2D):
            return vertex
        if not isinstance(vertex, tuple) or len(vertex) != 2:
            raise TypeError(f"{func_name} Input Vertices Input must be a tuple (x, y) or Vertex2D object")
        if not all(isinstance(vertex[i], (int, float)) for i in range(2)):
            raise TypeError(f"{func_name} Input Vertex elements must be integers or floats")
        return Vertex2D(*vertex)

    @staticmethod
    def list_of_Vertex2D(vertices, func_ref) -> list[Vertex2D]:
        """

        :param vertices: List of vertices as tuples
        :return: List of Vertex2D objects
        """
        func_name = func_ref.__name__
        if all(isinstance(vertex, Vertex2D) for vertex in vertices):
            return vertices
        if not all(isinstance(vertex, tuple) for vertex in vertices):
            raise TypeError(f"{func_name} Input Vertices must be tuples or Vertex2D objects")
        if not all(len(vertex) == 2 for vertex in vertices):
            raise TypeError(f"{func_name} Input Vertices tuples must have 2 elements (x, y)")
        _vertices = []
        for vertex in vertices:
            if not all(isinstance(vertex[i], (int, float)) for i in range(2)):
                raise TypeError(f"{func_name} Input Vertex elements must be integers or floats")
            _vertices.append(Vertex2D(*vertex))
        return _vertices

    @staticmethod
    def check_Line2D(line: Line2D, func_ref) -> bool:
        """

        :param line: Line2D object to check
        """
        func_name = func_ref.__name__
        if not isinstance(line, Line2D):
            raise TypeError(f"{func_name} Input Line must be a Line2D object. Got {type(line)}")
        return True

    @staticmethod
    def check_Segment2D(segment, func_ref):
        """

        :param segment: Segment2D object to check
        """
        func_name = func_ref.__name__
        if not isinstance(segment, Segment2D):
            raise TypeError(f"{func_name} Segment must be a Segment2D object. Got {type(segment)}")
        return True


class Vertex2D(GeometryObserver):
    """
    Coordinate system is as follows:
    - x-axis is horizontal
    - y-axis is vertical
    - Origin is at (0, 0) and can be set to 'topleft' or 'bottomleft' (Default is 'topleft')

    """

    def __init__(self, x, y):
        if not all(isinstance(i, float) or isinstance(i, int) for i in [x, y]):
            raise TypeError("Coordinates must be integers or floats")
        self.x = float(x)
        self.y = float(y)
        GeometryConfig.register_observer(self)
        self._origin = GeometryConfig.get_origin()

    def __str__(self):
        return f"({self.x}, {self.y})"

    @property
    def origin(self):
        return self._origin

    def update_origin(self):
        self._origin = GeometryConfig.get_origin()

    def equals(self, vertex):
        vertex = GeometryUtils.Vertex2D(vertex, self.equals)
        return math.isclose(self.x, vertex.x) and math.isclose(self.y, vertex.y)


    def distance_to_vertex(self, vertex):
        return ((vertex.x - self.x) ** 2 + (vertex.y - self.y) ** 2) ** 0.5

    def closest_vertex(self, vertices):
        return min(vertices, key=lambda vertex: self.distance_to_vertex(vertex))

    def farthest_vertex(self, vertices):
        return max(vertices, key=lambda vertex: self.distance_to_vertex(vertex))

    def is_above_line(self, line) -> bool:
        """
        :param line: Line2D object
        :return: True if the vertex is above the line, False otherwise
        """
        GeometryUtils.check_Line2D(line, self.is_above_line)
        if line.is_vertical:
            raise ValueError(f"{self.is_above_line.__name__} Line is vertical")
        y_at = line.y_at(self.x)
        if self._origin == 'bottomleft':
            return self.y > y_at
        else:
            return self.y < y_at

    def is_below_line(self, line) -> bool:
        return not (self.is_above_line(line) or self.is_on_line(line))

    def is_right_of_line(self, line: Line2D) -> bool:
        """
        Essentially same functionality as is_above_line
        :param line: Line2D object
        :return: True if the vertex is right of the line, False otherwise
        """
        if line.is_horizontal:
            raise ValueError(f"{self.is_right_of_line.__name__} Line is horizontal")
        return self.x > line.x_at(self.y)

    def is_left_of_line(self, line) -> bool:
        """
        Essentially same functionality as is_below_line
        :param line:
        :return:
        """
        return not (self.is_right_of_line(line) or self.is_on_line(line))

    def is_on_line(self, line: Line2D) -> bool:
        """
        :param line: Line2D object
        :return: True if the vertex is on the line, False otherwise
        """
        if line.is_horizontal:
            return math.isclose(self.y, line.y_at(self.x))
        elif line.is_vertical:
            return math.isclose(self.x, line.x_at(self.y))
        else:
            return math.isclose(self.y, line.y_at(self.x)) and math.isclose(self.x, line.x_at(self.y))

    def is_on_segment(self, segment: Segment2D) -> bool:
        """

        :param segment: Segment as a list of 2 tuples or a Line2D object
        :return: True if the vertex is on the segment, False otherwise
        """
        return self.is_on_line(segment) and self.x >= min(segment.A.x, segment.B.x) and self.x <= max(segment.A.x, segment.B.x) and self.y >= min(segment.A.y, segment.B.y) and self.y <= max(segment.A.y, segment.B.y)


    def collinear(self, vertices) -> bool:
        """
        :param vertices: List of Vertex2D objects or tuples
        :return: True if all vertices are collinear, False otherwise
        """
        if len(vertices) < 2:
            raise ValueError("At least 2 vertices are required")
        vertices = GeometryUtils.list_of_Vertex2D(vertices, self.collinear)
        for vertex in vertices[1:]:
            if not vertex.is_on_line(Line2D([self, vertices[0]])):
                return False
        return True


class Line2D(GeometryObserver):

    def __init__(self, vertices):
        vertexA, vertexB = GeometryUtils.list_of_Vertex2D(vertices, self.__init__)
        self.A = vertexA
        self.B = vertexB
        GeometryConfig.register_observer(self)
        self._origin = GeometryConfig.get_origin()

    @classmethod
    def from_segment(cls, segment: Segment2D):
        GeometryUtils.check_Segment2D(segment, cls.from_segment)
        return cls([segment.A, segment.B])


    def __str__(self):
        return f"Line2D({self.A}, {self.B})"

    @property
    def origin(self):
        return self._origin

    def update_origin(self):
        self._origin = GeometryConfig.get_origin()

    @property
    def slope(self):
        if self.A and self.B and self.A.x != self.B.x:
            return (self.B.y - self.A.y) / (self.B.x - self.A.x)
        else:
            return None

    @property
    def x_intercept(self):
        if self.slope:
            return -self.y_intercept / self.slope
        else:
            return self.A.x

    @property
    def y_intercept(self):
        if self.slope:
            return self.A.y - self.slope * self.A.x
        else:
            return self.A.y

    @property
    def is_horizontal(self):
        return self.slope == 0

    @property
    def is_vertical(self):
        return self.slope == None

    def is_parallel_to(self, line: Line2D):
        if self.slope is None and line.slope is None:
            return True
        elif self.slope is None or line.slope is None:
            return False
        else:
            return math.isclose(self.slope, line.slope)


    def is_perpendicular_to(self, line: Line2D):
        if self.slope is None and line.slope is None:
            return False
        elif line.slope is None:
            return math.isclose(self.slope, 0)
        elif self.slope is None:
            return math.isclose(line.slope, 0)
        else:
            return math.isclose(self.slope * line.slope, -1)

    def collinear(self, line: Line2D):
        GeometryUtils.check_Line2D(line, self.collinear)
        return self.is_parallel_to(line) and self.A.is_on_line(line)

    def x_at(self, y):
        if self.is_horizontal:
            raise ValueError(f"{self.x_at.__name__} Line is horizontal")
        elif self.is_vertical:
            return self.A.x
        else:
            return (y - self.y_intercept) / self.slope

    def y_at(self, x):
        if self.is_vertical:
            raise ValueError(f"{self.y_at.__name__} Line is vertical")
        elif self.is_horizontal:
            return self.A.y
        else:
            return self.slope * x + self.y_intercept

    def angle_with_line(self, line: Line2D): # TODO: Fix angles
        pass


    def intersects(self, line: Line2D) -> bool: # TODO: Implement func for intersect line with segment
        GeometryUtils.check_Line2D(line, self.intersects)
        return not self.is_parallel_to(line)


    def intersection(self, line: Line2D):
        """

        :param line: Line2D object
        :return: Intersection point as Vertex2D object
        """
        GeometryUtils.check_Line2D(line, self.intersection)
        if self.is_parallel_to(line):
            return None
        if self.is_vertical:
            x = self.A.x
            y = line.y_at(x)
        elif line.is_vertical:
            x = line.A.x
            y = self.y_at(x)
        else:
            slope1 = self.slope
            slope2 = line.slope
            y_intercept1 = self.y_intercept
            y_intercept2 = line.y_intercept
            x = (y_intercept2 - y_intercept1) / (slope1 - slope2)
            y = slope1 * x + y_intercept1
        return Vertex2D(x, y)


    def intersects_segment(self, segment: Segment2D, include_endpoints=True):
        GeometryUtils.check_Segment2D(segment, self.intersects_segment)
        segment_line = Line2D.from_segment(segment)
        intersection = self.intersection(segment_line)
        if intersection:
            if intersection.is_on_segment(segment):
                if not include_endpoints:
                    if intersection.equals(segment.A) or intersection.equals(segment.B):
                        return False
                    else:
                        return True
                return True

    def plot_n_save(self): # TODO: Fix coordinates system
        import matplotlib.pyplot as plt
        plt.plot([self.A.x, self.B.x], [self.A.y, self.B.y], color='blue')
        timestamp = _helpers.timestamp()
        plt.savefig(f"line_{timestamp}.png")


class Segment2D(Line2D):

    def __str__(self):
        return f"Segment2D({self.A}, {self.B})"

    def equals(self, segment:Segment2D):
        GeometryUtils.check_Segment2D(segment, self.equals)
        return (self.A.equals(segment.A) and self.B.equals(segment.B)) or (self.A.equals(segment.B) and self.B.equals(segment.A))


    @property
    def length(self):
        if self.A and self.B:
            return ((self.B.x - self.A.x) ** 2 + (self.B.y - self.A.y) ** 2) ** 0.5
        else:
            return None

    @property
    def projectionX(self):
        if self.A and self.B:
            return Segment2D([Vertex2D(self.A.x, 0), Vertex2D(self.B.x, 0)])
        else:
            return None

    @property
    def projectionY(self):
        if self.A and self.B:
            return Segment2D([Vertex2D(0, self.A.y), Vertex2D(0, self.B.y)])
        else:
            return None

    def intersects(self, segment: Segment2D, include_endpoints=True):
        """
        Parallel segments are considered non-intersecting. For parallel segments, use overlaps method
        :param segment: Segment2D object
        :param include_endpoints: Whether to include the endpoints as intersections
        :return: Returns True if the segments intersect, False otherwise
        """
        GeometryUtils.check_Line2D(segment, self.intersects)
        if self.is_parallel_to(segment):
            return False

        lines_intersection = super().intersection(segment)

        if not lines_intersection:
            return False

        if not lines_intersection.is_on_segment(self):
            return False

        if not include_endpoints:
            if any(lines_intersection.equals(vertex) for vertex in [self.A, self.B, segment.A, segment.B]):
                return False

        return True


    def intersection(self, segment:Segment2D):
        """

        :param segment: Segment2D object
        :return: Returns the intersection point as Vertex2D object. If the segments do not intersect, None is returned. If the segments overlap/parallel, None is returned. For overlapping segments, use the overlap method
        """
        if not self.intersects(segment):
            return None
        else:
            return super().intersection(segment)


    def overlaps(self, segment: Segment2D):
        GeometryUtils.check_Segment2D(segment, self.overlaps)
        if not self.is_parallel_to(segment):
            return False
        common_vertices=0
        for vertex in [self.A, self.B]:
            if vertex.is_on_segment(segment):
                common_vertices += 1
        for vertex in [segment.A, segment.B]:
            if vertex.is_on_segment(self):
                common_vertices += 1

        if common_vertices >= 2:
            return True

        return False


    def overlap(self, segment:Segment2D):
        """
        Returns the overlapping region of the two segments if they overlap. If they just intersect, the intersection point is returned. For pure intersection, the intersects method is strongly suggested

        :param segment: Segment2D object
        :return: The overlapping region of the two segments if they overlap, None otherwise
        """
        if self.overlaps(segment):
            if self.equals(segment) or self.equals(Segment2D([segment.B, segment.A])):
                return self
            else:
                to_return = []
                if self.A.is_on_segment(segment):
                    to_return.append(self.A)
                if self.B.is_on_segment(segment):
                    to_return.append(self.B)
                if segment.A.is_on_segment(self) and not any(segment.A.equals(vertex) for vertex in to_return):
                    to_return.append(segment.A)
                if segment.B.is_on_segment(self) and not any(segment.B.equals(vertex) for vertex in to_return):
                    to_return.append(segment.B)
            if len(to_return) == 1:
                return to_return[0]
            if len(to_return) == 2:
                return Segment2D(to_return)
            else:
                raise ValueError(f"{self.overlap.__name__}: Problem with overlap calculation (overlap points = {len(to_return)}. This error should not occur. Please report this issue")
        elif self.intersects(segment):
            return self.intersection(segment)
        else:
            return None




class Quadrilateral(GeometryObserver):

    def __init__(self, vertices: list[Vertex2D], check_quad_validity=True):
        """

        Args:
            vertices: List of 4 vertices as Vertex2D objects
            check_quad_validity: Whether to check if the vertices form a valid parallelogram. Default is True. This arg solely exists to improve performance. Set to False for optimal performance. Caution: Non valid quads may cause issues.
        """
        # _vertices = GeometryUtils.list_of_Vertex2D(vertices, self.__init__)

        GeometryConfig.register_observer(self)
        self._origin = GeometryConfig.get_origin()

        self._A = vertices[0]
        self._B = vertices[1]
        self._C = vertices[2]
        self._D = vertices[3]
        self.__updatelines()
        if check_quad_validity:
            self.__check_quad_validity()
        self._type = "quadrilateral"


    @classmethod
    def non_oriented_vertices(cls, vertices):
        vertices = GeometryUtils.list_of_Vertex2D(vertices, cls.non_oriented_vertices)
        _origin = GeometryConfig.get_origin()
        if _origin == 'topleft':
            left_to_right = sorted(vertices, key=lambda v: (v.x, v.y))
            top_to_bottom = sorted(left_to_right[:2], key=lambda v: (v.y, -v.x))
        else:
            left_to_right = sorted(vertices, key=lambda v: (v.x, -v.y))
            top_to_bottom = sorted(left_to_right[:2], key=lambda v: (-v.y, -v.x))

        _A = top_to_bottom[0]
        _D = top_to_bottom[1]

        if _origin == 'topleft':
            top_to_bottom = sorted(left_to_right[2:], key=lambda v: (v.y, v.x))
        else:
            top_to_bottom = sorted(left_to_right[2:], key=lambda v: (-v.y, v.x))

        _B = top_to_bottom[0]
        _C = top_to_bottom[1]

        vertices = [_A, _B, _C, _D]

        instance = cls(vertices)

        return instance


    def __str__(self):
        return f"Quadrilateral({self.A}, {self.B}, {self.C}, {self.D})"

        
    def __updatelines(self):
        if not self._A or not self._B or not self._C or not self._D:
            raise ValueError("Vertices are missing")
        self._AB = Segment2D([self._A, self._B])
        self._BC = Segment2D([self._B, self._C])
        self._CD = Segment2D([self._C, self._D])
        self._DA = Segment2D([self._D, self._A])

    def __check_quad_validity(self):
        for vertex in [self._A, self._B, self._C, self._D]:
            triplet = [v for v in [self._A, self._B, self._C, self._D] if v != vertex]
            if triplet[0].collinear(triplet[1:]):
                raise ValueError(f"Collinear vertices: {triplet} cannot form a quadrilateral")

        for seg in [self.AB, self.BC, self.CD, self.DA]:
            intersects = 0
            for quad_seg in [self.AB, self.BC, self.CD, self.DA]:
                if seg == quad_seg:
                    continue
                if seg.intersects(quad_seg):
                    intersects += 1
            if intersects > 2:
                raise ValueError(
                    f"{self.__init__.__name__} The lines of the quadrilateral intersect more than twice. Cannot form a quadrilateral")

    @property
    def origin(self):
        return self._origin

    def update_origin(self):
        self._origin = GeometryConfig.get_origin()

    @classmethod
    def rectangle(cls, x, y, width, height, check_validity=True):
        """

        Args:
            x: Origin x-coordinate
            y: Origin y-coordinate
            width: Width of the rectangle
            height: Height of the rectangle
            check_validity: Whether to check if the vertices form a valid parallelogram. Default is True. This arg solely exists to improve performance. Set to False for optimal performance. Caution: Non valid quads may cause issues.

        Returns: Quadrilateral object

        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be greater than 0")
        A = Vertex2D(x, y)
        B = Vertex2D(x + width, y)
        C = Vertex2D(x + width, y + height)
        D = Vertex2D(x, y + height)
        rectangle = cls([A, B, C, D], check_validity)
        rectangle._type = "rectangle"
        return rectangle

    @classmethod
    def square(cls, x, y, side, check_validity=True):
        """

        Args:
            x: Origin x-coordinate
            y: Origin y-coordinate
            side: Length of the side
            check_validity: Whether to check if the vertices form a valid parallelogram. Default is True. This arg solely exists to improve performance. Set to False for optimal performance. Caution: Non valid quads may cause issues.

        Returns: Quadrilateral object

        """
        if side <= 0:
            raise ValueError("Side must be greater than 0")
        square = cls.rectangle(x, y, side, side, check_validity)
        square._type = "square"
        return square

    @classmethod
    def rhombus(cls, x, y, side, height, check_validity=True):
        """

        Args:
            x: Origin x-coordinate
            y: Origin y-coordinate
            side: Length of the side
            height: Height of the rhombus
            check_validity: Whether to check if the vertices form a valid parallelogram. Default is True. This arg solely exists to improve performance. Set to False for optimal performance. Caution: Non valid quads may cause issues.

        Returns: Quadrilateral object

        """
        
        if side <= 0 or height <= 0:
            raise ValueError("Side and height must be greater than 0")
        A = Vertex2D(x, y)
        B = Vertex2D(x + side, y)
        C = Vertex2D(x + side + height, y + height)
        D = Vertex2D(x + height, y + height)
        rhombus=cls([A, B, C, D], check_validity)
        rhombus._type = "rhombus"
        return rhombus

    @classmethod
    def trapezoid(cls, x, y, small_base, big_base, height, check_validity=True):
        """

        Args:
            x: Origin x-coordinate
            y: Origin y-coordinate
            small_base: Length of the small base
            big_base: Length of the big base
            height: Height of the trapezoid
            check_validity: Whether to check if the vertices form a valid parallelogram. Default is True. This arg solely exists to improve performance. Set to False for optimal performance. Caution: Non valid quads may cause issues.

        Returns: Quadrilateral object

        """
        if small_base <= 0 or big_base <= 0 or height <= 0:
            raise ValueError("Small base, big base and height must be greater than 0")
        A = Vertex2D(x, y)
        B = Vertex2D(x + small_base, y)
        C = Vertex2D(x + big_base, y + height)
        D = Vertex2D(x, y + height)
        trapezoid = cls([A, B, C, D], check_validity)
        trapezoid._type = "trapezoid"
        return trapzoid

    # TODO: Add kite class method

    # Vertex getters
    @property
    def A(self):
        return self._A

    @property
    def B(self):
        return self._B

    @property
    def C(self):
        return self._C

    @property
    def D(self):
        return self._D

    @property
    def AB(self) -> Segment2D:
        return self._AB

    @property
    def BC(self) -> Segment2D:
        return self._BC

    @property
    def CD(self) -> Segment2D:
        return self._CD

    @property
    def DA(self) -> Segment2D:
        return self._DA

    @property
    def width(self):
        return max(self.A.x, self.B.x, self.C.x, self.D.x) - min(self.A.x, self.B.x, self.C.x, self.D.x) # TODO: Implement for each type of Quad separately

    @property
    def height(self):
        return max(self.A.y, self.B.y, self.C.y, self.D.y) - min(self.A.y, self.B.y, self.C.y, self.D.y) # TODO: Implement for each type of Quad separately


    def equals(self, quad):
        """

        :param quad: Quadrilateral object
        :return: True if this quadrilateral is equal to the given quadrilateral, False otherwise
        """
        if not isinstance(quad, Quadrilateral):
            raise ValueError("Argument must be a Quadrilateral object")

        if quad.is_rectangle and self._type == "rectangle":
            if self.A.equals(quad.A) and self.B.equals(quad.B) and self.C.equals(quad.C) and self.D.equals(quad.D):
                return True

        test_quad1 = Quadrilateral.non_oriented_vertices([self.A, self.B, self.C, self.D])
        test_quad2 = Quadrilateral.non_oriented_vertices([quad.A, quad.B, quad.C, quad.D])

        return (all([test_quad1.A.equals(test_quad2.A), test_quad1.B.equals(test_quad2.B), test_quad1.C.equals(test_quad2.C), test_quad1.D.equals(test_quad2.D)])
                and all([test_quad1.AB.equals(test_quad2.AB), test_quad1.BC.equals(test_quad2.BC), test_quad1.CD.equals(test_quad2.CD), test_quad1.DA.equals(test_quad2.DA)]))


    @property
    def sides(self) -> list[Segment2D]:
        return [self.AB, self.BC, self.CD, self.DA]

    @property
    def perimeter(self):
        return self.AB.length + self.BC.length + self.CD.length + self.DA.length

    @property
    def area(self):
        return 0.5 * abs((self.A.x * self.B.y + self.B.x * self.C.y + self.C.x * self.D.y + self.D.x * self.A.y) - (
                    self.B.x * self.A.y + self.C.x * self.B.y + self.D.x * self.C.y + self.A.x * self.D.y))

    @property
    def is_parallelogram(self):
        return self.AB.is_parallel_to(self.CD) and self.BC.is_parallel_to(self.DA)

    @property
    def is_rectangle(self):
        return self.AB.is_parallel_to(self.CD) and self.AB.is_perpendicular_to(self.BC)

    @property
    def is_rhombus(self):
        return self.is_parallelogram and self.AB.length == self.BC.length == self.CD.length == self.DA.length

    @property
    def is_square(self):
        return self.is_rectangle and self.is_rhombus

    @property
    def is_trapezoid(self):
        return self.AB.slope == self.CD.slope or self.BC.slope == self.DA.slope

    @property
    def is_kite(self):
        return self.AB.length == self.CD.length or self.BC.length == self.DA.length

    @property
    def type(self):
        return self._type



    def shared_side(self, quad: Quadrilateral):
        """

        :param quad: Quadrilateral object
        :return: Segment2D object if the quadrilaterals share a side, None otherwise
        """
        # quad = GeometryUtils.check_Quadrilateral(quad) # TODO: Implement check for quad
        for side in [self.AB, self.BC, self.CD, self.DA]:
            for quad_side in [quad.AB, quad.BC, quad.CD, quad.DA]:
                if side.equals(quad_side):
                    return side
        return None

    def has_on_perimeter(self, vertex):
        vertex = GeometryUtils.Vertex2D(vertex, self.has_on_perimeter)
        return any(vertex.is_on_segment(side) for side in [self.AB, self.BC, self.CD, self.DA])


    def encloses_vertex(self, vertex, include_sides=True): # TODO: Refine this to use either triangles or sum of angles
        # vertex = GeometryUtils.Vertex2D(vertex, self.encloses_vertex)
        if self._type == "rectangle":
            if include_sides:
                return self.A.x <= vertex.x <= self.B.x and self.A.y <= vertex.y <= self.D.y
            else:
                return self.A.x < vertex.x < self.B.x and self.A.y < vertex.y < self.D.y
        if include_sides:
            return not vertex.is_above_line(self.AB) and not vertex.is_below_line(self.CD) and not vertex.is_right_of_line(
            self.BC) and not vertex.is_left_of_line(self.DA)
        else:
            return not vertex.is_above_line(self.AB) and not vertex.is_below_line(self.CD) and not vertex.is_right_of_line(self.BC) and not vertex.is_left_of_line(self.DA) and not self.has_on_perimeter(vertex)


    def encloses_segment(self, segment: Segment2D, includes_sides=True) -> bool:
        """

        :param segment: Segment2D object
        :param includes_sides: Include the sides of the quadrilateral in the check
        :return: True if this quadrilateral encloses the given segment, False otherwise
        """
        GeometryUtils.check_Segment2D(segment, self.encloses_segment)

        if self.has_on_perimeter(segment.A) and self.has_on_perimeter(segment.B) and any(side.collinear(segment) for side in [self.AB, self.BC, self.CD, self.DA]):
            return includes_sides

        if self._type == "rectangle":
            return self.encloses_vertex(segment.A, include_sides=includes_sides) and self.encloses_vertex(segment.B, include_sides=includes_sides)

        for seg in [self.AB, self.BC, self.CD, self.DA]:
            if seg.intersects(segment, include_endpoints=False): # If a line starts and ends inside a concave quad, it will intersect it
                return False
        return self.encloses_vertex(segment.A, include_sides=includes_sides) and self.encloses_vertex(segment.B, include_sides=includes_sides)


    def encloses_quad(self, quad: Quadrilateral, include_sides=True) -> bool:
        """

        :param quad: Quadrilateral object
        :param include_sides: Include the sides of the quadrilateral in the check
        :return: True if this quadrilateral encloses the given quadrilateral, False otherwise
        """
        # quad = GeometryUtils.check_Quadrilateral(quad) # TODO: Implement check for quad
        return all(self.encloses_segment(seg, include_sides) for seg in [quad.AB, quad.BC, quad.CD, quad.DA])


    def intersects_quad(self, quad, include_sides=True):
        """

        :param quad: Quadrilateral object
        :return: True if this quadrilateral intersects with the given quadrilateral, False otherwise
        """
        if not isinstance(quad, Quadrilateral):
            raise ValueError("Argument must be a Quadrilateral object")
        for side in [self.AB, self.BC, self.CD, self.DA]:
            for quad_side in [quad.AB, quad.BC, quad.CD, quad.DA]:
                if side.intersects(quad_side, include_endpoints=include_sides):
                    return True
        return False

    def intersections_with_quad(self, quad: Quadrilateral) -> list[Vertex2D]:
        """

        :param quad: Quadrilateral object
        :return: List of intersection points [Vertex2D]
        """
        # quad = GeometryUtils.check_Quadrilateral(quad) # TODO: Implement check for quad
        intersections = []
        for segment in [self.AB, self.BC, self.CD, self.DA]:
            for quad_seg in [quad.AB, quad.BC, quad.CD, quad.DA]:
                if segment.intersects(quad_seg):
                    intersection = segment.intersection(quad_seg)
                    if intersection not in intersections:
                        intersections.append(intersection)
        return intersections

    def overlaps(self, quad):
        """

        :param quad: Quadrilateral object
        :return: True if this quadrilateral overlaps with the given quadrilateral, False otherwise
        """
        if not isinstance(quad, Quadrilateral):
            raise ValueError("Argument must be a Quadrilateral object")

        if self._type == "rectangle" and quad.is_rectangle:
            return any(self.encloses_vertex(vertex, include_sides=True) for vertex in [quad.A, quad.B, quad.C, quad.D]) or any(self.encloses_vertex(vertex, include_sides=True) for vertex in [self.A, self.B, self.C, self.D])


        return self.intersects_quad(quad) or any(self.encloses_vertex(vertex, include_sides=True) for vertex in [quad.A, quad.B, quad.C, quad.D]) or any (side.overlaps(quad_side) for side in [self.AB, self.BC, self.CD, self.DA] for quad_side in [quad.AB, quad.BC, quad.CD, quad.DA])


    def split_quad_by_line(self, line: Line2D): # Only works for convex quads. TODO: Implement for concave quads
        """

        :param line: Line2D object
        :return: List of 2 Quadrilateral objects after splitting the quadrilateral by the line
        """
        GeometryUtils.check_Line2D(line, self.split_quad_by_line)
        intersections = []
        for side in [self.AB, self.BC, self.CD, self.DA]:
            if side.collinear(line):
                if GeometryConfig._verbose:
                    print(f"Line {line} is collinear with a side {side} of the quadrilateral {self}")
                return None
            if line.intersects_segment(side):
                intersection = line.intersection(side)
                if intersection not in intersections:
                    intersections.append(intersection)
        if len(intersections) != 2:
            if GeometryConfig._verbose:
                print(f"Line {line} does not intersect exactly 2 sides of the quadrilateral {self}")
            return None

        right_ups = []
        left_downs = []
        # Find the two points above or right of line
        for vertex in [self.A, self.B, self.C, self.D]:
            if line.is_vertical:
                right_ups.append(vertex) if vertex.is_right_of_line(line) else left_downs.append(vertex)
            else:
                right_ups.append(vertex) if vertex.is_above_line(line) else left_downs.append(vertex)

        if len(right_ups) != 2 or len(left_downs) != 2:
            if GeometryConfig._verbose:
                print("Could not determine exactly two points above or right of the line and two points below or left of the line")
            return None

        quad1 = Quadrilateral.non_oriented_vertices([right_ups[0], right_ups[1], intersections[0], intersections[1]])
        quad2 = Quadrilateral.non_oriented_vertices([left_downs[0], left_downs[1], intersections[0], intersections[1]])
        return [quad1, quad2]

    def split_quad_by_lines(self, lines: list[Line2D]) -> list[Quadrilateral]:
        quads = [self]
        while any(q.split_quad_by_line(l) is not None for l in lines for q in quads):
            for line in lines:
                for quad in quads:
                    split_quads = quad.split_quad_by_line(line)
                    if split_quads:
                        quads.extend(split_quads)
                        quads.remove(quad)
                        break
        return quads

    def split_rect_by_horizontal_lines(self, lines: list[Line2D]) -> list[Quadrilateral]:
        rects = []
        quad = self
        _lines = [line for line in lines]
        _lines = sorted(_lines, key=lambda l: l.y_intercept)
        for line in _lines:
            split_quads = quad.split_quad_by_line(line)
            if split_quads:
                # Append the rect with the lower y value first
                rects.append(min(split_quads, key=lambda q: min(q.A.y, q.B.y, q.C.y, q.D.y)))
                quad = max(split_quads, key=lambda q: min(q.A.y, q.B.y, q.C.y, q.D.y))

        rects.append(quad)
        return rects

    def split_rect_by_vertical_lines(self, lines: list[Line2D]) -> list[Quadrilateral]:
        rects = []
        quad = self
        _lines = [line for line in lines]
        _lines = sorted(_lines, key=lambda l: l.x_intercept)

        for line in _lines:
            split_quads = quad.split_quad_by_line(line)
            if split_quads:
                rects.append(min(split_quads, key=lambda q: min(q.A.x, q.B.x, q.C.x, q.D.x)))
                quad = max(split_quads, key=lambda q: min(q.A.x, q.B.x, q.C.x, q.D.x))


        rects.append(quad)
        return rects


    # TODO: Under construction
    # def join_rectangles_with_two_overlapping_segments(self, quads: list[Quadrilateral]):
    #
    #     min_x = min(self.A.x, self.B.x, self.C.x, self.D.x)
    #     min_y = min(self.A.y, self.B.y, self.C.y, self.D.y)
    #     max_x = max(self.A.x, self.B.x, self.C.x, self.D.x)
    #     max_y = max(self.A.y, self.B.y, self.C.y, self.D.y)
    #     for quad in quads:
    #         # if not quad.is_rectangle:
    #         #     if GeometryConfig._verbose:
    #         #         print("All quadrilaterals must be rectangles")
    #         #     return None
    #         common_sides = []
    #         for side in [self.AB, self.BC, self.CD, self.DA]:
    #             for quad_side in [quad.AB, quad.BC, quad.CD, quad.DA]:
    #                 if side.equals(quad_side) or (side.overlaps(quad_side) and side.is_parallel_to(quad_side)) and side not in common_sides:
    #                     common_sides.append(side)
    #                     min_x = min(min_x, min(side.A.x, side.B.x), min(quad_side.A.x, quad_side.B.x))
    #                     min_y = min(min_y, min(side.A.y, side.B.y), min(quad_side.A.y, quad_side.B.y))
    #                     max_x = max(max_x, max(side.A.x, side.B.x), max(quad_side.A.x, quad_side.B.x))
    #                     max_y = max(max_y, max(side.A.y, side.B.y), max(quad_side.A.y, quad_side.B.y))
    #                 if len(common_sides) == 2:
    #                     break
    #             if len(common_sides) == 2:
    #                 break
    #         if len(common_sides) < 2:
    #             if GeometryConfig._verbose:
    #                 print("Could not determine exactly 2 common sides")
    #             return None
    #
    #     return Quadrilateral.rectangle(min_x, min_y, max_x - min_x, max_y - min_y)



    # TODO: Under construction
    # def join_rectangle(self, quad: Quadrilateral):
    #     """
    #
    #     :param quad:
    #     :return:
    #     """
    #     # quad = GeometryUtils.check_Quadrilateral(quad) # TODO: Implement check for quad
    #
    #     if not self.is_rectangle or not quad.is_rectangle:
    #         if GeometryConfig._verbose:
    #             print("Both quadrilaterals must be rectangles")
    #         return None
    #     if quad.encloses_quad(self) or self.encloses_quad(quad):
    #         if GeometryConfig._verbose:
    #             print("One rectangle cannot enclose the other")
    #         return None
    #     shared_vertices = []
    #     for vertex in [self.A, self.B, self.C, self.D]:
    #         if any(vertex.equals(quad_vertex) for quad_vertex in [quad.A, quad.B, quad.C, quad.D]):
    #             shared_vertices.append(vertex)
    #     if len(shared_vertices) != 2:
    #         if GeometryConfig._verbose:
    #             print("Both rectangles must share exactly 2 vertices")
    #         return None
    #     final_vertices = []
    #     for vertex in self.A, self.B, self.C, self.D:
    #         if vertex not in shared_vertices and any(not vertex.is_on_segment(quad_seg) for quad_seg in [quad.AB, quad.BC, quad.CD, quad.DA]):
    #             final_vertices.append(vertex)
    #     for vertex in quad.A, quad.B, quad.C, quad.D:
    #         if vertex not in shared_vertices and any(not vertex.is_on_segment(self_seg) for self_seg in [self.AB, self.BC, self.CD, self.DA]):
    #             final_vertices.append(vertex)
    #     if len(final_vertices) != 4:
    #         if GeometryConfig._verbose:
    #             print("Could not determine the vertices of the joined rectangle")
    #         return None
    #     return Quadrilateral.non_oriented_vertices(final_vertices)


    def plot_on_axes(self, ax, color='blue', linewidth=1):
        import matplotlib.pyplot as plt
        ax.plot([self.A.x, self.B.x], [self.A.y, self.B.y], color=color, linewidth=linewidth)
        ax.plot([self.B.x, self.C.x], [self.B.y, self.C.y], color=color, linewidth=linewidth)
        ax.plot([self.C.x, self.D.x], [self.C.y, self.D.y], color=color, linewidth=linewidth)
        ax.plot([self.D.x, self.A.x], [self.D.y, self.A.y], color=color, linewidth=linewidth)
        ax.text(self.A.x, self.A.y, "A")
        ax.text(self.B.x, self.B.y, "B")
        ax.text(self.C.x, self.C.y, "C")
        ax.text(self.D.x, self.D.y, "D")


    def plot_n_save(self, color = 'blue', filename="quad.png"):
        # Plot quadrilateral with text
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot([self.A.x, self.B.x], [self.A.y, self.B.y], color=color)
        plt.plot([self.B.x, self.C.x], [self.B.y, self.C.y], color=color)
        plt.plot([self.C.x, self.D.x], [self.C.y, self.D.y], color=color)
        plt.plot([self.D.x, self.A.x], [self.D.y, self.A.y], color=color)
        plt.text(self.A.x, self.A.y, "A")
        plt.text(self.B.x, self.B.y, "B")
        plt.text(self.C.x, self.C.y, "C")
        plt.text(self.D.x, self.D.y, "D")
        plt.savefig(filename)
        plt.close()



def point_in_quad(point: [tuple, Vertex2D], quad: [tuple, Quadrilateral]):
    """

    :param point: Point of 2 elements (x, y). tuple or pylothouse-math.Vertex2D
    :param quad: Quad of 4 points. list[tuple] or pylothouse-math.Quadrilateral object
    :return: Returns True if point is inside quadrilateral, False otherwise
    """

    if isinstance(quad, list):
        quad = Quadrilateral([Vertex2D(*point) for point in quad])

    if isinstance(point, tuple):
        point = Vertex2D(*point)

    if not isinstance(quad, Quadrilateral):
        raise ValueError("quad must be a list of 4 tuples or a Quadrilateral object")
    if not isinstance(point, Vertex2D):
        raise ValueError("point must be a tuple of 2 elements or a Vertex2D object")

    point_is_in = True
    if point.is_above_line(quad.AB) or point.is_below_line(quad.CD) or point.is_right_of_line(
            quad.BC) or point.is_left_of_line(quad.DA):
        # Plot lines and point
        point_is_in = False
    return point_is_in
