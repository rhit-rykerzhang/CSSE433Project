import pymongo
from pymongo import MongoClient
client = MongoClient("mongodb://433-34.csse.rose-hulman.edu:27017")
db = client['tutorial']
document = (
    {
        'Type': 'Book',
        'Title': 'Introduction to MongoDB',
        'ISBN': '9871-3051-4352',
        'Publisher': 'Rose-Hulman Press',
        'Authors': ['Austin Niccum', '10Gen', 'Tim Hawkins']
    }
)
print(type(document))
# result = db.media.insert_one(document)
# cursor = db.media.find()
# for data in cursor:
# print(data)
