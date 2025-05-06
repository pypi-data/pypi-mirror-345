from setuptools import setup

setup(
    name='dkrresource',
    version='1.2',
    author='Leticia Figueiredo',
    author_email='leticia.figueiredo@dkr.tec.br',
    description="DKR Resource",
    install_requires=["sqlalchemy", "requests", "psycopg2-binary"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
