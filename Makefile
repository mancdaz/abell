clean:
	find . -name '*.pyc' -delete

server:
	python3 manage.py runserver --host 0.0.0.0
