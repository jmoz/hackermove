import asyncio
import json
import logging
from datetime import datetime
from json import JSONDecodeError
from urllib.parse import urlencode

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from .http import get

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Query:
    def __init__(
        self,
        location: str,
        min_beds: int | None = None,
        max_beds: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ):
        self.location = location
        self.location_identifier = None
        self.min_beds = min_beds
        self.max_beds = max_beds
        self.min_price = min_price
        self.max_price = max_price
        self._search_base_url = "https://www.rightmove.co.uk/typeAhead/uknostreet/"
        self._base_url = "https://www.rightmove.co.uk/property-for-sale/find.html"
        self._n = 2

    async def get_location_identifier(self) -> str:
        """
        Split location search every 2 chars with /
        foobar -> fo/ob/ar
        :return:
        """
        query = "/".join([self.location.upper()[i: i + self._n] for i in range(0, len(self.location), self._n)])
        result = await get(self._search_base_url + query)

        try:
            result_json = json.loads(result)
        except JSONDecodeError as e:
            logger.error(f"Location not found: {e}")
            raise RuntimeError

        try:
            location = result_json["typeAheadLocations"][0]
            location_identifier = location["locationIdentifier"]
            logger.info(f"Found location {location}")
        except KeyError as e:
            logger.error(f"Error finding location: {e}", exc_info=True)
            raise RuntimeError

        return location_identifier

    async def get(self) -> str:
        """
        Get the location identifier first from the location search string, then construct a parameterised request
        from instance vars, then create the url.

        Output: https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93953&maxBedrooms=1&minBedrooms=1&maxPrice=600000&minPrice=400000&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=
        :return:
        """
        self.location_identifier = await self.get_location_identifier()

        params = {
            "locationIdentifier": self.location_identifier,
            "minBedrooms": self.min_beds or "",
            "maxBedrooms": self.max_beds or "",
            "minPrice": self.min_price or "",
            "maxPrice": self.max_price or "",
            "sortType": "6",  # Sort by newest so data is always fresh, but limited to max results from site
            "propertyTypes": "",
            "includeSSTC": "false",
            "mustHave": "",
            "dontShow": "",
            "furnishTypes": "",
            "keywords": "",
        }
        sorted_params = sorted(params.items(), key=lambda x: x[0])

        url = f"{self._base_url}?{urlencode(sorted_params)}"
        logger.info(f"Url: {url}")
        return url


class Hackermove:
    def __init__(
        self,
        url: str | None = None,
        query: Query | None = None,
        filter_size: bool = False,
        filter_percentile: int | bool = False,
    ):
        """
        Provide the url to process and filtering options.
        Instance vars can be overriden to update functionality.

        :param url:
        :param filter_size:
        :param filter_percentile:
        """
        self.url = url
        self.query = query
        self.filter_size = filter_size
        self.filter_percentile = filter_percentile
        self.results = None
        self.df = None

        self._json_var = "window.jsonModel"
        self._base_url = "https://www.rightmove.co.uk"

    def fetch(self, as_df: bool = False) -> list[dict] | pd.DataFrame:
        """
        Client code function so user doesn't need to mess with asyncio.

        :param as_df:
        :return:
        """
        return asyncio.run(self._fetch(as_df))

    async def _fetch(self, as_df: bool = False) -> list[dict] | pd.DataFrame:
        """
        Fetch and process the url then return either the data or dataframe and further filtering.

        :param as_df:
        :return:
        """
        if self.query:
            self.url = await self.query.get()

        self.results = await self.process_url(self.url)
        # remove duplicates by id
        self.results = list({x["id"]: x for x in self.results}.values())
        # sort the results desc by date (ordering could be wrong because of advertisements)
        self.results = sorted(self.results, key=lambda x: datetime.fromisoformat(x["date"]), reverse=True)

        if as_df:
            self.df = pd.DataFrame(self.results)
            self.df = self.clean_data(self.df)

            if self.filter_size:
                self.df = self.df[self.df["size"].notna()]

            if self.filter_percentile:
                self.df = self.df[
                    (self.df["size"] > self.df["size"].quantile(self.filter_percentile / 100))
                    & (self.df["size"] < self.df["size"].quantile((100 - self.filter_percentile) / 100))
                ]

            return self.df

        return self.results

    async def process_url(self, url: str, recurse: bool = True) -> list[dict]:
        """
        Fetch the url then process the html into data, optionally recurse for any more pages.

        :param url:
        :param recurse:
        :return:
        """
        result = await get(url)

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

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and add any fields to the dataframe of results.
        Extend and override this method to change functionality.

        :param data:
        :return:
        """
        data = data.fillna(value=np.nan)
        data = data[~data.duplicated()]
        data["date"] = pd.to_datetime(data["date"])
        try:
            # catch any errors for when small results with no size
            data["size"] = data["size"].str.replace(" sq. ft.", "").str.replace(",", "").astype("float64")
        except AttributeError:
            pass
        data["value"] = (data.price / data["size"]).round(0)
        return data

    def parse_property(self, item: dict) -> dict:
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
            "size": item["displaySize"] or self.parse_summary_size(item["summary"]) or None,
            "url": f"{self._base_url}{item['propertyUrl']}",
            "date": item["listingUpdate"]["listingUpdateDate"],
            "property_type": item["propertySubType"],
            "tenure": self.parse_summary_tenure(item["summary"]),
        }

    def parse_summary_size(self, summary: str) -> int:
        """
        We may be able to parse the size from the summary intro text.
        Extend and override this method to change functionality.

        :param summary:
        :return:
        """
        pass

    def parse_summary_tenure(self, summary: str) -> str | None:
        """
        We may be able to parse the tenure from the summary intro text.

        :param summary:
        :return:
        """
        if "lease" in summary:
            return "Leasehold"
        elif "freehold" in summary:
            return "Freehold"
        else:
            return None
