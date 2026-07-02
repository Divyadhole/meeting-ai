.PHONY: run test benchmark api

run: benchmark

benchmark:
	python3 run_pipeline.py

test:
	python3 -m unittest discover -s tests -v

api:
	PYTHONPATH=src uvicorn meeting_ai.api:app --reload
