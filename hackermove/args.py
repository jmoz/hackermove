import argparse
from argparse import Namespace


def load_args() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, help="Search url")
    parser.add_argument("--location", type=str, help="Location search string")
    parser.add_argument("--beds", default=None, type=int, help="Beds")
    parser.add_argument("--minbeds", default=None, type=int, help="Minimum beds")
    parser.add_argument("--maxbeds", default=None, type=int, help="Maximum beds")
    parser.add_argument("--minprice", default=None, type=int, help="Minimum price")
    parser.add_argument("--maxprice", default=None, type=int, help="Maximum price")
    parser.add_argument("--types", default=None, type=str, help="Property types, csv")
    parser.add_argument("--rows", default=20, type=int, help="Number of rows to display in table")
    args = parser.parse_args()
    return args
