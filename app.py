"""
app.py
Interfaz web (Streamlit) para que cualquier persona colaboradora le haga preguntas al agente
sin tocar código ni abrir los documentos originales. Esta es la app que se despliega en OCI.

Ejecutar localmente:
    streamlit run app.py
"""

import streamlit as st

from src.router import ask

st.set_page_config(page_title="Asistente de Documentos Internos", page_icon="📄")

st.title("Asistente de Documentos Internos")
st.caption(
    "Preguntá en lenguaje natural sobre las ventas (CSV) o las políticas/manuales (PDF) "
    "de la empresa. El agente busca la respuesta por vos."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Escribí tu pregunta...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            try:
                answer = ask(question)
            except Exception as exc:  # noqa: BLE001
                answer = f"Ocurrió un error al procesar la pregunta: {exc}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    st.header("Ejemplos de preguntas")
    st.markdown(
        "- ¿Cuál fue el producto más vendido en diciembre de 2015?\n"
        "- ¿Qué lenguajes de programación se usan en el back-end?\n"
        "- ¿Cuál es la política de trabajo remoto?\n"
    )
