import os
from dotenv import load_dotenv
from google import genai

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
Usa una historia divertida sobre muchos gatitos como metáfora.
Manten las sentencias cortas pero conversacionales, casuales, y entretenidas.
Genera una ilustración únicamente con tinta negra sobre fondo blanco, minimalista muy linda para cada sentencia. Que la ilustración no contenga letras y refleje el contenido de la sentencia. El lienzo es de 10x15 cm. horizontal. 
Comienza tu explicación sin ningún comentario extra.
Sigue hasta que termines.'''

        full_prompt = user_prompt + additional_instructions
        
        try:
            response_stream = self.chat.send_message_stream(
                full_prompt, config={"response_modalities": ["TEXT", "IMAGE"]}
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
 