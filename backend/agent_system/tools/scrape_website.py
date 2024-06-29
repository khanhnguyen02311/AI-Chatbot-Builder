from langchain_core.tools import tool
from langchain.agents import Tool
from langchain_community.document_loaders import WebBaseLoader


@tool
def website_scrape_util(url: str) -> str:
    """Scrape the provided web page for detailed information."""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return "\n\n".join(
            [f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>' for doc in docs]
        )
    except Exception as e:
        return "Error happened when using tool: " + str(e) + ". You should check your input, it must be a valid URL."


    # Todo: custom website scraper, clean and extract to string


def get_scrape_website_tool():
    return Tool(
        name="scrape_website",
        description="Scrape specific web page using an URL you provided for detailed information. You should use the search_google tool first, and then take the webpage URL you like to provide to this tool.",
        func=website_scrape_util,
    )


if __name__ == "__main__":
    tool = get_scrape_website_tool()
    result = tool.run("https://vinpearl.com/vi/40-dia-diem-du-lich-viet-nam-noi-tieng-nhat-dinh-nen-den-mot-lan")
    print(result)
    # print(website_scrape_util.run("https://vinpearl.com/vi/40-dia-diem-du-lich-viet-nam-noi-tieng-nhat-dinh-nen-den-mot-lan"))
