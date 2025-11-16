FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask requests

COPY pihole-proxy.py .

EXPOSE 5555

CMD ["python", "beszels-proxy.py"]
