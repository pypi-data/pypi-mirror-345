from setuptools import setup, find_packages
from pathlib import Path

# La descripción larga va a ser el mismo fichero README.md
long_desc = Path("README.md").read_text("utf-8")

# Datos del paquete
setup(
    name="utilsdsp",
    version="0.1.5",
    author="Duniesky Salazar Pérez",
    author_email="<duniesky.salazar@gmail.com>",
    description="Algunas funciones útiles",
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/dunieskysp/utils_dsp',
    packages=find_packages(),
    install_requires=[
        "outputstyles>=1.0.0",
        "validators>=0.28.1",
        "requests>=2.31.0",
        "tqdm>=4.66.2",
        "curl_cffi>=0.9.0"
    ],
    keywords=['python', 'utilsdsp'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]

)
