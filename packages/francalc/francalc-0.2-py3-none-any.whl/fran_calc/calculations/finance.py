from ..modules import run_test

def calculate_simple_interest(principal: float, rate: float, time: float) -> float:
    """
    Calcula o juro simples.
    :param principal: Capital inicial
    :param rate: Taxa de juros (em porcentagem)
    :param time: Tempo (em anos)
    :return: Juro simples
    """
    return principal * (rate / 100) * time	

def calculate_percentage_change(original: float, new: float) -> float:
    """
    Calcula a variação percentual entre dois valores.
    :param original: Valor original
    :param new: Novo valor
    :return: Variação percentual
    """
    return ((new - original) / original) * 100

def calculate_compound_interest(principal: float, rate: float, time: float) -> float:
    """
    Calcula o juro composto.
    :param principal: Capital inicial
    :param rate: Taxa de juros (em porcentagem)
    :param time: Tempo (em anos)
    :return: Montante total após o tempo
    """
    return principal * ((1 + (rate / 100)) ** time)

# tabela IRPF mensal (valores em R$)
# [(limite_inferior, limite_superior, aliquota), ...]
FAIXAS_IRPF = [
    (0.00,    1903.98, 0.00  ),  # isento
    (1903.99, 2826.65, 0.075 ),  # 7.5%
    (2826.66, 3751.05, 0.15  ),  # 15%
    (3751.06, 4664.68, 0.225 ),  # 22.5%
    (4664.69, float('inf'), 0.275),  # 27.5%
]

def calculate_income_tax(renda_mensal: float) -> float:
    """
    Retorna o valor do IRPF devido sobre uma dada renda mensal,
    calculado de forma progressiva.
    """
    imposto = 0.0

    for limite_inf, limite_sup, aliquota in FAIXAS_IRPF:
        if renda_mensal > limite_inf:
            # Quanto dessa faixa será tributado?
            base_tributavel = min(renda_mensal, limite_sup) - limite_inf
            imposto += base_tributavel * aliquota

    return imposto

if __name__ == "__main__":
    # Testa a função com valores de exemplo
    run_test(calculate_simple_interest, 1000, 5, 2)  # Exemplo: 1000, 5%, 2 anos
    run_test(calculate_percentage_change, 100, 150)  # Exemplo: 100 para 150
    run_test(calculate_compound_interest, 1000, 5, 2)  # Exemplo: 1000, 5%, 2 anos
    run_test(calculate_income_tax, 3000)  # Exemplo: Renda mensal de 3000