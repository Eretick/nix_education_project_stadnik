FROM python:3.8
EXPOSE 5000
COPY ./flask_app /app
WORKDIR /app
RUN pip install -r requirements.txt
#ENTRYPOINT ['python']
RUN export FLASK_APP=app.py

# CMD ["python", "app.py"]  # before gunicorn
CMD ["gunicorn", "-b 0.0.0.0:5000", "-w 4", "app:films_app"]