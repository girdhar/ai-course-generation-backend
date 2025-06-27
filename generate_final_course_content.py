from learning_course_builder import InteractiveCourseBuilder
from azure.storage.blob import BlobServiceClient
import os
import json

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

def execute_task(message_body):
    data = json.loads(message_body)
    task_id = data["task_id"]
    summaries = read_blob_as_text(data["summary_blob"])
    # print("Summary from Blob = ", summaries)
    course_name=data["course_name"]
    course_type=data["course_type"]
    course_length=data["course_length"]
    course_length_structure = read_blob_as_text(data["structure_blob"])
    # print("Structure from Blob = ", course_length_structure)
    builder = InteractiveCourseBuilder()
    html_course = builder.generate_interactive_course(
        summaries=summaries,
        course_name=course_name,
        course_type=course_type,
        course_length=course_length,
        structure_choice=course_length_structure, output_type="html"
    )
    course_html_blob_name = f"{task_id}.html"
    container_client.get_blob_client(course_html_blob_name).upload_blob(html_course, overwrite=True)

    course_final_json = builder.generate_interactive_course(
        summaries=summaries,
        course_name=course_name,
        course_type=course_type,
        course_length=course_length,
        structure_choice=course_length_structure, output_type="json"
    )
    course_json_blob_name = f"{task_id}_final_course_content.json"
    container_client.get_blob_client(course_json_blob_name).upload_blob(course_final_json, overwrite=True)
    print("Task Execution is completed....")

def read_blob_as_text(blob_name: str) -> str:
    blob_client = container_client.get_blob_client(blob_name)
    downloader = blob_client.download_blob()
    content = downloader.readall().decode('utf-8')
    return content
