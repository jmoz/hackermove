import asyncio
import json

import aiohttp
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


class Hackermove:
    def __init__(self, url, filter_size: bool = False, filter_percentile: int | bool = False):
        """
        Provide the url to process and filtering options.
        Instance vars can be overriden to update functionality.

        :param url:
        :param filter_size:
        :param filter_percentile:
        """
        self.url = url
        self.filter_size = filter_size
        self.filter_percentile = filter_percentile
        self.results = None
        self.df = None

        self._json_var = "window.jsonModel"
        self._base_url = "https://www.rightmove.co.uk"

    def fetch(self, as_df: bool = False):
        """
        Client code function so user doesn't need to mess with asyncio.

        :param as_df:
        :return:
        """
        return asyncio.run(self._fetch(as_df))

    async def _fetch(self, as_df: bool = False):
        """
        Fetch and process the url then return either the data or dataframe and further filtering.

        :param as_df:
        :return:
        """
        self.results = await self.process_url(self.url)

        if as_df:
            self.df = pd.DataFrame(self.results)
            self.df = self.clean_data(self.df)

            if self.filter_size:
                self.df = self.df[self.df["size"].notna()]

            if self.filter_percentile:
                self.df = self.df[
                    (self.df["size"] > self.df["size"].quantile(self.filter_percentile / 100)) &
                    (self.df["size"] < self.df["size"].quantile((100 - self.filter_percentile) / 100))
                ]

            return self.df

        return self.results

    async def get(self, url: str):
        """
        GET url using aiohttp.

        :param url:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def process_url(self, url: str, recurse: bool = True):
        """
        Fetch the url then process the html into data, optionally recurse for any more pages.

        :param url:
        :param recurse:
        :return:
        """
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

    def clean_data(self, data: pd.DataFrame):
        """
        Clean and add any fields to the dataframe of results.
        Extend and override this method to change functionality.
        
        :param data: 
        :return: 
        """
        data = data.fillna(value=np.nan)
        data["size"] = data["size"].str.replace(" sq. ft.", "").str.replace(",", "").astype("float64")
        data["value"] = (data.price / data["size"]).round(0)
        return data

    def parse_property(self, item: dict):
        """
        Parse each of the property item data we receive. Not all data is used atm.
        Extend and override this method to change functionality.

        :param item: 
        :return: 
        """
        return {
            "id": item["id"],
            "address": item["displayAddress"],
            "bedrooms": item["bedrooms"],
            "bathrooms": item["bathrooms"],
            "price": item["price"]["amount"],
            "size": item["displaySize"] or None,
            "url": f"{self._base_url}{item['propertyUrl']}",
        }
