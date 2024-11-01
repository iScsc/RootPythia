import logging
import sqlite3
from os import getenv, path

from database.db_structure import (
    sql_create_user_table,
    sql_add_user,
    sql_get_user,
    sql_get_users,
    sql_has_user,
)
from classes import User
from classes import Challenge


DB_FILE_NAME = "RootPythia.db"


class InvalidUser(Exception):
    def __init__(self, idx=None, message=None):
        self.idx = idx

        if message is None:
            self.message = "Invalid User"
            if self.idx is not None:
                self.message += f": {self.idx}"
        else:
            self.message = (message % self.idx) if "%s" in message else message

        super().__init__(self.message)


class DatabaseManager:
    def __init__(self, api_manager):
        self.logger = logging.getLogger(__name__)

        self.DB_FOLDER = getenv("DB_FOLDER")
        if self.DB_FOLDER is None or not path.isdir(self.DB_FOLDER):
            self.logger.critical("DB_FOLDER: '%s', is not a directory", self.DB_FOLDER)
            raise OSError(f"DB_FOLDER: '{self.DB_FOLDER}', is not a directory")

        # Init Connection object allowing interaction with the database
        db_file_path = path.join(self.DB_FOLDER, DB_FILE_NAME)
        self.db = sqlite3.connect(db_file_path)
        self.logger.info("Succesfully connected to database '%s'", db_file_path)
        self._init_db()

        self.api_manager = api_manager

    def _init_db(self):
        """Private function that initializes the database tables (see db_strucure.py)"""
        cur = self.db.cursor()
        cur.execute(sql_create_user_table)
        cur.close()

    def get_api_manager(self):
        return self.api_manager

    async def add_user(self, idx):
        """Call the API Manager to get a user by his id then create a User object and store it"""
        cur = self.db.cursor()

        # Check wether the user is already added
        if self.has_user(idx):
            return None

        # Retreive information from RootMe API
        raw_user_data = await self.api_manager.get_user_by_id(idx)
        user = User(raw_user_data)

        cur.execute(sql_add_user, user.to_tuple())
        self.db.commit()
        self.logger.debug("Add user '%s'", repr(user))
        cur.close()
        return user

    def has_user(self, idx):
        cur = self.db.cursor()
        res = cur.execute(sql_has_user, (idx, )).fetchone()
        cur.close()
        return res is not None

    def get_user(self, idx):
        """Retrieve the user object whose id matches 'id', None if not found"""
        cur = self.db.cursor()
        res = cur.execute(sql_get_user, (idx, )).fetchone()
        if res is None:
            return None
        user = User(res)
        cur.close()
        return user

    def get_users(self):
        cur = self.db.cursor()
        res = cur.execute(sql_get_users).fetchall()
        users = [User(elt) for elt in res]
        cur.close()
        return users

    async def fetch_user_new_solves(self, idx):
        user = self.get_user(idx)
        if user is None:
            raise InvalidUser(idx, "DatabaseManager.fetch_user_new_solves: User %s not in database")

        raw_user_data = await self.api_manager.get_user_by_id(idx)
        user.update_new_solves(raw_user_data)
        if not user.has_new_solves():
            self.logger.debug("'%s' hasn't any new solves", user)
            return

        self.logger.info("'%s' has %s new solves", user, user.nb_new_solves)
        for challenge_id in user.yield_new_solves(raw_user_data):
            challenge_data = await self.api_manager.get_challenge_by_id(challenge_id)
            challenge = Challenge(challenge_id, challenge_data)
            self.logger.debug("'%s' solved '%s'", repr(user), repr(challenge))
            yield challenge
