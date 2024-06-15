from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from configurations.envs import Qdrant, ChatModels

_default_embedding_model = "openai@text-embedding-3-small"


class EmbeddingModelWrapper:
    def __init__(self, model_name: str = _default_embedding_model):
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


def init_embedding_structure():
    collection_name = Qdrant.COLLECTION_PREFIX + _default_embedding_model
    if not QDRANT_SESSION.collection_exists(collection_name=collection_name):
        QDRANT_SESSION.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=ChatModels.ALLOWED_EMBEDDING_MODELS[_default_embedding_model], distance=Distance.COSINE))


QDRANT_SESSION = QdrantClient(f"{Qdrant.HOST}:{Qdrant.PORT}")
DEFAULT_EMBEDDING_MODEL = EmbeddingModelWrapper()
