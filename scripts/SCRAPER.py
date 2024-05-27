from tqdm import tqdm
from stqdm import stqdm
import requests
import ssl
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
ssl._create_default_https_context = ssl._create_unverified_context

SLEEP_TIME = float(os.getenv('SLEEP_TIME'))
UNKNOWN = "Unknown"
NA = "NA"
NOT_AVAILABLE = "Not Available"
# SLEEP_TIME = 0.3

def convert_contract_amount_to_numeric(x):
    unit_multiplier = {'K': 1e3, "Lac": 1e5, "Cr": 1e7}
    if "Documents" in x or UNKNOWN in x:
        return -99999
    for u, v in unit_multiplier.items():
        if u in x:
            try:
                numeric_value = float(x.split()[1])
                return round(numeric_value * v, 2)
            except ValueError:
                return -99999
    try:
        return round(float(x.split()[-1]), 2)
    except ValueError:
        return -99999

def standardize_tender_data(df):
    """
    This function standardizes the data in the dataframe.
    """
    def column_with_dash(column_string):
        return list(df.loc[df[column_string].str.contains("-")].index)
        
    city_with_dash = column_with_dash('City')
    state_with_dash = column_with_dash("State")
    indices_with_dash = list(set(city_with_dash + state_with_dash))
    
    indices_state_with_unknown = list(df.loc[(df['State'] == UNKNOWN) & (df['City'] != UNKNOWN)].index)
    indices_contract_with_NA = list(df.loc[df["Contract Amount"] == NA].index)

    for i in indices_with_dash:
        state_in_city_col = df.iloc[i, 5].split(' - ')[-1].strip()
        state_in_state_col = df.iloc[i, 9].split(' - ')[-1].strip()
        if state_in_city_col == state_in_state_col:
            state = state_in_city_col
            df.at[i, "City"] = 'Multi-City'
            df.at[i, "State"] = state
        else:
            df.at[i, "City"] = 'Multi-City'
            df.at[i, "State"] = "Multi-State"
    for i in indices_state_with_unknown:
        actual_state = df.iloc[i, 5].strip()
        df.at[i, 'State'] = actual_state
        df.at[i, 'City'] = UNKNOWN
    for i in indices_contract_with_NA:
        df.at[i, "Contract Amount"] = UNKNOWN
        
    df.replace(UNKNOWN, NOT_AVAILABLE, inplace=True)
    return df
    
def format_scraping_time(x):
    """
    This function formats the scraping time.
    """
    minute = x // 60
    second = x % 60
    if second == 0 or second == 1:
        if minute == 0 or minute == 1:
            return f'{minute} Minute {second} Second'
        else:
            return f'{minute} Minutes {second} Second'
    else:
        if minute == 0 or minute == 1:
            return f'{minute} Minute {second} Seconds'
        else:
            return f'{minute} Minutes {second} Seconds'
        
def generate_tender_page_urls(url, end_page_number):
    url = url.replace("?", "/tender-page-1?", 1)
    if end_page_number == 1:
        return [url]
    else:
        return [url.replace("1", str(i), 1) for i in range(1, end_page_number + 1)]

def parse_tender_tab_information(tab):
    """
    This function parses the tender tab information.
    """
    try:
        link = tab.find('a')
        if link:
            link_title = link.get('title')
            link_url = link['href']
        else:
            link_title = UNKNOWN
            link_url = UNKNOWN

        date_element = tab.find_all('span', class_='truncate textHeading')[0]
        amount_element = tab.find_all('span', class_='truncate textHeading')[1]
        location_element = tab.find('span', class_='truncate relative tender-locations')
        stage_element = tab.find('span', class_='info-chip-title m-r-15')
        categories_element = tab.find('span', class_='text-box')

        # Use a function to extract text safely, providing a default value if the element is not found.
        def get_text(element, default=UNKNOWN):
            return element.get_text() if element else default

        return {
            "Title": link_title,
            "URL": link_url,
            "Contract Date": get_text(date_element),
            "Contract Amount": get_text(amount_element),
            "Location": get_text(location_element),
            "Stage": get_text(stage_element),
            "Categories": get_text(categories_element)
            }
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def prepare_scraped_tender_data(df):
    df['Tender_ID'] = df['Title'].str.split(" - ").str[0].str.strip()
    
    df['Stage'] = df['Stage'].fillna(UNKNOWN)
    df['Stage'] = df['Stage'].str.split(":").str[-1].str.strip()
    df.loc[df['Stage'].str.contains('AOC'), 'Stage'] = 'AOC'
    
    df['Description'] = df['Title'].str.split(" - ").str[1]
    df['Description'] = df['Description'].fillna(UNKNOWN)
    df['Description'] = df['Description'].str.replace('', ' ')

    df["Contract Date"] = df["Contract Date"].fillna(UNKNOWN)
    
    df['Contract Amount'] = df['Contract Amount'].fillna(UNKNOWN)
    df['Contract Amount'] = df['Contract Amount'].str.strip()
    df['numeric_amount'] = df['Contract Amount'].apply(convert_contract_amount_to_numeric)

    df['City'] = df['Location'].str.split(',').str[0].str.strip()
    df["City"] = df['City'].fillna(UNKNOWN)
    df['State'] = df['Location'].str.split(',').str[1].str.strip()
    df["State"] = df['State'].fillna(UNKNOWN)
    
    df['Authority'] = df['URL'].str.split("/").str[5].str.replace("-", " ").str.title()
    df.drop(columns=['Title', 'Location'], axis=1, inplace=True)
    return df

def SCRAPE_WEBPAGE_TO_DF(url, end_page_number):
    """
    This function scrapes the webpage to a dataframe.
    """
    start = time.time()
    df = pd.DataFrame()
    end_page_number = int(end_page_number)

    tab_links = []
    for link in stqdm (generate_tender_page_urls(url, end_page_number),
                       ncols=100, colour="#30d18b", frontend=True, backend=True):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        time.sleep(SLEEP_TIME+0.7)
        tab_containers = soup.find_all('div', class_='block card clearfix')
        tab_links.extend(tab_containers)
        time.sleep(SLEEP_TIME)
        
    # data_list = [parse_tender_tab_information(tab) for tab in tqdm (tab_links, ncols=100, colour="#ffbe8e")
    #                              if (parse_tender_tab_information(tab), time.sleep(SLEEP_TIME))]
    
    data_list = []
    for tab in stqdm(tab_links, ncols=100, colour="#ffbe8e",
                     backend=True, frontend=True):
        data = parse_tender_tab_information(tab)
        time.sleep(SLEEP_TIME)
        data_list.append(data)
        
    data = pd.DataFrame(data_list)
    df = prepare_scraped_tender_data(data)
    column_order = ['Description', 'Authority', 'Stage', 'Contract Date', 'Contract Amount',
                    'City', 'URL', 'Tender_ID', 'numeric_amount', 'State', 'Categories']
    df = df[column_order]
    df = standardize_tender_data(df)
    end = time.time()
    time_elapsed = round(end - start)
    return df, time_elapsed