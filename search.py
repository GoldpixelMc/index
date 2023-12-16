import json
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import sys

async def scrape_website(session, url, keyword, results):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            html_content = await response.text()

        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.title.text.strip()
        about_section = soup.find('meta', attrs={'name': 'description'})
        about = about_section.get('content') if about_section else "Not available"

        if keyword.lower() in html_content.lower():
            result_html = f"""
                <div class="result">
                    <div class="title">{title}</div>
                    <div><a href="{url}" target="_blank">{url}</a></div>
                    <div class="about">About: {about}</div>
                </div>
            """
            results.append(result_html)

    except (aiohttp.ClientError, Exception):
        pass

async def main(keyword):
    with open('websites.json', 'r') as file:
        config = json.load(file)

    websites = config.get("websites", [])
    results = []

    async with aiohttp.ClientSession() as session:
        # Make asynchronous requests for initial websites
        tasks = [scrape_website(session, website.get("url", ""), keyword, results) for website in websites]
        await asyncio.gather(*tasks)

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py <keyword>")
        sys.exit(1)

    keyword = sys.argv[1]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(main(keyword))

    for result in results:
        print(result)

