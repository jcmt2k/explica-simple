import base64
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QTextEdit, QPushButton, QLabel, QMessageBox, QApplication, QScrollArea, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
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
        self.setGeometry(100, 100, 800, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Escribe aquí tu pregunta...")
        self.input_text.setFixedHeight(100)
        
        # Crear un layout horizontal para los botones
        buttons_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generar Explicación")
        self.clear_button = QPushButton("Limpiar")
        
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.clear_button)
        
        main_layout.addWidget(self.input_text)
        main_layout.addLayout(buttons_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        self.slides_container = QWidget()
        self.slides_layout = QVBoxLayout(self.slides_container)
        self.slides_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.slides_container)

        self.generate_button.clicked.connect(self.generate_explanation)
        self.clear_button.clicked.connect(self._clear_slides)  # Conectar el botón limpiar

        try:
            self.gemini_client = GeminiClient()
        except ValueError as e:
            self.show_error_and_disable(str(e))

    def _clear_slides(self):
        # Bloquear el layout mientras se limpia
        self.slides_container.setEnabled(False)
        
        while self.slides_layout.count():
            child = self.slides_layout.takeAt(0)
            if child.widget():
                child.widget().hide()  # Ocultar antes de eliminar
                child.widget().deleteLater()
        
        QApplication.processEvents()
        self.slides_container.setEnabled(True)

    def _add_slide(self, image_data, caption_text):
        """Creates a slide with content and adds it to the layout."""
        if not image_data and not caption_text:
            return

        slide_frame = QFrame()
        slide_frame.setFrameShape(QFrame.Shape.StyledPanel)
        slide_layout = QGridLayout(slide_frame)
        slide_layout.setContentsMargins(10, 10, 10, 10)

        # Contenedor principal con layout vertical
        container = QWidget()
        container_layout = QVBoxLayout(container)  # Cambiado a QVBoxLayout
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(1)  # Espacio entre imagen y texto

        # Configuración de la imagen
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

        # Configuración del texto
        caption_label = QLabel(caption_text)
        caption_label.setObjectName("caption")
        caption_label.setWordWrap(True)
        caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption_label.setMinimumWidth(self.width() - 40)
        caption_label.setMaximumWidth(self.width() - 40)
        
        # Agregar los widgets al layout verticalmente
        container_layout.addWidget(image_label)
        container_layout.addWidget(caption_label)

        # Estilo actualizado para el contenedor y el texto
        font_size = (self.width() - 40) // 30
        container.setStyleSheet(f"""
            QLabel#caption {{
                background-color: #f5f5f5;
                color: #0f0f0f;
                padding: 15px;
                border-radius: 5px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
        """)

        slide_layout.addWidget(container, 0, 0)
        self.slides_layout.addWidget(slide_frame)

    def generate_explanation(self):
        user_prompt = self.input_text.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Entrada vacía", "Por favor, escribe una pregunta.")
            return

        # Deshabilitar el botón antes de limpiar
        self.generate_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        
        # Limpiar y forzar actualización
        self._clear_slides()
        for _ in range(3):  # Forzar múltiples ciclos de eventos
            QApplication.processEvents()
        
        try:
            self.gemini_client.start_new_chat()
            stream_generator = self.gemini_client.generate_story_in_chat(user_prompt)
            
            current_image = None
            current_text = ""

            for part in stream_generator:
                QApplication.processEvents()
                if part.get("error"):
                    self.show_error_and_disable(part["error"])
                    return
                
                if part.get("text"):
                    current_text += part["text"]
                    print("LLegó texto###", part["text"])
            
                if part.get("inline_data"):
                    current_image = part["inline_data"]
                    print("LLegó imagen###")
                    self._add_slide(current_image, current_text)
                    current_text = ""
                    

        except Exception as e:
            self.show_error_and_disable(f"Error durante la generación: {e}")
        finally:
            self.generate_button.setEnabled(True)
            self.clear_button.setEnabled(True)

    def show_error_and_disable(self, message):
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
        """Actualiza el tamaño de todos los slides cuando la ventana cambia de tamaño"""
        font_size = (self.width() - 40) // 30
        
        for i in range(self.slides_layout.count()):
            slide_frame = self.slides_layout.itemAt(i).widget()
            if slide_frame:
                container = slide_frame.layout().itemAt(0).widget()
                if container:
                    container.setStyleSheet(f"""
                        QLabel#caption {{
                            background-color: #f5f5f5;
                            color: #0f0f0f;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: {font_size}px;
                            font-weight: bold;
                        }}
                    """)
                    
                    for j in range(container.layout().count()):
                        widget = container.layout().itemAt(j).widget()
                        if isinstance(widget, (ResizablePixmapLabel, QLabel)):
                            widget.setMinimumWidth(self.width() - 40)
                            widget.setMaximumWidth(self.width() - 40)
                            if isinstance(widget, ResizablePixmapLabel):
                                widget.setMinimumHeight(400)
        QApplication.processEvents()