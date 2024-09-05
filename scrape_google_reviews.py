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

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

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
            print (data_raw)
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
            #               i
            # time stap 0 > 0 > 0 > 1 > 6

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
    path = f"reviews_google_{search_input}__{timestamp}.json"

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
        time.sleep(1)
        await page.mouse.wheel(0, 35000)
        time.sleep(1)
        # search for most recent
        #await page.locator("text='Sort'").first.click()
        await page.locator("text='Ordina'").first.click()
        
        time.sleep(1)
        #await page.locator("text='Valutazione più bassa'").first.click()
        
        await page.keyboard.press('ArrowDown') # newest
        time.sleep(1)
        await page.keyboard.press('ArrowDown') #highest rating
        time.sleep(1)
        await page.keyboard.press('ArrowDown') #lowest rating
        
        time.sleep(1)
        
        await page.keyboard.press('Enter')
        time.sleep(1)
        n=4
        for i in range(n):
            await page.mouse.wheel(0, 35000)
            # get a response
            page.on(
                "response",
                lambda response: asyncio.create_task(
                    check_json(response, path)))
            print(f'{i+1}/{n} scrolling')
            time.sleep(1)

        # save to a csv file
        df = read_json_as_dataframe(path)
        df.to_csv(f'data/reviews_{search_input}.csv', index=False)
        time.sleep(1)
        await page.close(run_before_unload=True)
        time.sleep(1)
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
        # Extract the number of years (1) and subtract it from the current date
        years_ago = 1
        date = now - relativedelta(years=years_ago)

    elif 'anni fa' in timestamp:
        # Extract the number of years and subtract it from the current date
        years_ago = int(timestamp.split()[0])
        date = now - relativedelta(years=years_ago)
    elif 'settimane fa' in timestamp :
        # Extract the number of months and subtract it from the current date
        weeks_ago = int(timestamp.split()[0])
        date = now - relativedelta(weeks=weeks_ago)
    elif  'settimana fa' in timestamp:
        # Extract the number of months and subtract it from the current date
        weeks_ago = 1
        date = now - relativedelta(weeks=weeks_ago)

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
    """
    Generates a color for a word based on its position and font size, using a grey scale.

    Args:
        word (str): The word to be colored.
        font_size (int): The font size of the word.
        position (tuple): The (x, y) position of the word in the visualization.
        orientation (str): The orientation of the word (e.g., horizontal, vertical).
        random_state (int, optional): Seed for the random number generator (default is None).
        **kwargs: Additional keyword arguments.

    Returns:
        str: A color in HSL (Hue, Saturation, Lightness) format with varying lightness for grey scale.
    """
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
    
def update_column_names(df):
    """
    Updates column names by replacing 'x' with 'abs' and 'y' with 'perc'.
    
    Args:
        df (pd.DataFrame): The DataFrame whose column names need to be updated.
    
    Returns:
        pd.DataFrame: The DataFrame with updated column names.
    """
    # Create a dictionary for renaming columns
    rename_dict = {col: col.replace('x', 'abs').replace('y', 'perc') for col in df.columns}
    
    # Rename the columns
    df = df.rename(columns=rename_dict)
    
    return df

def calculate_ratings_and_averages_per_period(df, index_column):
    """
    Calculates both the number of ratings per year and the average rating per year,
    then combines these metrics into a single DataFrame and prints the result.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with 'year' and 'rating' columns.

    Returns:
        pd.DataFrame: A DataFrame containing the number of ratings and the average rating per year.
    """

    # Calculate the number of ratings per year
    ratings_per_period = df.groupby(index_column)['rating'].count().reset_index().rename(columns={'rating': 'number_of_ratings'})
    
    # Calculate the average rating per year
    average_rating_by_year = df.groupby(index_column)['rating'].mean().round(2).reset_index().rename(columns={'rating': 'average_rating'})
    
    # Merge the two results into a single DataFrame
    combined_table = pd.merge(ratings_per_period, average_rating_by_year, on=index_column)
    combined_table = update_column_names(combined_table)
    
    # Print the result
    print(f"Combined ratings and averages per {index_column}:")
    print(combined_table)
    
def calculate_rating_distribution(df, index_column):
    """
    Calculates the distribution of ratings (absolute counts and percentages) per year and prints the results.

    Args:
        df (pd.DataFrame): The DataFrame containing the data with a 'year' column.
        index_column : 'year' | 'month'

    Returns:
        None
    """

    rating_distribution = df.pivot_table(
        index=index_column,
        columns='rating',
        aggfunc='size',
        fill_value=0
    )
    rating_distribution = rating_distribution.reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
    rating_distribution_perc = round(rating_distribution.div(rating_distribution.sum(axis=1), axis=0) * 100, 2)
    
    # Add a 'total' column with the sum of ratings for each row
    rating_distribution['total'] = rating_distribution.sum(axis=1)

    combined_table = pd.merge(rating_distribution, rating_distribution_perc, on=index_column)
    combined_table = update_column_names(combined_table)
    
    # Print the result
    print(f"Ratings distributions, absolute and percentage, per {index_column}:")
    print(combined_table)

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
    df['month'] = df['date'].dt.to_period('M')
    print (df)
    calculate_ratings_and_averages_per_period(df, 'year')
    calculate_rating_distribution(df, 'year')

    #df = df[df['date'] >= (datetime.now() - relativedelta(months=12))].copy()
    calculate_ratings_and_averages_per_period(df, 'month')
    calculate_rating_distribution(df, 'month')
    wordcloud(df)

def main():
    #RETRIEVE
    # SEARCH_INPUT = "Goodsouls Kitchen - Vegan Restaurant"
    SEARCH_INPUT = "Kia Ora Café"
    SEARCH_INPUT = "Gummy Bear Restaurant Thai food and Vegan food"
    
    asyncio.run(main_google_reviews(SEARCH_INPUT))
    
    # ANALYSE
    #path = f"reviews_google_{SEARCH_INPUT}.json"

    #path = f"reviews_google_goodsouls_kitchen_{timestamp}.json"
    #path = f"reviews_google_Kia Ora Café_{timestamp}.json"
    path = f"reviews_google_{SEARCH_INPUT}_{timestamp}.json"
    path = "reviews_google_Gummy Bear Restaurant Thai food and Vegan food__20240818_230759.json"
    # path = "reviews_google_Kia Ora Café__20240818_225641.json"
    analyse(path)
    
if __name__ == '__main__':
    main()