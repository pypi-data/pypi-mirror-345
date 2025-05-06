FROM python:3.13.3-slim

ARG VERSION

WORKDIR /timeplus
ADD ./requirements.txt /timeplus
RUN pip3 install -r requirements.txt

ADD ./simulator.py /timeplus/simulator.py

ENTRYPOINT ["python", "simulator.py"]
