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

create-admin:
	@(if test -n '$(username)' & test -n '$(email)' & test -n '$(password)'; then \
  		docker-compose exec backuper python ./project/manage.py createdefaultadmin -u $(username) -e $(email) -p $(password); \
  	  else \
  	    docker-compose exec backuper python ./project/manage.py createdefaultadmin; \
  	  fi)

create-user:
	@(if test -n '$(username)' & test -n '$(email)' & test -n '$(password)'; then \
  		docker-compose exec backuper python ./project/manage.py createdefaultuser -u $(username) -e $(email) -p $(password); \
  	  else \
  	    docker-compose exec backuper python ./project/manage.py createdefaultuser; \
  	  fi)

create-default-users: create-admin create-user
