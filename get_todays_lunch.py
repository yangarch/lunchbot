import requests
import time
import yaml
import os
from datetime import date, datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from slack_sdk import WebClient
import imageio.v3 as iio
import imageio

from PIL import Image

with open(f'{os.environ["PROJECT_PATH"]}/lunchbot/cred/key.yaml', encoding="UTF-8") as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)

def get_screenshot_old(path,str_today):
    """deprecated. 

    """
    img_path = f"{path}/{str_today}.png"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_argument("window-size=400,1600")
    url = cred["url"]
    
    #driver = webdriver.Chrome(DRIVER, options=chrome_options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(2)
    try:
        button = driver.find_element(By.CLASS_NAME, "close_pop_up")
        button.click()
        print("find element and click")
        time.sleep(2)
    except:
        print("can't find element")
    
    screenshot = driver.save_screenshot(img_path)
    
    driver.quit()

def get_screenshot(path,str_today):
    url = "https://bob.efoodist.com/notice/noticeDetail?notice_id=NT_230702YT71VR"
    img_path = f"{path}/{str_today}.png"
    
    #chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    service = Service(ChromeDriverManager().install())
    #chromedriver_version = "114.0.5735.16"
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    driver.get(url)
    time.sleep(1)

    # 이미지 URL 찾기
    images = driver.find_elements(By.CSS_SELECTOR, "img[src$='.png']")    
    src = images[0].get_attribute('src')

    # 이미지 다운로드
    response = requests.get(src)
    if response.status_code == 200:
        with open(img_path, 'wb') as file:
            file.write(response.content)

    driver.quit()  # 브라우저 종료


def send_slack(path, str_today):
    TOKEN = cred["SLACK_TOKEN"]
    client = WebClient(TOKEN)

    #calc date
    # 현재 날짜 구하기
    current_date = datetime.now()

    # 현재 날짜의 요일 구하기 (월요일은 0, 일요일은 6)
    current_weekday = current_date.weekday()

    # 이번 주의 월요일과 금요일 날짜 구하기
    monday_date = current_date - timedelta(days=current_weekday)  # 월요일
    str_mon = datetime.strftime(monday_date, '%m월%d일')
    friday_date = monday_date + timedelta(days=4)  # 금요일
    str_fri = datetime.strftime(friday_date, '%m월%d일')
    # 이번 주가 몇 번째 주인지 구하기
    week_number = current_date.isocalendar()[1]

    img = f"{path}/{str_today}.png"
    #img1 = f"{path}/{str_today}-01.png"
    #img2 = f"{path}/{str_today}-02.png"

    auth_test = client.auth_test()
    bot_user_id = auth_test["user_id"]
    
    #sending channel
    channel = "wlog-lunch"
    #channel = "wlog-testchannel_kiseok"

    # upload_first_file =client.files_upload(
    #     channels=channel,  # You can specify multiple channels here in the form of a string array
    #     title=f"{str_today}_01",
    #     file=img,
    #     initial_comment=f"{str_today}",
    # )

    upload_and_then_share_file = client.files_upload(
        channels=channel,  # You can specify multiple channels here in the form of a string array
        title=f"{str_today}",
        file=img,
        initial_comment=f"{week_number}주차 {str_mon} ~ {str_fri} 식단표"
    )

    channel_code = upload_and_then_share_file["file"]['channels'][0] = upload_and_then_share_file["file"]['channels'][0]
    msg_timestamp = upload_and_then_share_file["file"]['shares']['public'][channel_code][0]['ts']
    
    #reaction part
    # reaction_a = client.reactions_add(
    #     channel = channel_code,
    #     name = "choice_a",
    #     timestamp=msg_timestamp
    # )

    # reaction_b = client.reactions_add(
    #     channel = channel_code,
    #     name = "choice_b",
    #     timestamp=msg_timestamp
    # )

    # reaction_c = client.reactions_add(
    #     channel = channel_code,
    #     name = "choice_c",
    #     timestamp=msg_timestamp
    # )

    # reaction_s = client.reactions_add(
    #     channel = channel_code,
    #     name = "green_salad",
    #     timestamp=msg_timestamp
    # )

    # reaction_sw = client.reactions_add(
    #     channel = channel_code,
    #     name = "sandwich",
    #     timestamp=msg_timestamp
    # )

    # reaction_lb = client.reactions_add(
    #     channel = channel_code,
    #     name = "bento",
    #     timestamp=msg_timestamp
    # )

    # reaction_rm = client.reactions_add(
    #     channel = channel_code,
    #     name = "ramen",
    #     timestamp=msg_timestamp
    # )

    # reaction_rm = client.reactions_add(
    #     channel = channel_code,
    #     name = "zap",
    #     timestamp=msg_timestamp
    # )

def image_cut_old(path, str_today):
    """deprecated
    """
    img = f"{path}/{str_today}.png"
    # Read the image
    img = iio.imread(img)
    # Cut the image in half
    s1 = img[:1750, :]
    s2 = img[1750:, :]

    # Save each half
    imageio.imsave(f"{path}/{str_today}-01.png", s1)
    imageio.imsave(f"{path}/{str_today}-02.png", s2)

def image_cut(path, str_today):
    """
    img 가로 길이가 매번 달라서 포기

    """

    org_img_path = f"{path}/{str_today}.png"
    original = Image.open(org_img_path)

    width, height = original.size

    # 점심 메뉴 섹션의 y 좌표
    upper_y = 840  # 점심 메뉴 시작 부분
    lower_y = 2480 # 점심 메뉴 끝 부분
    """
    header 90 - 320
    칸 340
    320, 840
    """

    crop_header = (90, 840, 320, 2480)
    header = original.crop(crop_header)

    day_width = 340

    # 각 요일에 대한 이미지를 크롭하고 결과를 저장
    cropped_images_paths = []
    for day in range(5):
        left_x = 320 + day * day_width
        right_x = left_x + day_width
        cropped = original.crop((left_x, upper_y, right_x, lower_y))

        comb_width = header.width + cropped.width
        comb_height = header.height
        comb_image = Image.new('RGB', (comb_width, comb_height))
        comb_image.paste(header,(0,0))
        comb_image.paste(cropped, (header.width, 0))


        cropped_path = f'lunch_menu_{day}.png'
        comb_image.save(cropped_path)
        cropped_images_paths.append(cropped_path)


def main():
    today = datetime.now()
    print(f"{today} lunchbot starting")
    str_today = datetime.strftime(today, '%Y-%m-%d')
    img_path = f"{os.environ['PROJECT_PATH']}/lunchbot/screenshot"
    
    get_screenshot(img_path,str_today)
    
    #image_cut(img_path,str_today)
    
    send_slack(img_path,str_today)
    
    print(f"{today} lunchbot ends")
if __name__ == "__main__":
    main()

    """
    패치 예정 리스트
    사진 더 잘보이게 자르기
    상세 사진도 보여주기

    """