# setup.py
from setuptools import setup, find_packages

setup(
    name="francalc",          # nome no PyPI
    version="0.3.0",
    author="Lukydnomo",
    packages=find_packages(),       # encontra fran_calculator e fran_calculator.calculations
    include_package_data=True,
    install_requires=[              # só se você tiver deps externas
        "requests", "pathlib", "colorama"
    ],
    entry_points={                  # se quiser criar script 'franCalc' no PATH
        "console_scripts": [
            "franCalc = fran_calc.gui:main",
        ],
    },
)
