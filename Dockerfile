FROM python:3.9
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ADD . /driverite
WORKDIR /driverite
RUN pip install -r requirements.txt
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]