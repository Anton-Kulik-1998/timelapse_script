import os
import threading
import time
from datetime import datetime, timedelta
from timelapse.timelapse_creator import TimelapseCreator
from timelapse.utils import setup_logging
from timelapse.utils import logging

def run_timelapse_daily(timelapse_creator):
    """Функция для ежедневного запуска процесса обработки фото."""
    while True:
        current_date = datetime.now().strftime('%Y%m%d')
        
        try:
            timelapse_creator.process_day(current_date)
            logging.info(f"Обработка завершена для даты: {current_date}")
        except Exception as e:
            logging.error(f"Ошибка в процессе обработки: {e}")

        next_run_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_sleep = (next_run_time - datetime.now()).total_seconds()

        logging.info(f"Следующий запуск через {time_to_sleep / 3600:.2f} часов.")
        time.sleep(time_to_sleep)

def main():
    """Основная функция программы, запускающая таймлапс в отдельном потоке."""
    setup_logging()

    camera_dirs = os.getenv("CAMERA_DIRS", "").split(",")
    destination_dirs = os.getenv("DESTINATION_DIRS", "").split(",")

    if not camera_dirs or not destination_dirs:
        logging.error("Не указаны директории камер или директории для сохранения фотографий.")
        return

    timelapse_creator = TimelapseCreator(camera_dirs, destination_dirs)

    timelapse_thread = threading.Thread(target=run_timelapse_daily, args=(timelapse_creator,))
    timelapse_thread.daemon = True
    timelapse_thread.start()

    while timelapse_thread.is_alive():
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Прерывание программы пользователем.")
            break

if __name__ == "__main__":
    main()
