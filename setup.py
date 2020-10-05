from lyncs_setuptools import setup

setup(
    "lyncs_utils",
    install_requires=[
        "lyncs_setuptools",
        "gitpython",
        "cmake",
    ],
    extras_require={"test": ["pytest", "pytest-cov", "ipython"]},
)
