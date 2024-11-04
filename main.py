import os
import threading
import time
from datetime import datetime, timedelta
from timelapse.timelapse_creator import TimelapseCreator
from timelapse.utils import setup_logging
from timelapse.utils import logging

def run_timelapse_daily(timelapse_creator, run_time, target_times):
    """Функция для ежедневного запуска процесса обработки фото."""
    while True:
        # Ждём, пока не наступит время запуска
        now = datetime.now()
        target_run_time = now.replace(hour=run_time.hour, minute=run_time.minute, second=0, microsecond=0)
        
        if now >= target_run_time:
            # Если текущее время уже прошло целевое время, то запустим копирование на следующий день
            target_run_time += timedelta(days=1)

        time_to_sleep = (target_run_time - now).total_seconds()
        logging.info(f"Ждем до {target_run_time.strftime('%Y-%m-%d %H:%M:%S')} ({time_to_sleep / 3600:.2f} часов).")
        time.sleep(time_to_sleep)

        current_date = datetime.now().strftime('%Y%m%d')
        
        try:
            timelapse_creator.process_day(current_date, target_times)
            logging.info(f"Обработка завершена для даты: {current_date}")
        except Exception as e:
            logging.error(f"Ошибка в процессе обработки: {e}")

        # Устанавливаем точное время следующего запуска на следующий день в то же время
        target_run_time = target_run_time.replace(day=(target_run_time + timedelta(days=1)).day)
        time_to_sleep = (target_run_time - datetime.now()).total_seconds()
        logging.info(f"Следующий запуск запланирован на {target_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(time_to_sleep)

def main():
    """Основная функция программы, запускающая таймлапс в отдельном потоке."""
    setup_logging()

    # Получаем пути к директориям камер и назначения через переменные окружения
    camera_dirs = os.getenv("CAMERA_DIRS", "").split(",")
    destination_dirs = os.getenv("DESTINATION_DIRS", "").split(",")
    copy_time = os.getenv("COPY_TIME", "18:00")  # Время копирования (по умолчанию 18:00)
    target_times = os.getenv("TARGET_TIMES", "09:00,12:00,15:00").split(",")  # Временные метки для поиска фото

    if not camera_dirs or not destination_dirs:
        logging.error("Не указаны директории камер или директории для сохранения фотографий.")
        return

    # Преобразуем строковое время копирования в объект времени
    run_hour, run_minute = map(int, copy_time.split(":"))
    run_time = datetime.now().replace(hour=run_hour, minute=run_minute, second=0, microsecond=0).time()

    # Инициализируем обработчик таймлапса
    timelapse_creator = TimelapseCreator(camera_dirs, destination_dirs)

    # Запускаем обработку в отдельном потоке
    timelapse_thread = threading.Thread(target=run_timelapse_daily, args=(timelapse_creator, run_time, target_times))
    timelapse_thread.daemon = True  # Поток завершится вместе с основным потоком программы
    timelapse_thread.start()

    # Основной поток программы
    while timelapse_thread.is_alive():
        try:
            time.sleep(60)  # Просто поддерживаем основной поток в активном состоянии
        except KeyboardInterrupt:
            logging.info("Прерывание программы пользователем.")
            break

if __name__ == "__main__":
    main()