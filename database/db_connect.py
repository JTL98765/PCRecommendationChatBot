import database.connect as c
import database.config as cf

def connect_db():
    config = cf.load_config()
    connect = c.connect(config)
    return connect



