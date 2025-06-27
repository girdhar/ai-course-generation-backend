# from langchain.chat_models import AzureChatOpenAI
from langchain_community.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from prompts import (
    COURSE_STRUCTURE_SYSTEM_MSG,
    COURSE_STRUCTURE_HUMAN_TEMPLATE,
    COURSE_GENERATION_SYSTEM_MSG,
    COURSE_GENERATION_HUMAN_TEMPLATE,
    COURSE_GENERATION_SYSTEM_MSG_FOR_JSON,
    COURSE_GENERATION_HUMAN_TEMPLATE_FOR_JSON
)
from dotenv import load_dotenv
import os
load_dotenv()
from pdf_summarizer import PDFSummarizer
import json


class InteractiveCourseBuilder:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            api_version=os.getenv("AZURE_API_VERSION"),
            temperature=0.0
        )

    def propose_course_structures(self, summaries_text):
        prompt = [
            COURSE_STRUCTURE_SYSTEM_MSG,
            HumanMessage(content=COURSE_STRUCTURE_HUMAN_TEMPLATE.format(summaries=summaries_text))
        ]
        return self.llm(prompt).content.replace('```json','').replace('```','')

    def build_course_prompt(self, summaries_text, course_name, course_type, course_length, chosen_structure):
        return [
            COURSE_GENERATION_SYSTEM_MSG,
            HumanMessage(content=COURSE_GENERATION_HUMAN_TEMPLATE.format(
                summaries=summaries_text,
                course_name=course_name,
                course_type=course_type,
                course_length=course_length,
                structure=chosen_structure
            ))
        ]
    
    def build_course_prompt_for_json(self, summaries_text, course_name, course_type, course_length, chosen_structure):
        return [
            COURSE_GENERATION_SYSTEM_MSG_FOR_JSON,
            HumanMessage(content=COURSE_GENERATION_HUMAN_TEMPLATE_FOR_JSON.format(
                summaries=summaries_text,
                course_name=course_name,
                course_type=course_type,
                course_length=course_length,
                structure=chosen_structure
            ))
        ]

    def generate_interactive_course(self, summaries, course_name, course_type, course_length, structure_choice, output_type):
        print("structure choice", structure_choice)
        # full_summary = "\n".join(summaries)
        full_summary = summaries
        if output_type == "html":
            prompt = self.build_course_prompt(
                summaries_text=full_summary,
                course_name=course_name,
                course_type=course_type,
                course_length=course_length,
                chosen_structure=structure_choice
            )
            response = self.llm(prompt)
            response = response.content
            clear_resp = response.replace('```html','').replace('```','')
            return clear_resp
        else:
            prompt = self.build_course_prompt_for_json(
                summaries_text=full_summary,
                course_name=course_name,
                course_type=course_type,
                course_length=course_length,
                chosen_structure=structure_choice
            )
            response = self.llm(prompt)
            response = response.content
            clear_resp = response.replace('```json','').replace('```','')
            return clear_resp
