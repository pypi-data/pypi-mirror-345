from setuptools import setup, find_packages # type: ignore

LONG_DESCRIPTION: str = (
    'The depoc-api Python library makes HTTP requests to Depoc '
    'in order to retrieve, create, update, or delete resources '
    '(e.g. Order, Product, Contacts).'
)

setup(
    name='depoc',
    version='0.1.4',  
    description='Python bindings for the Depoc API',
    long_description=LONG_DESCRIPTION,
    author='Hugo Belém',
    url='https://github.com/hugobelem/depoc-api',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'requests >= 2.32.3',
        'click  >= 8.1.8',
        'appdirs >= 1.4.4',
        'rich >= 13.9.4', 
    ],
    entry_points={
        'console_scripts': [
            'depoc = depoc.cli:main',
        ],
    },
    python_requires='>=3.12',
    setup_requires=['wheel'],
) 
