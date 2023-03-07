FROM python:3.10.9

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /opt/root-pythia
COPY src ./src

ENTRYPOINT ["python3"]
CMD ["/opt/root-pythia/src/main.py"]
