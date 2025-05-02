from ..modules import run_test

def calculate_resistance(voltage: float, current: float) -> float:
    """
    Calcula a resistência elétrica usando a Lei de Ohm.
    :param voltage: Tensão em volts (V)
    :param current: Corrente em amperes (A)
    :return: Resistência em ohms (Ω)
    """
    if current == 0:
        raise ValueError("A corrente não pode ser zero.")
    return voltage / current

def simulate_rocket_launch(v0, g, t):
    """
    Simula o lançamento de um foguete.
    :param v0: Velocidade inicial (m/s)
    :param g: Aceleração da gravidade (m/s²)
    :param t: Tempo (s)
    :return: Altura máxima atingida (m)
    """
    return v0 * t - 0.5 * g * t**2

def calculate_average_speed(distance: float, time: float) -> float:
    """
    Calcula a velocidade média.
    :param distance: Distância percorrida (m)
    :param time: Tempo gasto (s)
    :return: Velocidade média (m/s)
    """
    if time == 0:
        raise ValueError("O tempo não pode ser zero.")
    return distance / time

def calculate_force_newthon(mass: float, acceleration: float) -> float:
    """
    Calcula a força usando a segunda lei de Newton.
    :param mass: Massa (kg)
    :param acceleration: Aceleração (m/s²)
    :return: Força (N)
    """
    return mass * acceleration

def calculate_gravitational_force(m1: float, m2: float, r: float) -> float:
    """
    Calcula a força gravitacional entre dois corpos.
    :param m1: Massa do corpo 1 (kg)
    :param m2: Massa do corpo 2 (kg)
    :param r: Distância entre os centros dos corpos (m)
    :return: Força gravitacional (N)
    """
    G = 6.67430e-11  # Constante gravitacional em m³/(kg·s²)
    return G * (m1 * m2) / r**2

def calculate_gravitational_potential_energy(mass: float, height: float) -> float:
    """
    Calcula a energia potencial gravitacional.
    :param mass: Massa (kg)
    :param height: Altura (m)
    :return: Energia potencial gravitacional (J)
    """
    g = 9.81  # Aceleração da gravidade em m/s²
    return mass * g * height

def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    """
    Calcula a energia cinética.
    :param mass: Massa (kg)
    :param velocity: Velocidade (m/s)
    :return: Energia cinética (J)
    """
    return 0.5 * mass * velocity**2

def calculate_coulomb_force(q1: float, q2: float, r: float) -> float:
    """
    Calcula a força eletrostática entre duas cargas.
    :param q1: Carga 1 (C)
    :param q2: Carga 2 (C)
    :param r: Distância entre as cargas (m)
    :return: Força eletrostática (N)
    """
    k = 8.9875517873681764e9  # Constante de Coulomb em N·m²/C²
    return k * (q1 * q2) / r**2

def calculate_escape_velocity(mass: float, radius: float) -> float:
    """
    Calcula a velocidade de escape de um corpo celeste.
    :param mass: Massa do corpo celeste (kg)
    :param radius: Raio do corpo celeste (m)
    :return: Velocidade de escape (m/s)
    """
    G = 6.67430e-11  # Constante gravitacional em m³/(kg·s²)
    return (2 * G * mass / radius)**0.5

if __name__ == "__main__":
    run_test(calculate_resistance, 10, 2)
    run_test(simulate_rocket_launch, 100, 9.81, 5)
    run_test(calculate_average_speed, 100, 2)
    run_test(calculate_force_newthon, 10, 9.81)
    run_test(calculate_gravitational_force, 5.972e24, 7.348e22, 3.844e8)
    run_test(calculate_gravitational_potential_energy, 10, 5)
    run_test(calculate_kinetic_energy, 10, 20)
    run_test(calculate_coulomb_force, 1e-6, -1e-6, 0.01)
    run_test(calculate_escape_velocity, 5.972e24, 6.371e6)