import requests
import time
import yaml
import os
from datetime import date, datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from slack_sdk import WebClient
import imageio.v3 as iio
import imageio

with open(f'{os.environ["JPOTV"]}/cred/path.yaml', encoding="UTF-8") as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)

def get_screenshot(path,str_today):
    img_path = f"{path}/{str_today}.png"
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_argument("window-size=400,1600")
    url = cred["url"]
    
    #driver = webdriver.Chrome(DRIVER, options=chrome_options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
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

def send_slack(path, str_today):
    TOKEN = cred["SLACK_TOKEN"]
    client = WebClient(TOKEN)

    img1 = f"{path}/{str_today}-01.png"
    img2 = f"{path}/{str_today}-02.png"

    auth_test = client.auth_test()
    bot_user_id = auth_test["user_id"]
    
    #sending channel
    channel = "wlog-lunch"
    #channel = "wlog-testchannel_kiseok"

    upload_first_file =client.files_upload(
        channels=channel,  # You can specify multiple channels here in the form of a string array
        title=f"{str_today}_01",
        file=img1,
        initial_comment=f"{str_today}",
    )

    upload_and_then_share_file = client.files_upload(
        channels=channel,  # You can specify multiple channels here in the form of a string array
        title=f"{str_today}_02",
        file=img2
    )

    channel_code = upload_and_then_share_file["file"]['channels'][0] = upload_and_then_share_file["file"]['channels'][0]
    msg_timestamp = upload_and_then_share_file["file"]['shares']['public'][channel_code][0]['ts']
    
    #reaction part
    reaction_a = client.reactions_add(
        channel = channel_code,
        name = "choice_a",
        timestamp=msg_timestamp
    )

    reaction_b = client.reactions_add(
        channel = channel_code,
        name = "choice_b",
        timestamp=msg_timestamp
    )

    reaction_c = client.reactions_add(
        channel = channel_code,
        name = "choice_c",
        timestamp=msg_timestamp
    )

    reaction_s = client.reactions_add(
        channel = channel_code,
        name = "green_salad",
        timestamp=msg_timestamp
    )

    reaction_sw = client.reactions_add(
        channel = channel_code,
        name = "sandwich",
        timestamp=msg_timestamp
    )

    reaction_lb = client.reactions_add(
        channel = channel_code,
        name = "bento",
        timestamp=msg_timestamp
    )

    reaction_rm = client.reactions_add(
        channel = channel_code,
        name = "ramen",
        timestamp=msg_timestamp
    )

    reaction_rm = client.reactions_add(
        channel = channel_code,
        name = "zap",
        timestamp=msg_timestamp
    )

def image_cut(path, str_today):
    img = f"{path}/{str_today}.png"
    # Read the image
    img = iio.imread(img)
    # Cut the image in half
    s1 = img[:1750, :]
    s2 = img[1750:, :]

    # Save each half
    imageio.imsave(f"{path}/{str_today}-01.png", s1)
    imageio.imsave(f"{path}/{str_today}-02.png", s2)

def main():
    today = datetime.now()
    print(f"{today} lunchbot starting")
    str_today = datetime.strftime(today, '%Y-%m-%d')
    img_path = f"{os.environ['PROJECT_PATH']}/lunchbot/screenshot"
    
    get_screenshot(img_path,str_today)
    
    image_cut(img_path,str_today)
    
    send_slack(img_path,str_today)
    
    print(f"{today} lunchbot ends")
if __name__ == "__main__":
    main()

    """
    패치 예정 리스트
    사진 더 잘보이게 자르기
    상세 사진도 보여주기

    """