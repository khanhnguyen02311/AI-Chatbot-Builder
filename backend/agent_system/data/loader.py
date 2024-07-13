import uuid
from datetime import datetime
import os
import mimetypes
import re
import subprocess
import pymupdf
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table
from langchain.text_splitter import RecursiveCharacterTextSplitter
from configurations.envs import General, Qdrant, ChatModels
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot_context as BotContextSchemas
from agent_system.data import QDRANT_SESSION, EMBEDDING_SESSION
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
                data = re.sub(
                    "(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])", " ", data
                )  # remove single newlines, keep multiple newlines

            # clean up
            data = re.sub("  +", " ", data)  # multiple blank spaces to single blank spaces
            data = re.sub(" *\n+ *", "\n", data)  # multiple newlines to single newlines and strip blank spaces around
            return data

        except Exception as e:
            print(e)
            return None

    def split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", " ", ""], chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        documents = text_splitter.create_documents([text])
        return [doc.page_content for doc in documents]

    def get_chunks_from_bot_context(
        self, bot_context: PostgresModels.BotContext, chunk_size: int = 800, chunk_overlap: int = 0
    ) -> list[str]:
        mime_type = mimetypes.guess_type(bot_context.filename)[0]
        if mime_type not in General.BOT_CONTEXT_ALLOWED_MIME_TYPES:
            raise Exception("Invalid file type, only txt/pdf/doc/docx files allowed")
        text_file = self.parse_to_text(bot_context.filename)
        split_chunks = self.split_text(text_file, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return split_chunks

    def load_chunks_to_chroma(self, bot_context: PostgresModels.BotContext, split_chunks: list[str]):
        #     # embedded_docs = embedding.embed_documents(docs_text)
        #     collection.add(
        #         documents=docs_text,
        #         ids=ids
        #     )
        pass

    def load_chunks_to_qdrant(
        self,
        chunks: list[str],
        bot_context: PostgresModels.BotContext,
        use_default_embedding: bool = True,
        custom_embedding_model_name: str | None = None,
        wait_for_completion: bool = True,
    ):
        if use_default_embedding is False or custom_embedding_model_name is not None:
            raise Exception("Custom embedding model not supported yet")

        metadata = {
            "id_bot_context": bot_context.id,
            "id_bot": bot_context.id_bot,
            "filename": bot_context.filename,
            "embedding_model": ChatModels.DEFAULT_EMBEDDING_MODEL_NAME,
        }
        collection_name = Qdrant.COLLECTION_PREFIX + ChatModels.DEFAULT_EMBEDDING_MODEL_NAME

        # USE EMBEDDING MODEL TO CONVERT DATA TO VECTORS
        embed_chunk_vecs = EMBEDDING_SESSION.embed_data(chunks)

        return QDRANT_SESSION.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(id=str(uuid.uuid1()), vector=chunk_vec, payload=dict(metadata, original_data=chunks[idx]))
                for idx, chunk_vec in enumerate(embed_chunk_vecs)
            ],
            wait=wait_for_completion,
        )


if __name__ == "__main__":
    # from agent_system.data import init_embedding_structure

    # init_embedding_structure()

    data_loader = DataLoader()
    extracted_text = data_loader.parse_to_text("testfile.txt")
    test_chunks = data_loader.split_text(extracted_text, 800, 0)
    print(f"testfile.txt is split into {len(test_chunks)} chunks. ")
    print(f"First chunk sample: \n'{test_chunks[0]}'")
    print("----")

    # test_bot_context = PostgresModels.BotContext(id=0, filename="testfile.txt", id_bot=0, time_created=datetime.now)
    # result = data_loader.load_chunks_to_qdrant(test_chunks, test_bot_context)
    # print("Chunks are loaded into Qdrant")
    # print("Result:", result.model_dump())
