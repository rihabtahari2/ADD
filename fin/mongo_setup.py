# fin/mongo_setup.py

import mongoengine

def init_mongoengine():
    mongoengine.connect(
        db='rihab',
        host='localhost',
        port=27017
    )
