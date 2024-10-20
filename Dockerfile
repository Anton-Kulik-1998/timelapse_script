# Базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Устанавливаем переменные окружения (опционально, можно передать при запуске)
# ENV CAMERA_DIRS="/path/to/camera1,/path/to/camera2"
# ENV DESTINATION_DIRS="/path/to/save1,/path/to/save2"

# Команда запуска скрипта
CMD ["python", "main.py"]
