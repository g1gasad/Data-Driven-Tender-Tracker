import os
from dotenv import load_dotenv
import sys
import pandas as pd
from src.logger import logging
from src.exception import CustomException
from scripts.GOOGLE import Create_Service
from scripts.SCRAPER import SCRAPE_WEBPAGE_TO_DF
from scripts.SHEET_SCRAMBLER import PUSH_DATA_TO_SHEET
from scripts.SHEET_SCRAMBLER import FETCH_OLD_DATA
from scripts.SHEET_SCRAMBLER import VALIDATE_AND_UPDATE
# from scripts.SCRAPER import format_scraping_time
from datetime import datetime

load_dotenv()

today = str(datetime.today())
CLIENT_SECRET_FILE = 'secrets/credentials.json'
API_NAME = os.getenv('API_NAME')
API_VERSION = os.getenv('API_VERSION')
SCOPES = [os.getenv('SCOPES')]
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)   
CATALYST_SPREADSHEET_ID = os.getenv('CATALYST_SPREADSHEET_ID')
AUTOMATION_SPREADSHEET_ID = os.getenv('AUTOMATION_SPREADSHEET_ID')


def scrape_and_update(params_list):
    for i, (url, end_page_number) in enumerate(params_list):
        if i == 0:
            try:
                SCRAPED_DF, _ = SCRAPE_WEBPAGE_TO_DF(url, end_page_number)
            except Exception as e:
                raise CustomException(e, sys)
            logging.info("Finished scraping data from first URL")
            
        else:
            print()
            try:
                NEXT_SCRAPED_DF, _ = SCRAPE_WEBPAGE_TO_DF(url, end_page_number)
                SCRAPED_DF = pd.concat([SCRAPED_DF, NEXT_SCRAPED_DF], axis=0, ignore_index=True)
            except Exception as e:
                raise CustomException(e, sys)
            
            logging.info("Finished scraping and concatenating NEXT data from URL")
    logging.info("Scraping Done")
    # print(format_scraping_time(time_elapsed))
    print(f"Scraped data shape: {SCRAPED_DF.shape}")
    
    current_time = datetime.now().hour, datetime.now().minute
    scraped_filename = f"scraped {today.split()[0]} {current_time}, Rows {SCRAPED_DF.shape[0]}.xlsx"
    file_path = os.path.join('data/scraped', scraped_filename)
    
    try:
        SCRAPED_DF.to_excel(file_path, index=False)
    except Exception as e:
        raise CustomException(e, sys)
    
    logging.info('Converted the scraped data into excel')
    
    try:
        PUSH_DATA_TO_SHEET(SERVICE=service, 
                            SPREADSHEET_ID=CATALYST_SPREADSHEET_ID,
                            DATAFRAME=SCRAPED_DF, 
                            WORKSHEET_NAME_STRING="New")
    except Exception as e:
        raise CustomException(e, sys)
    
    try:
        old_df = FETCH_OLD_DATA(service, CATALYST_SPREADSHEET_ID, "Old")
        pulled_file_path = os.path.join('data/pull',
                                        f"pulled {today.split()[0]} {current_time}, Rows {old_df.shape[0]}.xlsx")
        old_df.to_excel(pulled_file_path, index=False)
        print(f"Old data shape: {old_df.shape}")
        
        logging.info("Pulled old data as excel file")
        
    except Exception as e:
        raise CustomException(e, sys)
    
    try:
        UPDATED_DF = VALIDATE_AND_UPDATE(OLD_DATAFRAME=old_df, SCRAPED_DATAFRAME=SCRAPED_DF)
        print('Updated data shape:', UPDATED_DF.shape)
        updated_data_stats = UPDATED_DF['Updated'].value_counts().reset_index(drop=False)
        print(updated_data_stats)

        logging.info(f"{updated_data_stats}")
        
        updated_file_path = os.path.join('data/push', 
                                         f"updated {today.split()[0]} {current_time}, Rows {UPDATED_DF.shape[0]}.xlsx")
        UPDATED_DF.to_excel(updated_file_path, index=False)
        
        logging.info("Final data ready to push")

        PUSH_DATA_TO_SHEET(SERVICE=service,
                            SPREADSHEET_ID=CATALYST_SPREADSHEET_ID, 
                            DATAFRAME=UPDATED_DF, 
                            WORKSHEET_NAME_STRING="Updated")
    except Exception as e:
        raise CustomException(e, sys)
    
