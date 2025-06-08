FROM python:3.13-slim

WORKDIR /app
COPY generator.py .

RUN pip install kafka-python

CMD ["python", "generator.py"]
