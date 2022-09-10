FROM python:3.10
# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

WORKDIR /backend
COPY requirements.txt /backend/
RUN apt-get update
RUN apt-get install -y python3 pip
RUN apt-get install -y ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /backend/

# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
# RUN chmod +x /wait

# COPY wait-for-it.sh wait-for-it.sh

COPY wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh
CMD ./wait-for-it.sh db:3306 -s -t 30 -- uvicorn --host=0.0.0.0 --port 8000 main:app --reload
# CMD uvicorn --host=0.0.0.0 --port 8000 main:app --reload
#./wait-for-it.sh localhost:3306 -s -t 30 -- 

# wait-for-it.sh host:port [-s] [-t timeout] [-- command args]

# CMD uvicorn --host=0.0.0.0 --port 8000 main:app