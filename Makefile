lint:
	flake8 --config .flake8
	black --config black.toml --check .
	isort --check .

format:
	black --config black.toml .
	isort .

migrate:
	docker-compose exec backuper python ./project/manage.py migrate

makemigrations:
	docker-compose exec backuper python ./project/manage.py makemigrations

collectstatic:
	docker-compose exec backuper python ./project/manage.py collectstatic

create-default-users:
	docker-compose exec backuper python ./project/manage.py createdefaultadmin
	docker-compose exec backuper python ./project/manage.py createdefaultuser

fill-rclone-providers-model:
	docker-compose exec backuper python ./project/manage.py fill_rclone_providers
