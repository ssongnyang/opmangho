import aiohttp
from bs4 import BeautifulSoup


async def news_title(keyword: str) -> list[str]:
    # 키워드, URL
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1"

    # 웹 페이지 요청
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")

            # news_tit 부분 필터링
    articles = soup.select(".news_tit")
    return [article.text for article in articles]
