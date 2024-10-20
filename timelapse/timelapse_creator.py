import logging
from .camera_handler import CameraDirectoryHandler
from .photo_mover import PhotoMover

class TimelapseCreator:
    def __init__(self, camera_dirs, destination_dirs):
        """Инициализация создателя таймлапсов."""
        self.camera_handler = CameraDirectoryHandler(camera_dirs)
        self.photo_mover = PhotoMover(destination_dirs)
    
    def process_day(self, date):
        """Обрабатывает фотографии за конкретный день."""
        photos_by_camera = self.camera_handler.get_photos_for_day(date)
        
        for camera, photos in photos_by_camera.items():
            if photos:
                logging.info(f"Найдено {len(photos)} фото для камеры {camera} за {date}.")
                self.photo_mover.move_photos(photos)
            else:
                logging.info(f"Фото не найдено для камеры {camera} за {date}.")
