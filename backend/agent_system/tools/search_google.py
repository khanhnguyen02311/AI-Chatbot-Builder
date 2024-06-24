from configurations.envs import ChatModels
from langchain.agents import Tool
from langchain_google_community import GoogleSearchAPIWrapper

google_search_util = GoogleSearchAPIWrapper(
    google_api_key=ChatModels.GOOGLE_API_KEY, google_cse_id=ChatModels.GOOGLE_CSE_ID, k=5
)


def google_search_results_util(query: str):
    """Search Google using a query and get a list of results. Recommended to use the language related to the context of the conversation to get the best results."""
    try:
        return google_search_util.results(query, num_results=5)
    except Exception as e:
        return "Error happened when using tool: " + str(e) + ". You should check your input, it must be a query string."


def get_search_google_tool():
    return Tool(
        name="search_google",
        description="Search Google using a query and get a list of results. Recommended to use the language related to the context of the conversation to get the best results.",
        func=google_search_results_util,
    )


if __name__ == "__main__":
    tool = get_search_google_tool()
    print(tool.run("how to make a cake"))
