import pika
import sys
import random

# Define the rabbit-mq connection with a set amount of retries and delays in between
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="192.168.60.129", connection_attempts=5, retry_delay=1)
)

# Connect and create a channel
channel = connection.channel()

# Declare a task_queue which is durable (saves to disk for recovery purposes)
channel.queue_declare(queue="task_queue", durable=True)


session_number: int = random.randint(1, 1_000_000_000)
session_queue = f"testing_15.2.2.3_{session_number}"
print(session_queue)

channel.basic_publish(
    exchange="",
    routing_key="task_queue",
    body=session_queue,
    properties=pika.BasicProperties(delivery_mode=2, ),  # make message persistent
)

print("pushed message to task queue to initiate return queue")

channel.queue_declare(queue=session_queue)

test_output = ""

for method_frame, properties, body in channel.consume(session_queue):
    # Display the message parts and acknowledge the message
    print(method_frame, properties, body)
    test_output = body
    channel.basic_ack(method_frame.delivery_tag)

    # Escape out of the loop after receiving a message
    if method_frame.delivery_tag == 1:
        break

channel.queue_delete(queue="hello")
connection.close()
