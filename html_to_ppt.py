import os
import re
import tempfile
from typing import Tuple
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone

# === CONTENT EXTRACTION ===
def extract_chapters_from_html(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    chapters = []
    sections = soup.find_all(["section", "details", "div"], recursive=True)
    for sec in sections:
        title_tag = sec.find(["h2", "h3"])
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        content = sec.get_text(separator="\n", strip=True)
        chapters.append((title, content))
    return chapters

def extract_main_heading_from_html(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    heading = soup.find(["h1", "h2"])
    return heading.get_text(strip=True) if heading else "Course Title"

def delete_slide(prs: Presentation, index: int):
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    xml_slides.remove(slides[index])

# === SLIDE CREATION ===
def add_content_slide(prs, title, content, max_lines=10):
    slide_layout = prs.slide_layouts[5]
    lines = content.split('\n')
    chunks = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)]

    for i, chunk in enumerate(chunks):
        slide = prs.slides.add_slide(slide_layout)
        if slide.shapes.title:
            slide.shapes.title.text = f"{title}" + (f" (Part {i+1})" if len(chunks) > 1 else "")

        left = Inches(0.5)
        top = Inches(2.0)
        width = Inches(12.5)
        height = Inches(4.5)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        txBox.fill.background()
        tf = txBox.text_frame
        tf.word_wrap = True

        for line in chunk:
            stripped = line.strip()
            if not stripped:
                continue
            p = tf.add_paragraph()
            p.text = stripped
            p.level = 0
            p.font.size = Pt(16)
            p.font.name = 'Segoe UI'
            p.font.color.rgb = RGBColor(30, 30, 30)
            p.alignment = PP_ALIGN.LEFT
            p._element.get_or_add_pPr().buNone = True

            if re.match(r'^\d+\.\s', stripped):
                p.font.italic = True
                p.font.color.rgb = RGBColor(153, 51, 0)
            elif re.match(r'^[a-dA-D]\)', stripped):
                p.font.italic = True
                p.font.color.rgb = RGBColor(153, 51, 0)

# === PPT GENERATION AND AZURE UPLOAD ===
def generate_ppt_from_html(html_content: str, task_id: str) -> str:
    """
    Generates PPT from HTML content and uploads to Azure Blob Storage.
    Returns the public URL to the uploaded PPT.
    """
    template_path = "input.pptx"
    container_name = "aicoursecontent"  # replace with your Azure container name
    blob_name = f"{task_id}.pptx"
    azure_conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not azure_conn_str:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING environment variable")

    prs = Presentation(template_path)
    original_slide_count = len(prs.slides)

    # Add title slide
    title_layout = prs.slide_layouts[0]
    title_slide = prs.slides.add_slide(title_layout)
    if title_slide.shapes.title:
        title_slide.shapes.title.text = extract_main_heading_from_html(html_content)
    if len(title_slide.placeholders) > 1:
        title_slide.placeholders[1].text = "AI-Generated Learning Course"

    # Add chapter slides
    chapters = extract_chapters_from_html(html_content)
    for title, content in chapters:
        add_content_slide(prs, title, content)

    # Remove original template slides
    for i in range(original_slide_count - 1, -1, -1):
        delete_slide(prs, i)

    # Save to temp file and upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_file:
        local_path = tmp_file.name
        prs.save(local_path)

    try:
        blob_service = BlobServiceClient.from_connection_string(azure_conn_str)
        blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)

        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"✅ Uploaded PPTX to Azure Blob Storage: {blob_name}")

        ppt_url = generate_sas_url(blob_service, container_name, blob_name)
        return ppt_url
    finally:
        os.remove(local_path)

def generate_sas_url(blob_service, container_name, blob_name):
    sas_token = generate_blob_sas(
        account_name=blob_service.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry = datetime.now(timezone.utc) + timedelta(days=365) 
    )
    return f"https://{blob_service.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

