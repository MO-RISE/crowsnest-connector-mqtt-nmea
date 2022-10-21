FROM python:3.10-slim
# COPY --chmod=555 ./bin/* /usr/local/bin/
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /app

COPY brefv_spec/ brefv_spec/

COPY main.py main.py

CMD ["python3", "main.py"]