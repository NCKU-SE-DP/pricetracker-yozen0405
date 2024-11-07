from bs4 import BeautifulSoup
import requests
import json
    
def process_news_item(news):
    """
    Fetches detailed content from a news article.
    """
    response = requests.get(news["titleLink"])
    soup = BeautifulSoup(response.text, "html.parser")
    # 標題
    title = soup.find("h1", class_="article-content__title").text
    time = soup.find("time", class_="article-content__time").text
    # 定位到包含文章内容的 <section>
    content_section = soup.find("section", class_="article-content__editor")

    paragraphs = [
        p.text
        for p in content_section.find_all("p")
        if p.text.strip() != "" and "▪" not in p.text
    ]
    detailed_news = {
        "url": news["titleLink"],
        "title": title,
        "time": time,
        "content": paragraphs,
    }

    return detailed_news

def parse_summary_result(result):
    """
    Parses the summary result JSON and extracts 'summary' and 'reason'.

    :param result: The JSON-formatted summary result string.
    :return: A dictionary with keys 'summary' and 'reason', or an empty dictionary if parsing fails.
    """
    response_data = {}
    if result:
        try:
            result = json.loads(result)
            response_data["summary"] = result["影響"]
            response_data["reason"] = result["原因"]
        except json.JSONDecodeError:
            return response_data
    return response_data