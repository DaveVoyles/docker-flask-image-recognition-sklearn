FROM python:3
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential && pip install --upgrade pip && pip install numpy && pip install flask && pip install scipy && pip install scikit-learn && pip install matplotlib && pip install requests && pip install pillow
COPY . /app
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["app.py"]