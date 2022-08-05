from lyncs_setuptools import setup

setup(
    "lyncs_utils",
    extras_require={
        "numpy": ["numpy"],
        "clickit": ["click"],
        "test": ["pytest", "pytest-cov", "ipython", "numpy", "lyncs_setuptools"],
    },
)
