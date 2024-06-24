from qdrant_client.models import Filter, FieldCondition, MatchValue, ScoredPoint
from configurations.envs import Qdrant, ChatModels
from agent_system.data import QDRANT_SESSION, EMBEDDING_SESSION
from components.data.models import postgres as PostgresModels


class DataRetriever:
    def get_existed_bot_context_vectors(self, id_bot: int, id_bot_context: int):
        collection_name = Qdrant.COLLECTION_PREFIX + ChatModels.DEFAULT_EMBEDDING_MODEL_NAME

        filter_condition_list = [
            FieldCondition(key="id_bot", match=MatchValue(value=id_bot)),
            FieldCondition(key="id_bot_context", match=MatchValue(value=id_bot_context)),
        ]
        return QDRANT_SESSION.scroll(
            collection_name=collection_name, scroll_filter=Filter(must=filter_condition_list), with_payload=True, limit=2
        )

    def get_related_data_from_query(
        self, query: str, id_bot: int, id_bot_context: int | None = None, max_chunks: int = 3
    ) -> list[ScoredPoint]:
        """Get related chunks from bot context using a query"""
        # if id_bot_context is not None:
        #     raise Exception("Get data by specific bot context is not supported yet")

        collection_name = Qdrant.COLLECTION_PREFIX + ChatModels.DEFAULT_EMBEDDING_MODEL_NAME
        query_vector = EMBEDDING_SESSION.embed_data(query)

        filter_condition_list = []
        if id_bot is not None:
            filter_condition_list.append(FieldCondition(key="id_bot", match=MatchValue(value=id_bot)))
        if id_bot_context is not None:
            filter_condition_list.append(FieldCondition(key="id_bot_context", match=MatchValue(value=id_bot_context)))

        return QDRANT_SESSION.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=Filter(must=filter_condition_list),
            with_payload=True,
            limit=max_chunks,
        )


if __name__ == "__main__":
    from agent_system.data import init_embedding_structure

    init_embedding_structure()
    retriever = DataRetriever()

    print("TESTING get_existed_bot_context_vectors")
    existed_points = retriever.get_existed_bot_context_vectors(id_bot=0, id_bot_context=0)
    # records format: (list[Record], id offset for next scroll request)
    for record in existed_points[0]:
        print(f"ID: {record.id}")
        print(record.payload["original_data"])

    print("\nTESTING get_related_data_from_query")
    query_str = "ăn hải sản ở đâu"

    print(f"Your query string: {query_str}")
    related_chunks = retriever.get_related_data_from_query(query_str, id_bot=0, id_bot_context=0, max_chunks=5)
    for chunk in related_chunks:
        print(f"ID: {chunk.id} -- Score: {chunk.score}")
        print(chunk.payload["original_data"])
        print()
