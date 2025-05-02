venv:
	@echo "Run:"
	@echo "python3 -m venv .venv && source .venv/bin/activate"
	@echo "pip install -e ."

build:
	python3 -m pip install --upgrade build twine
	python3 -m build

pushtest: build
	grep "^version" pyproject.toml | awk -F\" '{print $2}'
	version=$(grep "^version" pyproject.toml | awk -F\" '{print $2}')
	python3 -m twine upload --repository testpypi dist/*$${version}*

pushpypi: build
	grep "^version" pyproject.toml | awk -F\" '{print $2}'
	version=$(grep "^version" pyproject.toml | awk -F\" '{print $2}')
	python3 -m twine upload dist/*
