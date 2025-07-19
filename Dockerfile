FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "backend/bridge.py"]  # Default to bridge; customize
