from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, YoutubeLoader, WebBaseLoader
import tempfile


def load_info(tipo, fonte):
    if tipo == 'site':
        loader = WebBaseLoader(fonte)
    elif tipo == 'youtube':
        loader = YoutubeLoader.from_youtube_url(fonte, add_video_info=False, language='pt')
    elif tipo == 'pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix='pdf') as temp_file:
            temp_file.write(fonte.read())
            temp_file_path = temp_file.name
        loader = PyPDFLoader(file_path=temp_file_path)
    elif tipo == 'csv':
        with tempfile.NamedTemporaryFile(delete=False, suffix='csv') as temp_file:
            temp_file.write(fonte.read())
            temp_file_path = temp_file.name
        loader = CSVLoader(file_path=temp_file_path, encoding='utf-8')
    elif tipo == 'txt':
        with tempfile.NamedTemporaryFile(delete=False, suffix='txt') as temp_file:
            temp_file.write(fonte.read())
            temp_file_path = temp_file.name
        loader = TextLoader(file_path=temp_file_path)
    
    documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in documentos])
    return documento


##########################################
# Teste

# url = 'https://www.defesacivil.df.gov.br/a-defesa-civil-do-distrito-federal/'
# url_youtube = 'https://www.youtube.com/watch?v=doH5apZnp7g'


# documento = load_info('csv', fonte=open(r'c:\Users\ener.beckmann\Downloads\tb_servidores - Export_bi_total.csv', 'rb'))
# print(documento)

