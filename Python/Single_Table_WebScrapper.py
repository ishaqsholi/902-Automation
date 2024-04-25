import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(webdriver_path):
    """Setup Firefox WebDriver."""
    service = FirefoxService(executable_path=webdriver_path)
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')  # Run in headless mode if you don't need a browser UI
    return webdriver.Firefox(service=service, options=options)

def scrape_table(table):
    """Scrape data from a single table."""
    headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, 'th')]
    rows = table.find_elements(By.CSS_SELECTOR, 'tr')[1:]  # Skip header row
    table_data = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        row_data = {header: cell.text.strip() for header, cell in zip(headers, cells)}
        table_data.append(row_data)
    return table_data

def test_scrape_webpage(driver, url):
    """Scrape the webpage and print outputs for diagnostics."""
    print("Navigating to:", url)
    driver.get(url)
    
    # Wait for the page to load dynamically if needed
    time.sleep(5)  # Adjust based on the observed load time of the page

    # Initialize a list to hold all scraped data
    all_data = []
    current_page = 0

    while True:
        current_page += 1
        print(f"Scraping Page {current_page}")
        
        # Process all tables on the current page
        try:
            tables = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table')))
            print(f"Found {len(tables)} table(s) on the current page.")

            for index, table in enumerate(tables):
                table_data = scrape_table(table)
                if table_data:
                    all_data.extend(table_data)
                    df = pd.DataFrame(table_data)
                    print("Extracted Data from Table", index+1, "on Page", current_page)
                    print(df)
                else:
                    print("No data extracted from Table", index+1, "on Page", current_page)

        except TimeoutException:
            print("Timed out waiting for tables to be present.")
        except Exception as e:
            print("An error occurred while processing tables:", e)

        # Find the 'Next' button and click it, or break if not found
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button.next, a.next')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)  # Wait for the next page to load
            else:
                print("Next button disabled, no more pages.")
                break
        except NoSuchElementException:
            print("No next page button found, stopping.")
            break
        except Exception as e:
            print("An error occurred while navigating pages:", e)
            break

def main(webdriver_path, url):
    """Main function to control the scraping process."""
    driver = setup_driver(webdriver_path)
    try:
        test_scrape_webpage(driver, url)
    finally:
        driver.quit()

if __name__ == "__main__":
    webdriver_path = 'path_to_your_geckodriver'  # Update this path
    url = 'Website with the table'  # Example URL with multiple pages
    main(webdriver_path, url)
