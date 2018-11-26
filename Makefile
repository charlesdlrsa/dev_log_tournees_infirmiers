clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__
	@rm -fr __pycache__
	@rm -fr build
	@rm -fr dist
	@rm -fr dev_log-*.dist-info
	@rm -fr dev_log.egg-info

wheel: clean
	@python3 setup.py bdist_wheel

install: clean wheel
	@pip3 install -U dist/*.whl

check_code:
	@flake8 scripts/* dev_log/*.py tests/*.py
