import os
import asyncio
from dotenv import load_dotenv

from webscrapper_client_api import WebscrapperClientAPIAsync


async def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    async with WebscrapperClientAPIAsync(api_key) as client:
        # Example with cookies
        cookies = {"session_id": "abc123", "user": "test"}

        result = await client.get_page(
            url="https://xvideos.com",
            cookies=cookies,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            referer="https://google.com",
        )
        # print(result)
        print(f"Status: {result['status_code']}")
        print(f"HTML length: {len(result['html'])}")

        # RKN check
        rkn_result = await client.check_rkn(url="https://xvideos.com")
        print(f"RKN check result: {rkn_result}")


if __name__ == "__main__":
    asyncio.run(main())
