import os
import time
import random
import json
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_TOPIC_TEST = os.environ.get("KAFKA_TOPIC_TEST", "test")
KAFKA_API_VERSION = os.environ.get("KAFKA_API_VERSION", "7.3.1")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    api_version=KAFKA_API_VERSION,
)
i = 0
while i <= 30:
    producer.send(
        KAFKA_TOPIC_TEST,
        json.dumps({"message": f"Hello, Kafka! - test {i}"}).encode("utf-8"),
    )
    i += 1
    time.sleep(random.randint(1, 5))
producer.flush()
