"""
ไฟล์นี้เหมือนกันกับไฟล์ scrapper_jup
แค่ไฟล์ scrapper_jup เอาไว้ Debugตอนเว็บเปลี่ยนโครงสร้าง
"""

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import bs4
import os

""" เวอร์ชันChrome driverอาจจะต้องเปลี่ยนถ้สChromeอัพเดท """

def open_web():
    options = webdriver.ChromeOptions()
    # เว็บไม่ปิดอัตโนมัติ
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    try:
        # ลองใช้ทรัพยากรณ์ chrome, chromedriverว่าเวอร์ชันตรงไหม
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print("อาจจะเวอร์ชั่น Chromedriver ไม่ตรง")
        print("Fix version chrome driver")
        # ถ้าเวอร์ชันไม่ตรงก็ install chrome driverใหม่
        from selenium.webdriver.chrome.service import Service
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("ตั้งค่าChromeเสร็จ")

    url = 'https://futureskill.co/course?paginPage=1&course=all'
    driver.get(url) # เปิดเว็บด้วยChrome

    time.sleep(1)
    # ซูมออกจากหน้าเว็บให้ข้อมูลโหลดทั้งหน้า
    driver.execute_script("document.body.style.zoom='70%'")
    return driver

# เก็บข้อมูลจากหน้าเว็บปัจจุบัน (ใช้แค่ bs4) เพราะไม่ได้คลิ๊กอะไร
def find_all_data(driver, course_names, course_prices, course_people):
    data = driver.page_source # อ่านข้อมูลhtmlทั้งหน้า
    soup = bs4.BeautifulSoup(data, features="html.parser") # แปลงเป็นhtmlที่คนเราอ่านได้

    # เลือก Card ทั้งหมด
    els = soup.select('#__next > div.min-h-screen.max-h-full.pt-12.md\:pt-20 > div.bg-white.min-h-screen.h-full.py-\[30px\].md\:py-\[40px\].xl\:py-\[80px\] > div > div.bg-white.w-\[960px\] > div:nth-child(3) > div.w-full.h-full > div.w-full.mt-12 > div.grid.grid-cols-1.md\:grid-cols-3.gap-4.place-items-center > div')

    i = 1 # index ของ select name
    for el in els:
        # หา ชื่อ, ราคา, คนเรียนทั้งหมดให้เรียบร้อย
        name = el.select_one(f'#__next > div.min-h-screen.max-h-full.pt-12.md\:pt-20 > div.bg-white.min-h-screen.h-full.py-\[30px\].md\:py-\[40px\].xl\:py-\[80px\] > div > div.bg-white.w-\[960px\] > div:nth-child(3) > div.w-full.h-full > div.w-full.mt-12 > div.grid.grid-cols-1.md\:grid-cols-3.gap-4.place-items-center > div:nth-child({i}) > div > div.pt-2.px-6.pb-6.md\:px-4.md\:pb-4.xl\:px-6.xl\:pb-6.card-shadow.rounded-b-2xl > div:nth-child(2) > a > span')
        price = el.find_all("div", {"class": "text-pinkFS-500 css-1p8ezsx e3nleyr1"})
        people = el.find_all("div", {"class": "text-neutralFS-300 css-19ne8l1 e1b99tl71"})
        
        if not price: # สำหรับคอร์สฟรีเข้าตัวนี้
            price = "คอร์สฟรี"
        else:
            # regular expression แบบพื้นฐาน python
            price = float(price[0].text.strip().replace("฿", '').replace(",", ""))

        # print(price)
        course_names.append(name.text.replace(" ", ''))
        course_prices.append(price)
        course_people.append(people[0].text)
        i+=1
    return course_names, course_prices, course_people


# คลิ๊กไปหน้าถัดไป
def next_page(driver):
    btnNext = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[4]')
    driver.execute_script("arguments[0].click();", btnNext)
    time.sleep(1)

# ดึงข้อมูลหน้าคอร์สเรียนว่ามีกี่หน้า
def len_pages(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, features="html.parser")
    all_pages = soup.select('#__next > div.min-h-screen.max-h-full.pt-12.md\:pt-20 > div.bg-white.min-h-screen.h-full.py-\[30px\].md\:py-\[40px\].xl\:py-\[80px\] > div > div.bg-white.w-\[960px\] > div:nth-child(3) > div.w-full.h-full > div.w-full.mt-12 > div.flex.justify-center.md\:justify-end.mt-\[50px\].mb-\[100px\] > div > div.dark\:text-neutralFS-50')
    # regular expression แบบพื้นฐาน python (clean data ดึงเอาแค่ตัวเลข)
    len_pages = int(all_pages[0].text.replace("/", '').replace(" ", ''))
    return len_pages

# รวมราคา
def find_sum_price(course_prices):
    new_course_price = []
    for price in course_prices:
        # เช็คว่าถ้าเป็นคอร์สฟนีไม่ต้องนำมาคำนวณ
        if price == "คอร์สฟรี":
            continue

        new_course_price.append(int(price))
        
    return sum(new_course_price)

# รวมยอดคนซื้อ
def find_sum_people(course_people):
    new_course_people = []
    for people in course_people:
        if people.isdigit():  # ตรวจสอบว่าเป็นตัวเลขหรือไม่
            new_course_people.append(int(people))
        else:
            new_course_people.append(int(people.replace(",", "")))

    return sum(new_course_people)

# สร้างตารางหลังจากดูดข้อมูลมาแล้ว
def make_dataframe(course_names, course_prices, course_people):
    data_course = pd.DataFrame([course_names, course_prices, course_people])
    data_course = data_course.transpose() # ตารางแบบแนวตั้ง
    data_course.columns = ['Name course', 'Price', 'People'] # หัวข้อตาราง
    return data_course

def main(): # ฟังก์ชันหลัก
    course_names = []
    course_prices = []
    course_people = []
    driver = open_web()
    lenPages = len_pages(driver=driver) # มีกี่หน้า
    # เริ่มอ่านข้อมูลไปทีละหน้า
    for lenPage in range(lenPages):
        time.sleep(0.5)
        course_names, course_prices, course_people = find_all_data(driver, course_names, course_prices, course_people)
        next_page(driver) # ไปหน้าถัดไป
    
    # ผลรวมของ ราคาทุกคอร์สและคนซื้อทุกคอร์ส
    sum_price = find_sum_price(course_prices)
    sum_people = find_sum_people(course_people)
    
    # สร้างตารางแล้ว return ออกไป
    data_frame_course = make_dataframe(course_names, course_prices, course_people)
    # เพิ่ม row ผลรวมและผลลัพธ์ที่รวมราคากับคนซื้อ
    data_frame_course = pd.concat([data_frame_course, pd.DataFrame({"Name course": "รวม", "Price": sum_price, "People": sum_people}, index=[len(data_frame_course)])])
    print(data_frame_course)
    return data_frame_course

if __name__ == '__main__':
    table_data = main() # ได้ตารางมา
    print(table_data)
    # เซฟลงโฟลเดอร์ที่อยู่ตอนนี้
    table_data.to_excel('Data_course_FutureSkill.xlsx')
