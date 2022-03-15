from lyncs_setuptools import setup

setup(
    "lyncs_utils",
    extras_require={
        "numpy": ["numpy"],
        "dbdict": ["sqlite3"],
        "test": ["pytest", "pytest-cov", "ipython", "numpy", "lyncs_setuptools"],
    },
)
