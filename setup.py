from setuptools import setup, find_packages

requirements = """
click
coverage
elasticsearch
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
    author='Zettafox',
    author_email='luis@zettafox',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['scripts/dev_log_hello_world',
             ],
)
