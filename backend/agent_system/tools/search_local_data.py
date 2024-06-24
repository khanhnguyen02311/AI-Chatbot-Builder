from langchain.agents import Tool
from langchain_core.tools import tool
from components.data.models import postgres as PostgresModels
from agent_system.data.retriever import DataRetriever


def get_search_local_data_tool(bot_context: PostgresModels.BotContext):
    @tool
    def search_local_data_util(query: str) -> list[str]:
        """Search from local file using a query to get related information"""
        try:
            data_retriever = DataRetriever()
            result = data_retriever.get_related_data_from_query(query, bot_context.id_bot, bot_context.id)
            return [point.payload["original_data"] for point in result]
        except Exception as e:
            return [f"Error happened when using tool: {str(e)}. You should check your input, it must be a query string."]

    tool_name = f"search_local_data_from_context_{bot_context.id}"
    tool_description = f"Search from local file using a query to get related information. The file context is about: {bot_context.description}."
    return Tool(name=tool_name, description=tool_description, func=search_local_data_util)


if __name__ == "__main__":
    test_bot_context = PostgresModels.BotContext(id=0, id_bot=0, description="Things you need to know about Quảng Bình")
    tool = get_search_local_data_tool(test_bot_context)
    result = tool.run("ăn hải sản ở đâu")

    print("Tool name: " + tool.name)
    print("Tool description: " + tool.description + "\n")
    for content in result:
        print(content)
        print()
