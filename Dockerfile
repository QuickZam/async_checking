FROM python:3.8-slim-buster
RUN apt-get -y update
RUN apt-get -y install git
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN apt-get install ffmpeg libsm6 libxext6  -y
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4000"]