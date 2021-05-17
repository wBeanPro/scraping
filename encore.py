import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from UliPlot.XLSX import auto_adjust_xlsx_column_width
import chromedriver_binary
import csv
import time
import sys
import os

# https://www.encorewire.com/products/index.html
class ScrapePlaces:
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        url = "https://www.encorewire.com/products/index.html"
        self.driver.get(url)
        category_list = self.driver.find_element_by_class_name('productsHome__products').find_element_by_id('viewGrid').find_elements_by_class_name('productsHome__column')
        print("Total Count:",len(category_list))
        index = 0
        df = pd.DataFrame()

        for i in range(len(category_list)):
            link = category_list[i].find_element_by_tag_name('a')
            # category_name = link.text
            link.click()
            self.waiting()
            pro_name = self.driver.find_element_by_class_name('product__header').find_element_by_class_name('product__wrapper').text
            df.at[index,"url"] = self.driver.current_url
            df.at[index,"Title"] = pro_name
            df.at[index,"Brand"] = "Encore Wire"
            meta_list = self.driver.find_elements_by_class_name("product__infobox-specs-tag")
            for j in range(len(meta_list)):
                meta_txt = ""
                meta_array = meta_list[j].find_elements_by_tag_name("a")
                for a_tag in meta_array:
                    meta_txt += a_tag.text + ","
                meta_title = self.driver.find_elements_by_class_name('product__infobox-specs-title')[j].text
                df.at[index,meta_title] = meta_txt[:-1]
            product_features_list = self.driver.find_element_by_class_name('product__features').find_element_by_tag_name("ul").find_elements_by_tag_name("li")
            pro_feature = ''
            for fe in product_features_list:
                if pro_feature!='':
                    pro_feature += " | "
                pro_feature += fe.text
            df.at[index,"Features"] = pro_feature
            pro_description = self.driver.find_element_by_id("description").find_element_by_tag_name("p").text
            df.at[index,"Description"] = pro_description
            img_src = self.driver.find_element_by_class_name('product__infobox-figure').find_element_by_tag_name("img").get_attribute("src")
            df.at[index,"Images"] = "[{\"Item_Image\":\""+img_src+"\",\"Detailed_Image\":\""+ img_src+"\",\"Zoom_Image\":\""+img_src+"\"}]"
            catalog = self.driver.find_element_by_class_name("button__download").get_attribute("href")
            df.at[index,"Assets"] = "{'Product_Pdf' : \""+catalog+"\"}"
            print(index,pro_name)
            writer = pd.ExcelWriter('sample_scraping.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
            # auto_adjust_xlsx_column_width(df, writer, sheet_name="Sheet2", margin=0)
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
                column_width = min(column_width, 300)
                col_idx = df.columns.get_loc(column)
                writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)
            writer.save()
            index += 1
            self.driver.execute_script("window.history.go(-1)")
            self.waiting()
            category_list = self.driver.find_element_by_class_name('productsHome__products').find_element_by_id('viewGrid').find_elements_by_class_name('productsHome__column')

    def waiting(self):
        timeout = 6# timeout , change if connection slow
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//button[@class='section-back-to-list-button']")))
            print('waiting done')
        except TimeoutException:
            # print('process item expcetion')
            
            pass
    
    def closeDriver(self):
        print("\n\nEnding Scrapper Session")
        self.driver.close()

if __name__ == "__main__":
    scrap = ScrapePlaces()
    scrap.closeDriver()
