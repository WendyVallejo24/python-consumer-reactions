# Import some necessary modules
# pip install kafka-python
# pip install pymongo
# pip install "pymongo[srv]"
from kafka import KafkaConsumer
from pymongo import MongoClient
from pymongo.server_api import ServerApi

import json

uri = 'mongodb+srv://wendy24:wendy_ptr2402@artists.klushnh.mongodb.net/?retryWrites=true&w=majority'
#uri = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.2'
#uri = "mongodb+srv://adsoft:adsoft-sito@cluster0.kzghgph.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
#client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

#try:
#    client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
#except Exception as e:
#    print(e)

# Connect to MongoDB and pizza_data database

try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    db = client.artists
    print("MongoDB Connected successfully!")
except:
    print("Could not connect to MongoDB")

consumer = KafkaConsumer('reactions',bootstrap_servers=['my-kafka-0.my-kafka-headless.kafka-wendyvallejo24.svc.cluster.local:9092'])
# Parse received data from Kafka
for msg in consumer:
    record = json.loads(msg.value)
    print(record)
    userId = record["userId"]
    objectId = record["objectId"]
    reactionId = record["reactionId"]

    # Create dictionary and ingest data into MongoDB
    try:
       reaction_rec = {'userId': userId, 'objectId': objectId, 'reactionId': reactionId }
       print (reaction_rec)
       reaction_id = db.artists_reactions.insert_one(reaction_rec)
       print("Data inserted with record ids", reaction_id)
    except:
       print("Could not insert into MongoDB")
    
    # Create dictionary and ingest data into MongoDB
    try:
       agg_result = db.artists_reactions.aggregate([
        {
            "$group": {
                "_id": {
                    "objectId": "$objectId",
                    "reactionId": "$reactionId"
                },
                "n": {"$sum": 1}
            }
        }
    ])
       db.artists_summary_reactions.delete_many({})
       for i in agg_result:
         print(i)
         summaryReactions_id = db.artists_summary_reactions.insert_one(i)
         print("Summary Reactions inserted with record ids", summaryReactions_id)

    except Exception as e:
       print(f'group by caught {type(e)}: ')
       print(e)
