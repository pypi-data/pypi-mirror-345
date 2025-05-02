from ..modules import safe_eval, run_test
from math import sqrt, factorial

def simple_arithmetic(expr: str):
    OP_MAP = {
        'add': '+',
        'sub': '-',
        'mul': '*',
        'truediv': '/',
        'floordiv': '//',
        'pow': '**',
        'mod': '%',
    }

    tokens = expr.split()
    # Troca cada token conhecido pelo seu símbolo
    py_tokens = [OP_MAP.get(tok, tok) for tok in tokens]
    py_expr = ' '.join(py_tokens)
    return safe_eval(py_expr)

def calculate_sqrt(radicando: int):
    if radicando < 0:
        raise ValueError("Raiz quadrada de número negativo não é real")
    return sqrt(radicando)

def calculate_factorial(numero: int):
    if numero < 0:
        raise ValueError("Número negativo não tem fatorial")
    return factorial(numero)

def calculate_percentage(part, total):
    return f"{part / total:.2%}"

def calculate_average(valores):
    numeros_str = valores
    numeros = [float(x.strip()) for x in numeros_str.split(',')]
    soma = sum(numeros)
    media = soma / len(numeros)
    return media

def find_min_and_max(valores):
    numeros = list(map(float, valores.split(", ")))
    minimo = min(numeros)
    maximo = max(numeros)

    return f'Mínimo: {int(minimo)}, Máximo: {int(maximo)}'

def calculate_lcm(*valores):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def lcm(a, b):
        return a * b // gcd(a, b)

    resultado = 1
    for num in valores:
        resultado = lcm(resultado, num)
    return resultado

def calculate_gcd(*valores):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    resultado = valores[0]
    for num in valores[1:]:
        resultado = gcd(resultado, num)
    return resultado

def check_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def int_to_roman(num):
    if not (0 < num < 4000):
        raise ValueError("Número fora do intervalo (1-3999)")
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num

if __name__ == "__main__":
    # simple_arithmetic("add 3 mul 5 sub 2 truediv 8 pow 4 mod 2")
    run_test(simple_arithmetic, "1+2**3")
    run_test(calculate_percentage, 50, 200)
    run_test(calculate_average, "1, 2, 3, 4, 5")
    run_test(find_min_and_max, "1, 2, 3, 4, 5")
    run_test(calculate_lcm, 7, 14, 21)
    run_test(calculate_gcd, 7, 14, 21)
    run_test(check_prime, 7)
    run_test(int_to_roman, 3999)