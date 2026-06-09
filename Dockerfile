FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY citizen_manager.py /app/citizen_manager.py

ENV MODE=api
ENV PORT=8000

CMD ["sh", "-c", "python citizen_manager.py $MODE"]
