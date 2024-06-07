from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from configurations.envs import Qdrant

QDRANT_CLIENT = None
EMBEDDING_MODEL = None


class EmbeddingModelWrapper:
    def __init__(self, model_name: str = "openai/text-embedding-3-small"):
        if model_name not in ["openai/text-embedding-3-small", "openai/text-embedding-3-large"]:  # , "vinai/phobert-base", "vinai/phobert-base-v2"]
            raise Exception("embedding model not supported for now")

        self.model_name = model_name
        self.model = OpenAIEmbeddings(model=model_name.split("/")[1])

    def embed_data(self, data: list[str] | str):
        if isinstance(self.model, OpenAIEmbeddings):
            if type(data) == list[str]:
                return self.model.embed_documents(data)
            else:
                return self.model.embed_query(data)
        raise Exception("embedding model error")


def init_embedding_structure(embedding_model_name: str = "openai/text-embedding-3-small"):
    global QDRANT_CLIENT, EMBEDDING_MODEL

    if QDRANT_CLIENT is None:
        QDRANT_CLIENT = QdrantClient(host=Qdrant.HOST, port=Qdrant.PORT)

    if not QDRANT_CLIENT.collection_exists(collection_name=Qdrant.COLLECTION_PREFIX + "openai_1536"):
        QDRANT_CLIENT.create_collection(
            collection_name=Qdrant.COLLECTION_PREFIX + "openai_1536",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

    EMBEDDING_MODEL = EmbeddingModelWrapper(embedding_model_name)
