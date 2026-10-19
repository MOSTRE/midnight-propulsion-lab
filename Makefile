.PHONY: test run figures app

test:
	python -m pytest -q

run:
	python -m midnight_propulsion_lab.cli run --samples 2000 --seed 20261019

figures:
	python -m midnight_propulsion_lab.cli figures

app:
	streamlit run app/streamlit_app.py
