FROM python:3.8
EXPOSE 5000
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
# CMD ["python", "app.py"]  # before gunicorn, keep for myself
CMD ["gunicorn", "-b 0.0.0.0:5000", "-w 4", "app:films_app"]