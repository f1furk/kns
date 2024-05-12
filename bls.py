import sys
import os
import requests
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QDateTimeEdit, QListWidget, QLineEdit, QFileDialog, QMessageBox, QListWidgetItem, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDateTime, Qt, QThread, pyqtSignal

class ImageModel:
    def __init__(self):
        self.api_key = "43401466-0b78c68fbc80d26c3cfd23694"
        self.base_url = "https://pixabay.com/api/"
        self.image_folder = "resimler/"
        os.makedirs(self.image_folder, exist_ok=True)
        self.previous_images = {"flower": [], "tree": []}

    def get_pixabay_images(self, query):
        params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "per_page": 200
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("totalHits", 0) > 0:
                images = data["hits"]
                return images
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Hata: {e}")
            return None

class ImageController:
    def __init__(self, model):
        self.model = model

    def get_random_images(self, query):
        images = self.model.get_pixabay_images(query)
        return images

class DownloadThread(QThread):
    image_downloaded = pyqtSignal(QPixmap, QPixmap)

    def __init__(self, flower_url, tree_url):
        super().__init__()
        self.flower_url = flower_url
        self.tree_url = tree_url
        self.stopped = False

    def run(self):
        flower_data = requests.get(self.flower_url).content
        tree_data = requests.get(self.tree_url).content

        flower_pixmap = QPixmap()
        tree_pixmap = QPixmap()

        if flower_data:
            flower_pixmap.loadFromData(flower_data)
        if tree_data:
            tree_pixmap.loadFromData(tree_data)

        if not self.stopped:
            self.image_downloaded.emit(flower_pixmap, tree_pixmap)

    def stop(self):
        self.stopped = True
        self.quit()

class FlowerTreeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doğum Günü Çiçek ve Ağaç Gösterici")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.model = ImageModel()
        self.controller = ImageController(self.model)
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.flower_label = QLabel(alignment=Qt.AlignCenter)
        self.flower_label.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 10px;")
        
        self.tree_label = QLabel(alignment=Qt.AlignCenter)
        self.tree_label.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 10px;")
        
        self.load_button = QPushButton("Resimleri Göster")
        self.load_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px; font-size: 16px;")
        self.load_button.clicked.connect(self.show_images)
        
        self.save_button = QPushButton("Resimleri Kaydet")
        self.save_button.setStyleSheet("background-color: #008CBA; color: white; border: none; padding: 10px; font-size: 16px;")
        self.save_button.clicked.connect(self.save_images)
        
        self.date_edit = QDateTimeEdit()
        self.date_edit.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 5px;")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        
        self.saved_images_list = QListWidget()
        self.saved_images_list.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 10px;")
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 5px;")
        self.file_path_edit.setPlaceholderText("Resimleri Kaydedilecek Klasör Seçin")
        
        self.filename_edit = QLineEdit()
        self.filename_edit.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 5px;")
        self.filename_edit.setPlaceholderText("Dosya Adı ve Uzantı Girin (Örn: myimage.jpg)")
        
        self.open_folder_button = QPushButton("Klasörü Aç")
        self.open_folder_button.setStyleSheet("background-color: #008CBA; color: white; border: none; padding: 10px; font-size: 16px;")
        self.open_folder_button.clicked.connect(self.open_image_folder)
        
        self.delete_button = QPushButton("Seçili Kaydı Sil")
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 10px; font-size: 16px;")
        self.delete_button.clicked.connect(self.delete_selected_image)
        
        self.browse_button = QPushButton("Klasör Seç")
        self.browse_button.setStyleSheet("background-color: #008CBA; color: white; border: none; padding: 10px; font-size: 16px;")
        self.browse_button.clicked.connect(self.browse_folder)
        
        self.preview_button = QPushButton("Önizle")
        self.preview_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px; font-size: 16px;")
        self.preview_button.clicked.connect(self.preview_selected_image)
        
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc; padding: 5px;")
        self.language_combo.addItems(["Türkçe", "English", "Español"])

        self.download_status_label = QLabel(alignment=Qt.AlignCenter)
        self.download_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        self.download_status_label.setText("")

    def create_layout(self):
        vbox = QVBoxLayout()
        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.date_edit)
        hbox_top.addWidget(self.load_button)
        hbox_top.addWidget(self.save_button)

        hbox_mid = QHBoxLayout()
        hbox_mid.addWidget(self.file_path_edit)
        hbox_mid.addWidget(self.browse_button)
        hbox_mid.addWidget(self.filename_edit)
        hbox_mid.addWidget(self.open_folder_button)

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addWidget(self.delete_button)
        hbox_bottom.addWidget(self.preview_button)
        hbox_bottom.addWidget(self.language_combo)

        vbox.addWidget(self.download_status_label)
        vbox.addWidget(self.flower_label)
        vbox.addWidget(self.tree_label)
        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_mid)
        vbox.addWidget(self.saved_images_list)
        vbox.addLayout(hbox_bottom)

        self.setLayout(vbox)

    def show_images(self):
        selected_date = self.date_edit.date()
        birthday = selected_date.toPyDate()

        if birthday in self.model.previous_images:
            flower_image, tree_image = self.model.previous_images[birthday]
        else:
            flower_images = self.controller.get_random_images("flower")
            tree_images = self.controller.get_random_images("tree")
            if flower_images and tree_images:
                flower_image = random.choice(flower_images)
                tree_image = random.choice(tree_images)
                self.model.previous_images[birthday] = (flower_image, tree_image)
            else:
                QMessageBox.critical(self, "Hata", "Resimler yüklenemedi!")
                return

        flower_url = flower_image["largeImageURL"]
        tree_url = tree_image["largeImageURL"]

        self.download_images_async(flower_url, tree_url)

    def download_images_async(self, flower_url, tree_url):
        if hasattr(self, "thread") and isinstance(self.thread, DownloadThread):
            self.thread.stop()
            self.thread.wait()

        self.thread = DownloadThread(flower_url, tree_url)
        self.thread.image_downloaded.connect(self.display_images)
        self.thread.start()
        self.download_status_label.setText("Resimler indiriliyor...")

    def display_images(self, flower_pixmap, tree_pixmap):
        flower_pixmap = flower_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.flower_label.setPixmap(flower_pixmap)

        tree_pixmap = tree_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.tree_label.setPixmap(tree_pixmap)

        self.download_status_label.setText("Resimler indirildi.")

    def save_images(self):
        selected_date = self.date_edit.date()
        birthday = selected_date.toPyDate()

        if birthday in self.model.previous_images:
            QMessageBox.warning(self, "Uyarı", "Bu tarihe ait resimler zaten kaydedildi.")
            return

        flower_image, tree_image = self.model.previous_images.get(birthday, (None, None))

        if flower_image and tree_image:
            self.model.previous_images[birthday] = (flower_image, tree_image)
            self.update_saved_images_list()

    def update_saved_images_list(self):
        self.saved_images_list.clear()
        for birthday, (flower_image, tree_image) in self.model.previous_images.items():
            item = QListWidgetItem(f"{birthday}: Flower - {flower_image['largeImageURL']}, Tree - {tree_image['largeImageURL']}")
            item.setData(Qt.UserRole, (flower_image['largeImageURL'], tree_image['largeImageURL']))
            self.saved_images_list.addItem(item)

    def open_image_folder(self):
        folder_path = self.file_path_edit.text()
        if os.path.isdir(folder_path):
            os.startfile(folder_path)
        else:
            QMessageBox.warning(self, "Uyarı", "Geçersiz klasör yolu!")

    def delete_selected_image(self):
        selected_item = self.saved_images_list.currentItem()
        if selected_item:
            index = self.saved_images_list.row(selected_item)
            self.saved_images_list.takeItem(index)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder_path:
            self.file_path_edit.setText(folder_path)

    def preview_selected_image(self):
        selected_item = self.saved_images_list.currentItem()
        if selected_item:
            urls = selected_item.data(Qt.UserRole)
            if urls:
                flower_url, tree_url = urls
                flower_pixmap = QPixmap(flower_url)
                tree_pixmap = QPixmap(tree_url)
                self.display_images(flower_pixmap, tree_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlowerTreeGUI()
    window.show()
    sys.exit(app.exec_())
