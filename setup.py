from setuptools import setup, find_packages

requirements = """
amplpy
click
coverage
elasticsearch
flask
flask_sqlalchemy==2.3.2
googlemaps
lxml
numpy
openpyxl
pandas==0.23.4
progressbar2
pyarrow
pytest
pytest-cov
requests
selenium
sendgrid
xlrd
xlsxwriter
"""
# numpy==1.14.3

setup(
    name='dev_log',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    author='',
    author_email='',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],
)
