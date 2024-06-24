from components.data.models import postgres as PostgresModels
from .search_google import get_search_google_tool
from .search_weather import get_search_weather_tool
from .scrape_website import get_scrape_website_tool
from .search_local_data import get_search_local_data_tool

tool_map = {
    "search_google": get_search_google_tool,
    "search_weather": get_search_weather_tool,
    "scrape_website": get_scrape_website_tool,
}


def get_tools_by_names(names: list):
    tools = []
    for name in names:
        if name in tool_map:
            tools.append(tool_map[name]())
        else:
            raise Exception("Tool not found")
    return tools


def get_retriever_tools_by_bot_context(bot_contexts: list[PostgresModels.BotContext]):
    tools = []
    for bot_context in bot_contexts:
        tools.append(get_search_local_data_tool(bot_context))
    return tools
