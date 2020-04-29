import requests
import datetime
import multiprocessing
from random import randint
from time import sleep
from pprint import pprint

ars_server = "http://192.168.60.129:8000"

api_dict = {
    1: "/run/whoami",
    2: "/scripts/windows/testing",
    3: "test/6",
    4: "/",
    5: "/files/shit/path/file/to/text.txt",
}


def main():
    api_test = int(input("number: "))

    if api_test == 2:
        req = {"ip": "15.15.15.24"}
        start = datetime.datetime.now()
        respond = requests.get(ars_server + api_dict[api_test], params=req)
        print(f"elapsed time - {datetime.datetime.now() - start}")

    else:
        respond = requests.get(ars_server + api_dict[api_test])

    pprint(respond.json())


def test_request():
    for _ in range(10):
        # Generates a random ip
        req = {"ip": f"{randint(0,256)}.{randint(0,256)}.{randint(0,256)}.{randint(0,256)}"}
        # Starts a counter
        start = datetime.datetime.now()
        # Sends the request
        respond = requests.get(ars_server + api_dict[2], params=req)

        # Prints data
        print(f"elapsed time - {datetime.datetime.now() - start}")
        pprint(respond.json())


def test():
    # Fetches number of cpu cores in pc
    cores = multiprocessing.cpu_count()

    # Creates multiprocessing pool of workers
    pool = multiprocessing.Pool(processes=cores)

    # Starts each worker with task
    for _ in range(cores):
        pool.apply_async(test_request)

    # Stay alive
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print(" [*] Exiting...")
        pool.terminate()
        pool.join()


if __name__ == "__main__":
    test()
