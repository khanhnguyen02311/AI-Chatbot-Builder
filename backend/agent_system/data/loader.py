import mimetypes
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

from configurations.envs import General
from components.data.models import postgres as PostgresModels


class DataLoader:
    def parse_to_text(self, filename: str):
        file_path = os.path.join(General.BOT_CONTEXT_FILE_LOCATION, filename)
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type not in General.BOT_CONTEXT_ALLOWED_MIME_TYPES:
            raise Exception("Invalid file type, only txt/pdf/doc/docx files allowed")

        return None

    def load_from_bot_context(self, bot_context: PostgresModels.BotContext):
        file_path = os.path.join(General.BOT_CONTEXT_FILE_LOCATION, bot_context.filename)
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type not in General.BOT_CONTEXT_ALLOWED_MIME_TYPES:
            return None
        if mime_type == "text/plain":
            with open(file_path, "r") as file:
                data = file.read()
            text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "."], chunk_size=1000, chunk_overlap=100)
            return data
        return None
        #         loader = TextLoader(file_path)
        #         documents = loader.load()
        #         return documents
        #     elif mt == "application/pdf":
        #         pass
        #     elif mt == "application/msword":
        #         pass
        #     elif mt == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        #         pass
        #     else:  # parser unsupported
        #         return None
        #     return None

        # with open(f"{os.path.join(General.BOT_CONTEXT_FILE_LOCATION, filename)}", 'r') as file:
        #     try:
        #         file_info = file.read()
        #     except Exception as e:
        #         print(e)
        #         return None
        #     return file_info
        pass

    def load_to_chroma(self, filename: str):
        with open(f"{os.path.join(General.BOT_CONTEXT_FILE_LOCATION, filename)}", 'r') as file:
            file_info = file.read()
            file.close()

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
