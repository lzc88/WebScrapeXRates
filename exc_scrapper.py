from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import os

# function to get link
exc_link = "https://www.x-rates.com/historical/?from=CURR&amount=1&date=YYYYMMDD"
def generate_link( base, currency, date ):
    return base.replace("CURR",currency).replace("YYYYMMDD",date)

# function to scrape by day
def daily_exc( cur, dateobj ):
    
    # format and extract date
    date = dateobj.strftime( "%Y-%m-%d" )
    yyyy = dateobj.year
    mm = dateobj.month
    dd = dateobj.day

    # http req using link for specified currency and date
    exc_day = generate_link( exc_link, cur, date )
    reqday = requests.get( exc_day )
    soupday = BeautifulSoup( reqday.content, "html.parser" )

    # exclude top 10 currencies else they will be repeated
    all_exc = soupday.select( "td a" )[20:]
    relev_exc = { "year" : yyyy, "month" : mm, "day" : dd }

    for exc in all_exc:
        if f'from={cur}' in exc.get("href"):
            href = exc.get( "href" )
            to_cur = href.split( sep = "to=" )[1]
            relev_exc[f'{cur} to {to_cur}'] = [exc.getText()]

    return pd.DataFrame(relev_exc)

# function to scrape by year
def yearly_exc( cur, year ):

    start_d = datetime.date( year, 1, 1 )
    end_d = datetime.date( year, 12, 31 )

    final = pd.DataFrame()

    while start_d <= end_d:

        exc_day = daily_exc( cur, start_d )
        final = pd.concat([final, pd.DataFrame(exc_day)])

        start_d += datetime.timedelta( days=1 )

    return final

# scrape and save to current directory as .xlsx file
# indicate desired currency, type (daily/yearly), start/end date
# data available only for the past decade e.g. currently 2023, earliest available date is 01-01-2023

currency = "CNY"
type = "yearly"
# daily
year = 2016
month = 2
day = 16
# yearly
start = 2022
end = 2023

# !!! will take some time to run
if type=="yearly":
    with pd.ExcelWriter(f'./{currency} Exchange Rates {start}-{end}.xlsx', engine="openpyxl", mode="w") as writer:
        for year in range( start, end ):
            exc_year = yearly_exc( currency, year )
            exc_year.to_excel( writer, sheet_name = f'{currency} {year}', index = False )
    print("Saved")
else:
    exc_day = daily_exc(currency, datetime.date(year, month, day))
    with pd.ExcelWriter(f'./{currency} Exchange Rates {year}-{month}-{day}.xlsx', engine="openpyxl", mode="w") as writer:
        exc_day.to_excel( writer, sheet_name = f'{currency} {year}-{month}-{day}', index = False )
    print("Saved")