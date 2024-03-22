from lyncs_setuptools import setup

setup(
    "lyncs_utils",
    install_requires=[
        "dataclasses",
    ],
    extras_require={
        "numpy": ["numpy"],
        "clickit": ["click"],
        "test": ["pytest", "pytest-cov", "ipython", "numpy", "lyncs_setuptools"],
    },
    entry_points={
        "pytest11": [
            "lyncs_utils = lyncs_utils.pytest",
        ],
    },
)
