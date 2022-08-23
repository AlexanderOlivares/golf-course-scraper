import os
import re
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from env_conifgs import dev_config as config
# if "PRODUCTION" in os.environ:
#     from env_configs import prod_config as config
# else:
#     from env_configs import dev_config as config

driver = config.driver

driver.get("https://www.codewars.com/users/AlexanderOlivares/stats")
time.sleep(5)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "stat")))

codewars_stats = driver.find_elements_by_class_name('stat')

codewars_total_completed_challenges = None
codewars_honor_percentile = None

for stat in codewars_stats:
    stat_text = stat.text
    descrip, value = stat_text.split(":")
    if descrip == "Total Completed Kata":
        codewars_total_completed_challenges = value
    if descrip == "Honor Percentile":
        codewars_honor_percentile = value


print(codewars_total_completed_challenges)
print(codewars_honor_percentile)


driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[1])
driver.get("https://edabit.com/user/2Qk2mFu9HBFzrB24i")

time.sleep(5)

# WebDriverWait(driver, 20).until(
#     EC.presence_of_element_located((By.XPATH, "/html/body/div/div/main/div/div/div[1]/div[1]/div[3]/div/div[1]/div[1]")))

edabit_xp = driver.find_element_by_xpath(
    "/html/body/div/div/main/div/div/div[1]/div[1]/div[3]/div/div[1]/div[1]").text


edabit_challenge_count = 10
load_more_button = driver.find_element_by_xpath(
    "/html/body/div/div/main/div/div/div[2]/div/div[2]/div[1]/div/button/span")

while load_more_button:
    try:
        load_more_button.click()
        # loaded_challenges = driver.find_elements_by_class_name("listitem")
        # print(len(loaded_challenges))
        edabit_challenge_count += 10
        time.sleep(5)
        print(edabit_challenge_count)
        load_more_button = driver.find_element_by_xpath(
            "/html/body/div/div/main/div/div/div[2]/div/div[2]/div[1]/div/button/span")
    except NoSuchElementException as e:
        print(e)
        break


print(edabit_xp)
print(edabit_challenge_count)

driver.quit()
