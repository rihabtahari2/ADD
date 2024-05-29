# fin/mongo_setup.py

from mongoengine import connect
from django.conf import settings
import logging
def connect_db():
    try:
        connect(
            db=settings.MONGOENGINE_USER['name'],
            username=settings.MONGOENGINE_USER['username'],
            password=settings.MONGOENGINE_USER['password'],
            host=settings.MONGOENGINE_USER['host'],
            port=settings.MONGOENGINE_USER['port'],
        )
        logging.info("MongoDB connection established successfully.")
    except Exception as e:
        logging.error("Failed to connect to MongoDB: %s", e)
