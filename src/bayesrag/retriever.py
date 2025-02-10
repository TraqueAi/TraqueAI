from bayesrag.embedder import get_embedding
from bayesrag.vector_db import VectorDB
# from bayesrag.config import QDRANT_COLLECTION
# from bayesrag.constant import SEND_TOPIC
import time
import queue
import uuid
from loguru import logger


def get_context(query):
    qclient=VectorDB()
    
    query_embedding = get_embedding(query)
    results,score = qclient.search_vector(query_embedding)

    logger.debug(f"Score: {score}")
    if score ==None:
        logger.info("No results found")
        return
    if score > 0.60:
        logger.info(f"Found in local VectorDb as score is higher that 60% .Score {score}")
        return results
   
    else:
        logger.debug("No relevant context found in local VectorDB,Ask LLM instead.")
        return None  # TODO: return appropriate message or None for no relevant context found in local VectorDB

    
    # return qclient.search_vector(query_embedding)


# def get_Relavant_Context_from_network(query,client,REPLAY_TOPIC,collection_name):

#     query_embedding = get_embedding(query)
#     qclient=VectorDB(collection_name)

#     results = qclient.search(
#         collection_name=collection_name,
#         query_vector=query_embedding,
#         limit=1,
#     )
    
#     logger.debug("Score: ", results[0].score)
#     if results[0].score > 0.001:
#         logger.debug("No relevant context found in local VectorDB, sending query to network")
#         data = {
#             "replay_topic": REPLAY_TOPIC,
#             "query": query,
#         }
#         # TODO: send request to other node to get relevant information 
#         client.send_message(SEND_TOPIC, data)
#         count=0  
#         reply=None
#         # Check the reply queue for a response
#         while count<3:
#             try:
#                 reply = client.reply_queue.get_nowait()# Wait for a reply for 10 seconds
#                 logger.critical(f"Received reply from another node: {reply}")
#                 if reply!=None:
#                     return reply
#                 # Process the reply as needed
#             except queue.Empty:
#                 logger.warning("No reply received in the last 10 seconds")
#                 count+=1
#                 time.sleep(10)
        
        
#         return reply  # TODO: return appropriate message or None for no relevant context found in local VectorDB
    
#     else:
#         print("Found in local VectorDb")
#         return results[0].payload["data"], results[0].score
    

if __name__ == '__main__':
    user_query = input("Enter your query or type 'q' to quit: ")
    from bayesrag.mq import Mqttclient 
    ID=uuid.uuid4()
    REPLAY_TOPIC = f"USER_TOPIC-{ID}"
    collection_name=f"law_docs_global"
    client = Mqttclient(collection_name=collection_name,replyTopic=REPLAY_TOPIC)
    while user_query.lower() != "q":
        relevant_context = get_context(user_query,collection_name)
        user_query = input("\nEnter your query or type 'q' to quit: ")

