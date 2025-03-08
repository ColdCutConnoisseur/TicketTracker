
import os


basedir = os.path.abspath(os.path.dirname(__file__))

SQLITE_DB_PATH = 'sqlite:///' + os.path.join(basedir, 'test_db.sqlite')


