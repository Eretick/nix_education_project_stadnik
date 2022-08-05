set_flask_app:
	export FLASK_APP=flask_app/app.py

get_flask_app:
	echo $(FLASK_APP)

app_logs:
	docker logs films_app

go_to_app:
	docker exec -it films_app bash

db_init:
	flask db init

db_migrate:
	flask db migrate

db_upgrade:
	flask db upgrade

db_downgrade:
	flask db downgrade

app_build:
	docker-compose --env-file .env.list up -d --build;
	#docker-compose exec -it flask db init;
	#docker-compose exec -it flask db migrate;
	#docker-compose exec -it flask db upgrade;


app_up:
	docker-compose --env-file .env.list up -d

app_down:
	echo $USER_SUDO_PASSWORD | sudo -S docker-compose down

volumes_remove:
	docker rm -f $(docker ps -aq)

stop_nginx:
	sudo -S nginx -s stop

look_80:
	sudo lsof -i -P -n | grep 80