from scripts.LOGIC_MAIN import scrape_and_update

def main():
    url = input('Paste the copied Link Address of the Page:')
    end_page_number = input("Enter the number of pages you want:")
    scrape_and_update(url, end_page_number)   
    
if __name__=='__main__':
    main()