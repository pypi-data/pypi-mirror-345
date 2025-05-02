from ..modules import run_test
from random import randint

def roll_dice(amount: int, sides: int):
    """
    Simula o lançamento de um dado N vezes.
    Retorna uma lista com os resultados dos lançamentos.
    """
    return [randint(1, sides) for _ in range(amount)]

if __name__ == "__main__":
    run_test(roll_dice, 20, 20)