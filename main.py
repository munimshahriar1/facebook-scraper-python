#!/usr/bin/env python
# coding: utf-8

# In[14]:


import time
start_time = time.time()


# In[15]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import csv
import pandas as pd
from bs4 import BeautifulSoup as bs4
import re


# In[16]:


chrome_options = webdriver.ChromeOptions()
# chrome_options.headless = True
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


# In[17]:


# Saving Query Data from csv to list
def savingQueryData(csvFile):
    queryDataCsv= pd.read_csv(csvFile)
    queryList = [i for i in queryDataCsv["query"]]
    locationList = [i for i in queryDataCsv["location"]]
    return queryList, locationList
    
def savingLoginData(csvFile):
    loginDataCsv = pd.read_csv(csvFile)
    emailList = [i for i in loginDataCsv["email"]]
    passwordList = [i for i in loginDataCsv["password"]]
    return emailList, passwordList

# Return searchable facebook url
def facebook_search_url(queryList, locationList):
    search_url_list = []
    for j in range(len(queryList)):
        splitQuery = queryList[j].split(" ")
        splitLocation = locationList[j].split(" ")

        searchUrl = "https://www.facebook.com/search/pages/?q="
        for i in splitQuery:
            searchUrl = searchUrl + i + "%20"
        for i in splitLocation:
            searchUrl = searchUrl + i + "%20"
        search_url_list.append(searchUrl)
    return search_url_list

queryList, locationList = savingQueryData("queries.csv")
search_url_list = facebook_search_url(queryList, locationList)

# search_url_list


# In[18]:


def generalInfo_aboutPage():
    soup = bs4(driver.page_source, "html.parser")
    list_info = soup.find_all("div", class_="je60u5p8")

    info = ""
    for idx, j in enumerate(list_info):
        for i in list_info[idx].findAll("span"):
            if not i.text in info:
                info = info + i.text + " "
        info = info.replace("General", "")
    return info

def collectURL(string):
    # findall() has been used 
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)      
    return [x[0] for x in url]

def collectEMAIL(string):
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', string)
    return match
def collectPHONE(string):
    match = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', string)
    return match

def mainScraper():
    #Html of about page
    html = driver.page_source
    soup = bs4(html, "html.parser")
    target_listing = soup.find_all("div", class_="sjgh65i0")

    master_list = []
    for idx,i in enumerate(target_listing):
    # Single Listing
        data_dict={}
        try:
            page_name = i.a["aria-label"]
            facebook_link = i.a["href"]
            data_dict["Page Name"] = page_name
            data_dict["Facebook Link"] = facebook_link
            facebook_link_aboutPage = facebook_link.replace("?__tn__=%3C", "about")
            if not "/about" in facebook_link_aboutPage:
                facebook_link_aboutPage = facebook_link_aboutPage.replace("about", "/about")
            print(facebook_link_aboutPage, "\n")
            if "facebook.com" in facebook_link_aboutPage:
                driver.get(facebook_link_aboutPage)
            time.sleep(5)
            #Accessing each lead's about page
            data_dict["Url"] = "".join(collectURL(generalInfo_aboutPage()))
            data_dict["Email"] = "".join(collectEMAIL(generalInfo_aboutPage()))
            data_dict["Phone Numer"] = "".join(collectPHONE(generalInfo_aboutPage()))
            data_dict["General Information"] = generalInfo_aboutPage()
        except:
            print("Error")
        master_list.append(data_dict)
        time.sleep(5)
        print(f"Percentage done: {idx/len(target_listing)*100}%")
    df = pd.DataFrame(master_list)
    return df
    


# In[19]:


emailList, passwordList = savingLoginData("login.csv")

driver.get("https://www.facebook.com")
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

username.clear()
username.send_keys(emailList[0])
password.clear()
password.send_keys(passwordList[0])

#target the login button and click it
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()


# In[ ]:


time.sleep(5)
for idx,url in enumerate(search_url_list):
    driver.get(url)
    time.sleep(2)
    for i in range(30):
        time.sleep(3)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
#     TODO: Solution for House Canda Sraping - Posts/Pages/Group ?
    time.sleep(2)
    df = mainScraper()
    queryList, locationList = savingQueryData("queries.csv")
    df.to_csv(f"{queryList[idx]} {locationList[idx]}.csv")
    break


# In[140]:


driver.quit()


# In[141]:


print("Time Taken",  (time.time() - start_time)/60, " min")


# In[233]:


# df


# In[ ]:




