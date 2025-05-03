from setuptools import setup

setup(
    name='dkrlog',
    version='2.1',
    author='Leticia Figueiredo',
    author_email='leticia.figueiredo@dkr.tec.br',
    description="DKR Log",
    install_requires=[
        "requests",
        "pytz",
        "logzero",
        "sqlalchemy",
        "psycopg2-binary"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
