import logging
import streamlit as st
import openai
import os
import json
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuración de la página
st.set_page_config(page_title="Chatbot Educativo", page_icon="🎨", layout="wide")

# Paleta de colores mejorada
ORANGE = "#FF8C00"
LIGHT_ORANGE = "#FFE9CC"
DARK_ORANGE = "#FF7F50"
BACKGROUND_COLOR = "#F0F2F6"  # Gris claro para un fondo más suave
SIDEBAR_COLOR = "#FFF5E1"

# Inicialización del estado de la sesión
if 'nombre' not in st.session_state:
    st.session_state['nombre'] = None
if 'historial' not in st.session_state:
    st.session_state['historial'] = []
if 'edad' not in st.session_state:
    st.session_state['edad'] = None
if 'tema' not in st.session_state:
    st.session_state['tema'] = None
if 'puntos' not in st.session_state:
    st.session_state['puntos'] = 0

# Definición de funciones para OpenAI
functions = [
    {
        "name": "generar_imagen",
        "description": "Genera una imagen a partir de una descripción proporcionada.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion": {
                    "type": "string",
                    "description": "Descripción de la imagen a generar."
                }
            },
            "required": ["descripcion"]
        }
    }
]

# Estilos CSS mejorados
st.markdown(f"""
<style>
    /* General Styling */
    body {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .main > div {{
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    /* Button Styling */
    .stButton>button {{
        background-color: {ORANGE} !important;
        color: white !important;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        padding: 12px 24px;
        font-size: 16px;
        transition: background-color 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {DARK_ORANGE} !important;
    }}
    /* Slider Styling */
    .stSlider .stSlider-thumb {{
        background-color: {ORANGE};
        border: 2px solid white;
    }}
    .stSlider .stSlider-track {{
        background-color: {ORANGE};
    }}
    /* Header Styling */
    h1 {{
        text-align: center;
        color: {ORANGE};
        font-family: 'Poppins', sans-serif;
        font-size: 48px;
    }}
    h2 {{
        text-align: center;
        color: {ORANGE};
        font-family: 'Poppins', sans-serif;
        font-size: 32px;
    }}
    /* Sidebar Styling */
    .sidebar .sidebar-content {{
        background-color: {SIDEBAR_COLOR};
        padding: 20px;
        border-radius: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }}
    /* Container Styling */
    .block-container {{
        max-width: 900px;
        margin: auto;
        padding-top: 40px;
    }}
    /* Text Input Styling */
    .stTextInput>div>div>input {{
        border-radius: 10px;
        border: 2px solid {ORANGE};
        padding: 10px;
        font-size: 16px;
        transition: border-color 0.3s;
    }}
    .stTextInput>div>div>input:focus {{
        border-color: {DARK_ORANGE};
    }}
    /* Text Area Styling */
    .stTextArea>div>div>textarea {{
        border-radius: 10px;
        border: 2px solid {ORANGE};
        padding: 10px;
        font-size: 16px;
        transition: border-color 0.3s;
    }}
    .stTextArea>div>div>textarea:focus {{
        border-color: {DARK_ORANGE};
    }}
    /* Markdown Text Styling */
    .stMarkdown p {{
        font-family: 'Verdana', sans-serif;
        font-size: 18px;
        line-height: 1.6;
    }}
    /* Chat Message Styling */
    .user-message {{
        background-color: {LIGHT_ORANGE};
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 12px;
        text-align: left;
        animation: fadeIn 0.5s ease-in-out;
    }}
    .bot-message {{
        background-color: {DARK_ORANGE};
        color: white;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 12px;
        text-align: left;
        animation: fadeIn 0.5s ease-in-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
</style>
""", unsafe_allow_html=True)

# Función para la encuesta inicial
def encuesta_inicial():
    st.title("🎓 Chatbot Educativo")
    st.subheader("Un chatbot amigable para aprender jugando y explorando.")
    st.header("¡Hola! Cuéntame un poco sobre ti.")
    with st.form("formulario_encuesta"):
        nombre = st.text_input("¿Cómo te llamas?", placeholder="Escribe tu nombre aquí")
        edad = st.slider("¿Cuántos años tienes?", 4, 12, 7)
        tema = st.selectbox(
            "¿Cuál es tu tema favorito para aprender?",
            ["🎨 Arte", "📐 Matemáticas", "🔬 Ciencia", "📚 Lectura", "🧩 Otro"]
        )
        submit = st.form_submit_button("Enviar 🎉")
        
        if submit and nombre:
            st.session_state['nombre'] = nombre
            st.session_state['edad'] = edad
            st.session_state['tema'] = tema
            logging.info(f"Encuesta completada: Nombre={nombre}, Edad={edad}, Tema Favorito={tema}")
            st.success(f"¡Gracias, {nombre}! Vamos a aprender sobre {tema}.")

# Función para interactuar con el chatbot
def interactuar_chatbot():
    st.title("🎓 Chatbot Educativo")
    st.subheader("Un chatbot amigable para aprender jugando y explorando.")

    # Barra lateral con información del usuario
    with st.sidebar:
        st.markdown(f"### 👋 ¡Hola, {st.session_state['nombre']}!")
        st.markdown(f"**Puntos:** {st.session_state['puntos']} ⭐")
        st.markdown(f"🔍 **Tema favorito:** {st.session_state['tema']}")
        st.markdown("🎯 Mantente explorando y aprendiendo para ganar más puntos.")
    
    st.header(f"¡Hola, {st.session_state['nombre']}! 😊")
    st.write("Escribe tu pregunta o solicitud abajo:")

    # Mostrar el historial de conversación
    for mensaje in st.session_state['historial']:
        if mensaje['rol'] == 'usuario':
            st.markdown(f"<div class='user-message'><strong>Tú:</strong> {mensaje['contenido']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'><strong>Chatbot:</strong> {mensaje['contenido']}</div>", unsafe_allow_html=True)
            if mensaje.get('imagen_url'):
                st.image(mensaje['imagen_url'], caption="Imagen generada", use_column_width=True)

    # Formulario para la entrada del usuario
    with st.form("entrada_usuario_form"):
        entrada_usuario = st.text_input("Escribe aquí:", placeholder="¿Cómo puedo aprender más sobre arte?")
        enviar = st.form_submit_button("Enviar 📨")
        if enviar and entrada_usuario.strip():
            procesar_mensaje_usuario(entrada_usuario.strip())
            st.rerun()

# Función para procesar el mensaje del usuario
def procesar_mensaje_usuario(mensaje):
    st.session_state['historial'].append({"rol": "usuario", "contenido": mensaje})
    logging.info(f"Entrada del usuario: {mensaje}")

    respuesta, imagen_url = generar_respuesta(mensaje)

    if imagen_url:
        st.session_state['puntos'] += 10
        respuesta_final = f"{respuesta}\n\n¡Excelente {st.session_state['nombre']}! Has ganado 10 puntos. 🎉"
        st.session_state['historial'].append({"rol": "chatbot", "contenido": respuesta_final, "imagen_url": imagen_url})
        logging.info(f"Respuesta del chatbot: {respuesta_final}")
    else:
        st.session_state['historial'].append({"rol": "chatbot", "contenido": respuesta})
        logging.info(f"Respuesta del chatbot: {respuesta}")

# Función para generar la respuesta del chatbot
def generar_respuesta(mensaje):
    try:
        all_messages = []
        system_msg = {
            "role": "system",
            "content": (
                f"Eres un chatbot educativo amigable que ayuda a niños de {st.session_state.get('edad','4')} a 12 años. "
                "Responde con claridad, sencillez y un lenguaje apropiado para su edad. Usa emojis si es relevante. "
                f"El usuario se llama {st.session_state.get('nombre','')}, le gusta {st.session_state.get('tema','')}. "
                "Si el usuario solicita una imagen o un dibujo, puedes llamar a la función 'generar_imagen'."
            )
        }
        all_messages.append(system_msg)

        for m in st.session_state['historial']:
            if m['rol'] == 'usuario':
                all_messages.append({"role":"user","content":m['contenido']})
            else:
                all_messages.append({"role":"assistant","content":m['contenido']})

        respuesta = openai.ChatCompletion.create(
            model="gpt-4o-2024-08-06",
            messages=all_messages,
            functions=functions,
            function_call="auto",
            max_tokens=150,
            temperature=0.7,
        )
        
        message = respuesta.choices[0].message
        if "function_call" in message:
            args = json.loads(message["function_call"]["arguments"])
            descripcion = args.get("descripcion", "")
            imagen_url = generar_imagen(descripcion)
            if imagen_url:
                return f"¡Aquí tienes la imagen de {descripcion}! 🎨", imagen_url
            else:
                return "Lo siento, no pude generar la imagen. 😔", None
        else:
            texto_respuesta = message['content'].strip()
            return texto_respuesta, None

    except Exception as e:
        logging.error(f"Error al generar la respuesta: {e}")
        return "Lo siento, tuve un problema procesando tu mensaje. 😕", None

# Función para generar imágenes usando OpenAI
def generar_imagen(descripcion):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=descripcion,
            size="1024x1024",
            n=1
        )
        url_imagen = response['data'][0]['url']
        logging.info(f"Imagen generada: {url_imagen}")
        return url_imagen
    except Exception as e:
        logging.error(f"Error al generar la imagen: {e}")
        return None

# Lógica principal de la aplicación
if st.session_state['nombre'] is None:
    encuesta_inicial()
else:
    interactuar_chatbot()
