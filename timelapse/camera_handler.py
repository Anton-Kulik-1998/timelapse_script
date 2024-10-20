import logging
from pathlib import Path
from datetime import datetime, timedelta

class CameraDirectoryHandler:
    def __init__(self, camera_dirs):
        """Инициализация обработчика директорий камер."""
        self.camera_dirs = [Path(d) for d in camera_dirs]


    def get_photos_for_day(self, date, target_times):
        """Находит фото для конкретной даты из всех камер."""
        result = {}

        for camera_dir in self.camera_dirs:
            day_dir = camera_dir / date / "images"
            
            if day_dir.exists() and day_dir.is_dir():
                photos = self.get_photos_for_time(day_dir, target_times)
                result[camera_dir] = photos
            else:
                logging.info(f"Директория {day_dir} не найдена для даты {date}. Возможно, она еще не создана.")
        
        return result
    
    def get_photos_for_time(self, day_dir, target_times):
        """Находит фотографии в указанной папке дня на основе временных меток."""
        photos = []
        all_files = list(day_dir.glob('*.jpg'))  # Предполагаем, что фото имеют расширение .jpg
        all_files.sort(key=lambda x: x.stat().st_mtime)  # Сортируем по времени изменения

        for target_time in target_times:
            target_time = datetime.strptime(target_time, '%H:%M').time()
            closest_photo = None
            min_diff = timedelta.max

            for file in all_files:
                file_time = datetime.fromtimestamp(file.stat().st_mtime).time()
                time_diff = abs(datetime.combine(datetime.today(), file_time) - datetime.combine(datetime.today(), target_time))
                
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_photo = file
            
            if closest_photo:
                photos.append(closest_photo)

        return photos

