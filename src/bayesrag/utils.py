from enum import Enum
from loguru import logger
class ClassificationResult(Enum):
    """
    a ClassificationResult enum.

    Returns:
        ClassificationResult.YES if the query is classified as a law-related question, 
        ClassificationResult.NO if it's not a law-related question, 
        ClassificationResult.ERROR if there's an error parsing the response.
    """
    
    YES = "yes"
    NO = "no"
    ERROR = "error"

def display_commands():
    logger.info("Available commands:")
    print("1. 'quit' - Exit the application ")
    print("2. 'query' - Query from vector with LLM")
    print("3. 'send' - Send vector data")
    print("4. 'insert <data_location>' - Insert new data from the specified location")

def wait_for_commands():
    
    
    while True:
        display_commands()
        command = input("\nEnter your command: ").strip().lower()
        
        if command == 'quit':
            return 'quit'
        elif command == 'query':
            return 'query'
        elif command == 'send':
            return 'send'
        elif command.startswith('insert '):
            return command
        else:
            logger.warning("Invalid command. Please enter a valid command.")