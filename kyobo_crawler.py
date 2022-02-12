# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # 교보문고 리뷰 데이터 수집

# +
# 크롤러 만들기

from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

import math
import time
import pandas as pd

# +
datas = []
data = {}
names, categories, all_rating, all_review = [], [], [], [] # 카테고리 별로 분리


url = 'http://www.kyobobook.co.kr/categoryRenewal/categoryTab.laf?pageNumber=1&perPage=20&mallGb=KOR&linkClass=01&ejkGb=&sortColumn=review_cnt&menuCode=004'

driver = webdriver.Chrome('C:/test/chromedriver.exe')
driver.implicitly_wait(10)
driver.get(url)


category = list(driver.find_element_by_xpath('//*[@id="container"]/div[1]/div[3]/p/span').text.split(' '))


for book_list in range(1, 40, 2):  # 책 리스트 1, 3, 5, 7로 xpath li[] 들어감

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="prd_list_type1"]/li['+str(book_list)+']/div/div[1]/div[2]/div[1]/a')))
    element.click()
    book_name = list(driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[1]/h1/strong').text.splitlines())
    categories += category
    names += book_name

    # 리뷰 영역으로 스크롤 해서 리뷰 창 띄우기
    actions = ActionChains(driver)
    review_pl = driver.find_element_by_xpath('//*[@id="kloverTotal"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", review_pl)

    time.sleep(5)

    try:
        review_num = driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[1]/div[4]/div/div').text.split()

    except:
        review_num = driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[1]/div[3]/div/div').text.split()


    review_num = (''.join(review_num[7])).strip('개)')  # 숫자만 뽑아내기
    page_num = math.ceil(int(review_num) / 5)

    
    print('='*10, book_name[0]+' 리뷰 수집','='*10)
    
    ratings, reviews = [], [] # 책 별로 분리
    for page in range(1, page_num):
        parentElement = driver.find_element_by_class_name('board_list')
        count = len(list(parentElement.find_elements_by_class_name('comment_wrap'))) # 리뷰 개수(마지막 페이지)

        for review_idx in range(1, count+1):
            try:
                rating = list(driver.find_element_by_xpath('//*[@id="box_detail_review"]/ul/li['+str(review_idx)+']/div[1]/dl/dd[3]').text.splitlines()[1])
                review = driver.find_element_by_xpath('//*[@id="box_detail_review"]/ul/li['+str(review_idx)+']/div[1]/dl/dd[5]/div').text
                ratings += rating   # 중복 제거 방지(append x)
                reviews.append(review)
            except:  # 평점 데이터 누락된 리뷰는 넘김
                pass

        # 리뷰 페이지 이동
        if page == 1:
            driver.find_element_by_xpath('//*[@id="box_detail_review"]/div[3]/div/a[10]').click()
        else:
            try:
                driver.find_element_by_xpath('//*[@id="box_detail_review"]/div[3]/div/a[12]').click()
                time.sleep(2)

            except:  # 마지막 페이지는 이동X
                pass
    print('='*10, '완료','='*10)

    all_rating.append(ratings)
    all_review.append(reviews)

    driver.back()
    time.sleep(3)
        
data["book_categories"] = categories
data["book_name"] = names
data["book_ratings"] = all_rating
data["book_review"] = all_review

print(data)
# -

# !pip install pymysql
# !pip install sqlalchemy

# +
# from sqlalchemy import create_engine
# import pymysql



# db_connection_str = 'mysql+mysqldb://yingzzi:pooiiioop@localhost:3306/book_review'
# db_connection = create_engine(db_connection_str)

# conn = db_connection.connect()

fic_p1 = pd.DataFrame(data)
fic_p1
fic_p1.to_csv("c:/test/fic_p1.csv", mode='w')
# fic_p1.to_sql(name='fic', con=db_connection, if_exists='append', index=False)
# -


