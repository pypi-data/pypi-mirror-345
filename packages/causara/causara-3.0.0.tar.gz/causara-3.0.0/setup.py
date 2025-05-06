from setuptools import setup, find_packages

setup(
    name="causara",
    version="3.0.0",
    author="causara UG",
    author_email="support@causara.com",
    description="Causara is a Python package for optimizing ANY function using Gurobi. "
                "You just provide the objective function and we use advanced AI to transform this function into a (Surrogate) Gurobi model. "
                "Additionally, we have developed an **AI-assisted GUI** designed to simplify the interaction and no-code modification of Gurobi models.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://www.causara.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*"],
    },
    license="Proprietary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9, <3.13",
    install_requires=[
        "torch",
        "bcrypt",
        "numpy<2",
        "scipy",
        "gurobipy",
        "pandas",
        "openpyxl",
        "reportlab",
        "psutil",
        "sympy",
        "tqdm",
        "pywebview",
        "qtpy; sys_platform == 'linux'",
        "PyQt5; sys_platform == 'linux'",
        "PyQtWebEngine; sys_platform == 'linux'",
        # Use cefpython3 on platforms other than Linux and macOS (e.g. Windows)
        "cefpython3; sys_platform != 'linux' and sys_platform != 'darwin'",
        "rdkit",
        "matplotlib",
        "folium",
        "orjson",
        "pyyaml",
        "pywin32; sys_platform=='win32'"
    ],
)
