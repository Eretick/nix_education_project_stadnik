set_sudo:
	export USER_SUDO_PASSWORD=9966

set_flask_app:
	export FLASK_APP=flask_app/app.py

get_flask_app:
	echo $(FLASK_APP)

app_logs:
	sudo docker logs films_app

go_to_app:
	sudo docker exec -it films_app bash

db_init:
	flask db init

db_migrate:
	flask db migrate

db_upgrade:
	flask db upgrade

db_downgrade:
	flask db downgrade

app_build:
	echo $(USER_SUDO_PASSWORD) | sudo -S docker-compose --env-file .env.list up -d --build

app_up:
	sudo docker-compose --env-file .env.list up -d

app_down:
	echo $USER_SUDO_PASSWORD | sudo -S docker-compose down

volumes_remove:
	echo $USER_SUDO_PASSWORD | sudo -S docker rm -f $(sudo docker ps -aq)

stop_nginx:
	echo $USER_SUDO_PASSWORD | sudo -S nginx -s stop

look_80:
	sudo lsof -i -P -n | grep 80