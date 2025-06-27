# import uvicorn
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from azure.storage.blob import BlobServiceClient
# from azure.storage.queue import QueueClient
# import os
# import uuid
# from dotenv import load_dotenv
# load_dotenv()
# from pdf_summarizer import PDFSummarizer
# import json
# import time
# from learning_course_builder import InteractiveCourseBuilder
# from generate_final_course_content import execute_task
# from threading import Thread

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Azure Blob Storage config
# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
# QUEUE_NAME =  os.getenv("QUEUE_NAME")

# # Initialize blob service client
# blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
# container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
# queue_client = QueueClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, QUEUE_NAME)
# try:
#     queue_client.create_queue()
# except Exception as e:
#     print(f"Queue already exists or failed to create: {e}")

# @app.get("/")
# def read_root():
#     return JSONResponse(content={"message": "✅ Server is running"}, status_code=200)
    
# @app.get("/status/{task_id}")
# def check_status(task_id: str):
#     blob_name = f"{task_id}.html"
#     blob_client = container_client.get_blob_client(blob_name)
#     if blob_client.exists():
#         print(f"Blob '{blob_name}' exists.")
#         return {"status": "completed"}
#     else:
#         print(f"Blob '{blob_name}' does NOT exist.")
#         return {"status": "processing"} 

# @app.get("/course_content_status/{task_id}")
# def check_status(task_id: str):
#     blob_name = f"{task_id}_final_course_content.json"
#     blob_client = container_client.get_blob_client(blob_name)
#     if blob_client.exists():
#         print(f"Blob '{blob_name}' exists.")
#         return {"status": "completed"}
#     else:
#         print(f"Blob '{blob_name}' does NOT exist.")
#         return {"status": "processing"}  

# @app.post("/upload/")
# async def upload_pdf(file: UploadFile = File(...)):
#     try:
#         if not file.filename.endswith(".pdf"):
#             raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#         task_id = str(uuid.uuid4())
#         blob_name = f"{task_id}.pdf"
#         blob_client = container_client.get_blob_client(blob_name)

#         contents = await file.read()
#         blob_client.upload_blob(contents, overwrite=True)

#         # Process PDF and summarize
#         summarizer = PDFSummarizer()
#         chunks = summarizer.read_and_chunk_pdf(blob_name)
#         summaries = summarizer.summarize_chunks(chunks)

#         summaries_text = "\n".join(summaries)
#         summary_blob_name = f"{task_id}_summary.txt"
#         container_client.get_blob_client(summary_blob_name).upload_blob(summaries_text, overwrite=True)

#         # Build structure
#         builder = InteractiveCourseBuilder()
#         structure_raw = builder.propose_course_structures(summaries_text)
#         structure_json = json.loads(structure_raw)

#         structure_json_blob_name = f"{task_id}_structure.json"
#         container_client.get_blob_client(structure_json_blob_name).upload_blob(
#             json.dumps(structure_json), overwrite=True
#         )
#         return {"task_id": task_id, "course_structure": structure_json}
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/start-course-creation")
# def start_task(data: dict):
#     html_gneration_task_id = str(uuid.uuid4())

#     task_id = str(data["task_id"])
#     blob_name = f"{task_id}.pdf"
#     summary_blob_name = f"{task_id}_summary.txt"
#     structure_json_blob_name = f"{task_id}_structure.json"

#     course_name=data["course_name"]
#     course_type=data["course_type"]
#     course_length=data["course_length"]

#     message = json.dumps({
#             "task_id": html_gneration_task_id,
#             "blob_name": blob_name,
#             "summary_blob": summary_blob_name,
#             "structure_blob": structure_json_blob_name,
#             "course_name":course_name,
#             "course_type":course_type,
#             "course_length":course_length,
#         })
#     queue_client.send_message(message)
#     return {"html_gneration_task_id": html_gneration_task_id, "status_url": f"/status/{html_gneration_task_id}"}
    

# def run_course_task():
#     while True:
#         messages = queue_client.receive_messages()
#         print("run_course_task function called.......")
#         for msg in messages:
#             # print("Message ID:", msg.id)
#             # print("Message Text:", msg.content)
#             msg_details = msg.content
#             queue_client.delete_message(msg)
#             execute_task(msg_details)
#         time.sleep(5)

# @app.on_event("startup")
# def startup_event():
#     Thread(target=run_course_task, daemon=True).start()

# # if __name__ == "__main__":
# #     uvicorn.run("main:app", host="0.0.0.0", port=8080)





from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient
import os
import uuid
from dotenv import load_dotenv
from pdf_summarizer import PDFSummarizer
import json
import time
from learning_course_builder import InteractiveCourseBuilder
from generate_final_course_content import execute_task
from threading import Thread
from html_to_ppt import generate_ppt_from_html


load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure Blob Storage config
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
QUEUE_NAME = os.getenv("QUEUE_NAME")

# Initialize blob service client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
queue_client = QueueClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, QUEUE_NAME)

try:
    queue_client.create_queue()
except Exception as e:
    print(f"Queue already exists or failed to create: {e}")

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "✅ Server is running"})

@app.route("/status/<task_id>", methods=["GET"])
def check_status(task_id):
    blob_name = f"{task_id}.html"
    blob_client = container_client.get_blob_client(blob_name)
    if blob_client.exists():
        # Download blob content as text
        blob_data = blob_client.download_blob()
        content = blob_data.readall().decode('utf-8')
        # print("Blob content:")
        # print(content)

        ppt_blob_url = generate_ppt_from_html(content, task_id)
        return {"status": "completed", "html_content": content, "ppt_url":ppt_blob_url}
    else:
        return {"status": "processing"}

@app.route("/course_content_status/<task_id>", methods=["GET"])
def check_course_content_status(task_id):
    blob_name = f"{task_id}_final_course_content.json"
    blob_client = container_client.get_blob_client(blob_name)
    if blob_client.exists():
        return {"status": "completed"}
    else:
        return {"status": "processing"}

@app.route("/upload/", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"detail": "No file uploaded"}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"detail": "Only PDF files are allowed."}), 400

    try:
        task_id = str(uuid.uuid4())
        blob_name = f"{task_id}.pdf"
        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(file.read(), overwrite=True)

        summarizer = PDFSummarizer()
        chunks = summarizer.read_and_chunk_pdf(blob_name)
        summaries = summarizer.summarize_chunks(chunks)

        summaries_text = "\n".join(summaries)
        summary_blob_name = f"{task_id}_summary.txt"
        container_client.get_blob_client(summary_blob_name).upload_blob(summaries_text, overwrite=True)

        builder = InteractiveCourseBuilder()
        structure_raw = builder.propose_course_structures(summaries_text)
        structure_json = json.loads(structure_raw)

        structure_json_blob_name = f"{task_id}_structure.json"
        container_client.get_blob_client(structure_json_blob_name).upload_blob(
            json.dumps(structure_json), overwrite=True
        )

        return jsonify({"task_id": task_id, "course_structure": structure_json})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/start-course-creation", methods=["POST"])
def start_task():
    data = request.get_json()
    html_gneration_task_id = str(uuid.uuid4())

    task_id = str(data["task_id"])
    blob_name = f"{task_id}.pdf"
    summary_blob_name = f"{task_id}_summary.txt"
    structure_json_blob_name = f"{task_id}_structure.json"

    course_name = data["course_name"]
    course_type = data["course_type"]
    course_length = data["course_length"]

    message = json.dumps({
        "task_id": html_gneration_task_id,
        "blob_name": blob_name,
        "summary_blob": summary_blob_name,
        "structure_blob": structure_json_blob_name,
        "course_name": course_name,
        "course_type": course_type,
        "course_length": course_length,
    })
    queue_client.send_message(message)
    return jsonify({"html_gneration_task_id": html_gneration_task_id, "status_url": f"/status/{html_gneration_task_id}"})

def run_course_task():
    while True:
        messages = queue_client.receive_messages()
        print("run_course_task function called.......")
        for msg in messages:
            msg_details = msg.content
            queue_client.delete_message(msg)
            execute_task(msg_details)
        time.sleep(5)

def start_background_thread():
    thread = Thread(target=run_course_task, daemon=True)
    thread.start()

start_background_thread()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
