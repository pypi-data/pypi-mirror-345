from ..modules import run_test
import re

def verify_cpf(cpf: str) -> bool:
    """
    Verifica se o CPF é válido.
    """
    if len(cpf) != 11 or not cpf.isdigit():
        return False

    # Verifica os dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[i]):
            return False

    return True

def verify_cnpj(cnpj: str) -> bool:
    """
    Verifica se o CNPJ fornecido é válido.
    Aceita entradas com ou sem pontuação, por ex. '12.345.678/0001-95' ou '12345678000195'.
    Retorna True se for um CNPJ válido, False caso contrário.
    """
    # Remove tudo que não for dígito
    cnpj_digits = re.sub(r'\D', '', cnpj)

    # Tem que ter 14 dígitos
    if len(cnpj_digits) != 14:
        return False

    # Não pode ser todos dígitos iguais (ex: '11111111111111')
    if cnpj_digits == cnpj_digits[0] * 14:
        return False

    def calc_digitos(base: str, pesos: list[int]) -> int:
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # pesos para o primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    # pesos para o segundo dígito verificador
    pesos2 = [6] + pesos1

    # calcula primeiro dígito
    dv1 = calc_digitos(cnpj_digits[:12], pesos1)
    # calcula segundo dígito (incluindo o primeiro)
    dv2 = calc_digitos(cnpj_digits[:12] + str(dv1), pesos2)

    return cnpj_digits.endswith(f"{dv1}{dv2}")

if __name__ == "__main__":
    run_test(verify_cpf, "79823479823")
    run_test(verify_cpf, "06445536000")
    run_test(verify_cnpj, "17766865000166")
    run_test(verify_cnpj, "79847982382366")