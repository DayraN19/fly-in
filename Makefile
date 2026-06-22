install:
	pip install -r requirements.txt

run:
	python3 flyin.py maps/easy/02_simple_fork.txt
debug:
	python3 -m pdb flyin.py

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 .
	mypy --strict .

clean:
	rm -rf __pycache__ .mypy_cache 