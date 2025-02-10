import pika
import threading
import time

# Function to send messages
def send_message():
    while True:
        time.sleep(10)  # Wait for 10 seconds
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        message = 'Hello World!'
        channel.basic_publish(exchange='', routing_key='hello', body=message)
        print(f" [x] Sent '{message}'")
        connection.close()

# Function to receive messages
def receive_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

# Start threads for sending and receiving messages
send_thread = threading.Thread(target=send_message)
receive_thread = threading.Thread(target=receive_message)

send_thread.start()
receive_thread.start()

# Keep the main thread running, otherwise signals are ignored.
send_thread.join()
receive_thread.join()
