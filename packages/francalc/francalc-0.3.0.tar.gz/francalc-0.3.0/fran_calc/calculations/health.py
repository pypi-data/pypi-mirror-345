from ..modules import run_test

def calculate_bmi(weight: float, height: float) -> str:
    """
    Calcula o IMC (Índice de Massa Corporal) a partir do peso e altura.
    Retorna uma string com a classificação do IMC.
    """
    if height <= 0:
        raise ValueError("Altura deve ser maior que zero.")
    if weight <= 0:
        raise ValueError("Peso deve ser maior que zero.")

    bmi = weight / (height ** 2)

    if bmi < 18.5:
        return "Abaixo do peso"
    elif 18.5 <= bmi < 24.9:
        return "Peso normal"
    elif 25 <= bmi < 29.9:
        return "Sobrepeso"
    else:
        return "Obesidade"
    
if __name__ == "__main__":
    run_test(calculate_bmi, 70, 1.75)  # Exemplo: peso 70 kg, altura 1.75 m