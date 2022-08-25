
def create_table(table_name):
    return f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
            codewars_completed VARCHAR(255),
            codewars_honor VARCHAR(255),
            edabit_xp VARCHAR(255)
            )
            """


def select_all(table_name):
    return f"""SELECT * FROM {table_name}"""


def update_table(table_name, col_name):
    return f"""UPDATE {table_name}
            SET {col_name} = (%s)
            """
