DATA_DIR = data

setup:
	pip install -r requirements.txt

test: setup
	python -m pytest test

generate: setup
	mkdir -p $(DATA_DIR)
	python -m synthetic.generate -t $(DATA_DIR)

notebook: generate
	DATA=$(DATA_DIR) jupyter notebook Model.ipynb

