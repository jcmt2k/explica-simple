# Explica Simple: Un Caso de Estudio

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg) ![PySide6](https://img.shields.io/badge/PySide6-Qt_for_Python-green.svg) ![Google Gemini](https://img.shields.io/badge/API-Google_Gemini-purple.svg)

**Explica Simple** es una aplicación de escritorio para Linux que transforma conceptos complejos en explicaciones visuales y sencillas. Más que una simple herramienta, este proyecto está **diseñado como un caso de estudio y un recurso de aprendizaje** para desarrolladores interesados en la creación de aplicaciones con Python, la integración de APIs de IA generativa y el diseño de interfaces de usuario.

La aplicación toma una pregunta del usuario y utiliza la API de Google Gemini para generar una historia contada a través de diapositivas, cada una con una ilustración única y un texto explicativo, todo en un encantador estilo de cómic minimalista.

## Stack Tecnológico

*   **Lenguaje:** Python 3.8+
*   **Interfaz Gráfica (GUI):** PySide6 (Qt for Python)
*   **IA Generativa:** Google Gemini API (para texto e imágenes)
*   **Manejo de Dependencias:** Pip y `requirements.txt`
*   **Gestión de Entorno:** `python-dotenv` para claves de API

## Características

*   **Explicaciones Visuales:** Genera una secuencia narrativa de imágenes y texto.
*   **Estilo de Arte Único:** Utiliza un *prompt* diseñado para obtener ilustraciones con un estilo "Manicito", inspirado en caricaturas clásicas.
*   **Interfaz Limpia y Sencilla:** Facilita la interacción del usuario.
*   **Generación de Contenido Dinámico**: Utiliza el modelo multimodal de Google Gemini para generar tanto el texto explicativo como las imágenes relevantes a partir de una simple pregunta.
*   **Interfaz de Usuario Intuitiva**: Construida con PySide6 (Qt for Python), la aplicación ofrece una experiencia de usuario limpia y sencilla.
*   **Visualización en Tiempo Real**: Las diapositivas se muestran en la interfaz a medida que se generan, proporcionando feedback visual inmediato al usuario sin esperar a que el proceso completo termine.
*   **Carrusel de Diapositivas Interactivo**:
    - **Navegación Manual**: Botones para avanzar y retroceder entre las diapositivas.
    - **Reproducción Automática**: Cada diapositiva se muestra durante 5 segundos antes de pasar automáticamente a la siguiente, permitiendo una visualización pasiva.
    - **Contador de Diapositivas**: Indica la posición actual dentro de la presentación (e.g., "3 / 10").
*   **Diseño Responsivo**: Los elementos de la interfaz se ajustan al tamaño de la ventana para una visualización óptima.

## Arquitectura y Tecnologías

El proyecto sigue una arquitectura cliente-servidor desacoplada, donde la aplicación de escritorio actúa como cliente de la API de Google Gemini.

- **Frontend (Interfaz de Usuario)**:
  - **Python 3**: Lenguaje principal de la aplicación.
  - **PySide6**: Framework para la creación de la interfaz gráfica de usuario (GUI).
  - **QTimer**: Utilizado para implementar la funcionalidad de reproducción automática.

- **Backend (Lógica de Negocio y API)**:
  - **Google Gemini API**: Servicio de IA para la generación de contenido multimodal (texto e imágenes).
  - **`google-generativeai`**: Biblioteca cliente oficial de Google para interactuar con la API.
  - **`python-dotenv`**: Para la gestión segura de claves de API a través de variables de entorno.

## Instalación y Uso

### Requisitos Previos

*   Python 3.8 o superior.
*   Una clave de API de Google Gemini. Puedes obtenerla en [Google AI Studio](https://aistudio.google.com/app/apikey).

### Pasos

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/jcmt2k/explica-simple.git
    cd explica-simple
    ```

2.  **Crea y activa un entorno virtual:**
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    
3.  **Instala las dependencias:**
    
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Configura tu API Key:**
    Crea un archivo `.env` en la raíz del proyecto y añade tu clave:
    ```
    GEMINI_API_KEY="TU_API_KEY_AQUI"
    ```

5.  **Ejecuta la aplicación:**
    
    ```bash
    python3 main.py
    ```

## Ejemplo de uso

https://github.com/user-attachments/assets/ed4c3a21-6856-4339-a2b8-bdffa68e51ca

https://github.com/user-attachments/assets/0f6ca8db-9854-4ce3-bf92-effb5130d7f7

## Caso de Estudio para Desarrolladores

Este repositorio es una excelente oportunidad para aprender sobre los siguientes conceptos:

### `gemini_client.py`
*   **Punto de Aprendizaje:** Cómo interactuar con una API de IA multimodal (texto e imagen) y procesar respuestas en *streaming*.
*   **Detalles:**
    *   **Autenticación Segura:** Carga de claves de API desde un archivo `.env` para no exponerlas en el código.
    *   **Prompt Engineering:** Diseño de un *prompt* detallado para guiar a la IA hacia un estilo de respuesta específico.
    *   **Manejo de Generadores:** Uso de `yield` para procesar los datos de la API a medida que llegan, en lugar de esperar a que la respuesta completa esté disponible.

### `main_window.py`
*   **Punto de Aprendizaje:** Construcción de una interfaz gráfica de usuario (GUI) con PySide6 y manejo de eventos.
*   **Detalles:**
    *   **Estructura de la UI:** Uso de layouts (`QVBoxLayout`, `QHBoxLayout`) para organizar los widgets de forma robusta.
    *   **Widgets Personalizados:** Creación de `ResizablePixmapLabel` para que las imágenes se ajusten dinámicamente al tamaño de la ventana.
    *   **Actualización Asíncrona de la UI:** Conexión de la lógica de la aplicación con la interfaz, asegurando que la ventana no se congele (`QApplication.processEvents()`) mientras se espera la respuesta de la API.
    *   **Estilos con CSS:** Aplicación de estilos a los widgets para una apariencia más pulida.

### `main.py`
*   **Punto de Aprendizaje:** Principio de Responsabilidad Única.
*   **Detalles:** Este archivo es deliberadamente simple. Su única función es instanciar y lanzar la aplicación, separando el punto de entrada de la lógica de la interfaz.

## Cómo Contribuir

Las contribuciones son bienvenidas. Si tienes ideas para mejorar la aplicación o el código, por favor, sigue estos pasos:

1.  Haz un "Fork" del repositorio.
2.  Crea una nueva rama para tu funcionalidad (`git checkout -b feature/nueva-caracteristica`).
3.  Realiza tus cambios y haz "commit" (`git commit -m 'Añade nueva característica'`).
4.  Haz "push" a tu rama (`git push origin feature/nueva-caracteristica`).
5.  Abre un "Pull Request".

## Licencia

Este proyecto está distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
