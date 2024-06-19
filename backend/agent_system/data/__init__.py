from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, WriteOrdering
from langchain_openai import OpenAIEmbeddings
from configurations.envs import Qdrant, ChatModels


class EmbeddingModelWrapper:
    def __init__(self, model_name: str = ChatModels.DEFAULT_EMBEDDING_MODEL_NAME):
        if model_name not in list(ChatModels.ALLOWED_EMBEDDING_MODELS.keys()):
            raise Exception("Embedding model not supported for now")

        self.model_name = model_name
        self.model_dimension = ChatModels.ALLOWED_EMBEDDING_MODELS[model_name]
        self.model = OpenAIEmbeddings(model=model_name.split("@")[1])
        # self.model = OpenAIEmbeddings(model=model_name.split("@")[1], dimension=self.model_dimension)  # dimension not supported

    def embed_data(self, data: str | list[str]):
        if isinstance(self.model, OpenAIEmbeddings):
            if type(data) == str:
                print("single query received.")
                return self.model.embed_query(data)
            else:
                print("chunks received.")
                return self.model.embed_documents(data)
        # elif isinstance(self.model, "phobert"):
        #     pass

        raise Exception("Embedding model not found or not supported")


def init_embedding_structure():
    collection_name = Qdrant.COLLECTION_PREFIX + ChatModels.DEFAULT_EMBEDDING_MODEL_NAME
    if not QDRANT_SESSION.collection_exists(collection_name=collection_name):
        print(f"Creating collection {collection_name}")
        create_coll_succeed = QDRANT_SESSION.create_collection(collection_name=collection_name,
                                                               vectors_config=VectorParams(size=ChatModels.ALLOWED_EMBEDDING_MODELS[ChatModels.DEFAULT_EMBEDDING_MODEL_NAME],
                                                                                           distance=Distance.COSINE),
                                                               timeout=5)
        if not create_coll_succeed:
            raise Exception("Collection creation failed")
        QDRANT_SESSION.create_payload_index(collection_name=collection_name,
                                            field_name="id_bot",
                                            field_schema="integer",
                                            ordering=WriteOrdering.MEDIUM)


QDRANT_SESSION = QdrantClient(f"{Qdrant.HOST}:{Qdrant.PORT}")
EMBEDDING_SESSION = EmbeddingModelWrapper()
