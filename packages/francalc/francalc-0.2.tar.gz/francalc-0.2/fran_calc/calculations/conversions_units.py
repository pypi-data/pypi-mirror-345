from ..modules import run_test
import requests
import re

def calculate_time(horario, horario_a_frente):
    # Converte o horário para minutos
    horas, minutos = map(int, horario.split(':'))
    total_minutos = horas * 60 + minutos

    # Converte o horário a frente para minutos
    horas_a_frente, minutos_a_frente = map(int, horario_a_frente.split(':'))
    total_minutos_a_frente = horas_a_frente * 60 + minutos_a_frente

    # Calcula a diferença em minutos
    diferenca_minutos = total_minutos + total_minutos_a_frente

    # Converte de volta para horas e minutos
    horas_resultado = diferenca_minutos // 60
    minutos_resultado = diferenca_minutos % 60

    return f"{horas_resultado:02}:{minutos_resultado:02}"

def celsius_to_fahrenheit(celsius):
    return f"{(celsius * 9/5) + 32:.2f}"

def meters_to_feet(meters):
    return f"{meters * 3.28084:.2f}"

def kilos_to_pounds(kilos):
    return f"{kilos * 2.20462:.2f}"

def fahrenheit_to_celsius(fahrenheit):
    return f"{(fahrenheit - 32) * 5/9:.2f}"

def feet_to_meters(feet):
    return f"{feet / 3.28084:.2f}"

def pounds_to_kilos(pounds):
    return f"{pounds / 2.20462:.2f}"

def decimal_to_binary(decimal):
    return bin(decimal)[2:]

def decimal_to_octal(decimal):
    return oct(decimal)[2:]

def decimal_to_hexadecimal(decimal):
    return hex(decimal)[2:]

def binary_to_decimal(binary):
    return int(str(binary), 2)

def octal_to_decimal(octal):
    return int(str(octal), 8)

def hexadecimal_to_decimal(hexadecimal):
    return int(str(hexadecimal), 16)

# mapeamento só para os cryptos que você quer (aqui só BTC)
_CRYPTO_IDS = {"BTC": "bitcoin"}

def convert_currency(amount: float, frm: str, to: str) -> float:
    """
    Converte `amount` de `frm` para `to`:
      - Fiat→Fiat: usa https://www.floatrates.com/daily/{base}.json
      - Fiat↔Crypto (ou Crypto↔Crypto): usa CoinGecko public API
    Não exige API key nem scraping de HTML.
    """
    frm, to = frm.upper(), to.upper()

    # Fiat ↔ Fiat
    if frm != to and frm not in _CRYPTO_IDS and to not in _CRYPTO_IDS:
        # FloatRates retorna {"usd":{...,"rate":0.19}, "eur":{...}}
        url = f"https://www.floatrates.com/daily/{frm.lower()}.json"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        rate_info = data.get(to.lower())
        if not rate_info:
            raise ValueError(f"Moeda fiat '{to}' não suportada por FloatRates")
        return f"{amount * rate_info["rate"]:.4f}"

    # Crypto → Fiat
    if frm in _CRYPTO_IDS and to not in _CRYPTO_IDS:
        coin = _CRYPTO_IDS[frm]
        vc = to.lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={vc}"
        resp = requests.get(url)
        resp.raise_for_status()
        price = resp.json().get(coin, {}).get(vc)
        if price is None:
            raise ValueError(f"Falha ao obter preço {frm}→{to}")
        return f"{amount * price:.4f}"

    # Fiat → Crypto
    if frm not in _CRYPTO_IDS and to in _CRYPTO_IDS:
        coin = _CRYPTO_IDS[to]
        vc = frm.lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={vc}"
        resp = requests.get(url)
        resp.raise_for_status()
        price = resp.json().get(coin, {}).get(vc)
        if price is None:
            raise ValueError(f"Falha ao obter preço {frm}→{to}")
        return f"{amount / price:.4f}"

    # Crypto → Crypto
    if frm in _CRYPTO_IDS and to in _CRYPTO_IDS:
        coin1 = _CRYPTO_IDS[frm]
        coin2 = _CRYPTO_IDS[to]
        # pega ambos em USD e faz cross‐rate
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={coin1},{coin2}&vs_currencies=usd"
        )
        resp = requests.get(url)
        resp.raise_for_status()
        js = resp.json()
        p1 = js.get(coin1, {}).get("usd")
        p2 = js.get(coin2, {}).get("usd")
        if p1 is None or p2 is None:
            raise ValueError(f"Falha ao obter preço {frm}→{to}")
        return f"{amount * (p1 / p2):.4f}"

    # caso forem iguais ou não suportados
    if frm == to:
        return f"{amount:.4f}"
    raise ValueError(f"Par de moedas não suportado: {frm} → {to}")

def real_to_dollar(real):
    return convert_currency(real, "BRL", "USD")

def real_to_euro(real):
    return convert_currency(real, "BRL", "EUR")

def real_to_argentine_peso(real):
    return convert_currency(real, "BRL", "ARS")

def real_to_bitcoin(real):
    return convert_currency(real, "BRL", "BTC")

def dollar_to_real(dolar):
    return convert_currency(dolar, "USD", "BRL")

def euro_to_real(euro):
    return convert_currency(euro, "EUR", "BRL")

def argentine_peso_to_real(peso):
    return convert_currency(peso, "ARS", "BRL")

def bitcoin_to_real(bitcoin):
    return convert_currency(bitcoin, "BTC", "BRL")

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converte valores R,G,B (0–255) para string HEX '#RRGGBB'."""
    for v in (r, g, b):
        if not (0 <= v <= 255):
            raise ValueError(f"Canal fora do intervalo: {v}")
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def hex_to_rgb(h: str) -> tuple[int,int,int]:
    """Converte string HEX (3 ou 6 dígitos, com ou sem '#') para tupla (R, G, B)."""
    h = h.lstrip('#')
    if len(h) == 3:
        # expande 'FAB' → 'FFAABB'
        h = ''.join(c*2 for c in h)
    if len(h) != 6 or not re.fullmatch(r'[0-9A-Fa-f]{6}', h):
        raise ValueError(f"Formato HEX inválido: '{h}'")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def convert_rgb_hex(value: str) -> str:
    """
    Detecta se `value` é RGB ou HEX e converte para o outro formato.
    - Input HEX: '#RRGGBB', 'RRGGBB', '#RGB' ou 'RGB'
      → output 'rgb(r, g, b)'
    - Input RGB: 'r, g, b' ou 'rgb(r, g, b)'
      → output '#RRGGBB'
    """
    v = value.strip()
    # --- tenta HEX ---
    if re.fullmatch(r'#?[0-9A-Fa-f]{3}(\b|$)', v) or re.fullmatch(r'#?[0-9A-Fa-f]{6}(\b|$)', v):
        r, g, b = hex_to_rgb(v)
        return f"rgb({r}, {g}, {b})"
    
    # --- tenta RGB ---
    m = re.fullmatch(
        r'(?:rgb\()?\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)?',
        v,
        re.IGNORECASE
    )
    if m:
        r, g, b = map(int, m.groups())
        return rgb_to_hex(r, g, b)
    
    raise ValueError(
        "Formato não reconhecido. Use '#RRGGBB', 'RRGGBB', '#RGB', 'RGB', "
        "'r, g, b' ou 'rgb(r, g, b)'."
    )

def ascii_to_binary(ascii_str: str) -> str:
    """Converte string ASCII para binário."""
    return ' '.join(format(ord(c), '08b') for c in ascii_str)

if __name__ == "__main__":
    run_test(calculate_time, "12:30", "02:00")
    run_test(convert_currency, 100, "BRL", "USD")
    run_test(real_to_dollar, 100)
    run_test(real_to_euro, 100)
    run_test(real_to_argentine_peso, 100)
    run_test(real_to_bitcoin, 100)
    run_test(dollar_to_real, 100)
    run_test(euro_to_real, 100)
    run_test(argentine_peso_to_real, 100)
    run_test(bitcoin_to_real, 100)
    run_test(celsius_to_fahrenheit, 100)
    run_test(meters_to_feet, 100)
    run_test(kilos_to_pounds, 100)
    run_test(fahrenheit_to_celsius, 100)
    run_test(feet_to_meters, 100)
    run_test(pounds_to_kilos, 100)
    run_test(decimal_to_binary, 100)
    run_test(decimal_to_octal, 100)
    run_test(decimal_to_hexadecimal, 100)
    run_test(binary_to_decimal, 100)
    run_test(octal_to_decimal, 100)
    run_test(hexadecimal_to_decimal, 100)
    run_test(convert_rgb_hex, "#FFAABB")
    run_test(convert_rgb_hex, "rgb(255,170,187)")
    run_test(ascii_to_binary, "FranCalculator")