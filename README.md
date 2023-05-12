# Hackermove

## Usage

### With url

Copy the url from a property listings page and pass it as the `url` param.

```python
hm = Hackermove(
    url="https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E93965&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false",
)
result = hm.fetch()
```

### With location

To search with a location string simply construct a `Query` object first and pass it as the `query` param. It will use the best result for the search which sometimes may not be the correct one.

```python
q = Query(
    location="Islington",
)
hm = Hackermove(
    query=q,
)
result = hm.fetch()
```


### Command line

Alternatively, you can use the command line to perform a search easily.

```
$ python -m hackermove -h
usage: __main__.py [-h] [--url URL] [--location LOCATION] [--beds BEDS] [--minbeds MINBEDS] [--maxbeds MAXBEDS] [--minprice MINPRICE] [--maxprice MAXPRICE] [--rows ROWS]

options:
  -h, --help           show this help message and exit
  --url URL            Search url
  --location LOCATION  Location search string
  --beds BEDS          Beds
  --minbeds MINBEDS    Minimum beds
  --maxbeds MAXBEDS    Maximum beds
  --minprice MINPRICE  Minimum price
  --maxprice MAXPRICE  Maximum price
  --rows ROWS          Number of rows to display in table
```

Simple search by location

```
$ python -m hackermove --location "Islington"
INFO:hackermove:Found location {'displayName': 'Islington (London Borough)', 'locationIdentifier': 'REGION^93965', 'normalisedSearchTerm': 'ISLINGTON LONDON BOROUGH'}
INFO:hackermove:Url: https://www.rightmove.co.uk/property-for-sale/find.html?dontShow=&furnishTypes=&includeSSTC=false&keywords=&locationIdentifier=REGION%5E93965&maxBedrooms=&maxPrice=&minBedrooms=&minPrice=&mustHave=&propertyTypes=&sortType=6
Latest
           id                                                     address  bedrooms  bathrooms    price    size                                                                 url                      date        property_type   value
1   134760656                                   College Cross, London, N1         1        1.0   395000   323.0  https://www.rightmove.co.uk/properties/134760656#/?channel=RES_BUY 2023-05-12 17:51:02+00:00            Apartment  1223.0
2   134758748                      St. Marys Grove, Islington, London, N1         3        1.0  1300000     NaN  https://www.rightmove.co.uk/properties/134758748#/?channel=RES_BUY 2023-05-12 17:24:03+00:00             Terraced     NaN
```

Simple search by url

```
$ python -m hackermove --url https://www.rightmove.co.uk/property-for-sale/find.html\?locationIdentifier\=REGION%5E93965\&maxBedrooms\=2\&minBedrooms\=2\&maxPrice\=600000\&sortType\=6\&propertyTypes\=\&includeSSTC\=false\&mustHave\=\&dontShow\=\&furnishTypes\=\&keywords\=
Latest
           id                                    address  bedrooms  bathrooms   price   size                                                                 url                      date property_type  value
1   134756045   Tufnell Mansions, Anson Road, London, N7         2        1.0  550000    NaN  https://www.rightmove.co.uk/properties/134756045#/?channel=RES_BUY 2023-05-12 16:54:03+00:00     Apartment    NaN
2   134752553              Mildmay Park, \nIslington, N1         2        1.0  600000    NaN  https://www.rightmove.co.uk/properties/134752553#/?channel=RES_BUY 2023-05-12 16:10:03+00:00          Flat    NaN
```