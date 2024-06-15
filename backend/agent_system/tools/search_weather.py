from configurations.envs import ChatModels
from langchain.agents import Tool
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper

weather_search_util = OpenWeatherMapAPIWrapper(openweathermap_api_key=ChatModels.OPENWEATHERMAP_API_KEY)


def get_search_weather_tool():
    return Tool(
        name="search_weather",
        description="Get current weather information of specific location. The input format is 'City, Country'.",
        func=weather_search_util.run)


if __name__ == "__main__":
    print(weather_search_util.run("Da Lat, Vietnam"))
