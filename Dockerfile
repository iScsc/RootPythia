FROM python:3.10.9

WORKDIR /opt/pyflag-bot
COPY src ./src

ENTRYPOINT ["python3"]
CMD ["/opt/pyflag-bot/src/main.py"]
