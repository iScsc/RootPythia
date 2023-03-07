FROM python:3.10.9
RUN apt-get update && pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /opt/pyflag-bot
COPY src ./src

ENTRYPOINT ["python3"]
CMD ["/opt/pyflag-bot/src/main.py"]
