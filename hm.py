import asyncio
import json

import aiohttp
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.min_rows', 20)
pd.set_option('display.width', None)

LOCATIONS = {
    "Hackney": "REGION%5E93953",
    "Islington": "REGION%5E93965",
}


class Wrongmove:
    def __init__(self, url, filter_size: bool = False, filter_percentile: int | bool = False):
        self.url = url
        self.filter_size = filter_size
        self.filter_percentile = filter_percentile
        self.results = None
        self.df = None

        self._json_var = "window.jsonModel"
        self._base_url = "https://www.rightmove.co.uk"

    async def fetch(self, as_df: bool = False):
        self.results = await self.process_url(self.url)

        if as_df:
            self.df = pd.DataFrame(self.results)
            self.df = self.df.fillna(value=np.nan)
            self.df["size"] = self.df["size"].str.replace(" sq. ft.", "").str.replace(",", "").astype("float64")
            self.df["value"] = (self.df.price / self.df["size"]).round(0)

            if self.filter_size:
                self.df = self.df[self.df["size"].notna()]
                self.df = self.df.sort_values("size", ascending=False)

            if self.filter_percentile:
                self.df = self.df[
                    (self.df["size"] > self.df["size"].quantile(self.filter_percentile / 100)) &
                    (self.df["size"] < self.df["size"].quantile((100 - self.filter_percentile) / 100))
                ]

            print(f"Median price: {self.df.price.median()}")
            print(f"Mean price: {self.df.price.mean()}")
            if self.filter_size:
                print(f"Median size: {self.df['size'].median()}")
                print(f"Mean size: {self.df['size'].mean()}")

            return self.df

        return self.results

    async def get(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def process_url(self, url: str, recurse: bool = True):
        result = await self.get(url)

        parsed = BeautifulSoup(result, "lxml")
        script_tags = parsed.find_all("script")
        json_raw = [i.string for i in script_tags if i.string and self._json_var in i.string][0]
        parsed_json = json.loads(json_raw.replace(f"{self._json_var} =", ""))

        properties = []
        for p in parsed_json["properties"]:
            properties.append(self.parse_property(p))

        if recurse:
            tasks = []
            for p in parsed_json["pagination"]["options"][1:]:
                tasks.append(self.process_url(f"{self.url}&index={p['value']}", recurse=False))

            task_results = await asyncio.gather(*tasks)
            properties.extend([r for result in task_results for r in result])

        return properties

    def parse_property(self, item: dict):
        return {
            "id": item["id"],
            "address": item["displayAddress"],
            "bedrooms": item["bedrooms"],
            "bathrooms": item["bathrooms"],
            "price": item["price"]["amount"],
            "size": item["displaySize"] or None,
            "url": f"{self._base_url}{item['propertyUrl']}",
        }


async def main():
    rm = Wrongmove(
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93953&maxBedrooms=1&minBedrooms=1&maxPrice=600000&minPrice=400000&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93953&maxBedrooms=2&minBedrooms=2&maxPrice=600000&minPrice=400000&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E61305&maxBedrooms=1&minBedrooms=1&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93965&maxBedrooms=1&minBedrooms=1&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        filter_size=True,
        filter_percentile=5,
    )
    result = await rm.fetch(as_df=True)

    # result = result[(result["price"] >= 400000) & (result["price"] <= 600000)]

    print("Sorted by size")
    print(result[:20])

    print("Sorted by value")
    print(result.sort_values("value")[:20])


if __name__ == "__main__":
    asyncio.run(main())
