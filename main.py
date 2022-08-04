import time
import pandas as pd
from bs4 import BeautifulSoup as bs4
import re
import csv
import datetime
import sys
import time
import requests
from PyQt5.QtGui import QIcon
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os.path
import random
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import *


class Scraper:
    def __init__(self) -> None:
        pass

    def runScraper(self, queryList, locationList):
        # STEP 1: Getting login data from file
        self.emailList, self.passwordList = self.savingLoginData("login.csv")

        # STEP 2: Generating Query and Location List from Config File
        queryList, locationList = queryList, locationList
        search_url_list = self.facebook_search_url(queryList, locationList)

        print(queryList, locationList)
    
        # STEP 3: Initializing Selenium
        self.initSelenium()

        # STEP 4: Initiate the Scraper
        time.sleep(5)
        for idx,url in enumerate(search_url_list):
            self.driver.get(url)
            time.sleep(2)
            # Scrolling the Pages: Change range to 30
            for i in range(30):
                time.sleep(3)
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
            time.sleep(2)
            df = self.scraper()
            queryList, locationList = self.savingQueryData("queries.csv")
            df.to_csv(f"scraper_output/{queryList[idx]} {locationList[idx]}.csv")
            break
        print("DONE")
        self.driver.quit()

    def initSelenium(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.headless = True
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        self.driver.get("https://www.facebook.com")

        username = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

        username.clear()
        username.send_keys(self.emailList[0])
        password.clear()
        password.send_keys(self.passwordList[0])

        #target the login button and click it
        button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

            
    # Saving Query Data from csv to list
    def savingQueryData(self, csvFile):
        queryDataCsv= pd.read_csv(csvFile)
        queryList = [i for i in queryDataCsv["query"]]
        locationList = [i for i in queryDataCsv["location"]]
        return queryList, locationList
        
    def savingLoginData(self, csvFile):
        loginDataCsv = pd.read_csv(csvFile)
        emailList = [i for i in loginDataCsv["email"]]
        passwordList = [i for i in loginDataCsv["password"]]
        return emailList, passwordList

    # Return searchable facebook url
    def facebook_search_url(self, queryList, locationList):
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

    def generalInfo_aboutPage(self):
        soup = bs4(self.driver.page_source, "html.parser")
        list_info = soup.find_all("div", class_="je60u5p8")

        info = ""
        for idx, j in enumerate(list_info):
            for i in list_info[idx].findAll("span"):
                if not i.text in info:
                    info = info + i.text + " "
            info = info.replace("General", "")
        return info

    def collectURL(self, string):
        # findall() has been used 
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex,string)      
        return [x[0] for x in url]

    def collectEMAIL(self, string):
        match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', string)
        return match
    def collectPHONE(self, string):
        match = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', string)
        return match

    def scraper(self):
        #Html of about page
        html = self.driver.page_source
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
                print("\n", facebook_link_aboutPage)
                if "facebook.com" in facebook_link_aboutPage:
                    self.driver.get(facebook_link_aboutPage)
                time.sleep(5)
                #Accessing each lead's about page
                data_dict["Url"] = "".join(self.collectURL(self.generalInfo_aboutPage()))
                data_dict["Email"] = "".join(self.collectEMAIL(self.generalInfo_aboutPage()))
                data_dict["Phone Numer"] = "".join(self.collectPHONE(self.generalInfo_aboutPage()))
                data_dict["General Information"] = self.generalInfo_aboutPage()
            except:
                print("Error")
            master_list.append(data_dict)
            time.sleep(5)
            print(f" Percentage done: {(idx+1)/len(target_listing)*100}%")
        df = pd.DataFrame(master_list)
        return df


class MainWindow(QMainWindow):

    # Constructor
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.status = ""

        self.setWindowTitle("Facebook scraper")
        self.setFixedSize(780, 400)

        # # Upload Config Button - Todo: Import the Config File
        self.buttonUpload = QPushButton("Load Configuration", self)
        self.buttonUpload.move(300, 10)
        self.buttonUpload.resize(150, 25)
        self.buttonUpload.clicked.connect(self.uploadOldConfig)

        # self.labelKeywords = QLabel("Keywords", self) 
        # self.labelKeywords.move(50, 50)

        # self.textAreaKeywords = QPlainTextEdit("", self)
        # self.textAreaKeywords.move(50, 80)
        # self.textAreaKeywords.resize(320, 150)

        # self.labelLocations = QLabel("Locations", self)
        # self.labelLocations.move(400, 50)

        # self.textAreaLocations = QPlainTextEdit("", self)
        # self.textAreaLocations.move(400, 80)
        # self.textAreaLocations.resize(320, 150)

        # # Start Button
        self.buttonStart = QPushButton("", self)
        self.buttonStart.setIcon(QIcon("start.png"))
        self.buttonStart.setStyleSheet("border-radius : 50;")
        self.buttonStart.move(50, 50)
        self.buttonStart.setIconSize(QSize(40, 40))
        self.buttonStart.resize(40, 40)
        self.buttonStart.clicked.connect(self.start)

        # # Stop Button
        self.buttonStop = QPushButton("", self)
        self.buttonStop.setIcon(QIcon("stop.png"))
        self.buttonStop.setStyleSheet("border-radius : 50;")
        self.buttonStop.move(120, 50)
        self.buttonStop.setIconSize(QSize(40, 40))
        self.buttonStop.resize(40, 40)
        self.buttonStop.setEnabled(False)
        # self.buttonStop.clicked.connect(self.stop)

        self.labelProcessing = QLabel("", self)
        self.labelProcessing.move(190, 320)
        self.labelProcessing.resize(300, 25)
        self.labelProcessing.hide()

        self.labelNextDownlooad = QLabel("", self)
        self.labelNextDownlooad.move(320, 320)
        self.labelNextDownlooad.resize(300, 25)

        self.labelRecordsDb = QLabel("", self)
        self.labelRecordsDb.move(550, 320)
        self.labelRecordsDb.resize(150, 25)

        # # First Dotted Line
        self.label_dotted1 = QLabel("", self)
        self.label_dotted1.move(50, 40)
        self.label_dotted1.resize(670, 2)
        self.label_dotted1.setStyleSheet("border-top :1px ; border-style:dotted;")

        # # Second Dotted Line
        # self.label_dotted2 = QLabel("", self)
        # self.label_dotted2.move(50, 250)
        # self.label_dotted2.resize(670, 2)
        # self.label_dotted2.setStyleSheet("border-top :1px ; border-style:dotted;")

        self.labelResult = QLabel("", self)
        self.labelResult.setEnabled(False)
        self.labelResult.hide()
    
    def uploadOldConfig(self):
        self.queryList, self.locationList = self.savingQueryData("queries.csv")

    # Saving Query Data from csv to list
    def savingQueryData(self, csvFile):
        queryDataCsv= pd.read_csv(csvFile)
        queryList = [i for i in queryDataCsv["query"]]
        locationList = [i for i in queryDataCsv["location"]]
        return queryList, locationList

    def start(self):
        scraper = Scraper()
        scraper.runScraper(self.queryList, self.locationList)     


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())