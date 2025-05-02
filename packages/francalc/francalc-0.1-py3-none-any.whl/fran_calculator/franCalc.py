from modules import clear, print_in_columns
from calculations.basic_math import (
    simple_arithmetic,
    calculate_percentage,
    find_min_and_max,
    calculate_lcm,
    calculate_gcd,
    check_prime,
    int_to_roman,
    calculate_average,
    calculate_sqrt,
    calculate_factorial
    )
from calculations.algebra_equations import (
    arithmetic_progression,
    geometric_progression,
    solve_quadratic_equation,
    solve_linear_system
)
from calculations.geometry import (
    calculate_perimeter_losangle,
    calculate_perimeter_paralelogram,
    calculate_perimeter_triangle,
    calculate_area_losangle,
    calculate_area_paralelogram,
    calculate_area_circle,
    calculate_area_trapezoid,
    calculate_volume_cube,
    calculate_volume_parallelepiped,
    calculate_volume_cylinder,
    calculate_volume_sphere,
    calculate_volume_cone,
    calculate_volume_piramid,
    calculate_volume_prism
)
from calculations.conversions_units import (
    calculate_time,
    celsius_to_fahrenheit,
    meters_to_feet,
    kilos_to_pounds,
    fahrenheit_to_celsius,
    feet_to_meters,
    pounds_to_kilos,
    decimal_to_binary,
    decimal_to_octal,
    decimal_to_hexadecimal,
    binary_to_decimal,
    octal_to_decimal,
    hexadecimal_to_decimal,
    real_to_dollar,
    real_to_euro,
    real_to_argentine_peso,
    real_to_bitcoin,
    dollar_to_real,
    euro_to_real,
    argentine_peso_to_real,
    bitcoin_to_real,
    convert_rgb_hex,
    ascii_to_binary
)
from calculations.probability import (
    roll_dice
)
from calculations.date_age import (
    calculate_age
)
from calculations.health import (
    calculate_bmi
)
from calculations.finance import (
    calculate_simple_interest,
    calculate_percentage_change,
    calculate_compound_interest,
    calculate_income_tax
)
from calculations.physics_engineering import (
    calculate_resistance,
    simulate_rocket_launch,
    calculate_average_speed,
    calculate_force_newthon,
    calculate_gravitational_force,
    calculate_gravitational_potential_energy,
    calculate_escape_velocity,
    calculate_coulomb_force,
    calculate_kinetic_energy
)
from calculations.validation_indetifiers import (
    verify_cpf,
    verify_cnpj
)
from calculations.miscellaneous import (
    count_coins
)

ACTIONS = {
    1: (simple_arithmetic, [('expressao', str)]),
    2: (calculate_sqrt, [('radicando', int)]),
    3: (calculate_factorial, [('numero', int)]),
    4: (calculate_percentage, [('parte', int), ('total', int)]),
    5: (calculate_average, [('valores', int)]),
    6: (find_min_and_max, [('valores', int)]),
    7: (calculate_lcm, [('valores', int)]),
    8: (calculate_gcd, [('valores', int)]),
    9: (check_prime, [('numero', int)]),
    10: (int_to_roman, [('numero', int)]),
    11: (arithmetic_progression, [('a1', int), ('razao', int), ('termos', int)]),
    12: (geometric_progression, [('a1', int), ('razao', int), ('termos', int)]),
    13: (solve_quadratic_equation, [('a', int), ('b', int), ('c', int)]),
    14: (solve_linear_system, [('a1', int), ('b1', int), ('a2', int), ('b2', int), ('c1', int), ('c2', int)]),
    15: {
        'title': 'perimeter',
        'sub': {
            1: (calculate_perimeter_paralelogram, [('lado1', int), ('lado2', int)]),
            2: (calculate_perimeter_triangle, [('lado1', int), ('lado2', int), ('lado3', int)]),
            3: (calculate_perimeter_losangle, [('lado', int)])
        }
    },
    16: {
        'title': 'area',
        'sub': {
            1: (calculate_area_paralelogram, [('base', int), ('altura', int)]),
            2: (calculate_area_losangle, [('diagonal maior', int), ('diagonal menor', int)]),
            3: (calculate_area_trapezoid, [('base maior', int), ('base menor', int), ('altura', int)]),
            4: (calculate_area_circle, [('raio', int)])
        }
    },
    17: {
        'title': 'volume',
        'sub': {
            1: (calculate_volume_cube, [('lado', int)]),
            2: (calculate_volume_parallelepiped, [('largura', int), ('altura', int), ('comprimento', int)]),
            3: (calculate_volume_cylinder, [('raio', int), ('altura', int)]),
            4: (calculate_volume_sphere, [('raio', int)]),
            5: (calculate_volume_cone, [('raio', int), ('altura', int)]),
            6: (calculate_volume_piramid, [('base', int), ('altura', int)]),
            7: (calculate_volume_prism, [('base', int), ('altura', int)])
        }
    },
    18: (calculate_time, [('horario', str), ('horario_a_frente', str)]),
    19: {
        'title': 'convert_measurements',
        'sub': {
            1: (celsius_to_fahrenheit, [('celsius', int)]),
            2: (meters_to_feet, [('meters', int)]),
            3: (kilos_to_pounds, [('kilos', int)]),
            4: (fahrenheit_to_celsius, [('fahrenheit', int)]),
            5: (feet_to_meters, [('pés', int)]),
            6: (pounds_to_kilos, [('libras', int)])
        }
    },
    20: {
        'title': 'convert_bases',
        'sub': {
            1: (decimal_to_binary, [('decimal', int)]),
            2: (decimal_to_octal, [('decimal', int)]),
            3: (decimal_to_hexadecimal, [('decimal', int)]),
            4: (binary_to_decimal, [('binário', int)]),
            5: (octal_to_decimal, [('octal', int)]),
            6: (hexadecimal_to_decimal, [('hexadecimal', int)])
        }
    },
    21: {
        'title': 'convert_currency',
        'sub': {
            1: (real_to_dollar, [('real', float)]),
            2: (real_to_euro, [('real', float)]),
            3: (real_to_argentine_peso, [('real', float)]),
            4: (real_to_bitcoin, [('real', float)]),
            5: (dollar_to_real, [('dolar', float)]),
            6: (euro_to_real, [('euro', float)]),
            7: (argentine_peso_to_real, [('peso', float)]),
            8: (bitcoin_to_real, [('bitcoin', float)])
        }
    },
    22: (convert_rgb_hex, [('value', str)]),
    23: (ascii_to_binary, [('ascii_str', str)]),
    24: (roll_dice, [('quantidade', int), ('lados', int)]),
    25: (calculate_age, [('data_nascimento (YYYY-MM-DD)', str)]),
    26: (calculate_bmi, [('peso', float), ('altura', float)]),
    27: (calculate_simple_interest, [('capital', float), ('taxa', float), ('tempo (anos)', float)]),
    28: (calculate_percentage_change, [('original', float), ('novo', float)]),
    29: (calculate_compound_interest, [('capital', float), ('taxa', float), ('tempo (anos)', float)]),
    30: (calculate_income_tax, [('renda', float)]),
    31: (calculate_resistance, [('tensao', float), ('corrente', float)]),
    32: (simulate_rocket_launch, [('v0 (m/s)', float), ('ag (m/s²)', float), ('t (s)', float)]),
    33: (calculate_average_speed, [('distancia', float), ('tempo', float)]),
    34: (calculate_force_newthon, [('massa', float), ('aceleracao', float)]),
    35: (calculate_gravitational_force, [('massa1', float), ('massa2', float), ('distancia', float)]),
    36: (calculate_gravitational_potential_energy, [('massa', float), ('altura', float)]),
    37: (calculate_kinetic_energy, [('massa', float), ('velocidade', float)]),
    38: (calculate_coulomb_force, [('carga1', float), ('carga2', float), ('distancia', float)]),
    39: (calculate_escape_velocity, [('massa', float), ('raio', float)]),
    40: (verify_cpf, [('cpf', str)]),
    41: (verify_cnpj, [('cnpj', str)]),
    42: (count_coins, [('moedas', str)])
}

# 2. Função genérica que, dado a lista de nomes, faz um input() para cada
def coleta_inputs(param_specs):
    args = []
    for name, typ in param_specs:
        while True:
            val = input(f"Digite {name} ({typ.__name__}): ")
            try:
                # converte pra int, float, ou deixa como str
                args.append( typ(val) )
                break
            except ValueError:
                print(f"⚠️  Entrada inválida, precisa ser um {typ.__name__}. Tente de novo.")
    return args

def initCalc():
    clear()
    print("=== Calculadora ===\n")
    # monta lista de strings do menu
    menu = []
    for key, entry in ACTIONS.items():
        if isinstance(entry, dict):
            menu.append(f"{key}. {entry['title']}")
        else:
            fn, specs = entry
            names = ', '.join(name for name, _ in specs)
            menu.append(f"{key}. {fn.__name__} — {names}")

    # imprime em colunas (detectando automaticamente quantas colunas cabem)
    print_in_columns(menu)
    print()

    escolha = input("Escolha a operação: ")
    if not escolha.isdigit() or (op := int(escolha)) not in ACTIONS:
        print("Opção inválida!")
        input("Enter para continuar...")
        return initCalc()

    entry = ACTIONS[op]
    # Se entry for dict, trata submenu
    if isinstance(entry, dict):
        clear()
        title = entry['title']
        submenu = entry['sub']
        print(f"--- {title} ---\n")
        for sk, subentry in submenu.items():
            fn, specs = subentry
            names = ', '.join(n for n, _ in specs)
            print(f"{sk}. {fn.__name__} — {names}")
        print()
        sub = input("Escolha a sub-opção: ")
        if not sub.isdigit() or (subop := int(sub)) not in submenu:
            print("Sub-opção inválida!")
            input("Enter para continuar...")
            return initCalc()
        fn, specs = submenu[subop]
    else:
        fn, specs = entry

    # coleta e chama
    try:
        args = coleta_inputs(specs)
        resultado = fn(*args)
        print(f"\nResultado: {resultado}\n")
    except Exception as e:
        print(f"\nErro: {e}\n")

    input("Pressione Enter para continuar...")
    initCalc()


if __name__ == "__main__":
    # Executa a função principal
    initCalc()