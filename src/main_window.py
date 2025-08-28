import base64
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QTextEdit, QPushButton, QLabel, QMessageBox, QApplication, QStackedWidget, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from gemini_client import GeminiClient

class ResizablePixmapLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1, 1)
        self._pixmap = QPixmap()
        self.setScaledContents(False)

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self):
        if self._pixmap.isNull():
            return
        scaled_pixmap = self._pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        super().setPixmap(scaled_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Explica Simple")
        self.setGeometry(100, 100, 800, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Escribe aquí tu pregunta...")
        self.input_text.setFixedHeight(100)
        
        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generar Explicación")
        self.clear_button = QPushButton("Limpiar")
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.clear_button)
        
        main_layout.addWidget(self.input_text)
        main_layout.addLayout(buttons_layout)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("< Anterior")
        self.slide_counter_label = QLabel("0 / 0")
        self.next_button = QPushButton("Siguiente >")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.slide_counter_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        main_layout.addLayout(nav_layout)

        self.generate_button.clicked.connect(self.generate_explanation)
        self.clear_button.clicked.connect(self._clear_slides)
        self.prev_button.clicked.connect(self._go_to_previous_slide)
        self.next_button.clicked.connect(self._go_to_next_slide)

        self.autoplay_timer = QTimer(self)
        self.autoplay_timer.setInterval(5000)
        self.autoplay_timer.timeout.connect(self._autoplay_next_slide)

        try:
            self.gemini_client = GeminiClient()
        except ValueError as e:
            self.show_error_and_disable(str(e))
        
        self._update_nav_buttons()

    def _clear_slides(self):
        self.autoplay_timer.stop()
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        self._update_nav_buttons()

    def _add_slide(self, image_data, caption_text):
        if not image_data and not caption_text:
            return

        if self.stacked_widget.count() == 1 and self.stacked_widget.widget(0).objectName() == "loading_label":
            self._clear_slides()

        slide_frame = QFrame()
        slide_frame.setFrameShape(QFrame.Shape.StyledPanel)
        slide_layout = QGridLayout(slide_frame)
        slide_layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(1)

        image_label = ResizablePixmapLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if image_data:
            try:
                image_bytes = image_data['data']
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                if not pixmap.isNull():
                    image_label.setPixmap(pixmap)
                    image_label.setMinimumWidth(self.width() - 40)
                    image_label.setMaximumWidth(self.width() - 40)
                    image_label.setMinimumHeight(400)
            except Exception as e:
                image_label.setText(f"No se pudo cargar la imagen: {e}")

        caption_label = QLabel(caption_text)
        caption_label.setObjectName("caption")
        caption_label.setWordWrap(True)
        caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption_label.setMinimumWidth(self.width() - 40)
        caption_label.setMaximumWidth(self.width() - 40)
        
        container_layout.addWidget(image_label)
        container_layout.addWidget(caption_label)

        font_size = (self.width() - 40) // 30
        container.setStyleSheet(f'''
            QLabel#caption {{
                background-color: #f5f5f5;
                color: #0f0f0f;
                padding: 15px;
                border-radius: 5px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
        ''')

        slide_layout.addWidget(container, 0, 0)
        self.stacked_widget.addWidget(slide_frame)

    def _autoplay_next_slide(self):
        current_index = self.stacked_widget.currentIndex()
        count = self.stacked_widget.count()
        if current_index < count - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)
            self._update_nav_buttons()
        else:
            self.autoplay_timer.stop()

    def _go_to_next_slide(self):
        self.autoplay_timer.stop()
        new_index = self.stacked_widget.currentIndex() + 1
        if new_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(new_index)
            self._update_nav_buttons()

    def _go_to_previous_slide(self):
        self.autoplay_timer.stop()
        new_index = self.stacked_widget.currentIndex() - 1
        if new_index >= 0:
            self.stacked_widget.setCurrentIndex(new_index)
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        count = self.stacked_widget.count()
        current_index = self.stacked_widget.currentIndex()
        
        if count == 0 or (count == 1 and self.stacked_widget.widget(0).objectName() == "loading_label"):
            self.slide_counter_label.setText("0 / 0")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            self.slide_counter_label.setText(f"{current_index + 1} / {count}")
            self.prev_button.setEnabled(current_index > 0)
            self.next_button.setEnabled(current_index < count - 1)

    def generate_explanation(self):
        user_prompt = self.input_text.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Entrada vacía", "Por favor, escribe una pregunta.")
            return

        self.generate_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self._clear_slides()
        
        loading_label = QLabel("Generando explicación y diapositivas...")
        loading_label.setObjectName("loading_label")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(loading_label)
        self._update_nav_buttons()
        QApplication.processEvents()
        
        try:
            self.gemini_client.start_new_chat()
            
            first_slide_added = False
            current_text = ""
            for part in self.gemini_client.generate_story_in_chat(user_prompt):
                if part.get("error"):
                    self.show_error_and_disable(part["error"])
                    return
                
                if part.get("text"):
                    current_text += part["text"]
            
                if part.get("inline_data"):
                    self._add_slide(part.get("inline_data"), current_text)
                    current_text = ""
                    if not first_slide_added:
                        self.autoplay_timer.start()
                        first_slide_added = True
                
                self._update_nav_buttons()
                QApplication.processEvents()

            if current_text:
                self._add_slide(None, current_text)
                if not first_slide_added:
                    self.autoplay_timer.start()
                    first_slide_added = True

        except Exception as e:
            self.show_error_and_disable(f"Error durante la generación: {e}")
        finally:
            self.generate_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self._update_nav_buttons()

    def show_error_and_disable(self, message):
        self.autoplay_timer.stop()
        QMessageBox.critical(self, "Error", message)
        self._clear_slides()
        if hasattr(self, 'generate_button'):
            self.generate_button.setEnabled(False)
        if hasattr(self, 'input_text'):
            self.input_text.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_slides_size()

    def _update_slides_size(self):
        font_size = (self.width() - 40) // 30
        
        for i in range(self.stacked_widget.count()):
            slide_frame = self.stacked_widget.widget(i)
            if slide_frame and slide_frame.objectName() != "loading_label":
                container = slide_frame.layout().itemAt(0).widget()
                if container:
                    container.setStyleSheet(f'''
                        QLabel#caption {{
                            background-color: #f5f5f5;
                            color: #0f0f0f;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: {font_size}px;
                            font-weight: bold;
                        }}
                    ''')
                    
                    for j in range(container.layout().count()):
                        widget = container.layout().itemAt(j).widget()
                        if isinstance(widget, (ResizablePixmapLabel, QLabel)):
                            widget.setMinimumWidth(self.width() - 40)
                            widget.setMaximumWidth(self.width() - 40)
                            if isinstance(widget, ResizablePixmapLabel):
                                widget.setMinimumHeight(400)
        QApplication.processEvents()

