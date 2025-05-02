#!/usr/bin/env python3
import sys
import pkgutil
import importlib
import inspect
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QListWidget,
    QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator

# Import ACTIONS mapping to build parameter specs
def flatten_actions(actions, specs):
    for key, val in actions.items():
        if isinstance(val, tuple):
            fn, params = val
            specs[fn.__name__] = params
        elif isinstance(val, dict) and 'sub' in val:
            flatten_actions(val['sub'], specs)

from fran_calc.fran_calc import ACTIONS
PARAM_SPECS = {}
flatten_actions(ACTIONS, PARAM_SPECS)

class ModuleTab(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self._load_functions()
        self._init_ui()

    def _load_functions(self):
        pkg = importlib.import_module(f"fran_calc.calculations.{self.module_name}")
        self.functions = {
            name: func for name, func in inspect.getmembers(pkg, inspect.isfunction)
            if name in PARAM_SPECS
        }

    def _init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left panel: filter + list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filtrar funções...")
        self.search.textChanged.connect(self._filter_functions)
        left_layout.addWidget(self.search)
        self.list_widget = QListWidget()
        self.list_widget.addItems(sorted(self.functions.keys()))
        self.list_widget.currentTextChanged.connect(self._on_function_selected)
        left_layout.addWidget(self.list_widget)

        # Right panel: form + result
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.form_widget)
        right_layout.addWidget(self.scroll)
        self.calculate_btn = QPushButton("Calcular")
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.clicked.connect(self._on_calculate)
        right_layout.addWidget(self.calculate_btn)
        self.result_label = QLabel("Resultado:")
        right_layout.addWidget(self.result_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)

    def _filter_functions(self, text):
        self.list_widget.clear()
        for name in sorted(self.functions.keys()):
            if text.lower() in name.lower():
                self.list_widget.addItem(name)

    def _on_function_selected(self, fn_name):
        # Clear existing form
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.removeRow(i)
        self.inputs = []
        self.fn = self.functions.get(fn_name)
        for param_name, typ in PARAM_SPECS.get(fn_name, []):
            le = QLineEdit()
            if typ is int:
                le.setValidator(QIntValidator())
            elif typ is float:
                le.setValidator(QDoubleValidator())
            self.form_layout.addRow(f"{param_name} ({typ.__name__}):", le)
            self.inputs.append((typ, le))
        self.calculate_btn.setEnabled(bool(self.inputs))
        self.result_label.setText("Resultado:")

    def _on_calculate(self):
        try:
            args = [typ(le.text()) for typ, le in self.inputs]
            result = self.fn(*args)
            self.result_label.setText(f"Resultado: {result}")
        except Exception as e:
            self.result_label.setText(f"Erro: {e}")

class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FranCalculator GUI")
        self.resize(900, 600)
        self._init_ui()

    def _init_ui(self):
        tabs = QTabWidget()
        import fran_calc.calculations as calc_pkg
        for _, mod_name, _ in pkgutil.iter_modules(calc_pkg.__path__):
            tabs.addTab(ModuleTab(mod_name), mod_name.replace('_', ' ').title())
        self.setCentralWidget(tabs)

def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
