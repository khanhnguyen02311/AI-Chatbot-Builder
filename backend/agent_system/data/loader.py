import os
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DataLoader:
    def __load_from_filename(self, filename: str):
        # documents = []
        # with open(f"{os.path.abspath(__file__)}/../../etc/userdata/{filename}",'w') as file:
        #     for text in lst_info:
        #         file.write(text)
        #     file.close()
        # with open('tourism.txt','r') as file:   
        #     temp = file.read()
        pass

    def load_to_chroma(self, filename: str):
        # documents = self.__load_from_filename(filename)
        file_info = []
        with open(filename, 'w') as file:
            file_info.append()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        
        documents = text_splitter.create_documents(file_info)
        file.close()
        docs_text = [doc.page_content for doc in documents]
        # embedding = OpenAIEmbeddings()
        # embedded_docs = embedding.embed_documents(docs_text)
        collection.add(
            documents=docs_text,
            ids=ids
        )

    def load_to_postgres():
        pass
