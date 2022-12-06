import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from selenium.webdriver.chrome.options import Options
import json
import numpy as np

options = Options()
options.headless = True

path = 'C:\Program Files\chromedriver.exe'
driver = webdriver.Chrome(path)
path_usernames ='C:/Users/Aida/Documents/MIS/Courses/CS520- Causal Inference/Project/code"'

profiles = pd.read_csv("l0.csv")
profile_links = list(profiles['user_url_review'])

profiles['reviews'] = None


# collect Profile information
def collect_profile_info(link: str) -> dict:
    driver.get(link)
    item_links= []
    error = False

    while error is False:

        user_profile = driver.find_element(By.CLASS_NAME, value='Dsdjn').text
        firstname = driver.find_element(By.CLASS_NAME, value='OUDwj').text

        table_cells = driver.find_element_by_xpath("//*[contains(text(), 'BTPVX')]")
        #current_page = table_cells[-1].find_element_by_tag_name('b').text
        #table = driver.find_element_by_class_name('forumsearchresults')
        #rows = table.find_elements_by_class_name('topofgroup')
        #print(f'found {len(rows)} links on page {current_page}')

        for i in table_cells:
            i.click()

        try:
            next_button = table_cells[-1].find_element_by_xpath("//*[contains(text(), 'Next')]")
            review = driver.find_element(By.CLASS_NAME, value="fullText").text


            review_date = driver.find_element(By.CLASS_NAME, value='ratingDate').text
            review_rate = driver.find_element(By.CLASS_NAME, value='ui_bubble_rating').text
            review_title = driver.find_element(By.CLASS_NAME, value='title').text
            stay_date = driver.find_element(By.CLASS_NAME, value="stay_date_label").text
            hotelname = driver.find_element(By.CLASS_NAME, value="altHeadInline").text

            next_button.click()
            time.sleep(1)

        except NoSuchElementException:
            print('No further page to scrape.')
            error = True
            user_profile = None
            firstname= None
            review_date = None
            review_title= None
            review_rate= None
            review= None
            stay_date= None
            hotelname= None

    return dict(user_profile= user_profile, firstname= firstname, review_date= review_date, review_title= review_title,
                review_rate= review_rate, review= review, stay_date=stay_date, hotelname=hotelname)



profiles['user_url_review'][2]

driver.get(profiles['user_url_review'][2])

table_cells = driver.find_element("xpath", "//*[contains('BTPVX')]")

for i in table_cells:
    i.click()

review = driver.find_element(By.CLASS_NAME, value="fullText").text

user_profile = driver.find_element(By.CLASS_NAME, value='Dsdjn').text
user_profile

firstname= driver.find_element(By.CLASS_NAME, value='OUDwj').text
firstname

review_date = driver.find_element(By.CLASS_NAME, value='VrCoN').text
review_date

review_rate = driver.find_element(By.CLASS_NAME, value='ui_bubble_rating ').text
review_rate

review_title = driver.find_element(By.CLASS_NAME, value='AzIrY').text
review_title

stay_date = driver.find_element(By.CLASS_NAME, value="Ci").text
stay_date

review = driver.find_element(By.CLASS_NAME, value="BTPVX").text
review





def collect_threatened_reviews(browser):
    # collect all the links  to all the forum posts
    item_links = []
    error = False
    while error is False:
        table_cells = browser.find_elements_by_tag_name('td')
        current_page = table_cells[-1].find_element_by_tag_name('b').text
        table = browser.find_element_by_class_name('forumsearchresults')
        rows = table.find_elements_by_class_name('topofgroup')
        print(f'found {len(rows)} links on page {current_page}')
        for i in rows:
            item_links.append(i.find_element_by_tag_name('a').get_attribute('href'))

        try:
            next_button = table_cells[-1].find_element_by_xpath("//*[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(1)

        except NoSuchElementException:
            print('No further page to scrape.')
            error = True

    pd.DataFrame(item_links, columns=[f'review_{file}_link']).to_csv(f'Review {file} Links.csv', index=False)
    # iterate over the links and collect the text of the review threats
    with open(f'{file}.csv', newline='', mode='a') as csvfile:
        link_reader = csv.writer(csvfile, delimiter='|', quotechar='"')
        header = ['review_title', 'review_text', 'review_date', 'author',
                  'user_profile', ]
        link_reader.writerow(header)
        for item_link in item_links:
            browser.get(item_link)

            # locate the main post and collect all the information.
            review_box = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CLASS_NAME,
                                                                                         "firstPostBox")))
            print(f'Review {item_links.index(item_link)}: {item_link}')
            row = [
                get_title(review_box),  # post_title
                get_text(review_box),  # post_text
                get_date(review_box),  # post_date
                get_author(review_box),  # author
                get_author_profile(review_box)  # user_profile
            ]

            link_reader.writerow(row)
    browser.close()



if __name__ == '__main__':

    driver = get_browser()
    driver.get(args.url)

    if args.collect_authors:
        collect_authors(driver)
    else:
        collect_threatened_reviews(driver)
