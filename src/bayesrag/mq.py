import paho.mqtt.client as mqtt
import time
import json

from bayesrag.retriever import get_context
from bayesrag.constant import RECEVICE_TOPIC,AGG_RECEIVE_TOPIC,AGG_SEND_TOPIC

from bayesrag.ipfs import IPFSManager
import queue
from loguru import logger


class Mqttclient:
    def __init__(self, broker_address="mqtt.eclipseprojects.io", broker_port=1883,replyTopic="USER_TOPIC-",isAdmin=False):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.replyTopic=replyTopic  # Topic to which the response will be sent.
        self.ADMIN_NODE=isAdmin
        self.ipfs=IPFSManager()
        self.reply_queue = queue.Queue()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, self.broker_port)
        self.client.loop_start()
        

    def on_connect(self,client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe(RECEVICE_TOPIC)
        client.subscribe(self.replyTopic)
        if self.ADMIN_NODE:
            client.subscribe(AGG_RECEIVE_TOPIC)
            

    def subscribe(self, topic):
        self.client.subscribe(topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        if msg.topic == self.replyTopic:
            self.handle_reply(msg.payload)  
        elif msg.topic == AGG_SEND_TOPIC:
            self.handle_vector_Message(msg.payload)
        else :
            self.handle_message(msg.payload)  # Call the function to handle the received message.

    def handle_reply(self, data):
        # Compare each node reponse and take the highest accurancy
        data = json.loads(data)
        logger.warning(f"Queue size {self.reply_queue.qsize()}")
        # Process the reply here.
        # Need Triggered Method so i can send it to receiver so he get reponse information
        self.reply_queue.put(data)

    def handle_vector_Message(self, data):
        data = json.loads(data)
        print("Handle vector message")
        print("-"*100)
        source_embedding = [self.deserialize_record(record) for record in data.get("data")]
        logger.info("received vector message", source_embedding)
        # Process Vector Message
        from bayesrag.vector_db import VectorDB
        vectorDb = VectorDB()
        vectorDb.merge_embeddings(source_embedding)
        
        directory_path=f"./qdrant_data/collections/{vectorDb.collection_name}"
        
        # Upload to IPFS
        self.ipfs.upload_directory(directory_path)

    
    def deserialize_record(self, record):
        # Convert each record back to the original format
        from qdrant_client.models import Record
        return Record(id=record['id'], payload=record['payload'], vector=record['vector'])


    def serialize_record(self,record):
        # Convert each record to a serializable format (dict)
        return {
            'id': record.id,
            'payload': record.payload,
            'vector': record.vector
        }
    
    
    def handle_message(self,data):
        data = json.loads(data)
        replayTopic=data.get('replay_topic')
        query=data.get('query')
        context,score=get_context(query)
        
        if context:
            data={"context":context,"score":score}
            self.send_message(replayTopic,data)

    def send_message(self,send_topic,payload:dict):
        payload = json.dumps(payload)  # Convert the payload to JSON string before sending it.
        self.client.publish(send_topic, payload,qos=2)
        logger.info(f"Sent message: {payload}")
    
    def send_vector(self,scroll_result):
        Vect_Data = [self.serialize_record(record) for record in scroll_result[0]]
        data={"data":Vect_Data}
        payload = json.dumps(data) 
        self.client.publish(AGG_SEND_TOPIC,payload)
        logger.info(f"Vector sent to admin: ")


    def stop(self):
        self.client.loop_stop()   
        self.client.disconnect()



    
if __name__ == "__main__":
    import uuid
    import argparse

    parser = argparse.ArgumentParser(description="Get node type information to send vector to admin")
    parser.add_argument("--collectionName", type=str, required=True,help="Name of the collection of Vector DB")
    parser.add_argument("--nodetype",type=str,help="Node Type")
    args=parser.parse_args()

    
    ID=uuid.uuid4()
    REPLAY_TOPIC = f"USER_TOPIC-{ID}"
    collections=args.collectionName
    logger.info(f"Collection Name: {collections} ")

    if args.nodetype:
        client=Mqttclient(collection_name=collections,replyTopic=REPLAY_TOPIC,isAdmin=True)  
    else:
        client=Mqttclient(collection_name=collections,replyTopic=REPLAY_TOPIC,isAdmin=False)
        QDRANT_HOST = "http://localhost:6333"  # Local Qdrant
        from qdrant_client import QdrantClient

        qclient = QdrantClient(url=QDRANT_HOST)

        
        ##TODO: 
        # Need a function to  quite,send vector and  insert new based key like quit,send,insert (provide datalocation)
    from bayesrag.utils import wait_for_commands
    while True:
            command = wait_for_commands()
            if command == 'quit':
                break
            elif command == 'send':
                scroll_result=qclient.scroll(collection_name=collections,with_vectors=True) 
                client.send_vector(scroll_result)
            elif command.startswith('insert '):
                data_location = command.split(' ', 1)[1]
                client.insert_new_data(data_location)

    client.stop()
    logger.info("MQTT client stopped.")

