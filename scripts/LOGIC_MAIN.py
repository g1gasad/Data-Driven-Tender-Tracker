import os
import sys
from src.logger import logging
from src.exception import CustomException
from scripts.GOOGLE import Create_Service
from scripts.SCRAPER import SCRAPE_WEBPAGE_TO_DF
from scripts.SHEET_SCRAMBLER import PUSH_DATA_TO_SHEET
from scripts.SHEET_SCRAMBLER import FETCH_DATA
from scripts.SHEET_SCRAMBLER import VALIDATE_AND_UPDATE
from scripts.SCRAPER import format_scraping_time
from datetime import datetime

today = str(datetime.today())
CLIENT_SECRET_FILE = 'secrets/credentials.json'
API_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)   
CATALYST_SPREADSHEET_ID = '1sqQf7PtC5j4aMtYdKS4uD-ypmvuNGkP7TeQHtGENZcs'
AUTOMATION_SPREADSHEET_ID = '120Ae4G5aBSP3mTXaSrIyqt0bC__lFRzgLFVdhHc6wN4'
SLEEP_TIME = 0.3


def scrape_and_update(url, end_page_number):
    try:
        SCRAPED_DF, time_elapsed = SCRAPE_WEBPAGE_TO_DF(url, end_page_number, SLEEP_TIME)
        print(format_scraping_time(time_elapsed))
        print(f"Scraped data shape: {SCRAPED_DF.shape}")
        logging.info("Scraping Done")
        current_time = datetime.now().hour, datetime.now().minute
        scraped_filename = f"scraped {today.split()[0]} {current_time}, Rows {SCRAPED_DF.shape[0]}.xlsx"
        file_path = os.path.join('data/scraped', scraped_filename)
        SCRAPED_DF.to_excel(file_path, index=False)
        logging.info('Converted the scraped data into excel')
        
    except Exception as e:
        raise CustomException(e, sys)   
    
    try:
        PUSH_DATA_TO_SHEET(SERVICE=service, 
                            SPREADSHEET_ID=CATALYST_SPREADSHEET_ID,
                            DATAFRAME=SCRAPED_DF, 
                            WORKSHEET_NAME_STRING="New")

        old_df, new_df = FETCH_DATA(service, CATALYST_SPREADSHEET_ID, "Old", "New")
        pulled_file_path = os.path.join('data/pull', f"pulled {today.split()[0]} {current_time}.xlsx")
        old_df.to_excel(pulled_file_path, index=False)
        print(f"Old data shape: {old_df.shape}")
        logging.info("Pulled old data as excel file")
        
    except Exception as e:
        raise CustomException(e, sys)
    
    try:
        UPDATED_DF = VALIDATE_AND_UPDATE(OLD_DATAFRAME=old_df, NEW_DATAFRAME=new_df)
        print('Updated data shape: ', UPDATED_DF.shape)
        print(UPDATED_DF['Updated'].value_counts().reset_index(drop=False))

        updated_file_path = os.path.join('data/push', f"updated {today.split()[0]} {current_time}.xlsx")
        UPDATED_DF.to_excel(updated_file_path, index=False)
        
        logging.info("Final data ready to push")

    # PUSH_DATA_TO_SHEET(SERVICE=service,
    #                     SPREADSHEET_ID=AUTOMATION_SPREADSHEET_ID, 
    #                     DATAFRAME=UPDATED_DF, 
    #                     WORKSHEET_NAME_STRING="DF")
    except Exception as e:
        raise CustomException(e, sys)
    
