import streamlit as st
import os
from dotenv import load_dotenv
from loaders import load_info

from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI

################################################################################
# Configurações e inicialização
################################################################################

MESSAGE_EXAMPLE = [
    ('user', 'sou user'),
    ('assistant', 'sou assistant'),
    ('ai', 'sou ai'),
    ('human', 'sou human'),
]

CONFIG_MODELOS = {
    'Groq': {'modelos': ['llama-3.3-70b-versatile','gemma2-9b-it']},
    'OpenAI': {'modelos': []},
}
# OpenAi: gpt-4o-mini

MEMORIA_ZERO = ConversationBufferMemory()

SYSTEM_MESSAGE_TEMPLATE = '''
Você é um assistente de chatbot da SUDEC.
Você deve responder as perguntas dos usuários de forma clara e objetiva.
Você possui acesso às seguintes informações de documentos E sites:
'''

def start_chat():
    if not 'info' in st.session_state:
        st.session_state['info'] = []
    if not 'chat' in st.session_state:
        st.session_state['chat'] = None
    if not 'messages' in st.session_state:
        st.session_state['messages'] = MEMORIA_ZERO

################################################################################
# Página de chat
################################################################################

def carrega_modelo(provedor, modelo): 
    
    if provedor == 'Groq':
        return ChatGroq(model=modelo, api_key= os.getenv('GROQ_API_KEY'))
    #elif provedor == 'OpenAI':
    #    return ChatOpenAI(model=modelo, api_key=st.secrets['OPENAI_API_KEY'])

def gera_chain():

    system_message = SYSTEM_MESSAGE_TEMPLATE.join([f'\n\n{tipo}: {info}' for tipo, info in st.session_state['info']])

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')]
    )
   
    chat = st.session_state['chat']
    chain = template | chat
    st.session_state['chain'] = chain


def chat_page():
    st.header("Bem vindo ao Chatbot da SUDEC")
    
    chain = st.session_state.get("chain")
    if not chain:
        st.error("Por favor, selecione um modelo e carregue documentos.")
        st.stop()

    memoria = st.session_state.get("messages", MEMORIA_ZERO)
    
    for message in memoria.buffer_as_messages:
        # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
        with st.chat_message(message.type):
            st.markdown(message.content)

    input_user = st.chat_input("Digite sua mensagem")

    if input_user:
        with st.chat_message('user'):
            st.markdown(input_user)
        
        with st.chat_message('ai'):
            resposta = st.write_stream(chain.stream({
                    'chat_history': memoria.buffer_as_messages,
                    'input': input_user,
                }))
            
        memoria.chat_memory.add_user_message(input_user)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['messages'] = memoria

################################################################################
# Sidebar
################################################################################

def uploads():
    # Dictionary mapping file types to their input methods
    input_file_type = {
        'site': lambda: st.text_input('Digite a url do site'),
        'youtube': lambda: st.text_input('Digite a url do site'),
        'pdf': lambda: st.file_uploader('Faça o upload do arquivo', type=['pdf']),
        'csv': lambda: st.file_uploader('Faça o upload do arquivo', type=['csv']),
        'txt': lambda: st.file_uploader('Faça o upload do arquivo', type=['txt'])
    }
    
    tipo = st.selectbox("Selecione o tipo de arquivo", input_file_type.keys())
    info = input_file_type[tipo]()
    if tipo and info:      
        loaded_info = load_info(tipo, info)
        return tipo, loaded_info

def model_selection():
    provedor = st.selectbox("Selecione o provedor", CONFIG_MODELOS.keys())
    modelo = st.selectbox("Selecione o modelo", CONFIG_MODELOS[provedor]['modelos'])
    return provedor, modelo

def sidebar():
    tabs = st.tabs(['Uploads', 'Modelo'])
    with tabs[0]:
        st.markdown("#### Carregar Informações  ")
        new_info = uploads()
        if new_info:
            st.info(f'Informações tipo {new_info[0]} carregadas.')
        if st.button('Salvar informações') and new_info:
            st.session_state['info'].append(new_info)
            st.success(f'Informações tipo {st.session_state['info'][-1][0]} salvas com sucesso!')
            st.info(f' {len(st.session_state['info'])} informações salvas!')
    
    with tabs[1]:
        st.markdown("#### Selecione o modelo ")
        provedor, modelo = model_selection()
        if st.button('Chamar assistente'):
            if st.session_state['info'] == []:
                st.warning('Nenhuma informação caregada. Deseja continuar sem informações?')
                if st.button('Continuar'):
                    st.session_state['chat'] = carrega_modelo(provedor, modelo)
                    gera_chain()
            else:
                st.session_state['chat'] = carrega_modelo(provedor, modelo)
                gera_chain() 
    
def main():
    load_dotenv()
    start_chat()
    with st.sidebar:
        sidebar()
    chat_page()

if __name__ == "__main__":
    main()