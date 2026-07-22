setup:
	python -m venv venv
	./venv/Scripts/pip install -r requirements.txt
run:
    # Put linux path if need
	./venv/Scripts/python manage.py runserver

up:
	docker-compose up --build
down:
	docker-compose down -v
