from ..modules import run_test
from math import sqrt

def arithmetic_progression(a1, razao, termos):
    return [a1 + (i - 1) * razao for i in range(1, termos + 1)]

def geometric_progression(a1, razao, termos):
    return [a1 * (razao ** (i - 1)) for i in range(1, termos + 1)]

def solve_quadratic_equation(a, b, c):
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return "No real roots"
    elif discriminant == 0:
        x = -b / (2 * a)
        return [x]
    else:
        x1 = (-b + sqrt(discriminant)) / (2 * a)
        x2 = (-b - sqrt(discriminant)) / (2 * a)
        return [x1, x2]

def solve_linear_system(a, b, c, d, e, f):
    # Determinante
    det = a * d - b * c
    if det == 0:
        return "No unique solution"
    else:
        x = (e * d - b * f) / det
        y = (a * f - e * c) / det
        return [x, y]

if __name__ == "__main__":
    run_test(arithmetic_progression, 2, 7, 170)
    run_test(geometric_progression, 2, 7, 20)
    run_test(solve_quadratic_equation, 1, -3, 2)
    run_test(solve_linear_system, 1, 1, -2, 1, -2, 13)