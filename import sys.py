import sys
import os
import random
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDateTimeEdit,
    QListWidget,
    QLineEdit,
    QComboBox,
    QColorDialog,
    QFormLayout,
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import QDateTime, Qt, QPoint, QRect, QSize

class ImageModel:
    def __init__(self):
        self.api_key = "43400770-a11bc88630ec55e2abaff07e7"
        self.base_url = "https://pixabay.com/api/"
        self.image_folder = "resimler/"
        os.makedirs(self.image_folder, exist_ok=True)
        self.previous_birthday = None
        self.previous_images = None
        self.saved_images = []

    def get_pixabay_images(self, query):
        params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "per_page": 200,
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        if data["totalHits"] > 0:
            images = data["hits"]
            return images
        else:
            return None


class ImageController:
    def __init__(self, model):
        self.model = model

    def get_random_images(self):
        flower_images = self.model.get_pixabay_images("flower")
        tree_images = self.model.get_pixabay_images("tree")
        return random.choice(flower_images), random.choice(tree_images)


class FlowerTreeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doğum Günü Çiçek ve Ağaç Gösterici")
        self.setGeometry(200, 200, 1200, 800)

        self.model = ImageModel()
        self.controller = ImageController(self.model)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.flower_label = QLabel(alignment=Qt.AlignCenter)
        self.tree_label = QLabel(alignment=Qt.AlignCenter)
        self.load_button = QPushButton("Resimleri Göster")
        self.load_button.clicked.connect(self.show_images)
        self.save_button = QPushButton("Resimleri Kaydet")
        self.save_button.clicked.connect(self.save_images)
        self.date_edit = QDateTimeEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.saved_images_list = QListWidget()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Resimleri Kaydedilecek Klasör Seçin")
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("Dosya Adı ve Uzantı Girin (Örn: myimage.jpg)")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Küçük", "Orta", "Büyük"])
        self.frame_combo = QComboBox()
        self.frame_combo.addItems(["Çerçeve Yok", "Basit Çerçeve", "Kalın Çerçeve"])
        self.bg_color_button = QPushButton("Arkaplan Rengi Seç")
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Resmin Üzerine Yazı Girin")
        self.text_color_button = QPushButton("Yazı Rengi Seç")
        self.draw_button = QPushButton("Resme Çizim Yap")

    def create_layout(self):
        vbox = QVBoxLayout()
        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.date_edit)
        hbox_top.addWidget(self.load_button)
        hbox_top.addWidget(self.save_button)

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addWidget(self.file_path_edit)
        hbox_bottom.addWidget(self.filename_edit)

        form_layout = QFormLayout()
        form_layout.addRow("Resim Boyutu:", self.size_combo)
        form_layout.addRow("Çerçeve Tipi:", self.frame_combo)
        form_layout.addRow(self.bg_color_button)
        form_layout.addRow("Resim Üzerine Yazı:", self.text_edit)
        form_layout.addRow(self.text_color_button)
        form_layout.addRow(self.draw_button)

        vbox.addWidget(self.flower_label)
        vbox.addWidget(self.tree_label)
        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_bottom)
        vbox.addWidget(self.saved_images_list)
        vbox.addLayout(form_layout)

        self.setLayout(vbox)

    def show_images(self):
        selected_date = self.date_edit.date()
        birthday = selected_date.toPyDate()

        if birthday == self.model.previous_birthday and self.model.previous_images:
            flower_image, tree_image = self.model.previous_images
        else:
            flower_image, tree_image = self.controller.get_random_images()
            self.model.previous_birthday = birthday
            self.model.previous_images = (flower_image, tree_image)

        flower_url = flower_image["largeImageURL"]
        tree_url = tree_image["largeImageURL"]

        self.download_and_display_images(flower_url, tree_url)

    def download_and_display_images(self, flower_url, tree_url):
        flower_filename = self.model.image_folder + "flower.jpg"
        tree_filename = self.model.image_folder + "tree.jpg"

        flower_data = requests.get(flower_url).content
        tree_data = requests.get(tree_url).content

        with open(flower_filename, 'wb') as file:
            file.write(flower_data)
        with open(tree_filename, 'wb') as file:
            file.write(tree_data)

        size_option = self.size_combo.currentText()
        frame_option = self.frame_combo.currentText()

        flower_pixmap = self.apply_image_modifications(flower_filename, size_option, frame_option)
        tree_pixmap = self.apply_image_modifications(tree_filename, size_option, frame_option)

        self.flower_label.setPixmap(flower_pixmap.scaledToWidth(600))
        self.tree_label.setPixmap(tree_pixmap.scaledToWidth(600))

    def apply_image_modifications(self, image_path, size_option, frame_option):
        pixmap = QPixmap(image_path)
        target_size = QSize(600, 400)  # Hedef boyut: 600x400

        if size_option == "Küçük":
            target_size = QSize(300, 200)
        elif size_option == "Orta":
            target_size = QSize(500, 300)

        pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio)
        painter = QPainter(pixmap)

        if frame_option != "Çerçeve Yok":
            pen_width = 2 if frame_option == "Basit Çerçeve" else 6
            pen_color = Qt.black  # Çerçeve rengi siyah olarak ayarlandı, değiştirebilirsiniz
            painter.setPen(QPen(pen_color, pen_width))

            frame_rect = QRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
            painter.drawRect(frame_rect)

        bg_color = self.bg_color_button.palette().window().color()  # Arka plan rengi alındı
        painter.fillRect(pixmap.rect(), bg_color)

        text = self.text_edit.text()
        if text:
            text_color = self.text_color_button.palette().windowText().color()
            font = QFont("Arial", 20)
            painter.setFont(font)
            painter.setPen(QColor(text_color))
            painter.drawText(QPoint(10, pixmap.height() - 10), text)

        painter.end()
        return pixmap

    def save_images(self):
        selected_date = self.date_edit.date()
        birthday = selected_date.toPyDate()
        if birthday == self.model.previous_birthday and self.model.previous_images:
            flower_image, tree_image = self.model.previous_images
            self.model.saved_images.append((flower_image, tree_image))
            self.update_saved_images_list()

    def update_saved_images_list(self):
        self.saved_images_list.clear()
        for flower_image, tree_image in self.model.saved_images:
            self.saved_images_list.addItem(f"Flower: {flower_image['largeImageURL']}, Tree: {tree_image['largeImageURL']}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlowerTreeGUI()
    window.show()
    sys.exit(app.exec_())
