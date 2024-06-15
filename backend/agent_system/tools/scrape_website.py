from configurations.envs import ChatModels
from langchain_core.tools import tool
from langchain.agents import Tool


@tool
def website_scrape_util(url: str, **kwargs):
    # Todo: scrape, clean and extract to string
    return "Scraping utility not implemented yet."


def get_scrape_website_tool():
    return Tool(
        name="scrape_website",
        description="Scrape a website and get the content.",
        func=website_scrape_util)


if __name__ == "__main__":
    print(website_scrape_util("https://vinpearl.com/vi/40-dia-diem-du-lich-viet-nam-noi-tieng-nhat-dinh-nen-den-mot-lan"))
