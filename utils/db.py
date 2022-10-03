
def create_table(table_name):
    return f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                course_id VARCHAR(255) NOT NULL PRIMARY KEY,
                course_name VARCHAR(255) NOT NULL,
                is_nine_hole_course BOOLEAN,
                blue_par_front VARCHAR[],
                blue_par_back VARCHAR[],
                blue_hole_yardage_front VARCHAR[],
                blue_hole_yardage_back VARCHAR[],
                blue_total_yardage_front VARCHAR,
                blue_total_yardage_back VARCHAR,
                blue_handicap_front VARCHAR[],
                blue_handicap_back VARCHAR[],
                blue_slope VARCHAR,
                blue_rating VARCHAR,
                white_par_front VARCHAR[],
                white_par_back VARCHAR[],
                white_hole_yardage_front VARCHAR[],
                white_hole_yardage_back VARCHAR[],
                white_total_yardage_front VARCHAR,
                white_total_yardage_back VARCHAR,
                white_handicap_front VARCHAR[],
                white_handicap_back VARCHAR[],
                white_slope VARCHAR,
                white_rating VARCHAR,
                red_par_front VARCHAR[],
                red_par_back VARCHAR[],
                red_hole_yardage_front VARCHAR[],
                red_hole_yardage_back VARCHAR[],
                red_total_yardage_front VARCHAR,
                red_total_yardage_back VARCHAR,
                red_handicap_front VARCHAR[],
                red_handicap_back VARCHAR[],
                red_slope VARCHAR,
                red_rating VARCHAR
            )
            """


def select_all(table_name):
    return f"""SELECT * FROM {table_name}"""


def update_table(table_name, col_name):
    return f"""UPDATE {table_name}
            SET {col_name} = (%s)
            """
