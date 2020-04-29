import worker
import time
import random


def test1():
    time.sleep(2)


def test2():
    print("shit")
    time.sleep(6)


# A new callback function that will replace the base callback function inside of the base worker class
def new_callback(channel, method, properties, body: bytes):
    # Received a finish message, exit condition met
    if body == "finish":
        raise worker.StopWorkerException("Received finish message, exiting.")

    # THIS IS WHERE THE WORKER WILL DO THE WORK
    # print("here we do shit")
    # time.sleep(4)

    if random.randint(0, 100) < 50:
        test1()
    else:
        test2()
    # THIS IS WHERE THE WORKER WILL DO THE WORK

    # Declares the queue that the fast api will listen to in order to receive the results from
    channel.queue_declare(queue=body.decode())

    # Returns answers
    channel.basic_publish(
        exchange="",
        routing_key=body,
        body="RESULT HERE",  # THE RESULT IS RETURN IN THE BODY ARGUMENT
    )

    # Sends ack response that the message was handled, so it can be removed safely from queue
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print("starting....")
    worker_manager = worker.WorkerManager(16, "192.168.60.129", new_callback)

    worker_manager.start()


if __name__ == "__main__":
    main()
