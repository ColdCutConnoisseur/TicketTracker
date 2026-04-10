"""DB path and connection config"""

import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

host = "hirenick.mysql.pythonanywhere-services.com"
user = "hirenick"
db = "hirenick$Tickets"

SQLITE_DB_PATH = 'sqlite:///' + os.path.join(basedir, 'test_db.sqlite')

MYSQL_HOSTED_DB_PATH = f"mysql://{user}:{os.getenv('DB_PASS')}@{host}/{db}"


USE_HOSTED = False
MY_DB = None

if USE_HOSTED:
    MY_DB = MYSQL_HOSTED_DB_PATH

elif not USE_HOSTED:
    MY_DB = SQLITE_DB_PATH
