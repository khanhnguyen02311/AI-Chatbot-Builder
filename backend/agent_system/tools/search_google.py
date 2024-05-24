from configurations.envs import ChatModels
from langchain.agents import Tool
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper

google_search_util = GoogleSearchAPIWrapper(google_api_key=ChatModels.GOOGLE_API_KEY, google_cse_id=ChatModels.GOOGLE_CSE_ID, k=5)


def get_search_google_tool():
    return Tool(
        name="search_google",
        description="Search Google using a query and get a list of results. Recommended to use the language related to the context of the conversation to get the best results.",
        func=google_search_util.run)


if __name__ == "__main__":
    print(google_search_util.run("how to make a cake"))
