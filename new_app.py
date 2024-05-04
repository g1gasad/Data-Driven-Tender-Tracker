from scripts.LOGIC_MAIN import scrape_and_update

def main():
    number_of_links = int(input("How many links to scrape: "))
    
    if number_of_links == 1:
        single_url = input('Paste the copied Link Address: ')
        single_end_page_number = input("Enter the number of pages you want: ")
        scrape_and_update(single_url, single_end_page_number)
    
    else:
        url_list = []
        end_page_number_list = []
        for i in range(number_of_links):
            url = input(f'Paste the copied Link Address {i+1}: ')
            end_page_number = input("Enter number of pages you want: ")
            
            url_list.append(url)
            end_page_number_list.append(end_page_number)
            
        
if __name__=='__main__':
    main()   