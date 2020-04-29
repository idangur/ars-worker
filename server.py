from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shlex
import subprocess
import traceback
import time
import datetime


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandResponse(BaseModel):
    message: str
    time_elapsed: datetime.timedelta
    process_output: str = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(
    item_id: int = 12,  # Defaults to 12
    q: str = Query(
        ...,  # This means the parameter q is REQUIRED
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    ),
):
    return {"item_id": item_id, "q": q}


@app.get("/files/{file_path:path}")
async def read_user_me(file_path: str):
    return {"file_path": file_path}


@app.get("/test/{sleep_time}")
def sleepy(sleep_time: int):
    start = datetime.datetime.now()
    time.sleep(sleep_time)
    return {"time_elapsed": (datetime.datetime.now() - start).seconds}


@app.get("/run/{command}", response_model=CommandResponse)
def run_commands(command: str):
    start = datetime.datetime.now()
    try:
        process_output: subprocess.CompletedProcess = subprocess.run(
            shlex.split(command), capture_output=True
        )
        process_output.check_returncode()
    except subprocess.CalledProcessError:
        return {
            "message": "process return not 0",
            "time_elapsed": datetime.datetime.now() - start,
        }
    except subprocess.TimeoutExpired:
        return {
            "message": "timeout expired",
            "time_elapsed": datetime.datetime.now() - start,
        }
    except Exception:
        return {
            "message": "unkown error",
            "stacktrace": traceback.format_exc(),
            "time_elapsed": datetime.datetime.now() - start,
        }

    # os.system(f"cmd /c {command}")

    decoded_stderr: str = process_output.stderr.decode("utf-8")
    decoded_stdout: str = process_output.stdout.decode("utf-8")

    if process_output.stderr:
        return {
            "message": "subprocess fail",
            "process_output": decoded_stderr,
            "time_elapsed": datetime.datetime.now() - start,
        }

    return {
        "message": "subprocess finished",
        "process_output": decoded_stdout,
        "time_elapsed": datetime.datetime.now() - start,
    }
