from ..modules import run_test
from datetime import datetime

def calculate_age(birth_date: str):
    """
    Calcula a idade em anos, meses e dias a partir de duas datas no formato 'YYYY-MM-DD'.
    """

    # Converte as strings para objetos datetime
    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
    current_date = datetime.now()

    # Calcula a diferença entre as datas
    delta = current_date - birth_date

    # Converte a diferença para anos, meses e dias
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30

    return f"{years} anos, {months} meses, {days} dias"

if __name__ == "__main__":
    run_test(calculate_age, '2010-05-29')