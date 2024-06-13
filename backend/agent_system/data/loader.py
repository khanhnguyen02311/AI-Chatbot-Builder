import os
import mimetypes
import re
import subprocess
import pymupdf
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from configurations.envs import General, Qdrant
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot_context as BotContextSchemas
from . import EmbeddingModelWrapper, DEFAULT_EMBEDDING_MODEL, QDRANT_SESSION
from qdrant_client.models import PointStruct


class DataLoader:
    def parse_to_text(self, filename: str) -> str | None:
        """Used to extract & clean text from txt/pdf/doc/docx files"""

        file_path = os.path.join(General.BOT_CONTEXT_FILE_LOCATION, filename)
        mime_type = mimetypes.guess_type(file_path)[0]
        try:
            data = ""
            # txt file, use default read lib
            if mime_type == "text/plain":
                with open(file_path, "r") as file:
                    data = file.read()
            # pdf file, use pymupdf
            elif mime_type == "application/pdf":
                for page in pymupdf.open(file_path):
                    data += page.get_text().replace("\n", " ") + "\n"
            # docx file, use python-docx
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_docx = docx.Document(file_path)
                for content in file_docx.iter_inner_content():
                    if isinstance(content, Paragraph):
                        data += content.text + "\n"
                    elif isinstance(content, Table):
                        for row in content.rows:
                            print("\n|", end="")
                            for cell in row.cells:
                                data += cell.text
                                print("|", end="")
                        print("\n")
            # doc file, use antiword package from shell
            else:
                result = subprocess.run(["antiword", file_path], capture_output=True)
                data = result.stdout.decode("utf-8")
                # antiword doesn't keep paragraph structure but split newline for display
                data = re.sub('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', data)  # remove single newlines, keep multiple newlines

            # clean up
            data = re.sub('  +', ' ', data)  # multiple blank spaces to single blank spaces
            data = re.sub(' *\n+ *', '\n', data)  # multiple newlines to single newlines and strip blank spaces around
            return data

        except Exception as e:
            print(e)
            return None

    def split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", ".", " ", ""], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents = text_splitter.create_documents([text])
        return [doc.page_content for doc in documents]

    def get_chunks_from_bot_context(self, bot_context: PostgresModels.BotContext, chunk_size: int = 800, chunk_overlap: int = 0) -> list[str]:
        mime_type = mimetypes.guess_type(bot_context.filename)[0]
        if mime_type not in General.BOT_CONTEXT_ALLOWED_MIME_TYPES:
            raise Exception("Invalid file type, only txt/pdf/doc/docx files allowed")
        text_file = self.parse_to_text(bot_context.filename)
        split_chunks = self.split_text(text_file, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return split_chunks

    def load_chunks_to_chroma(self, bot_context: PostgresModels.BotContext, split_chunks: list[str]):
        # documents = text_splitter.create_documents(file_info)
        #     file.close()
        #     docs_text = [doc.page_content for doc in documents]
        #     # embedding = OpenAIEmbeddings()
        #     # embedded_docs = embedding.embed_documents(docs_text)
        #     collection.add(
        #         documents=docs_text,
        #         ids=ids
        #     )
        pass

    def load_chunks_to_qdrant(self, bot_context: PostgresModels.BotContext, chunks: list[str], use_default_embedding: bool = True, custom_embedding_model_name: str | None = None):
        metadata = {
            "bot_context": BotContextSchemas.BotContextFULL.model_validate(bot_context).model_dump()
        }

        if use_default_embedding:
            metadata["embedding_model"] = DEFAULT_EMBEDDING_MODEL.model_name
            embed_chunk_vecs = DEFAULT_EMBEDDING_MODEL.embed_data(chunks)
            collection_name = Qdrant.COLLECTION_PREFIX + DEFAULT_EMBEDDING_MODEL.model_name
        else:
            embedding = EmbeddingModelWrapper(model_name=custom_embedding_model_name)
            metadata["embedding_model"] = custom_embedding_model_name
            embed_chunk_vecs = embedding.embed_data(chunks)
            collection_name = Qdrant.COLLECTION_PREFIX + custom_embedding_model_name
            # todo: some kinds of saving the embedding model name to the database for later searchs

        QDRANT_SESSION.upload_points(
            collection_name=collection_name,
            points=[PointStruct(vector=chunk_vec, metadata=metadata) for chunk_vec in embed_chunk_vecs],
            metadata=metadata
        )


if __name__ == "__main__":
    data_loader = DataLoader()
    extracted_text = data_loader.parse_to_text("testfile.txt")
    chunks = data_loader.split_text(extracted_text, 800, 0)
    for i in chunks:
        print("--NEW CHUNK--")
        print(i)
