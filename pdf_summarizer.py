# from langchain.chat_models import AzureChatOpenAI

# from langchain_openai import AzureChatOpenAI
# from langchain_openai import AzureChatOpenAI
from langchain_community.chat_models import AzureChatOpenAI



from langchain.schema import SystemMessage, HumanMessage
from PyPDF2 import PdfReader
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

class PDFSummarizer:
    """
    A utility class to summarize PDF documents using Azure OpenAI and LangChain.
    Splits the document into chunks, summarizes each asynchronously, and returns the combined result.
    """
    def __init__(self):
        """
        Initialize the PDF summarizer with chunking and Azure OpenAI LLM settings.
        """
        self.azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        self.pages_per_chunk = int(os.getenv("PAGES_PER_CHUNK"))
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            api_version=os.getenv("AZURE_API_VERSION"),
            temperature=0.0
        )

    def read_and_chunk_pdf(self, blob_name):
        """
        Reads a PDF from Azure Blob Storage and chunks it into segments of defined page size.

        Returns:
            List of tuples: [((start_page, end_page), chunk_text)]
        """
        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
        container_client = blob_service_client.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Download and read the blob as bytes
        pdf_bytes = blob_client.download_blob().readall()
        reader = PdfReader(BytesIO(pdf_bytes))

        chunks = []
        temp_text = ""
        start_page = 1

        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                temp_text += f"\n\n--- Page {i} ---\n{text.strip()}"
            if i % self.pages_per_chunk == 0 or i == len(reader.pages):
                chunks.append(((start_page, i), temp_text.strip()))
                temp_text = ""
                start_page = i + 1

        return chunks

    def build_prompt(self, start_page, end_page, chunk_text):
        """
        Builds the system and user messages for summarizing a given chunk.

        Args:
            start_page (int): Start page number
            end_page (int): End page number
            chunk_text (str): Extracted text of the chunk

        Returns:
            List of LangChain message objects
        """
        return [
            SystemMessage(content=(
                "You are a highly intelligent assistant that specializes in reading and summarizing PDF documents. "
                "Your task is to accurately and clearly summarize the content of the provided PDF pages. "
                "Ensure that you retain all key information, facts, data points, and context. "
                "Do not omit any important detail or rephrase in a way that changes the original meaning."
            )),
            HumanMessage(content=(
                f"Please summarize the content from **pages {start_page} to {end_page}** of the PDF document below. "
                "Make sure the summary is detailed, organized, and faithful to the original content:\n\n"
                f"{chunk_text}"
            ))
        ]

    def summarize_chunks(self, chunks):
        """
        Summarizes each chunk of the document asynchronously using a thread pool.

        Args:
            chunks (list): List of ((start_page, end_page), text) tuples

        Returns:
            List of summary strings for each chunk
        """
        summaries = []

        def summarize_single_chunk(start_end, chunk_text):
            start_page, end_page = start_end
            prompt = self.build_prompt(start_page, end_page, chunk_text)
            response = self.llm(prompt)
            return f"Pages {start_page}-{end_page} Summary:\n{response.content}\n\n"

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_chunk = {
                executor.submit(summarize_single_chunk, start_end, chunk_text): (start_end, chunk_text)
                for start_end, chunk_text in chunks
            }

            for future in as_completed(future_to_chunk):
                try:
                    result = future.result()
                    summaries.append(result)
                except Exception as e:
                    summaries.append(f"Error summarizing chunk: {e}")

        return summaries
    

# summarizer = PDFSummarizer()
# blob_name = "7b448b13-014b-4a0d-b455-c3dea6fe8cd4.pdf"
# chunks = summarizer.read_and_chunk_pdf(blob_name)
# # # print("chunks")
# summaries = summarizer.summarize_chunks(chunks)
# print("\n".join(summaries))
