from os.path import abspath, dirname
import mysql.connector as mysql
from lib.bot import config

class MOC_DB:
    def __init__(self) -> None:
        pass

    def connect(self):
        self.connection = mysql.connect(user=config["DATABASE"]["USER"], password=config["DATABASE"]["PASS"], host=config["DATABASE"]["HOST"], database=config["DATABASE"]["DB_NAME"], autocommit=True)
        self.cursor = self.connection.cursor(buffered=True)

    def execute(self, command, *values):
        self.cursor.execute(command, tuple(values))

    def field(self, command, *values):
        self.cursor.execute(command, tuple(values))
        fetch = self.cursor.fetchone()
        if fetch is not None:
            return fetch[0]
        return None

    def record(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchone()

    def records(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchall()

    def column(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return [item[0] for item in self.cursor.fetchall()]



