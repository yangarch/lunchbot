import requests
import time
import yaml
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import stat

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from slack_sdk import WebClient

from PIL import Image

load_dotenv()

with open(f'{os.environ["PROJECT_PATH"]}/lunchbot/cred/key.yaml', encoding="UTF-8") as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)


def set_chromedriver_permissions(path):
    # 사용자 권한을 읽기, 쓰기, 실행 가능하게 설정
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    # 그룹 및 다른 사용자도 실행 가능하게 설정
    os.chmod(path, stat.S_IRUSR | stat.S_IXUSR)


def get_screenshot(path, str_today):
    url = "https://bob.efoodist.com/notice/noticeDetail?notice_id=NT_230702YT71VR"
    img_path = f"{path}/{str_today}.png"

    # chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")

    driver_path = ChromeDriverManager().install()

    last_slash_index = driver_path.rfind("/")

    # chromedirver issue
    new_path = driver_path[:last_slash_index] + "/chromedriver"
    set_chromedriver_permissions(new_path)

    service = Service(new_path)
    # chromedriver_version = "114.0.5735.16"
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    driver.get(url)
    time.sleep(1)

    # 이미지 URL 찾기
    images = driver.find_elements(By.CSS_SELECTOR, "img[src$='.png']")
    if not images:
        images = driver.find_elements(By.CSS_SELECTOR, "img[src$='.jpg']")
    src = images[0].get_attribute("src")

    # 이미지 다운로드
    response = requests.get(src)
    if response.status_code == 200:
        with open(img_path, "wb") as file:
            file.write(response.content)

    driver.quit()  # 브라우저 종료


def send_slack(path, str_today):
    TOKEN = cred["SLACK_TOKEN"]
    client = WebClient(TOKEN)

    current_date = datetime.now()
    current_weekday = current_date.weekday()
    monday_date = current_date - timedelta(days=current_weekday)
    str_mon = datetime.strftime(monday_date, "%m월%d일")
    friday_date = monday_date + timedelta(days=4)
    str_fri = datetime.strftime(friday_date, "%m월%d일")
    week_number = current_date.isocalendar()[1]

    img_path = f"{path}/{str_today}.png"
    filesize = os.path.getsize(img_path)
    filename = os.path.basename(img_path)

    # Step 1: get upload URL
    upload_url_response = client.files_getUploadURLExternal(
        filename=filename,
        length=filesize
    )
    upload_url = upload_url_response["upload_url"]
    file_id = upload_url_response["file_id"]

    # Step 2: upload file
    with open(img_path, "rb") as f:
        upload_response = requests.put(upload_url, data=f)
        upload_response.raise_for_status()

    # Step 3: complete upload and share
    channel_name = "wlog-lunch"
    
    response = client.conversations_list()
    channel_id = None
    for ch in response["channels"]:
        if ch["name"] == channel_name:
            channel_id = ch["id"]
            break
    if channel_id is None:
        raise ValueError(f"Channel '{channel_name}' not found.")
    
    client.files_completeUploadExternal(
        files=[{
            "id": file_id,
            "title": f"{str_today}"
        }],
        channel_id=channel_id,
        initial_comment=f"{week_number}주차 {str_mon} ~ {str_fri} 식단표"
    )

    file_info = client.files_info(file=file_id)
    image_url = file_info["file"]["url_private"]

    client.chat_postMessage(
        channel=channel_id,
        text=f"{week_number}주차 {str_mon} ~ {str_fri} 식단표",
        blocks=[
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": f"{str_today} 식단표"
            }
        ]
    )


def image_cut(path, str_today):
    """
    img 가로 길이가 매번 달라서 포기

    """

    org_img_path = f"{path}/{str_today}.png"
    original = Image.open(org_img_path)

    width, height = original.size

    # 점심 메뉴 섹션의 y 좌표
    upper_y = 840  # 점심 메뉴 시작 부분
    lower_y = 2480  # 점심 메뉴 끝 부분
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
        comb_image = Image.new("RGB", (comb_width, comb_height))
        comb_image.paste(header, (0, 0))
        comb_image.paste(cropped, (header.width, 0))

        cropped_path = f"lunch_menu_{day}.png"
        comb_image.save(cropped_path)
        cropped_images_paths.append(cropped_path)


def main():
    today = datetime.now()
    print(f"{today} lunchbot starting")
    str_today = datetime.strftime(today, "%Y-%m-%d")
    img_path = f"{os.environ['PROJECT_PATH']}/lunchbot/screenshot"

    get_screenshot(img_path, str_today)

    # image_cut(img_path,str_today)

    send_slack(img_path, str_today)

    print(f"{today} lunchbot ends")


if __name__ == "__main__":
    main()

    """
    패치 예정 리스트
    사진 더 잘보이게 자르기
    상세 사진도 보여주기

    """
