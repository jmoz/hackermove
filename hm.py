import pandas as pd
from hackermove import Hackermove

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.min_rows', 20)
pd.set_option('display.width', None)

LOCATIONS = {
    "Hackney": "REGION%5E93953",
    "Islington": "REGION%5E93965",
}


def main():
    hm = Hackermove(
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93953&maxBedrooms=1&minBedrooms=1&maxPrice=600000&minPrice=400000&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93953&maxBedrooms=2&minBedrooms=2&maxPrice=600000&minPrice=400000&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        # "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E61305&maxBedrooms=1&minBedrooms=1&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93965&maxBedrooms=1&minBedrooms=1&sortType=6&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=",
        filter_size=True,
        filter_percentile=5,
    )
    result = hm.fetch(as_df=True)

    # result = result[(result["price"] >= 400000) & (result["price"] <= 600000)]

    print("Most expensive")
    print(result.sort_values("price", ascending=False)[:10])

    print("Least expensive")
    print(result.sort_values("price")[:10])

    print("Sorted by size")
    print(result[:20])

    print("Sorted by value")
    print(result.sort_values("value")[:20])

    print(f"Median price: {result.price.median()}")
    print(f"Mean price: {result.price.mean()}")
    if hm.filter_size:
        print(f"Median size: {result['size'].median()}")
        print(f"Mean size: {result['size'].mean()}")


if __name__ == "__main__":
    main()
