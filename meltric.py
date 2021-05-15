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

# //https://meltric.com/
class ScrapePlaces:
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        url = "https://meltric.com/all.html"
        self.driver.get(url)
        category_list = self.driver.find_element_by_class_name('type-list').find_elements_by_tag_name('li')
        index = 0
        df = pd.DataFrame()
        

        for i in range(len(category_list)):
            if index > 200 :
                break
            link = category_list[i].find_element_by_tag_name('a')
            category_name = link.text
            link.click()
            self.waiting()
            category_list = self.driver.find_element_by_class_name('type-list').find_elements_by_tag_name('li')
            sub_link_ul = category_list[i].find_element_by_tag_name("ul")
            sub_link_list = sub_link_ul.find_elements_by_tag_name('li')
            for j in range(len(sub_link_list)):
                if index > 200 :
                    break
                sub_link = sub_link_list[j].find_element_by_tag_name('a')
                sub_category_name = sub_link.text
                sub_link.click()
                self.waiting()
                table_list = self.driver.find_elements_by_class_name('result-table')
                for k in range(len(table_list)):
                    if index > 200 :
                        break
                    row_list = table_list[k].find_element_by_class_name('large-only').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
                    for l in range(len(row_list)):
                        if index > 200 :
                            break
                        sku = row_list[l].find_element_by_tag_name('a').get_attribute('sku')
                        description = row_list[l].find_element_by_class_name('tooltipdisplay').get_attribute('innerHTML')
                        product_link = row_list[l].find_elements_by_tag_name('a')[1]
                        self.driver.execute_script("arguments[0].click();", product_link)
                        # product_link.click()
                        self.waiting()
                        df.at[index,"url"] = self.driver.current_url
                        title = self.driver.find_element_by_class_name('products-detail').find_element_by_class_name('main').find_element_by_tag_name('h1').text
                        df.at[index,"Title"] = title
                        df.at[index,"Brand"] = "Meltric"
                        df.at[index,"Long/Short Descriptions"] = description.replace("  ","");
                        spec_list = self.driver.find_element_by_class_name('large-only').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr');
                        spec_text = ''
                        app_stand_val = ""
                        accessory_size = ""
                        for spec in spec_list:
                            key = spec.find_element_by_tag_name("th").text
                            value = spec.find_element_by_tag_name("td").text
                            if key == "Base Drawing Number" or key == "Catalog" or key == "Instructions":
                                continue
                            elif key == "Applicable Standards":
                                app_stand_val = spec.find_element_by_tag_name("td").get_attribute('innerHTML').replace("\t","").replace("\n","")
                            elif key == "Accessory Size":
                                accessory_size = value
                            else:
                                spec_text += "\""+ key + "\":\"" + value + "\","
                        df.at[index,"Specifications"] = "{"+spec_text[:-1]+"}"
                        breadcrumb_list = self.driver.find_element_by_class_name('breadcrumbs').find_elements_by_tag_name('a')
                        breadcrumb_txt = ""
                        for breadcrumb_item in breadcrumb_list:
                            breadcrumb_txt += breadcrumb_item.text+"/"
                        df.at[index,"Breadcrumb"] = breadcrumb_txt[:-1]
                        df.at[index,"Category/Subcategory"] = category_name
                        df.at[index,"Product SKU Number"] = "["+sku+"]"
                        file_list = self.driver.find_element_by_class_name('large-only').find_elements_by_tag_name('a')
                        file_text = ''
                        for file in file_list:
                            file_text += "'"+file.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_tag_name('th').text + "' : \"" + file.get_attribute('href') + "\","
                        product_pdf = self.driver.find_element_by_class_name("productpdf").get_attribute("href")
                        df.at[index,"Assets"] = "{'product_pdf' : \""+product_pdf+"\","+file_text[:-1]+"}"

                        # img = self.driver.find_element_by_class_name('productimages').find_elements_by_tag_name('img').get_attribute('src')
                        img_txt = ""
                        detail_img_list = self.driver.find_element_by_class_name('sidebar').find_elements_by_class_name('active')
                        for detail_img_item in detail_img_list:
                            detail_img = detail_img_item.find_element_by_class_name('thumbnails')
                            detail_img_src = detail_img.find_element_by_tag_name('img').get_attribute('src')
                            img_txt += "{\"item_image\":\""+detail_img_src+"\",\"Detailed_Image\":\""+ detail_img_src+"\",\"Zoom_Image\":\""+detail_img_src+"\"},"
                        # print("["+img_txt[:-1]+"]");
                        df.at[index,"Image"] = "["+img_txt[:-1]+"]"
                        df.at[index,"Applicable Standards"] = app_stand_val.replace("<br>", " | ")
                        df.at[index,"Accessory Size"] = accessory_size
                        df.at[index,"Series"] = sub_category_name + " Series"
                        index = index + 1
                        print(index,sku)
                        # df.to_csv("sample_scraping.xlsx", index=False)
                        writer = pd.ExcelWriter('sample_scraping.xlsx', engine='xlsxwriter')
                        df.to_excel(writer, sheet_name='Sheet2', startrow=0, index=False)
                        # auto_adjust_xlsx_column_width(df, writer, sheet_name="Sheet2", margin=0)
                        for column in df:
                            column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
                            column_width = min(column_width, 300)
                            col_idx = df.columns.get_loc(column)
                            writer.sheets['Sheet2'].set_column(col_idx, col_idx, column_width)
                        writer.save()
                        self.driver.execute_script("window.history.go(-1)")
                        self.waiting()
                        table_list = self.driver.find_elements_by_class_name('result-table')
                        row_list = table_list[k].find_element_by_class_name('large-only').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
                        
                category_list = self.driver.find_element_by_class_name('type-list').find_elements_by_tag_name('li')
                sub_link_ul = category_list[i].find_element_by_tag_name("ul")
                sub_link_list = sub_link_ul.find_elements_by_tag_name('li')
            self.driver.get(url)
            category_list = self.driver.find_element_by_class_name('type-list').find_elements_by_tag_name('li')
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
