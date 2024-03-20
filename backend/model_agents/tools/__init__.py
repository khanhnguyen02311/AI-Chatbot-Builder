from configurations.envs import ChatModels
from langchain_core.tools import tool
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.agents import Tool

google_search_util = GoogleSearchAPIWrapper(google_api_key=ChatModels.GOOGLE_API_KEY, google_cse_id=ChatModels.GOOGLE_CSE_ID, k=5)
weather_search_util = OpenWeatherMapAPIWrapper(openweathermap_api_key=ChatModels.OPENWEATHERMAP_API_KEY)


@tool
def website_scrape_util(url: str, **kwargs):
    """Scrape a website and get the content."""
    pass


def get_google_search_tool():
    return Tool(
        name="google_search",
        description="Search Google and get a list of results.",
        func=google_search_util.run)


def get_weather_search_tool():
    return Tool(
        name="weather_search",
        description="Get current weather information of specific location. The input format is 'City, Country'.",
        func=weather_search_util.run)


def get_tools_by_names(names: list):
    tools = []
    for name in names:
        if name == "google_search":
            tools.append(get_google_search_tool())
        elif name == "weather_search":
            tools.append(get_weather_search_tool())
    return tools
