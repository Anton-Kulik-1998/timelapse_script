import os
import shutil
import logging
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CameraDirectoryHandler:
    def __init__(self, camera_dirs):
        """Инициализация обработчика директорий камер.
        
        Args:
            camera_dirs (list of str): Список путей к директориям с папками ежедневных фото.
        """
        self.camera_dirs = [Path(d) for d in camera_dirs]
    
    def get_photos_for_time(self, day_dir, target_times):
        """Находит фотографии в указанной папке дня на основе временных меток.
        
        Args:
            day_dir (Path): Путь к папке конкретного дня.
            target_times (list of datetime.time): Список целевых временных отметок для отбора фото.
        
        Returns:
            list of Path: Список путей к файлам, подходящих по времени.
        """
        photos = []
        all_files = list(day_dir.glob('*.jpg'))  # Предполагаем, что фото имеют расширение .jpg
        all_files.sort(key=lambda x: x.stat().st_mtime)  # Сортируем по времени изменения
        
        for target_time in target_times:
            closest_photo = None
            min_diff = timedelta.max  # Максимально возможное время
            
            for file in all_files:
                file_time = datetime.fromtimestamp(file.stat().st_mtime).time()
                time_diff = abs(datetime.combine(datetime.today(), file_time) - datetime.combine(datetime.today(), target_time))
                
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_photo = file
            
            if closest_photo:
                photos.append(closest_photo)
        
        return photos
    
    def get_photos_for_day(self, date):
        """Находит фото для конкретной даты из всех камер.
        
        Args:
            date (str): Дата в формате 'YYYYMMDD' (например, '20241019').
        
        Returns:
            dict: Словарь, где ключи — директории камер, а значения — списки выбранных фото.
        """
        target_times = [datetime.strptime(t, '%H:%M').time() for t in ['09:00', '12:00', '15:00']]
        result = {}
        
        for camera_dir in self.camera_dirs:
            day_dir = camera_dir / date
            if day_dir.exists() and day_dir.is_dir():
                photos = self.get_photos_for_time(day_dir, target_times)
                result[camera_dir] = photos
            else:
                logging.warning(f"Директория {day_dir} не найдена или не является папкой.")
        
        return result


class PhotoMover:
    def __init__(self, destination_dirs):
        """Инициализация класса для перемещения фото.
        
        Args:
            destination_dirs (list of str): Список путей для сохранения фотографий.
        """
        self.destination_dirs = [Path(d) for d in destination_dirs]
    
    def move_photos(self, photos):
        """Перемещает фото в доступные директории назначения.
        
        Args:
            photos (list of Path): Список фотографий для перемещения.
        """
        for dest_dir in self.destination_dirs:
            if not dest_dir.exists():
                logging.warning(f"Директория назначения {dest_dir} недоступна. Пропуск.")
                continue

            for photo in photos:
                try:
                    dest_path = dest_dir / photo.name
                    shutil.copy2(photo, dest_path)  # Копируем фото, сохраняя метаданные
                    logging.info(f"Фото {photo.name} успешно перемещено в {dest_path}")
                except Exception as e:
                    logging.error(f"Ошибка при перемещении {photo.name}: {e}")


class TimelapseCreator:
    def __init__(self, camera_dirs, destination_dirs):
        """Инициализация создателя таймлапсов.
        
        Args:
            camera_dirs (list of str): Список директорий камер.
            destination_dirs (list of str): Список директорий для сохранения фото.
        """
        self.camera_handler = CameraDirectoryHandler(camera_dirs)
        self.photo_mover = PhotoMover(destination_dirs)
    
    def process_day(self, date):
        """Обрабатывает фотографии за конкретный день.
        
        Args:
            date (str): Дата в формате 'YYYYMMDD'.
        """
        photos_by_camera = self.camera_handler.get_photos_for_day(date)
        
        for camera, photos in photos_by_camera.items():
            if photos:
                logging.info(f"Найдено {len(photos)} фото для камеры {camera} за {date}.")
                self.photo_mover.move_photos(photos)
            else:
                logging.info(f"Фото не найдено для камеры {camera} за {date}.")


def run_timelapse_daily(timelapse_creator):
    """Функция для ежедневного запуска процесса обработки фото."""
    while True:
        # Текущая дата
        current_date = datetime.now().strftime('%Y%m%d')
        
        try:
            timelapse_creator.process_day(current_date)
            logging.info(f"Обработка завершена для даты: {current_date}")
        except Exception as e:
            logging.error(f"Ошибка в процессе обработки: {e}")

        # Рассчитываем оставшееся время до следующего дня
        next_run_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_sleep = (next_run_time - datetime.now()).total_seconds()

        logging.info(f"Следующий запуск через {time_to_sleep / 3600:.2f} часов.")
        
        time.sleep(time_to_sleep)  # Засыпаем до следующего дня


def main():
    """Основная функция программы, запускающая таймлапс в отдельном потоке."""
    
    # Получаем пути к директориям камер и назначения через переменные окружения
    camera_dirs = os.getenv("CAMERA_DIRS", "").split(",")
    destination_dirs = os.getenv("DESTINATION_DIRS", "").split(",")

    if not camera_dirs or not destination_dirs:
        logging.error("Не указаны директории камер или директории для сохранения фотографий.")
        return

    timelapse_creator = TimelapseCreator(camera_dirs, destination_dirs)

    # Запускаем обработку в отдельном потоке
    timelapse_thread = threading.Thread(target=run_timelapse_daily, args=(timelapse_creator,))
    timelapse_thread.daemon = True  # Поток завершится вместе с основным потоком программы
    timelapse_thread.start()

    # Основной поток программы можно завершить или продолжить выполнение других задач
    while timelapse_thread.is_alive():
        try:
            time.sleep(60)  # Просто поддерживаем основной поток в активном состоянии
        except KeyboardInterrupt:
            logging.info("Прерывание программы пользователем.")
            break


if __name__ == "__main__":
    main()
