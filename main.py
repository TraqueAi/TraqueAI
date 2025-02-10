import argparse
import sys
from bayesrag.data_loader import load_directory_pdf
from bayesrag.text_splitter import split_texts
from bayesrag.vector_db import  VectorDB
from bayesrag.retriever import get_context
from bayesrag.generator import generate_response,classify_query
from bayesrag.utils import ClassificationResult
from bayesrag.evaluator import deepEvalutor
from bayesrag.config import QDRANT_HOST,QDRANT_COLLECTION,REPLAY_TOPIC

from bayesrag.mq import Mqttclient
from qdrant_client import QdrantClient
from bayesrag.utils import wait_for_commands
from loguru import logger





logger.debug(f"QDRANT_HOST: {QDRANT_HOST}", )

def query():
    user_query = input("Enter your query or type 'q' to quit: ")

    while user_query.lower() != "q":
        relevant_context = get_context(user_query)
        print("-" * 100)
        # TODO 
        # Query classification
        # result = classify_query(user_query)

        # if result == ClassificationResult.YES:
        #     relevant_context = get_context(user_query,collection_name=QDRANT_COLLECTION)

        #     print("-" * 100)
        # else:
        #     relevant_context = None
        response_text = ""
        for text in generate_response(user_query, relevant_context):
            print(text, end=" ")
            response_text += text
        # Prompt the user to decide if evaluation is needed
        is_evaluator = input("\nDo you need evaluation? (Y/N): ").strip().lower()

        if is_evaluator == 'y':
            evaluator: dict = deepEvalutor(user_query,response_text,[relevant_context])  # Assuming this function returns a dictionary with score and reason
            print(f"Score: {evaluator['score']}\nReason: {evaluator['reason']}")
        elif is_evaluator == 'n':
            print("Evaluation skipped.")
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
        user_query = input("\nEnter your query or type 'q' to quit: ")

def insertData(DATA_DIR,QDRANT_COLLECTION):
    # Load and split documents
    documents = load_directory_pdf(DATA_DIR)
    text_chunks = split_texts(documents)
    
    # Create vector database and upsert embeddings
    vectorDb=VectorDB(QDRANT_COLLECTION)
    vectorDb.create_db()
    vectorDb.upsert_embeddings(text_chunks)
    

def main():
    parser = argparse.ArgumentParser(description="Run the BayesRAG query system.")
    parser.add_argument('--data-dir', type=str, help="Directory containing the PDF documents.")
    parser.add_argument("--nodetype",type=str,help="Node Type")    
    args = parser.parse_args()


    if args.nodetype is not None and args.nodetype.lower() == "admin":
        client=Mqttclient(replyTopic=REPLAY_TOPIC,isAdmin=True)  
    else:
        client=Mqttclient(replyTopic=REPLAY_TOPIC,isAdmin=False)

    qclient = QdrantClient(url=QDRANT_HOST)
    if args.data_dir:
        insertData(args.data_dir,QDRANT_COLLECTION)
        logger.info("PreProcess completed successfully.")

    while True:
            command = wait_for_commands()
            if command == 'quit':
                logger.warning('Quitting')
                break

            elif command =='query':
                query()

            elif command == 'send':
                scroll_result=qclient.scroll(collection_name=QDRANT_COLLECTION,with_vectors=True) 
                client.send_vector(scroll_result)
            elif command.startswith('insert '):
                data_location = command.split(' ', 1)[1]
                insertData(data_location,QDRANT_COLLECTION)
                logger.info("insertData completed successfully.")


    client.stop()
    logger.info("MQTT client stopped.")            

if __name__ == "__main__":
    main()
