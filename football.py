from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import csv
import time
import sys
import os
from datetime import datetime, timezone
from selenium.webdriver.support.select import Select

class ScrapePlaces:
    def __init__(self,url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_extension('extension_3_10_1_0.crx')
        options.add_argument("--ignore-certificate-errors-spki-list")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(url)
        self.item_index = 0
        self.df = pd.DataFrame()
    def findItems(self):
        season_id_selector = Select(self.driver.find_element_by_id("season_id_selector"))
        cur_selected_option_txt = season_id_selector.first_selected_option.text
        cur_selected_index = 0
        option_list = self.driver.find_element_by_id("season_id_selector").find_elements_by_tag_name("option")
        for i in range(len(option_list)):
            if option_list[i].text == cur_selected_option_txt:
                cur_selected_index = i
                break
        while(cur_selected_index>=0):
            season_id_selector = Select(self.driver.find_element_by_id("season_id_selector"))
            print(season_id_selector)
            self.fileName = season_id_selector.first_selected_option.text.replace("/","-") + ".xlsx"
            print(self.fileName)
            flag = 0
            while(flag==0):
                matches_table = self.driver.find_element_by_xpath("//table[@class='matches   ']").find_element_by_tag_name("tbody").find_elements_by_class_name("match")
                for match in matches_table:
                    if match.get_attribute("data-status") != "Played":
                        continue
                    home = match.find_element_by_class_name('team-a').find_element_by_tag_name("a").text
                    away = match.find_element_by_class_name('team-b').find_element_by_tag_name("a").text
                    score = match.find_element_by_class_name('extra_time_score').text
                    timestamp = match.get_attribute("data-timestamp")
                    dt_object = datetime.fromtimestamp(int(timestamp))
                    dt_object = dt_object.replace(tzinfo=timezone.utc).astimezone(tz=None)

                    print(dt_object.strftime('%Y'),dt_object.strftime('%m.%d. %H:%M'),home,away,score.replace("-",":"))

                    self.df.at[self.item_index,"Year"] = dt_object.strftime('%Y')
                    self.df.at[self.item_index,"Time"] = dt_object.strftime('%m.%d. %H:%M')
                    self.df.at[self.item_index,"Home"] = home
                    self.df.at[self.item_index,"Away"] = away
                    self.df.at[self.item_index,"Score"] = score.replace("-",":")
                    writer = pd.ExcelWriter(self.fileName, engine='xlsxwriter')
                    self.df.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
                    writer.save()
                    self.item_index = self.item_index + 1
                btn_previous = self.driver.find_element_by_id("page_competition_1_block_competition_matches_summary_10_previous")
                if 'disabled' in btn_previous.get_attribute('class').split():
                    flag = 1
                    break
                else:
                    btn_previous.click()
                    self.waiting()
            cur_selected_index = cur_selected_index - 1
            season_id_selector = Select(self.driver.find_element_by_id("season_id_selector"))
            if cur_selected_index == -1:
                break
            season_id_selector.select_by_index(cur_selected_index)
            self.waiting()
            

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
    url = input('Enter search url: ')
    print("Search Url => ",url)
    scrap = ScrapePlaces(url)
    scrap.findItems()
    scrap.closeDriver()
