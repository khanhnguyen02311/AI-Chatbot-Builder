from .search_google import get_search_google_tool
from .search_weather import get_search_weather_tool

tool_map = {
    "search_google": get_search_google_tool,
    "search_weather": get_search_weather_tool
}


def get_tools_by_names(names: list):
    tools = []
    for name in names:
        if name in tool_map:
            tools.append(tool_map[name]())
    return tools
