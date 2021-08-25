from lyncs_setuptools import setup

setup(
    "lyncs_utils",
    install_requires=[
        "numpy",
    ],
    extras_require={
        "test": ["pytest", "pytest-cov", "ipython", "numpy", "lyncs_setuptools"]
    },
)
