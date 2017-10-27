from setuptools import setup, find_packages

setup(
    name='Margatsni',
    version='1.0',
    author='Solid State Group',
    packages=find_packages(),
    py_modules = ['app'],
    zip_safe=False,
    install_requires=['flask','python-instagram', 'flask_bootstrap', 'instagram', 'pytest']
	)

'''
A4 - libraries
Calvin Teng - flask_sqlalchemy
Aaron Reyes - bs4
Ismail Abbas - Scrapy
Brandon Nguyen - python-instagram
Oscar Alcaraz - flask_bootstrap
'''
