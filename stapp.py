import sys
import streamlit as st
from scripts.LOGIC_MAIN import scrape_and_update
from src.logger import logging

def main():
    st.title('Tender Data Scraping Application')

    number_of_links = st.number_input("How many links to scrape:", min_value=1, step=1)

    params_list = []
    for i in range(number_of_links):
        input_url = st.text_input(f'Paste the copied Link Address {i+1}:')
        input_end_page_number = st.number_input(f"Enter number of pages you want for Link {i+1}:", min_value=1, step=1)
        params_list.append((input_url, input_end_page_number))

    if st.button('Start Scraping'):
        logging.info(f"Scraping initiated for {params_list}")
        scrape_and_update(params_list)
        st.success("Scraping completed successfully!")
        
        
if __name__ == '__main__':
    main()
