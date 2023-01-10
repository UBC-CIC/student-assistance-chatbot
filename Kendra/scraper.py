from selenium import webdriver
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
op = webdriver.ChromeOptions()
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import os
URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea"
SELECTOR = ".table.table-striped > tbody > tr > td > a"
BASE_DIRECTORY = "./classes/"
REGEX = "^.*dept=([^&]*)&course=([^&]*)&section=([^&]*)"

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = uc.Chrome(options=chrome_options)

def scrape(url):
    driver.get(url)
    subjBox = driver.find_elements(By.CSS_SELECTOR, SELECTOR)
    urls = []
    for subj in subjBox:
        innerUrl = subj.get_attribute("href")
        if "https://ssc.adm.ubc.ca/" not in innerUrl:
            if innerUrl > "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-department&dept=ELI":
                urls.append(innerUrl)
            
    if len(urls) != 0:
        for innerUrl in urls:
            scrape(innerUrl)
    else:
        try:
            courseMain = driver.find_element(By.XPATH, "//*[@role='main']").text.replace("Save To Worklist","")
            result = re.search(REGEX,driver.current_url)
            directory = BASE_DIRECTORY + result.groups()[0] + "/" + result.groups()[1] + "/"
            filename = result.groups()[2] + ".txt"
            os.makedirs(os.path.dirname(directory),exist_ok=True)
            with open(directory + filename, "w+", encoding="utf-8") as f:
                f.write(courseMain)
        except:
            # Weird case for ELI department
            pass

scrape(URL)
    
    
    

# def scrape(url):
#     driver.get(url)
#     subjBox = driver.find_elements(By.CSS_SELECTOR, SELECTOR)
#     urls = []
#     for subj in subjBox:
#         innerUrl = subj.get_attribute("href")
#         if "https://ssc.adm.ubc.ca/" not in innerUrl:
#             if innerUrl > "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-department&dept=ELI":
#                 urls.append(innerUrl)

#     for innerUrl in urls:
#         helper(innerUrl)

# def helper(url):
#     print(url)
#     driver.get(url)
#     subjBox = driver.find_elements(By.CSS_SELECTOR, SELECTOR)
#     urls = []
#     for subj in subjBox:
#         innerUrl = subj.get_attribute("href")
#         if "https://ssc.adm.ubc.ca/" not in innerUrl:
#             urls.append(innerUrl)
            
#     if len(urls) != 0:
#         for innerUrl in urls:
#             helper(innerUrl)
#     else:
#         try:
#             courseMain = driver.find_element(By.XPATH, "//*[@role='main']").text.replace("Save To Worklist","")
#             result = re.search(REGEX,driver.current_url)
#             directory = BASE_DIRECTORY + result.groups()[0] + "/" + result.groups()[1] + "/"
#             filename = result.groups()[2] + ".txt"
#             os.makedirs(os.path.dirname(directory),exist_ok=True)
#             with open(directory + filename, "w+", encoding="utf-8") as f:
#                 f.write(courseMain)
#         except:
#             # Weird case for ELI department
#             pass

scrape(URL)