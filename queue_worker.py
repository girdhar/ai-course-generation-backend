import json
import time
from azure.storage.queue import QueueClient
import os

QUEUE_NAME =  os.getenv("QUEUE_NAME")
queue_client = QueueClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), QUEUE_NAME)

def handle_queue_message(message_body):
    data = json.loads(message_body)
    task_id = data["task_id"]
    blob_name = data["blob_name"]

    print(f"Processing: {task_id}")
    print(f"Blob Name: {blob_name}")
    

def run_worker():
    while True:
        messages = queue_client.receive_messages()
        for msg in messages:
            handle_queue_message(msg.content)
            queue_client.delete_message(msg)
        time.sleep(5)

if __name__ == "__main__":
    run_worker()
