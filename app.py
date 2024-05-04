from scripts.LOGIC_MAIN import scrape_and_update
from src.logger import logging

def main():
    number_of_links = int(input("How many links to scrape: "))
    print()
    params_list = []
    for i in range(number_of_links):
        input_url = input(f'Paste the copied Link Address {i+1}: ')
        print()
        input_end_page_number = input("Enter number of pages you want: ")
        print()
        params_list.append((input_url, input_end_page_number))
        
    logging.info(f"{params_list}")
    scrape_and_update(params_list)           
        
if __name__=='__main__':
    main()