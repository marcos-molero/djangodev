from setuptools import setup, find_packages

def leer_requisitos():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name='imed',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=leer_requisitos(),
    author='Marcos Molero',
    author_email='molero.marcos@hotmail.com',
    description='Administración médica',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
)