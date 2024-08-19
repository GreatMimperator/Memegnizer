import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

SLEEP_BETWEEN_ACTIONS_SECS = 1


def style_contains_pointer_events(locator):
    def _predicate(driver):
        element = driver.find_element(*locator)
        style = element.get_attribute('style')
        return 'pointer-events: unset' in style

    return _predicate


def receive_image_ocr(image_full_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # не открывать gui браузера

    # Настройка и запуск вебдрайвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://www.imgocr.com/")
        driver.set_window_size(1142, 1398)
        time.sleep(SLEEP_BETWEEN_ACTIONS_SECS)
        driver.find_element(By.CSS_SELECTOR, ".icon").click()
        time.sleep(SLEEP_BETWEEN_ACTIONS_SECS)
        driver.find_element(By.ID, "fileInput").send_keys(image_full_path)
        time.sleep(SLEEP_BETWEEN_ACTIONS_SECS)
        driver.find_element(By.ID, "submit_processor").click()
        WebDriverWait(driver, 30).until(
            style_contains_pointer_events((By.CSS_SELECTOR, ".justify-content-around > a:nth-child(2)"))
        )
        return driver.find_elements(By.TAG_NAME, "textarea")[0].get_attribute("value")
    finally:
        driver.close()


if __name__ == '__main__':
    print(
        receive_image_ocr(
            "/home/imperator/Downloads/Downloads с телефона/Download-images-videos-only-2/Wn8sQ0rnK2U.png"
        )
    )
