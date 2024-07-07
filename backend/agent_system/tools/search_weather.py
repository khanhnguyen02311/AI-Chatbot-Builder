from configurations.envs import ChatModels
from langchain.agents import Tool
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper

weather_search_util = OpenWeatherMapAPIWrapper(openweathermap_api_key=ChatModels.OPENWEATHERMAP_API_KEY)


def weather_search_result_util(location: str):
    """Get current weather information of specific location. The input format is 'City, Country'. Examples: 'Tỉnh Quảng Bình,VN', 'Da Lat,VN'"""
    try:
        return weather_search_util.get_current_weather(location)
    except Exception as e:
        return (
            "Error happened when using tool: "
            + str(e)
            + '. You should check your input, it must be a valid location format ("City, Country").'
        )


def get_search_weather_tool():
    return Tool(
        name="search_weather",
        description="Get current weather information of specific location. The input format is 'City, Country'. Examples: 'Tỉnh Quảng Bình,VN', 'Da Lat,VN'",
        func=weather_search_util.run,
    )


if __name__ == "__main__":
    print(weather_search_util.run("Da Lat, VN"))
