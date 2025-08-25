class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def print_point(self):
        print("Point({}, {})".format(self.x, self.y))


pt1 = Point(5.0, 10.0)
pt2 = Point(7.0, 12.0)

# pt1.print_point()
# pt2.print_point()


class Polygon:
    def __init__(self, points=[]):
        self.points = points

    def is_closed(self):
        if self.points[0] == self.points[-1]:
            print("is closed")
            return True
        else:
            print("not closed")
            return False

    def make_closed(self):
        if self.is_closed():
            print("polygon is already closed")
        else:
            self.points.append(self.points[0])


pt3 = Point(6.0, 1.0)

polygon = Polygon([pt1,pt2,pt3])

polygon.is_closed()

polygon.make_closed()

polygon.is_closed()
