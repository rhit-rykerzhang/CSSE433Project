import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://433-34.csse.rose-hulman.edu:27017")
# client = MongoClient("mongodb://137.112.104.247:27017")

db = client['pokemon']
# document = (
#     {
#         'Type': 'Book',
#         'Title': 'Introduction to MongoDB',
#         'ISBN': '9871-3051-4352',
#         'Publisher': 'Rose-Hulman Press',
#         'Authors': ['Austin Niccum', '10Gen', 'Tim Hawkins']
#     }
# )
# print(type(document))
# result = db.media.insert_one(document)
# cursor = db.pokedex.find({'name': '1'})
# print(cursor.min)
# db.pokedex.create_index('name-form', unique=True)
cursor = db.pokedex.find()
# exec(test)
for data in cursor:
    print(data)
# print(data['name'])
# print(cursor.)
