import pandas as pd

from hackermove import Hackermove, Query
from hackermove.args import load_args

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.min_rows", 20)
pd.set_option("display.width", None)

LOCATIONS = {
    "Hackney": "REGION%5E93953",
    "Islington": "REGION%5E93965",
}


def main() -> None:
    args = load_args()

    if args.url:
        url = args.url
        q = None
    elif args.location:
        url = None
        q = Query(
            location=args.location,
            min_beds=args.minbeds or args.beds,
            max_beds=args.maxbeds or args.beds,
            min_price=args.minprice,
            max_price=args.maxprice,
        )
    else:
        raise RuntimeError("Must specify a url or location")

    hm = Hackermove(
        url=url,
        query=q,
        filter_size=False,
        filter_percentile=False,
    )
    result = hm.fetch(as_df=True)

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

    print(f"Total results: {len(result)}")
    print(f"Median price: {result.price.median()}")
    print(f"Mean price: {result.price.mean()}")
    if hm.filter_size:
        print(f"Median size: {result['size'].median()}")
        print(f"Mean size: {result['size'].mean()}")


if __name__ == "__main__":
    main()
