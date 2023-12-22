sql_create_user_table = """ CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            username text NOT NULL,
                            score int,
                            rank int,
                            nb_solves int
                        );"""


sql_add_user = """INSERT INTO users(id,username,score,rank,nb_solves) VALUES(?,?,?,?,?);"""
