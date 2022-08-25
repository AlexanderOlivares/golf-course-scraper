from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
import sentry_sdk
from utils.db import select_all, create_table, update_table

sentry_sdk.init(
    dsn="https://267bf5c2907c4df6a33e064e046120e8@o1142418.ingest.sentry.io/6683044",
    traces_sample_rate=1.0
)

if "PRODUCTION" in os.environ:
    from env_conifgs import prod_config as config
else:
    from env_conifgs import dev_config as config

try:
    driver = config.driver

    driver.get("https://www.codewars.com/users/AlexanderOlivares/stats")

    time.sleep(7)

    WebDriverWait(driver, 20).until(
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

    print(
        f'Codewars challenges completed: {codewars_total_completed_challenges}')
    print(f'Codewars honor percentile: {codewars_honor_percentile}')

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://edabit.com/user/2Qk2mFu9HBFzrB24i")

    time.sleep(7)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/main/div/div/div[1]/div[1]/div[3]/div/div[1]/div[1]")))

    edabit_xp = driver.find_element_by_xpath(
        "/html/body/div/div/main/div/div/div[1]/div[1]/div[3]/div/div[1]/div[1]").text

    print(f'edabit xp: {edabit_xp}')

    try:
        cur = config.cursor
        conn = config.conn

        create_table_command = create_table("code_challenge_stats")
        cur.execute(create_table_command)
        conn.commit()

        select_query = select_all("code_challenge_stats")
        cur.execute(select_query)
        existing_stats = cur.fetchall()

        time.sleep(5)

        if not existing_stats:
            insert_command = f'INSERT INTO code_challenge_stats (codewars_completed, codewars_honor, edabit_xp) VALUES (%s, %s, %s)'
            insert_values = (codewars_total_completed_challenges,
                             codewars_honor_percentile, edabit_xp)

            cur.execute(insert_command, insert_values)
            conn.commit()
            print('row inserted')

        if existing_stats:
            existing_codewars_completed, existing_codewars_honor, existing_edabit_xp = existing_stats[
                0]

            if int(codewars_total_completed_challenges) > int(existing_codewars_completed):
                update_command = update_table(
                    "code_challenge_stats", "codewars_completed")
                cur.execute(update_command,
                            (codewars_total_completed_challenges,))
                conn.commit()
                print(
                    f'updated codewars completed to {codewars_total_completed_challenges}')

            if codewars_honor_percentile != existing_codewars_honor:
                update_command = update_table(
                    "code_challenge_stats", "codewars_honor")
                cur.execute(update_command, (codewars_honor_percentile,))
                conn.commit()
                print(f'updated codewars honor to {codewars_honor_percentile}')

            if int(edabit_xp.replace(",", "")) > int(existing_edabit_xp.replace(",", "")):
                update_command = update_table(
                    "code_challenge_stats", "edabit_xp")
                cur.execute(update_command, (edabit_xp,))
                conn.commit()
                print(f'updated edabit xp {edabit_xp}')

    except Exception as e:
        print(str(e))
        sentry_sdk.capture_exception(e)
    finally:
        if cur is not None:
            print('cursor was open')
            cur.close()
        if conn is not None:
            print('connection was successful')

except NoSuchElementException:
    print(str(NoSuchElementException))
    sentry_sdk.capture_exception(NoSuchElementException)
    driver.quit()

except Exception as e:
    print(str(e))
    sentry_sdk.capture_exception(e)
    driver.quit()

finally:
    driver.quit()
