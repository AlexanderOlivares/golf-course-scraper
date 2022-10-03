from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
import json
# import sentry_sdk
from utils.db import select_all, create_table, update_table

# sentry_sdk.init(
#     dsn="https://267bf5c2907c4df6a33e064e046120e8@o1142418.ingest.sentry.io/6683044",
#     traces_sample_rate=1.0
# )

if "PRODUCTION" in os.environ:
    from env_conifgs import prod_config as config
else:
    from env_conifgs import dev_config as config

try:
    driver = config.driver

    # add env var here
    driver.get(
        "")

    # time.sleep(7)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "right-content")))

    get_course = driver.find_elements_by_class_name("right-content")

    parse_by_line = get_course[0].text.split("\n")
    print(parse_by_line)

    course_deatils = {
        "course_name": "",
        "is_nine_hole_course": True,
        "blue": {
            "par_front": [],
            "par_back": [],
            "hole_yardage_front": [],
            "hole_yardage_back": [],
            "total_yardage_front": "",
            "total_yardage_back": "",
            "handicap_front": [],
            "handicap_back": [],
            "slope": "",
            "rating": "",
        },
        "white": {
            "par_front": [],
            "par_back": [],
            "hole_yardage_front": [],
            "hole_yardage_back": [],
            "total_yardage_front": "",
            "total_yardage_back": "",
            "handicap_front": [],
            "handicap_back": [],
            "slope": "",
            "rating": "",
        },
        "red": {
            "par_front": [],
            "par_back": [],
            "hole_yardage_front": [],
            "hole_yardage_back": [],
            "total_yardage_front": "",
            "total_yardage_back": "",
            "handicap_front": [],
            "handicap_back": [],
            "slope": "",
            "rating": "",
        }
    }

    tee_dict = {
        "blue": "blue",
        "white": "white",
        "red": "red",
    }

    def get_tee_color(tee):
        tee_dict = {
            "Champion": "blue",
            "Men": "white",
            "Women": "red"
        }
        if tee in tee_dict:
            return tee_dict[tee]

    course_deatils["course_name"] = parse_by_line[0]

    current_tee_color = None
    front_or_back_nine = "front"

    for i in parse_by_line:
        parse_line = i.split(" ")

        if parse_line[0] == "Back":
            front_or_back_nine = "back"
            course_deatils["is_nine_hole_course"] = False

        tee_color = get_tee_color(parse_line[0])

        if tee_color:
            current_tee_color = tee_color
        if current_tee_color not in tee_dict:
            continue
        if tee_color:
            course_deatils[current_tee_color][f"hole_yardage_{front_or_back_nine}"] = parse_line[2:-3]
            course_deatils[current_tee_color][f"total_yardage_{front_or_back_nine}"] = parse_line[11]
            course_deatils[current_tee_color]["rating"] = parse_line[12]
            course_deatils[current_tee_color]["slope"] = parse_line[13]
        if parse_line[0] == "Par":
            course_deatils[current_tee_color][f"par_{front_or_back_nine}"] = parse_line[1:]
        if parse_line[0] == "S.I.":
            course_deatils[current_tee_color][f"handicap_{front_or_back_nine}"] = parse_line[1:]

    print(json.dumps(course_deatils, indent=2))

    try:
        cur = config.cursor
        conn = config.conn

        create_table_command = create_table("courses")
        cur.execute(create_table_command)
        conn.commit()

        insert_command = f'INSERT INTO courses (course_id, course_name, is_nine_hole_course) VALUES (%s, %s, %s)'
        insert_values = ("1234-a", course_deatils["course_name"],
                         course_deatils["is_nine_hole_course"])
        cur.execute(insert_command, insert_values)
        conn.commit()
        print('row inserted')

        # TODO gather valid items to make the insert command
        # column names are comma seperated string
        # values %s * lenght of col names
        # insert values is a tuple
        for k, v in course_deatils.items():
            if k in ["red", "white", "blue"]:
                print(v)

    except Exception as e:
        print(str(e))
        # sentry_sdk.capture_exception(e)
    finally:
        if cur is not None:
            print('cursor was open')
            cur.close()
        if conn is not None:
            print('connection was successful')

except NoSuchElementException:
    print(str(NoSuchElementException))
    # sentry_sdk.capture_exception(NoSuchElementException)
    driver.quit()

except Exception as e:
    print(str(e))
    # sentry_sdk.capture_exception(e)
    driver.quit()

finally:
    driver.quit()
