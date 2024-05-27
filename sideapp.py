import os
import streamlit as st
from scripts.LOGIC_MAIN import scrape_and_update  # Ensure scrape_and_update returns required data
from src.logger import logging

# Function to load CSS file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the custom CSS
load_css("css/sidebar.css")

def main():
    st.title('Tender Data Scraping Application')

    with st.sidebar:
        st.header("Scraping Parameters")
        number_of_links = st.number_input("How many links to scrape:", min_value=1, step=1)

        params_list = []
        for i in range(number_of_links):
            input_url = st.text_input(f'Paste the copied Link Address {i+1}:')
            input_end_page_number = st.number_input(f"Enter number of pages you want for Link {i+1}:", min_value=1, step=1)
            params_list.append((input_url, input_end_page_number))
    
    if st.button('Start Scraping'):
        logging.info(f"Scraping initiated for {params_list}")
        
        with st.spinner('Scraping in progress...'):
            scraped_data_shape, old_data_shape, updated_data_shape, updated_data_stats = scrape_and_update(params_list)

        st.success("Scraping completed successfully!")

        st.write("### Scraping Summary")
        st.write(f"**Scraped Data Shape:** {scraped_data_shape}")
        st.write(f"**Old Data Shape:** {old_data_shape}")
        st.write(f"**Updated Data Shape:** {updated_data_shape}")

        st.write("### Updated Data Statistics")
        st.json(updated_data_stats)
        
            
if __name__ == '__main__':
    main()