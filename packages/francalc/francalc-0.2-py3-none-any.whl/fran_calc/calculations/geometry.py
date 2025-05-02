from ..modules import run_test
from math import pi

def calculate_perimeter_paralelogram(face1, face2):
    return 2 * (face1 + face2)

def calculate_perimeter_triangle(face1, face2, face3):
    return face1 + face2 + face3

def calculate_perimeter_losangle(face):
    return 4 * face

def calculate_area_paralelogram(base, height):
    return base * height

def calculate_area_losangle(large_diagonal, small_diagonal):
    return (large_diagonal * small_diagonal) / 2

def calculate_area_trapezoid(base1, base2, height):
    return ((base1 + base2) * height) / 2

def calculate_area_circle(radius):
    return pi * (radius ** 2)

def calculate_volume_cube(side):
    return side ** 3

def calculate_volume_parallelepiped(base, height):
    return base * height

def calculate_volume_cylinder(radius, height):
    return pi * (radius ** 2) * height

def calculate_volume_sphere(radius):
    return (4 / 3) * pi * (radius ** 3)

def calculate_volume_cone(radius, height):
    return (1 / 3) * pi * (radius ** 2) * height

def calculate_volume_piramid(base, height):
    return (1 / 3) * base * height

def calculate_volume_prism(base, height):
    return base * height

if __name__ == "__main__":
    run_test(calculate_perimeter_paralelogram, 2, 3)
    run_test(calculate_perimeter_triangle, 2, 3, 4)
    run_test(calculate_perimeter_losangle, 2)
    run_test(calculate_area_paralelogram, 2, 3)
    run_test(calculate_area_losangle, 2, 3)
    run_test(calculate_area_trapezoid, 2, 3, 4)
    run_test(calculate_area_circle, 2)
    run_test(calculate_volume_cube, 2)
    run_test(calculate_volume_parallelepiped, 2, 3)
    run_test(calculate_volume_cylinder, 2, 3)
    run_test(calculate_volume_sphere, 2)
    run_test(calculate_volume_cone, 2, 3)
    run_test(calculate_volume_piramid, 2, 3)
    run_test(calculate_volume_prism, 2, 3)