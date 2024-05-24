FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 /app/init_db.py
EXPOSE 8080
CMD ["gunicorn","-w", "4", "-b", "0.0.0.0:8080", "app:app"]
