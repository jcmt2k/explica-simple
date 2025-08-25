import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Cargar variables de entorno desde un archivo .env
load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash-preview-image-generation'
        self.chat = None

    def start_new_chat(self):
        self.chat = self.client.chats.create(model=self.model, history=[])

    def generate_story_in_chat(self, user_prompt: str):
        """
        The stable generator: combines robust parsing with the user's fix.
        """
        if not self.chat:
            raise RuntimeError("Sesión de Chat no iniciada. Primero llama a start_new_chat().")

        additional_instructions = '''
Usa una historia divertida, al estilo de los comics sin burbujas de texto, como metáfora.
Manten las sentencias cortas pero conversacionales, casuales, y entretenidas.

Genera una ilustración al estilo de ilustración de Manicito, minimalista y muy tierno para cada sentencia. Que la ilustración refleje el contenido de la sentencia. El lienzo es de 10x15 cm. horizontal.

Características clave del estilo de Manicito:
*Simplicidad y sobriedad:*
Los dibujos son despojados de detalles innecesarios, con un estilo casi minimalista. 
*Rasgos exagerados:*
Los personajes, como Charlie Brown o Snoopy, tienen características físicas simplificadas pero muy expresivas, que ayudan a transmitir sus emociones y personalidades de manera inmediata. 
*Líneas limpias:*
El uso de líneas de contorno bien definidas crea un aspecto claro y distintivo en los personajes y el entorno. 
*Diseño estilizado:*
A pesar de la sencillez, hay un cuidadoso diseño en las formas y proporciones, lo que lo hace fácilmente reconocible. Tiene un aire nostálgico que evoca una sensación de calidez y familiaridad. El aspecto es muy profesional y pulido, con una atención meticulosa a la composición y el equilibrio visual.
*Influencia del cartoon:*
El estilo se inspira en las caricaturas y los bocetos de personajes que resaltan rasgos específicos para una rápida identificación. También se observa una fuerte influencia del estilo Peanuts, con personajes que tienen cabezas grandes y cuerpos pequeños, lo que añade un toque de ternura y humor visual. Los fondos son simples, a menudo con pocos detalles, para mantener el enfoque en los personajes y sus interacciones. Los colores son suaves y limitados, evitando saturación para mantener la atmósfera tranquila y amigable. Las expresiones faciales y posturas corporales son clave para comunicar emociones y acciones de manera efectiva. Es un estilo que combina simplicidad con una gran capacidad para contar historias visuales de manera efectiva.
IMPORTANTE: 
    Nunca incluyas texto dentro de las imágenes.
    El texto que generes no debe describir la imagen.
    El texto que generes no debe estar numerado o con títulos.

Comienza tu explicación sin ningún comentario extra.
Sigue hasta que termines.'''

        full_prompt = user_prompt + additional_instructions
        config=types.GenerateContentConfig(
        #    system_instruction=additional_instructions,
            response_modalities=["TEXT", "IMAGE"],
            max_output_tokens=2000,
            #temperature=0.3,
            #top_p=0.8,
            #top_k=40,
        )
        try:
            #response_stream = self.chat.send_message_stream(
                #full_prompt, config={"response_modalities": ["TEXT", "IMAGE"]}
            response_stream = self.chat.send_message_stream(
                full_prompt, config=config
            )
            
            for chunk in response_stream:
                # This guard is the key to preventing the crash at the end of the stream.
                if chunk is None:
                    continue
                
                if not hasattr(chunk, 'candidates') or not chunk.candidates:
                    continue
                
                for candidate in chunk.candidates:
                    if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or candidate.content.parts is None:
                        continue

                    for part in candidate.content.parts:
                        part_dict = {}
                        if hasattr(part, 'text') and part.text:
                            part_dict['text'] = part.text
                        
                        if hasattr(part, 'inline_data') and part.inline_data:
                            part_dict['inline_data'] = {
                                'data': part.inline_data.data,
                                'mime_type': part.inline_data.mime_type
                            }
                        
                        if part_dict:
                            yield part_dict

        except Exception as e:
            print(f"Error al generar contenido: {e}")
            yield {"error": f"Lo siento, ha ocurrido un error al contactar a la IA. Detalles: {e}"}
 