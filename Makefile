set_flask_app:
    export FLASK_APP=flask_app/app.py

db_init:
    flask db init
    flask db migrate

db_upgrade:
    flask db migrate
    flask db upgrade

db_downgrade:
    flask db downgrade

app_build:
    sudo docker-compose --env-file .env up -d --build

app_up:
    sudo docker-compose --env-file .env up -d

app_down:
    sudo docker-compose down

volumes_remove:
	sudo docker rm -f $(sudo docker ps -aq)

stop_nginx:
    sudo nginx -s stop

look_80:
    sudo lsof -i -P -n | grep 80