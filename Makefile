clean:
	find . -name '*.pyc' -delete

server:
	python manage.py runserver --host 0.0.0.0
