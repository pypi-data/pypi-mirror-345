import ast
import operator
import logging
import traceback
from colorama import Fore, Style, init
import os
import math
import shutil

# SAFE EVAL
# 1. Mapeia nodos de operação AST para funções reais
ALLOWED_OPERATORS = {
    ast.Add:    operator.add,
    ast.Sub:    operator.sub,
    ast.Mult:   operator.mul,
    ast.Div:    operator.truediv,
    ast.Pow:    operator.pow,
    ast.USub:   operator.neg,    # suporte a -x
}
class SafeEvalVisitor(ast.NodeVisitor):
    def visit(self, node):
        # Método genérico: chama o adequado ou lança erro
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        elif isinstance(node.op, ast.Pow):
            return left ** right
        elif isinstance(node.op, ast.Mod):
            return left % right           # ← aqui você adiciona o suporte ao `%`
        else:
            raise ValueError(f"Operador não permitido: {node.op}")

    def visit_UnaryOp(self, node):
        # Para suportar números negativos
        if type(node.op) not in ALLOWED_OPERATORS:
            raise ValueError(f"Operador unário não permitido: {node.op}")
        operand = self.visit(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)

    def visit_Num(self, node):
        return node.n

    def visit_Constant(self, node):
        # Compatível com Python ≥3.8 (literais)
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Constante não-numérica: {node.value}")

    def visit_Paren(self, node):
        # Parênteses são tratados via composição de BinOp/UOp
        return self.visit(node.value)

    def generic_visit(self, node):
        # Rejeita tudo que não for explicitamente permitido
        raise ValueError(f"Nó não permitido: {node.__class__.__name__}")
def safe_eval(expr: str) -> float:
    """
    Avalia uma expressão aritmética apenas com +, -, *, /, ** e números.
    Lança ValueError em caso de qualquer outro conteúdo.
    """
    # 2. Parse na mode 'eval' para proibir atribuições, chamadas etc.
    tree = ast.parse(expr, mode='eval')
    visitor = SafeEvalVisitor()
    return visitor.visit(tree)

# Inicializa o Colorama (para cores no Windows)
init(autoreset=True)
# Configura o logger para escrever erros em test.log
logging.basicConfig(
    filename='.log',
    filemode='w',               # 'a' para acrescentar, 'w' para sobrescrever
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)
def run_test(func, *args, **kwargs):
    """
    Executa func(*args, **kwargs).
    Se não lançar exceção:
      - imprime em verde 'Passed' + resultado
      - retorna (True, resultado)
    Se lançar exceção:
      - imprime em vermelho 'Not passed'
      - grava o traceback completo em test.log
      - retorna (False, exceção)0

    """
    try:
        result = func(*args, **kwargs)
        print(Fore.GREEN + "Passed" + Style.RESET_ALL + " | " + Fore.YELLOW + f"{func.__qualname__}" + Style.RESET_ALL + f" | Result: {result}")
        return True, result
    except Exception as e:
        # imprime só a indicação de falha
        print(Fore.RED + "Not passed" + Style.RESET_ALL)
        # e registra o traceback completo no log
        logging.error("Test failed for %r with args=%r, kwargs=%r", func, args, kwargs)
        logging.error(traceback.format_exc())
        return False, e

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_in_columns(items: list[str], min_cols: int = 2,
                     padding: int = 4, max_width: int | None = None):
    """
    Mostra itens em várias colunas, tentando garantir pelo menos `min_cols`
    (a menos que seja impossível).  Lida melhor com itens muito longos.
    """
    cols, _ = shutil.get_terminal_size(fallback=(80, 20))
    if max_width is None:
        max_width = cols

    # Para descobrir o tamanho "típico" dos itens, ignoramos o 5% mais comprido
    sorted_by_len = sorted(items, key=len)
    cutoff_idx = int(len(sorted_by_len) * 0.95)
    typical_len = len(sorted_by_len[cutoff_idx]) + padding

    # Calcula colunas tentando usar typical_len; garante min_cols≥2 sempre que couber
    num_cols = max(min_cols, max_width // typical_len) or 1
    rows = math.ceil(len(items) / num_cols)

    for r in range(rows):
        line = []
        for c in range(num_cols):
            idx = c * rows + r
            if idx < len(items):
                # Usa largura fixa do “típico”, mas evita cortar
                line.append(items[idx].ljust(typical_len))
        print("".join(line))


# Exemplo de uso:
if __name__ == "__main__":
    run_test(safe_eval, "2 + 2 - 2 * 2 /  2 ** 2 % 2")