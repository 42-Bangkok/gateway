include .env
export

default:
	@echo "Please specify a target to make."
# Export python requirements to requirements.txt
req:
	poetry add poetry-plugin-export -G dev
	poetry export -f requirements.txt --output requirements.txt --without-hashes
# Migrate database
m:
	cd app &&\
	poetry run python manage.py migrate
# Make migrations
mm:
	cd app &&\
	poetry run python manage.py makemigrations
# Drop local database tables
drop-tables:
	psql "dbname=postgres host=db port=5432 user=postgres password=postgres" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" ;\
	exit 0;
# Re-initialize project
init-proj: drop-tables m
# Run hypercorn WSGI
hypercorn:
	cd app &&\
	python manage.py collectstatic --noinput &&\
	hypercorn app.asgi:application --workers 4 -b 0.0.0.0:8000
# Run celery worker
run-worker:
	cd app &&\
	poetry run celery -A app worker -l INFO -E
# Run celery scheduler; deprecated
run-beat:
	cd app &&\
	poetry run celery -A app beat -l INFO
# Run celery worker with database scheduler
run-db-beat:
	cd app &&\
	celery -A app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
# Tag & trigger github actions to build and push docker image
release:
	ver=$(shell date +%Y.%m.%d.%s) &&\
	echo $$ver &&\
	git tag -a $$ver -m "Release $$ver" &&\
	git push origin $$ver
update-intraprofile:
	cd app &&\
	poetry run python manage.py update_intraprofile
