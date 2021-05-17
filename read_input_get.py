import pandas as pd
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
    def __init__(self):
        self.driver = webdriver.Firefox()
        df = pd.read_csv('export.csv')
        streetList = df["streetname"].tolist()
        boroList = df["boro"].tolist()
        houseNoList = df["housenumber"].tolist()
        headerList = []
        for i in range(len(streetList)):
            
            self.driver.get("https://hpdonline.hpdnyc.org/HPDonline/provide_address.aspx")
            streetName = streetList[i]
            boroName = boroList[i]
            text_street = self.driver.find_element_by_id('txtStreet')
            text_street.send_keys(streetName)
            text_houseno = self.driver.find_element_by_id('txtHouseNo')
            text_houseno.send_keys(houseNoList[i])
            self.driver.find_element_by_xpath("//select[@name='ddlBoro']/option[text()='"+boroName.lower().capitalize()+"']").click()
            btn_search = self.driver.find_element_by_id('btnSearch')
            btn_search.click()
            timeout = 6# timeout , change if connection slow
            try:
                WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//button[@class='section-back-to-list-button']")))
                print('waiting done')
            except TimeoutException:
                # print('process item expcetion')
                
                pass
            try:
                btn_link = self.driver.find_element_by_id('lbtnRegistration')
                btn_link.click()
            except Exception:
                print("link_error")
                pass
            try:
                WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//button[@class='section-back-to-list-button']")))
                print('waiting done')
            except TimeoutException:
                # print('process item expcetion')
                
                pass
            try:
                table = self.driver.find_element_by_id('dgRegistration')
                last_name = table.find_element_by_xpath(".//tbody/tr[2]/td[4]").text
                first_name = table.find_element_by_xpath(".//tbody/tr[2]/td[5]").text
                # value = headline.find_element_by_xpath(".//td[0]/span").text
                print(last_name+" "+first_name)
                df.at[i,'HeadOfficeName'] = last_name+" "+first_name
                df.at[i,'Organization'] = table.find_element_by_xpath(".//tbody/tr[5]/td[3]").text
                df.to_csv("export.csv", index=False)
            except Exception:
                print("table_error")
                pass
        # dirName = 'dataFiles'
        # if not os.path.exists(dirName):
        #     os.mkdir(dirName)
        # self.fileName = dirName+'/'+q+'-'+time.strftime("%Y-%m-%d_%H-%M-%S")+'.csv';
        # print('Storage File => '+self.fileName)
        # self.fileCreated = False

    
    def closeDriver(self):
        print("\n\nEnding Scrapper Session")
        self.driver.close()

if __name__ == "__main__":
    scrap = ScrapePlaces()
    scrap.closeDriver()
