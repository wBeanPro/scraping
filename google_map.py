from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time
import sys
import os


class ScrapePlaces:
    def __init__(self,q):
        dirName = 'dataFiles'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        self.fileName = dirName+'/'+q+'-'+time.strftime("%Y-%m-%d_%H-%M-%S")+'.csv';
        print('Storage File => '+self.fileName)
        self.fileCreated = False
        self.driver = webdriver.Firefox()
        self.driver.get("https://www.google.com/maps/search/"+q)

    def findItemsOnPage(self,pageNum):
        time.sleep(10) # timeout , change if connection slow
        items = self.driver.find_elements_by_class_name('place-result-container-place-link')
        for i in range(len(items)):
            data = {}
            data['Page Number'] = pageNum;
            data['Page Position'] = i+1;
            #items = self.driver.find_elements_by_class_name('ad-badge')
            self.processItem(items[i],data)
            #refresh read dom items
            items = self.driver.find_elements_by_class_name('place-result-container-place-link')
            #break;
        self.getNextPage(pageNum+1)


    def getNextPage(self,pageNum):
        print('pageNum',pageNum)
        timeout = 5# timeout , change if connection slow
        pageLink = self.driver.find_element_by_id('mapsConsumerUiSubviewSectionGm2Pagination__section-pagination-button-next')
        # print('nextpage',len(pageLink))
        if(pageLink.get_attribute('disabled')!='true'):
            try:
                pageLink[1].click();
                time.sleep(timeout)
                self.findItemsOnPage(pageNum)
            except Exception:
                print('nextpageexception')
                pass

    def processItem(self,item,data):
        print('data',data)
        item.click();
        timeout = 6# timeout , change if connection slow
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//button[@class='section-back-to-list-button']")))
            print('waiting done')
        except TimeoutException:
            # print('process item expcetion')
            
            pass

        data['Name'] = self.byClass('section-hero-header-title-title')
        data['Address'] = self.byPath('//button[@data-tooltip="Copy address"]')
        data['Website'] = self.byPath('//button[@data-tooltip="Open website"]')
        data['Phone Number'] = self.byPath('//button[@data-tooltip="Copy phone number"]')

        # self.driver.find_element_by_class_name('section-back-to-list-button').click();
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//div[@class='section-result-content']")))
            print('waiting done')
        except TimeoutException:
            #print(TimeoutException)
            pass

        print(data)
        self.writeItemToFile(data)


    def writeItemToFile(self,item):
        if(not self.fileCreated):
            with open(self.fileName, mode='w') as itemFile:
                item_writer = csv.writer(itemFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                item_writer.writerow(list(item.keys()))
            self.fileCreated = True

        with open(self.fileName, mode='a', encoding="utf-8") as itemFile:
            item_writer = csv.writer(itemFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            item_writer.writerow(list(item.values()))

    def byClass(self,className):
        txt = ""
        try:
            txt = self.driver.find_element_by_class_name(className).text
        except Exception:
            print('by class expcetoin')
            
        return txt

    def byPath(self,path):
        txt = ""
        try:
            txt = self.driver.find_element_by_xpath(path).get_attribute('aria-label')
        except Exception:
            print('by path expcetoin')
        return txt

    def closeDriver(self):
        print("\n\nEnding Scrapper Session")
        self.driver.close()

if __name__ == "__main__":
    if(len(sys.argv)>=2):
        q = ""
        page_index = 1
        for i in range(len(sys.argv)):
            if i < 1:
                continue
            if q == "":
                q = sys.argv[i]
            else:
                q = q + " " + sys.argv[i]
        print("Search Term => ",q)
        scrap = ScrapePlaces(q)
        scrap.findItemsOnPage(page_index)
        scrap.closeDriver()
    else:
        print("Please run program using scrapper.py [search term]")
