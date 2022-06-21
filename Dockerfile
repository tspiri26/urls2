FROM python:3

COPY requirements.txt /root

WORKDIR /root

RUN pip3 install -r requirements.txt

COPY . /root

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
