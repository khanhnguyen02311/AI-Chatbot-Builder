from configurations.envs import ChatModels
from langchain.agents import Tool
from langchain_core.tools import tool


@tool
def search_local_data_util(query: str) -> str:
    """Search local-region data using a query."""
    
    return "test"


def get_search_local_data_tool():
    return Tool(
        name="search_local_data",
        description="Search local-region data using a query.",
        func=search_local_data_util)


if __name__ == "__main__":
    tool = get_search_local_data_tool()
    result = tool.run("query")
    print(result)
