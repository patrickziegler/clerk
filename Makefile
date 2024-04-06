python_ok := $(shell python3 -c "import sys; result = \"ok\" if sys.version_info.minor >= 11 else \"nok\"; print(result)")

install:
ifeq ("$(python_ok)", "ok")
	pip3 install -r requirements.txt --user --break-system-packages
else
	pip3 install -r requirements.txt --user
endif
	python3 setup.py install --user

develop:
	$(MAKE) venv
	bash -c "source .venv/bin/activate && python setup.py develop"

clean:
	rm -rf .venv build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

venv:
	$(MAKE) clean
	virtualenv --python=/usr/bin/python3 .venv
	bash -c "source .venv/bin/activate && pip install -r requirements.txt"
