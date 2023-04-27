import aiohttp


async def get(url: str):
    """
    GET url using aiohttp.

    :param url:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
