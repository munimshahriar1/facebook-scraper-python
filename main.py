import csv
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os.path

option = Options()
option.add_argument("--disable-infobars")
option.add_argument("--disable-extensions")
# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 1
})

email = ""
password = ""
i = 1
with open('login.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if i == 1:
            i = i + 1
            continue
        email = row[0]
        password = row[1]
        break

list = []
i = 1
with open('queries.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if i == 1:
            i = i + 1
            continue
        query = row[0]
        location = row[1]
        list.append({"query": query, "location": location})


def openFacebook(driver):
    url = "https://www.facebook.com"
    driver.get(url)


def checkExit(file_name):
    return os.path.exists(file_name)


def getLastPage(file_name):
    with open(file_name, "r", encoding="utf-8", errors="ignore") as scraped:
         final_line = scraped.readlines()[-1]
         return final_line


def login(driver):
    inputs = driver.find_elements(By.CLASS_NAME, "inputtext")
    # get Email
    emailInput = inputs[0]
    # get Password
    passwordInput = inputs[1]

    # send Values
    emailInput.send_keys(email)
    passwordInput.send_keys(password)

    # get Button Login
    loginButton = driver.find_element(By.TAG_NAME, "button")
    loginButton.click()


def openSearchPage(driver, query: str):
    time.sleep(5)
    url = "https://www.facebook.com/search/pages?q=" + query
    driver.get(url)


def applyLocation(driver, location: str):
    time.sleep(5)
    divLocation = driver.find_elements(By.TAG_NAME, "span")[58]
    divLocation.click()

    inputLocation = driver.find_elements(By.CSS_SELECTOR, "input[type='search']")[1]
    inputLocation.click()
    inputLocation.send_keys(location)
    time.sleep(4)
    ulLocation = driver.find_elements(By.TAG_NAME, "ul")[1]
    ulLocation.find_element(By.TAG_NAME, "li").click()


def startScraping(driver,query):
    listPages = []
    q = query.replace(" ","-") + ".csv"
    if (checkExit(q)):
        lastLink = getLastPage(q)
        lastLink = lastLink.split(",")[0].rstrip()
        if lastLink == "finished":
            return
        listPages = getOldList(q)
        print("last link ", lastLink)
        print(listPages)
    time.sleep(4)
    driverPages = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    openFacebook(driverPages)
    login(driverPages)
    html = driver.find_element_by_tag_name('html')

    finished = False
    while not finished:
        if "End of results" in html.text:
            finished = True

        for i in range(1, 15):
            html.send_keys(Keys.END)

        feed = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
        pages = feed.find_elements(By.CSS_SELECTOR, "a[role='link']")
        for page in pages:
            mFb = page.get_attribute("href").replace("www", "m")
            if mFb not in listPages:
                listPages.append(mFb)
                if mFb[-1] != "/":
                    mFb = mFb + "/"
                linkLikes = mFb + "community"
                driverPages.get(linkLikes)
                time.sleep(5)

                likes = \
                    driverPages.find_element(By.ID, "pages_msite_body_contents").find_element(By.TAG_NAME,
                                                                                              "div").find_elements(
                        By.TAG_NAME, "div")[1].find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME,
                                                                                             "div").find_element(
                        By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME,
                                                                                          "div").find_element(
                        By.TAG_NAME, "div").text
                print("likes : " + likes)
                follow = \
                    driverPages.find_element(By.ID, "pages_msite_body_contents").find_element(By.TAG_NAME,
                                                                                              "div").find_elements(
                        By.TAG_NAME, "div")[1].find_elements(By.TAG_NAME, "div")[9].text
                print("follow : " + follow)

                # linkInfo = mFb + "about"
                driverPages.get(mFb)
                time.sleep(5)
                try:
                    info = driverPages.find_element(By.ID, "pages_msite_body_contents")
                except:
                    continue
                images = info.find_elements(By.TAG_NAME, "img")

                listPhoneNumber = []
                listEmail = []
                listWebsites = []
                listLoc = []
                listInfo = []
                rating = ""
                checked = ""
                open = ""
                listInsta = []
                listYoutube = []
                listCat = []
                for image in images:
                    src = image.get_attribute("src")
                    if src == "https://static.xx.fbcdn.net/rsrc.php/v3/yn/r/IIz7DmH3RfV.png":
                        parent = image.find_element_by_xpath('..')
                        phoneNumber = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        listPhoneNumber.append(phoneNumber)
                        print("phone number " + phoneNumber)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yl/r/7wycyFqCurV.png":
                        parent = image.find_element_by_xpath('..')
                        em = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        listEmail.append(em)
                        print("email " + em)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/y5/r/ZWx4MakmUd4.png":
                        parent = image.find_element_by_xpath('..')
                        website = parent.find_element(By.TAG_NAME, "div").text
                        listWebsites.append(website)
                        print("website " + website)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/y8/r/PwUkFLBBA85.png":
                        parent = image.find_element_by_xpath('..')
                        location = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME,
                                                                                        "div").find_element(
                            By.TAG_NAME, "div").text
                        listLoc.append(location)
                        print("location " + location)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yG/r/yzxwaDMdZAx.png":
                        parent = image.find_element_by_xpath('..')
                        information = parent.find_element(By.TAG_NAME, "div").text
                        listInfo.append(information)
                        print("information " + information)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yD/r/qvZe07446FL.png":
                        parent = image.find_element_by_xpath('..')
                        rating = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        print("rating " + rating)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yt/r/GWGxn_Tx65X.png":
                        parent = image.find_element_by_xpath('..')
                        checked = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        print("checked " + checked)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yV/r/c-IOC1UqHiT.png":
                        parent = image.find_element_by_xpath('..')
                        open = parent.find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")[2].text
                        print("checked " + open)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/ys/r/oEVThCLaFzH.png":
                        parent = image.find_element_by_xpath('..')
                        instagram = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        listInsta.append(instagram)
                        print("instagram " + instagram)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/y8/r/7MR5nSXB08u.png":
                        parent = image.find_element_by_xpath('..')
                        youtube = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").text
                        listYoutube.append(youtube)
                        print("youtube " + youtube)

                    elif src == "https://static.xx.fbcdn.net/rsrc.php/v3/yV/r/_6QbEglrVsx.png":
                        parent = image.find_element_by_xpath('..')
                        cat = parent.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(
                            By.TAG_NAME,
                            "span").find_element(
                            By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").text
                        listCat.append(cat)
                        print("category " + cat)


                phoneNumber = " ".join(listPhoneNumber)
                insta = " ".join(listInsta)
                email = " ".join(listEmail)
                website = " ".join(listWebsites)
                info = " ".join(listInfo)
                loc = " ".join(listLoc)
                youtube = " ".join(listYoutube)
                cat = " ".join(listCat)

                facebookPage = page.get_attribute("href")

                data = [ facebookPage , likes , follow , phoneNumber ,  insta ,  email , website ,  info ,
                         loc , youtube , cat , rating ,  checked ,  open ]
                saveInfo(q,data)

                print("********************************************************")
                # print(info.text)
                time.sleep(5)


def saveInfo(file_name, data):
    with open(file_name, 'a') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(data)


def getOldList(file_name):
    listPages = []
    with open(file_name, 'r') as f:
        r = csv.reader(f)
        for ro in r:
            link = ro[0]
            link = link.replace("www", "m")
            listPages.append(link)
        return listPages

driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
openFacebook(driver)
# login facebook
login(driver)
for row in list:
    openSearchPage(driver, row.get("query"))
    applyLocation(driver, row.get("location"))
    startScraping(driver,row.get("query"))
