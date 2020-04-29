import pika
import time
import sys
import multiprocessing


# Exception for exiting the blocking consume condition when a finish message is met in the callback
class StopWorkerException(Exception):
    pass


def base_callback(channel, method, properties, body: bytes):
    # Received a finish message, exit condition met
    if body == "finish":
        raise StopWorkerException("Received finish message, exiting.")

    channel.queue_declare(queue=body.decode())

    time.sleep(4)

    channel.basic_publish(
        exchange="", routing_key=body, body="task finished",
    )

    # print(" [x] Done")
    channel.basic_ack(delivery_tag=method.delivery_tag)


class WorkerManager:
    def __init__(
        self,
        number_of_workers=multiprocessing.cpu_count(),
        host="localhost",
        callback_func=base_callback,
    ):
        self.number_of_workers = number_of_workers
        self.host = host
        self.callback = callback_func
        if sys.platform.startswith("linux"):
            self.system = "linux"
        else:
            self.system = "windows"

    def worker(self):
        while True:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host, connection_attempts=5, retry_delay=5
                )
            )
            channel = connection.channel()

            channel.queue_declare(queue=f"{self.system}_task_queue", durable=True)
            # print(" [*] Waiting for messages. To exit press CTRL+C")

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=f"{self.system}_task_queue", on_message_callback=self.callback,
            )

            try:
                channel.start_consuming()
            # except (StopWorkerException, KeyboardInterrupt):
            #     channel.stop_consuming()
            #     connection.close()
            #     break
            except pika.exceptions.ConnectionClosedByBroker:
                # Uncomment this to make the example not attempt recovery
                # from server-initiated connection closure, including
                # when the node is stopped cleanly
                #
                # break
                print("connection closed by broker")
                continue
            # Do not recover on channel errors
            except pika.exceptions.AMQPChannelError as err:
                print("Caught a channel error: {}, stopping...".format(err))
                break
            # Recover on all other connection errors
            except pika.exceptions.AMQPConnectionError:
                print("Connection was closed, retrying...")
                continue

    def start(self):
        # Creates multiprocessing pool of workers
        pool = multiprocessing.Pool(processes=self.number_of_workers)

        # Starts each worker with task
        for num in range(self.number_of_workers):
            print(f"starting pool worker {num}.")
            pool.apply_async(self.worker)

        # Stay alive
        try:
            while True:
                time.sleep(10)
        except (StopWorkerException, KeyboardInterrupt):
            print(" [*] Exiting...")
            pool.terminate()
            pool.join()
