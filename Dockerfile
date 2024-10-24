FROM python:3.11

LABEL authors="belyankinaer"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY app/ .

# Указываем команду для запуска приложения
CMD ["python", "main.py"]