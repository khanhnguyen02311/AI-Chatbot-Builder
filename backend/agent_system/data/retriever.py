from qdrant_client.models import Filter, FieldCondition, MatchValue, ScoredPoint
from configurations.envs import Qdrant, ChatModels
from agent_system.data import QDRANT_SESSION, EMBEDDING_SESSION
from components.data.models import postgres as PostgresModels


class DataRetriever:
    def get_related_data(self, query: str, id_bot: int, id_bot_context: int | None = None, max_chunks: int = 3) -> list[ScoredPoint]:
        """Get related chunks from bot context using a query"""

        collection_name = Qdrant.COLLECTION_PREFIX + ChatModels.DEFAULT_EMBEDDING_MODEL_NAME
        query_vector = EMBEDDING_SESSION.embed_data(query)

        return QDRANT_SESSION.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=Filter(
                must=[FieldCondition(key="id_bot", match=MatchValue(value=id_bot))]
            ),
            with_payload=True,
            limit=max_chunks,
        )


if __name__ == "__main__":
    import sys
    from agent_system.data import init_embedding_structure

    init_embedding_structure()
    retriever = DataRetriever()

    query_str = "ăn hải sản ở đâu"

    print(f"Your query string: {query_str}")
    related_chunks = retriever.get_related_data(query_str, 0, max_chunks=5)
    for chunk in related_chunks:
        print(f"ID: {chunk.id} -- Score: {chunk.score}")
        print(chunk.payload["original_data"])
        print()
