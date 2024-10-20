import logging
import shutil
from pathlib import Path

class PhotoMover:
    def __init__(self, destination_dirs):
        """Инициализация класса для перемещения фото."""
        self.destination_dirs = [Path(d) for d in destination_dirs]
    
    def move_photos(self, photos):
        """Перемещает фото в доступные директории назначения."""
        for dest_dir in self.destination_dirs:
            if not dest_dir.exists():
                logging.warning(f"Директория назначения {dest_dir} недоступна. Пропуск.")
                continue

            for photo in photos:
                try:
                    dest_path = dest_dir / photo.name
                    shutil.copy2(photo, dest_path)
                    logging.info(f"Фото {photo.name} успешно перемещено в {dest_path}")
                except Exception as e:
                    logging.error(f"Ошибка при перемещении {photo.name}: {e}")
