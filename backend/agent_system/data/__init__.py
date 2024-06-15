from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from configurations.envs import Qdrant, ChatModels


class EmbeddingModelWrapper:
    def __init__(self, model_name: str = "openai@text-embedding-3-small"):
        if model_name not in list(ChatModels.ALLOWED_EMBEDDING_MODELS.keys()):
            raise Exception("Embedding model not supported for now")

        self.model_name = model_name
        self.model_dimension = ChatModels.ALLOWED_EMBEDDING_MODELS[model_name]
        self.model = OpenAIEmbeddings(model=model_name.split("@")[1], dimension=self.model_dimension)

    def embed_data(self, data: str | list[str]):
        if isinstance(self.model, OpenAIEmbeddings):
            if type(data) == str:
                return self.model.embed_query(data)
            else:
                return self.model.embed_documents(data)
        # elif isinstance(self.model, "phobert"):
        #     pass

        raise Exception("Embedding model not found or not supported")


QDRANT_SESSION: QdrantClient | None = None
DEFAULT_EMBEDDING_MODEL: EmbeddingModelWrapper | None = None


def init_embedding_structure(default_embedding_model_name: str = "openai@text-embedding-3-small"):
    global QDRANT_SESSION, DEFAULT_EMBEDDING_MODEL

    DEFAULT_EMBEDDING_MODEL = EmbeddingModelWrapper(model_name=default_embedding_model_name)

    if QDRANT_SESSION is None:
        QDRANT_SESSION = QdrantClient(f"{Qdrant.HOST}:{Qdrant.PORT}")

    collection_name = Qdrant.COLLECTION_PREFIX + default_embedding_model_name

    if not QDRANT_SESSION.collection_exists(collection_name=collection_name):
        QDRANT_SESSION.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=ChatModels.ALLOWED_EMBEDDING_MODELS[default_embedding_model_name], distance=Distance.COSINE))
