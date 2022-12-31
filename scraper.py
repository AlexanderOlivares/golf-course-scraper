from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
import json
import uuid
import psycopg2.extras
from utils.db import create_table


def scrape_golf_course(course_urls):

    if "PRODUCTION" in os.environ:
        from env_conifgs import prod_config as config
    else:
        from env_conifgs import dev_config as config

    try:
        driver = config.driver

        for i in range(len(course_urls)):

            course_locations = course_urls[i].split("/")
            course_country = course_locations[4]
            course_state = course_locations[5]
            course_city = course_locations[6]

            driver.get(course_urls[i])

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "right-content")))

            get_course = driver.find_elements_by_class_name("right-content")

            course_scraped_text_list_by_newline = get_course[0].text.split(
                "\n")

            course_deatils = {
                "course_name": "",
                "is_nine_hole_course": True,
            }

            course_deatils["course_name"] = course_scraped_text_list_by_newline[0]

            tee_dict = {
                "blue": "blue",
                "white": "white",
                "red": "red",
            }

            for key in tee_dict.keys():
                course_deatils[key] = {
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

            def get_tee_color(tee_name):
                tee_name_to_color = {
                    "Champion": "blue",
                    "Men": "white",
                    "Women": "red"
                }
                if tee_name in tee_name_to_color:
                    return tee_name_to_color[tee_name]

            current_tee_color = None
            front_or_back_nine = "front"

            for scraped_newline in course_scraped_text_list_by_newline:
                newline_word_list = scraped_newline.split(" ")

                if newline_word_list[0] == "Back":
                    front_or_back_nine = "back"
                    course_deatils["is_nine_hole_course"] = False

                tee_color = get_tee_color(newline_word_list[0])

                if tee_color:
                    current_tee_color = tee_color
                if current_tee_color not in tee_dict:
                    continue
                if tee_color:
                    course_deatils[current_tee_color][
                        f"hole_yardage_{front_or_back_nine}"] = newline_word_list[2:-3]
                    course_deatils[current_tee_color][
                        f"total_yardage_{front_or_back_nine}"] = newline_word_list[11]
                    course_deatils[current_tee_color]["rating"] = newline_word_list[13]
                    course_deatils[current_tee_color]["slope"] = newline_word_list[12]
                if newline_word_list[0] == "Par":
                    course_deatils[current_tee_color][f"par_{front_or_back_nine}"] = newline_word_list[1:]
                if newline_word_list[0] == "S.I.":
                    course_deatils[current_tee_color][f"handicap_{front_or_back_nine}"] = newline_word_list[1:]

            print(json.dumps(course_deatils, indent=2))

            try:
                cur = config.cursor
                conn = config.conn

                create_table_command = create_table("courses")
                cur.execute(create_table_command)
                conn.commit()

                course_id = uuid.uuid4()
                psycopg2.extras.register_uuid()

                # non specific to tee color
                cols_to_insert = "course_id, course_name, course_country, course_state, course_city, is_nine_hole_course"
                vals_to_insert = [course_id, course_deatils["course_name"], course_country, course_state, course_city,
                                  course_deatils["is_nine_hole_course"]]

                # gather the columns that are specific to tee color
                for k in course_deatils.keys():
                    if k in tee_dict:
                        tee_color = k
                        for key, val in course_deatils[k].items():
                            if val:
                                cols_to_insert += f", {tee_color}_{key}"
                                vals_to_insert.append(val)

                placeholders = "%s, " * len(vals_to_insert)
                insert_command = f'INSERT INTO courses ({cols_to_insert}) VALUES ({placeholders[:-2]})'
                insert_values = tuple(vals_to_insert)
                cur.execute(insert_command, insert_values)
                conn.commit()
                print('row inserted')

            except Exception as e:
                print(str(e))
            finally:
                if cur is not None and (i < (len(course_urls) - 1)):
                    print('keeping cursor open')
                else:
                    print('closing cursor')
                    cur.close()
                if conn is not None:
                    print('connection was successful')

    except NoSuchElementException:
        print(str(NoSuchElementException))
        driver.quit()

    except Exception as e:
        print(str(e))
        driver.quit()

    finally:
        driver.quit()


# add urls to scrape to list
courses_to_scrape = [
    "https://courses.swingu.com/courses/United-States-of-America/Texas/Burnet/Delaware-Springs-Golf-Course/44545"]

scrape_golf_course(courses_to_scrape)
