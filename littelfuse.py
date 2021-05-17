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
        url = "https://www.littelfuse.com/products.aspx"
        self.driver.get(url)
        category_list = self.driver.find_element_by_class_name('product-grid').find_elements_by_tag_name('li')
        index = 0
        df = pd.DataFrame()
        for i in range(len(category_list)):
            link = category_list[i].find_element_by_tag_name('a')
            # category_name = link.text
            link.click()
            self.waiting()
            sub_category_list = self.driver.find_element_by_class_name('product-grid').find_elements_by_tag_name('li')
            for j in range(len(sub_category_list)):
                sub_link = sub_category_list[j].find_element_by_tag_name('a')
                sub_link.click()
                self.waiting()
                sub_sub_category_list_div = self.driver.find_element_by_class_name('product-grid')
                if sub_sub_category_list_div:
                    sub_sub_category_list = sub_sub_category_list_div.find_elements_by_tag_name('li')
                    for k in range(len(sub_sub_category_list)):
                        sub_sub_link = sub_sub_category_list[j].find_element_by_tag_name('a')
                        sub_sub_link.click()
                        self.waiting()
                        last_category_list = self.driver.find_elements_by_class_name('descriptive-box')
                        for l in range(len(last_category_list)):
                            last_link = last_category_list[l].find_element_by_tag_name("a")
                            self.driver.execute_script("arguments[0].click();", last_link)
                            # print(last_link.get_attribute("innerHTML"))
                            # last_link.click()
                            self.waiting()
                            product_list = self.driver.find_element_by_id('tblElecChars').find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
                            for m in range(len(product_list)):
                                product_link = product_list[m].find_element_by_tag_name("a")
                                sku = product_link.get_attribute("innerHTML")
                                print(index, sku)
                                self.driver.execute_script("arguments[0].click();", product_link)
                                self.waiting()
                                pro_name = self.driver.find_element_by_tag_name('h1').text
                                df.at[index,"url"] = self.driver.current_url
                                df.at[index,"Title"] = pro_name
                                df.at[index,"Brand"] = "littelfuse"
                                pro_description = self.driver.find_element_by_class_name('feaures-benefits-box').get_attribute("innerHTML")
                                df.at[index,"Long/Short Descriptions"] = pro_description.split("</div>", 1)[1].split("<br>",1)[0].replace("\n","").replace("\t","").replace("  ","");
                                pro_feature = ''
                                feature_list = self.driver.find_element_by_class_name('feaures-benefits-box').find_elements_by_tag_name("ul")[2].find_elements_by_tag_name("li")
                                for feature in feature_list:
                                    if pro_feature!='':
                                        pro_feature += " | "
                                    pro_feature += feature.text
                                df.at[index,"Features"] = pro_feature

                                applications = ''
                                applications_list = self.driver.find_element_by_class_name('feaures-benefits-box').find_elements_by_tag_name("ul")[1].find_elements_by_tag_name("li")
                                for app in applications_list:
                                    if applications!='':
                                        applications += " | "
                                    applications += app.text
                                df.at[index,"Applications"] = applications

                                spec_txt = ""
                                spec_list = self.driver.find_element_by_id("ElectricalCharacteristics").find_elements_by_tag_name("tbody")
                                for spec in spec_list:
                                    key = spec.find_element_by_tag_name("tr").find_element_by_tag_name("a").text
                                    value = spec.find_element_by_tag_name("tr").find_elements_by_tag_name("td")[1].text
                                    spec_txt += "\""+ key + "\":\"" + value + "\","
                                df.at[index,"Specifications"] = "{"+spec_txt[:-1]+"}"

                                breadcrumb_list = self.driver.find_element_by_class_name("breadcrumb").find_elements_by_tag_name("a")
                                breadcrumb_txt = ""
                                for breadcrumb_index in range(len(breadcrumb_list)):
                                    breadcrumb_txt += breadcrumb_list[breadcrumb_index].text+"/"
                                df.at[index,"Breadcrumb"] = breadcrumb_txt + sku
                                df.at[index,"Product SKU Number"] = "["+sku+"]"
                                img_txt = ""
                                detail_img = self.driver.find_element_by_class_name('zoomContainer').find_element_by_tag_name('img').get_attribute("src")
                                img_txt = "{\"Item_Image\":\""+detail_img+"\",\"Detailed_Image\":\""+ detail_img+"\",\"Zoom_Image\":\""+detail_img+"\"},"
                                df.at[index,"Image"] = "["+img_txt[:-1]+"]"

                                assets = ''
                                assets_datas = self.driver.find_element_by_id('tabTechRes').find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
                                for asset_data in assets_datas:
                                    key = asset_data.find_element_by_tag_name("a").get_attribute("innerHTML").replace("  ","")
                                    value = asset_data.find_element_by_tag_name("a").get_attribute("href")
                                    assets += "'"+key+"' : \""+value+"\"" + ","
                                df.at[index,"Assets"] = "{"+assets[:-1]+"}"

                                writer = pd.ExcelWriter('littelfuse.xlsx', engine='xlsxwriter')
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
                                product_list = self.driver.find_element_by_id('tblElecChars').find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
                            self.driver.execute_script("window.history.go(-1)")
                            self.waiting()
                            last_category_list = self.driver.find_elements_by_class_name('descriptive-box')
                        self.driver.execute_script("window.history.go(-1)")
                        self.waiting()
                        sub_sub_category_list = sub_sub_category_list_div.find_elements_by_tag_name('li')
                # else :
                #     continue
                self.driver.execute_script("window.history.go(-1)")
                self.waiting()
                sub_category_list = self.driver.find_element_by_class_name('product-grid').find_elements_by_tag_name('li')
            self.driver.execute_script("window.history.go(-1)")
            self.waiting()
            category_list = self.driver.find_element_by_class_name('product-grid').find_elements_by_tag_name('li')
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
