# Description: inspired from https://github.com/omarestrella/simplify.py


def getSquareDistance(p1, p2, xKey, yKey):
    """
    Square distance between two points
    """
    dx = p1[xKey] - p2[xKey]
    dy = p1[yKey] - p2[yKey]

    return dx * dx + dy * dy


def getSquareSegmentDistance(p, p1, p2, xKey, yKey):
    """
    Square distance between point and a segment
    """
    x = p1[xKey]
    y = p1[yKey]

    dx = p2[xKey] - x
    dy = p2[yKey] - y

    if dx != 0 or dy != 0:
        t = ((p[xKey] - x) * dx + (p[yKey] - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = p2[xKey]
            y = p2[yKey]
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = p[xKey] - x
    dy = p[yKey] - y

    return dx * dx + dy * dy


def simplifyRadialDistance(points, tolerance, xKey, yKey):
    length = len(points)
    prev_point = points[0]
    new_points = [prev_point]

    for i in range(length):
        point = points[i]

        if getSquareDistance(point, prev_point, xKey, yKey) > tolerance:
            new_points.append(point)
            prev_point = point

    if prev_point != point:
        new_points.append(point)

    return new_points


def simplifyDouglasPeucker(points, tolerance, xKey="x", yKey="y"):
    length = len(points)
    markers = [0] * length  # Maybe not the most efficent way?

    first = 0
    last = length - 1

    first_stack = []
    last_stack = []

    new_points = []

    markers[first] = 1
    markers[last] = 1

    while last:
        max_sqdist = 0

        for i in range(first, last):
            sqdist = getSquareSegmentDistance(points[i], points[first], points[last], xKey, yKey)

            if sqdist > max_sqdist:
                index = i
                max_sqdist = sqdist

        if max_sqdist > tolerance:
            markers[index] = 1

            first_stack.append(first)
            last_stack.append(index)

            first_stack.append(index)
            last_stack.append(last)

        # Can pop an empty array in Javascript, but not Python, so check
        # the length of the list first
        if len(first_stack) == 0:
            first = None
        else:
            first = first_stack.pop()

        if len(last_stack) == 0:
            last = None
        else:
            last = last_stack.pop()

    for i in range(length):
        if markers[i]:
            new_points.append(points[i])

    return new_points


def simplify(
    points: list[dict], tolerance: float = 0.1, highestQuality: bool = True, xKey: str = "x", yKey: str = "y"
) -> list[dict]:
    sqtolerance = tolerance * tolerance

    if not highestQuality:
        points = simplifyRadialDistance(points, sqtolerance, xKey, yKey)

    points = simplifyDouglasPeucker(points, sqtolerance, xKey, yKey)

    return points
