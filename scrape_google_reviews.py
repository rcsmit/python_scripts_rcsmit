""" This script scrapes Google Maps Reviews. 
https://levelup.gitconnected.com/web-scrape-google-maps-reviews-with-playwright-for-free-7d6f42f1719d"""

import time
import os
import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from os import path
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import random
def read_json_as_dataframe(file_path):
    """
    Reads a JSON file from the given path and returns it as a pandas DataFrame.

    Args:
        path (str): The file path to the JSON file.

    Returns:
        pd.DataFrame: DataFrame containing the JSON data.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Parse each JSON object and append to the list
            data.append(json.loads(line))

    # Convert the list of JSON objects to a DataFrame
    df = pd.DataFrame(data)
    return df


async def check_json(response, output_path):
    """ This function is triggered when we get a response from the
    network and tackles the response containing 'listugcposts'.
    The text is converted to json, and the data is obtained. """

    if "listugcposts" in response.url:
        content = await response.text()
        content = content.split(")]}'\n")[1]

        # Parse the string as JSON
        data_raw = json.loads(content)
        data_raw = data_raw[2]

        def safe_extract(data, *path, default=None):
            try:
                for key in path:
                    data = data[key]
                return data
            except (IndexError, KeyError, TypeError):
                return default

        for i, element in enumerate(data_raw):
            timestamp = data_raw[i][0][1][6]
            # if 'year' not in timestamp and 'years' not in timestamp:
        
            data = {
                'review': safe_extract(
                    data_raw, i, 0, 2, 15, 0, 0),
                'rating': safe_extract(
                    data_raw, i, 0, 2, 0, 0),
                'source': safe_extract(
                    data_raw, i, 0, 1, 13, 0),
                'timestamp': safe_extract(
                    data_raw, i, 0, 1, 6),
                'language': safe_extract(
                    data_raw, i, 0, 2, 14, 0),
            }
            print (data)
            # Load existing data into a set to avoid duplicates
            existing_data = set()
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        existing_data.add(line.strip())

            new_data_json = json.dumps(
                data, ensure_ascii=False)

            if new_data_json not in existing_data:
                # Write the new data to the JSON file
                with open(output_path, 'a', encoding='utf-8') as file:
                    file.write(new_data_json + '\n')


async def main_google_reviews(search_input):
    """ This is the main function to scrape Google Reviews """

    # google's main URL
    # url = (
    #     "https://www.google.com/maps/@38.7156642,-9.1243907,16z?entry=ttu")
    #Chiang Mai
    url = (
        "https://www.google.com/maps/@18.7943903,98.8740742,16z?entry=ttu")

    #Koh Phangan
    url = (
        "https://www.google.com/maps/@9.7563241,99.9631365,16z?entry=ttu")


    # file path
    path = f"reviews_google_{search_input}.json"


    async with async_playwright() as pw:
        # creates an instance of the Chromium browser and launches it
        browser = await pw.chromium.launch(headless=False)
        # creates a new browser page (tab) within the browser instance
        page = await browser.new_page()

        # go to url with Playwright page element
        await page.goto(url)
        await page.mouse.wheel(0, 35000)
        # avoid cookies
        # page.locator("text='Reject all'").first.click()
        page.locator("text='Rifiuta tutto'").first.click()
        # write what you're looking for
        time.sleep(1)
        await page.fill("#searchboxinput", search_input)

        time.sleep(2)

        # press enter
        await page.locator("#searchboxinput").click()
        time.sleep(1)

        # select the first element in the list of options
        await page.keyboard.press('ArrowDown')
        await page.keyboard.press('Enter')

        # get tab with the reviews
        #await page.locator("text='Reviews'").first.click()
        await page.locator("text='Recensioni'").first.click()

        # search for most recent
        #await page.locator("text='Sort'").first.click()
        await page.locator("text='Ordina'").first.click()
        
        time.sleep(1)
        
        await page.keyboard.press('ArrowDown')
        time.sleep(1)
        
        await page.keyboard.press('Enter')

        for i in range(200):
            await page.mouse.wheel(0, 35000)
            # get a response
            page.on(
                "response",
                lambda response: asyncio.create_task(
                    check_json(response, path)))
            print(f'{i+1}/200 scrolling')
            time.sleep(1)

        # save to a csv file
        df = read_json_as_dataframe(path)
        df.to_csv(f'data/reviews_{search_input}.csv', index=False)

        await page.close(run_before_unload=True)

    # remove json file
    # os.remove(path)




# Function to convert the timestamp to the correct date
def convert_timestamp_to_date(timestamp):
    """
    Converts a timestamp string to a datetime object.

    Adapt the strings to your own language !

    Args:
        timestamp (str): A string representing the timestamp.

    Returns:
        datetime: The corresponding datetime object.
    """
    now = datetime.now() 

    if 'un anno fa' in timestamp:
        # Extract the number of years and determine the date as January 1st of that year
        years_ago = 1
        date = now - relativedelta(years=years_ago)

    elif 'anni fa' in timestamp:
        # Extract the number of years and subtract it from the current date
        years_ago = int(timestamp.split()[0])
        date = now - relativedelta(years=years_ago)

    elif 'mese fa' in timestamp or 'mesi fa' in timestamp:
        # Extract the number of months and subtract it from the current date
        months_ago = int(timestamp.split()[0])
        date = now - relativedelta(months=months_ago)
    else:
        # Default case if the format doesn't match (you can customize this)
        date = now
    
    return date



def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(33, 73%%, %d%%)" % random.randint(60, 100)
def wordcloud(df):
    """
    Reads the text in column 'review' where the language is 'en' and makes a wordcloud of it

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'review' (and 'language') column.

    Result:
        Wordcloud in svg and png format
    """
    # Read the whole text.
    # Filter the rows where 'language' is 'en' and concatenate the reviews
    text = " ".join(df[df['language'] == 'en']['review'].dropna().astype(str))   

    # adding movie script specific stopwords
    stopwords = set(STOPWORDS)
    stopword_list = ["und", "sehr", "die", "da", "ist"]
    for s in stopword_list:
        stopwords.add(s)
    
    wc = WordCloud(max_words=100, stopwords=stopwords,  margin=10,
                random_state=1).generate(text)
    # store default colored image
    default_colors = wc.to_array()
    plt.title("Wordcloud")
    plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
            interpolation="bilinear")
    
    # PNG
    wc.to_file(f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    
    # SVG
    # https://stackoverflow.com/questions/44715044/how-to-pass-a-python-wordcloud-element-to-svgwrite-method-to-generate-a-svg-of-t
    wordcloud_svg = wc.to_svg(embed_font=True)
    f = open(f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg","w+")
    f.write(wordcloud_svg )
    f.close()
    plt.axis("off")
   
    plt.show()
    
def calculate_ratings_per_year(df):
    """
    Calculates the number of ratings per year and prints the result.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'year' column.

    Returns:
        None
    """
    ratings_per_year = df.groupby('year')['rating'].count().reset_index().rename(columns={'rating': 'number_of_ratings'})
    print("Ratings per year:")
    print(ratings_per_year)

def calculate_average_rating_by_year(df):
    """
    Calculates the average rating per year and prints the result.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'year' column.

    Returns:
        None
    """
    average_rating_by_year = df.groupby('year')['rating'].mean().round(2).reset_index()
    print("Average rating by year:")
    print(average_rating_by_year)

def calculate_rating_distribution(df):
    """
    Calculates the distribution of ratings (absolute counts and percentages) per year and prints the results.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'year' column.

    Returns:
        None
    """
    rating_distribution = df.pivot_table(
        index='year',
        columns='rating',
        aggfunc='size',
        fill_value=0
    )
    rating_distribution = rating_distribution.reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
    rating_distribution_perc = round(rating_distribution.div(rating_distribution.sum(axis=1), axis=0) * 100, 2)
    print("Rating distribution (absolute counts):")
    print(rating_distribution)
    print("Rating distribution (percentages):")
    print(rating_distribution_perc)

def calculate_average_rating_last_12_months(df):
    """
    Calculates the average rating by month for the last 12 months and prints the result.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'date' column.

    Returns:
        None
    """
    last_12_months = df[df['date'] >= (datetime.now() - relativedelta(months=12))]
    last_12_months['month'] = last_12_months['date'].dt.to_period('M')
    average_rating_by_month = last_12_months.groupby('month')['rating'].mean().round(2).reset_index()
    print("Average rating by month (last 12 months):")
    print(average_rating_by_month)

def analyse(path):
    """
    Performs a comprehensive analysis of the data at the given path and prints various metrics.

    Args:
        path (str): The file path to the JSON data.

    Returns:
        None
    """
    df = read_json_as_dataframe(path)
    df['date'] = df['timestamp'].apply(convert_timestamp_to_date)
    df['year'] = df['date'].dt.year

    calculate_ratings_per_year(df)
    calculate_average_rating_by_year(df)
    calculate_rating_distribution(df)
    calculate_average_rating_last_12_months(df)
    wordcloud(df)
if __name__ == '__main__':
    # SEARCH_INPUT = "Goodsouls Kitchen - Vegan Restaurant"
    SEARCH_INPUT = "Kia Ora Café"
    
    #asyncio.run(main_google_reviews(SEARCH_INPUT))
    
    #path = f"reviews_google_{SEARCH_INPUT}.json"
    path = "reviews_google_goodsouls_kitchen.json"
    #path = "reviews_google_Kia Ora Café.json"
    analyse(path)
    