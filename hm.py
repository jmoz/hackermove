import pandas as pd
from hackermove import Hackermove, Query

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.min_rows', 20)
pd.set_option('display.width', None)

LOCATIONS = {
    "Hackney": "REGION%5E93953",
    "Islington": "REGION%5E93965",
}


def main():
    q = Query(
        location="Walthamstow",
        min_beds=2,
        max_beds=2,
        min_price=350000,
        max_price=650000,
    )

    hm = Hackermove(
        query=q,
        filter_size=False,
        filter_percentile=False,
    )
    result = hm.fetch(as_df=True)

    # result = result[(result["price"] >= 400000) & (result["price"] <= 600000)]

    print("Latest")
    print(result.sort_values("date", ascending=False)[:10])

    print("Most expensive")
    print(result.sort_values("price", ascending=False)[:10])

    print("Least expensive")
    print(result.sort_values("price")[:10])

    print("Sorted by size")
    print(result.sort_values("size", ascending=False)[:20])

    print("Sorted by value")
    print(result.sort_values("value")[:20])

    print(f"Total results: {result.size}")
    print(f"Median price: {result.price.median()}")
    print(f"Mean price: {result.price.mean()}")
    if hm.filter_size:
        print(f"Median size: {result['size'].median()}")
        print(f"Mean size: {result['size'].mean()}")


if __name__ == "__main__":
    main()
