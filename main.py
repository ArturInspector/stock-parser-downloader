import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QSpinBox, QFileDialog, QProgressBar,
                            QMessageBox, QFrame, QTextEdit, QListWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient, QGradient
from pathlib import Path
import requests
from dotenv import load_dotenv, set_key
import os
import random
import google.generativeai as genai
#Создано при помощи Claude 3.5 sonnet.

class DownloadWorker(QThread):
    """Отдельный поток для загрузки"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, downloader, service, query, count, api_key, save_path):
        super().__init__()
        self.downloader = downloader
        self.service = service
        self.query = query
        self.count = count
        self.api_key = api_key
        self.save_path = save_path

    def run(self):
        try:
            if self.service == "Pexels":
                downloaded = self.downloader.download_pexels_videos(
                    self.query, self.count, self.api_key, self.save_path)
            elif self.service == "Pixabay":
                downloaded = self.downloader.download_pixabay_videos(
                    self.query, self.count, self.save_path)
            else:  # Both
                count_each = self.count // 2
                downloaded = 0
                downloaded += self.downloader.download_pexels_videos(
                    self.query, count_each, self.api_key, self.save_path)
                downloaded += self.downloader.download_pixabay_videos(
                    self.query, count_each, self.save_path)
            
            self.finished.emit(downloaded)
        except Exception as e:
            self.error.emit(str(e))

class VideoDownloader:
    """Класс для загрузки видео"""
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def download_pexels_videos(self, query, count, api_key, save_path):
        if self.progress_callback:
            self.progress_callback("Поиск видео на Pexels...")
            
        headers = {
            'Authorization': api_key
        }
        url = f'https://api.pexels.com/videos/search?query={query}&per_page={count}'
        
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            raise Exception("Превышен лимит запросов к Pexels API")
            
        data = response.json()
        videos = data.get('videos', [])
        
        if not videos:
            raise Exception("Видео не найдены на Pexels")
            
        downloaded = 0
        save_path = Path(save_path) / query
        save_path.mkdir(parents=True, exist_ok=True)
        
        for i, video in enumerate(videos[:count], 1):
            if self.progress_callback:
                self.progress_callback(f"Загрузка видео {i} из {count} (Pexels)")
                
            video_files = video.get('video_files', [])
            if not video_files:
                continue
                
            # Сортируем по качеству
            video_files.sort(key=lambda x: x.get('height', 0), reverse=True)
            video_url = video_files[0]['link']
            
            try:
                response = requests.get(video_url, stream=True, timeout=30)
                if response.status_code == 200:
                    file_path = save_path / f"px_video_{i}.mp4"
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    downloaded += 1
            except Exception as e:
                print(f"Ошибка при загрузке видео {i}: {str(e)}")
                
        return downloaded

    def download_pixabay_videos(self, query, count, save_path):
        if self.progress_callback:
            self.progress_callback("Поиск видео на Pixabay...")
            
        api_key = "26679812-b3df3c0530bd761873ce03ab3"
        base_url = "https://pixabay.com/api/videos/"
        
        # Улучшаем параметры запроса
        params = {
            'key': api_key,
            'q': query,
            'per_page': count * 2,  # Запрашиваем больше видео для лучшей выборки
            'lang': 'en',
            'order': 'latest',  # Сортировка по новизне
            'min_width': 1280,  # Минимальная ширина для качества
            'min_height': 720,  # Минимальная высота для качества
            'safesearch': 'true',  # Безопасный контент
            'page': 1  # Можно менять страницу для получения разных результатов
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('hits'):
                # Пробуем другую страницу, если нет результатов
                params['page'] = 2
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('hits'):
                    raise Exception("Видео не найдены на Pixabay")
            
            # Перемешиваем результаты для разнообразия
            hits = data.get('hits', [])
            random.shuffle(hits)
            
            downloaded = 0
            save_path = Path(save_path) / query
            save_path.mkdir(parents=True, exist_ok=True)
            
            for i, video in enumerate(hits[:count], 1):
                if self.progress_callback:
                    self.progress_callback(f"Загрузка видео {i} из {count} (Pixabay)")
                
                # Получаем ссылку на видео лучшего качества
                video_url = None
                for quality in ['large', 'medium', 'small']:
                    if video.get('videos', {}).get(quality, {}).get('url'):
                        video_url = video['videos'][quality]['url']
                        break
                
                if not video_url:
                    continue
                
                try:
                    response = requests.get(video_url, stream=True, timeout=30)
                    if response.status_code == 200:
                        file_path = save_path / f"pb_video_{i}.mp4"
                        total_size = int(response.headers.get('content-length', 0))
                        
                        # Пропускаем, если файл больше 100MB
                        if total_size > 100 * 1024 * 1024:
                            continue
                        
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        downloaded += 1
                except Exception as e:
                    print(f"Ошибка при загрузке видео {i}: {str(e)}")
                    continue
            
            return downloaded
            
        except Exception as e:
            print(f"Ошибка Pixabay: {str(e)}")
            raise Exception(f"Ошибка при загрузке с Pixabay: {str(e)}")

class StockVideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Stock Video Downloader')
        self.setMinimumSize(800, 600)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel('Stock Video Downloader')
        title.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # API ключи
        api_frame = QFrame()
        api_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        api_layout = QVBoxLayout(api_frame)
        
        # Pexels API
        pexels_layout = QHBoxLayout()
        pexels_label = QLabel('Pexels API Key:')
        self.pexels_key = QLineEdit()
        self.pexels_key.setPlaceholderText('Введите ваш Pexels API ключ')
        save_pexels = QPushButton('Сохранить')
        save_pexels.clicked.connect(lambda: self.save_api_key('pexels'))
        
        pexels_layout.addWidget(pexels_label)
        pexels_layout.addWidget(self.pexels_key)
        pexels_layout.addWidget(save_pexels)
        api_layout.addLayout(pexels_layout)
        
        # Добавляем Pixabay API
        pixabay_layout = QHBoxLayout()
        pixabay_label = QLabel('Pixabay API Key:')
        self.pixabay_key = QLineEdit()
        self.pixabay_key.setPlaceholderText('Введите ваш Pixabay API ключ')
        save_pixabay = QPushButton('Сохранить')
        save_pixabay.clicked.connect(lambda: self.save_api_key('pixabay'))
        
        pixabay_layout.addWidget(pixabay_label)
        pixabay_layout.addWidget(self.pixabay_key)
        pixabay_layout.addWidget(save_pixabay)
        api_layout.addLayout(pixabay_layout)
        
        # Добавляем Gemini API
        gemini_layout = QHBoxLayout()
        gemini_label = QLabel('Gemini API Key:')
        self.gemini_key = QLineEdit()
        self.gemini_key.setPlaceholderText('Введите ваш Gemini API ключ')
        save_gemini = QPushButton('Сохранить')
        save_gemini.clicked.connect(lambda: self.save_api_key('gemini'))
        
        gemini_layout.addWidget(gemini_label)
        gemini_layout.addWidget(self.gemini_key)
        gemini_layout.addWidget(save_gemini)
        api_layout.addLayout(gemini_layout)
        
        layout.addWidget(api_frame)
        
        # Параметры поиска
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        search_layout = QVBoxLayout(search_frame)
        
        # Сервис
        service_layout = QHBoxLayout()
        service_label = QLabel('Сервис:')
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Pexels', 'Pixabay', 'Оба сервиса'])
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_combo)
        search_layout.addLayout(service_layout)
        
        # Поисковый запрос
        query_layout = QHBoxLayout()
        query_label = QLabel('Поисковый запрос:')
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText('Введите тему для поиска')
        query_layout.addWidget(query_label)
        query_layout.addWidget(self.query_input)
        search_layout.addLayout(query_layout)
        
        # Количество видео
        count_layout = QHBoxLayout()
        count_label = QLabel('Количество видео:')
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spin)
        search_layout.addLayout(count_layout)
        
        layout.addWidget(search_frame)
        
        # Добавляем секцию для сценария/описания
        scenario_frame = QFrame()
        scenario_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #2b2b2b, stop:1 #353535);
                border: none;
                border-radius: 10px;
            }
        """)
        scenario_layout = QVBoxLayout(scenario_frame)
        
        scenario_label = QLabel('Сценарий/Описание:')
        scenario_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.scenario_input = QTextEdit()
        self.scenario_input.setPlaceholderText('Опишите ваш сценарий или идею...')
        self.scenario_input.setMinimumHeight(100)
        self.scenario_input.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                color: white;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #2a82da;
            }
        """)
        
        generate_btn = QPushButton('🤖 Сгенерировать промпты')
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        generate_btn.clicked.connect(self.generate_prompts)
        
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(self.scenario_input)
        scenario_layout.addWidget(generate_btn)
        
        # Список сгенерированных промптов
        prompts_frame = QFrame()
        prompts_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #353535, stop:1 #2b2b2b);
                border: none;
                border-radius: 10px;
            }
        """)
        prompts_layout = QVBoxLayout(prompts_frame)
        
        prompts_label = QLabel('Сгенерированные промпты:')
        prompts_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.prompts_list = QListWidget()
        self.prompts_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        self.prompts_list.itemDoubleClicked.connect(self.use_prompt)
        
        prompts_layout.addWidget(prompts_label)
        prompts_layout.addWidget(self.prompts_list)
        
        # Добавляем новые фреймы в основной layout
        layout.insertWidget(1, scenario_frame)  # После заголовка
        layout.insertWidget(2, prompts_frame)   # После сценария
        
        # Путь сохранения
        path_frame = QFrame()
        path_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        path_layout = QHBoxLayout(path_frame)
        
        path_label = QLabel('Путь сохранения:')
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Downloads" / "stock_videos"))
        browse_btn = QPushButton('Обзор')
        browse_btn.clicked.connect(self.browse_path)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        
        layout.addWidget(path_frame)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)
        
        # Кнопка загрузки
        self.download_btn = QPushButton('Скачать видео')
        self.download_btn.setMinimumHeight(50)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)
        
        # Загружаем API ключи
        self.load_api_keys()
        
        # Применяем темную тему
        self.apply_dark_theme()

    def apply_dark_theme(self):
        """Применяем темную тему вручную"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        self.setPalette(palette)
        
        # Стили для разных элементов
        style_sheet = """
        QFrame {
            background-color: #2b2b2b;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #3a3a3a;
            border: none;
            color: white;
            padding: 5px 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #454545;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
        QLineEdit {
            background-color: #1e1e1e;
            border: 1px solid #3a3a3a;
            color: white;
            padding: 5px;
            border-radius: 4px;
        }
        QComboBox {
            background-color: #1e1e1e;
            border: 1px solid #3a3a3a;
            color: white;
            padding: 5px;
            border-radius: 4px;
        }
        QSpinBox {
            background-color: #1e1e1e;
            border: 1px solid #3a3a3a;
            color: white;
            padding: 5px;
            border-radius: 4px;
        }
        QProgressBar {
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #2a82da;
        }
        """
        self.setStyleSheet(style_sheet)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if path:
            self.path_input.setText(path)

    def save_api_key(self, service):
        if service == 'pexels':
            key = self.pexels_key.text()
            if key:
                set_key('api.env', 'PEXELS_API_KEY', key)
                QMessageBox.information(self, 'Успех', 'Pexels API ключ сохранен')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Введите Pexels API ключ')
        elif service == 'pixabay':
            key = self.pixabay_key.text()
            if key:
                set_key('api.env', 'PIXABAY_API_KEY', key)
                QMessageBox.information(self, 'Успех', 'Pixabay API ключ сохранен')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Введите Pixabay API ключ')
        elif service == 'gemini':
            key = self.gemini_key.text()
            if key:
                set_key('api.env', 'GEMINI_API_KEY', key)
                QMessageBox.information(self, 'Успех', 'Gemini API ключ сохранен')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Введите Gemini API ключ')

    def load_api_keys(self):
        load_dotenv('api.env')
        pexels_key = os.getenv('PEXELS_API_KEY')
        pixabay_key = os.getenv('PIXABAY_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if pexels_key:
            self.pexels_key.setText(pexels_key)
        if pixabay_key:
            self.pixabay_key.setText(pixabay_key)
        if gemini_key:
            self.gemini_key.setText(gemini_key)

    def start_download(self):
        query = self.query_input.text()
        count = self.count_spin.value()
        save_path = self.path_input.text()
        service = self.service_combo.currentText()
        pexels_key = self.pexels_key.text()
        
        if not query:
            QMessageBox.warning(self, 'Ошибка', 'Введите поисковый запрос')
            return
        
        if not pexels_key and service in ['Pexels', 'Оба сервиса']:
            QMessageBox.warning(self, 'Ошибка', 'Введите API ключ для Pexels')
            return
        
        # Создаем и запускаем worker с передачей всех необходимых параметров
        self.download_worker = DownloadWorker(
            VideoDownloader(self.update_progress),
            service,
            query,
            count,
            pexels_key,
            save_path
        )
        
        # Подключаем сигналы
        self.download_worker.progress.connect(self.update_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        
        # Блокируем кнопку на время загрузки
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Запускаем загрузку
        self.download_worker.start()

    def update_progress(self, message):
        self.progress_bar.setFormat(message)

    def download_finished(self, count):
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, 'Успех', f'Загружено {count} видео')

    def download_error(self, error_message):
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, 'Ошибка', f'Ошибка при загрузке: {error_message}')

    def generate_prompts(self):
        """Генерация промптов через Gemini"""
        text = self.scenario_input.toPlainText()
        if not text:
            QMessageBox.warning(self, 'Ошибка', 'Введите сценарий или описание')
            return
            
        gemini_key = self.gemini_key.text()
        if not gemini_key:
            QMessageBox.warning(self, 'Ошибка', 'Введите API ключ для Gemini')
            return
        
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Создай 5 поисковых запросов на английском для поиска стоковых видео по следующему сценарию/описанию:
            {text}
            
            Запросы должны быть:
            1. Конкретными и детальными
            2. Подходящими для поиска стоковых видео
            3. С использованием профессиональных терминов
            4. Без авторских прав
            5. Оригинальными, помогающими пользователю найти стоки для видео.
            
            Формат ответа:
            1. [запрос 1]
            2. [запрос 2]
            и т.д.
            """
            
            response = model.generate_content(prompt)
            prompts = response.text.split('\n')
            
            # Обновляем список промптов
            self.prompts_list.clear()
            for p in prompts:
                if p.strip() and p[0].isdigit():
                    self.prompts_list.addItem(p.strip())
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка генерации промптов: {str(e)}')

    def use_prompt(self, item):
        """Использует выбранный промпт для поиска"""
        prompt_text = item.text().split('. ')[1]  # Убираем номер
        self.query_input.setText(prompt_text)

def main():
    app = QApplication(sys.argv)
    window = StockVideoDownloader()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
