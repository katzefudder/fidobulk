run:
	poetry run python ykbatch.py

test:
	poetry run python -m pytest

coverage:
	poetry run coverage run -m pytest
	poetry run coverage report -m

build:
	pyinstaller --noconsole --onefile --windowed --icon=favicon.icns ykbatch.py