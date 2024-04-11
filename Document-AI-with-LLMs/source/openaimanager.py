from openai._client import OpenAI
import re
from table import PhysicalStructure
import json

class OpenAIManager:
    def __init__(self):
        with open("E:/Git/TableUnderstanding/api_keys/openai_key.txt", "r") as file:
            key = file.read()
        self.client = OpenAI(api_key = key)

    def preparePrompt(self, html_table):
        with open("E:/Git/TableUnderstanding/prompts/prompt.txt", "r") as file:
            prompt = file.read()
        return re.sub(r'<_HTML_TABLE_>', html_table, prompt)

    def call(self, prompt):
        response = self.client.chat.completions.create(
            model = "gpt-4-1106-preview", #"gpt-3.5-turbo"
            response_format = {"type": "json_object"},
            temperature = 0,
            messages = [{"role": "user", "content": prompt}]
        ).choices[0]
        if response.finish_reason != "stop":
            print(f"Abnormal finish reason: {response.finish_reason}")
        return response.message.content

    # receives a string, returns only important objects
    def parseResponse(self, response):
        try:
            json_response = json.loads(response)
            header_region = json_response["Header_Analysis"]["header_row_range"]
            entries_region = json_response["Entries_Analysis"]["entries"]
            return header_region, entries_region
        except json.JSONDecodeError:
            # Handle invalid JSON format
            print("Invalid JSON format.")
            return None, None
        except KeyError:
            # Handle missing keys in JSON
            print("Missing JSON keys.")
            return None, None

if __name__ == "__main__":
    physical_structure = PhysicalStructure.from_spreadsheet('E:/Git/TableUnderstanding/example_files/header.xlsx')
    html_table = physical_structure.to_HTML()
    ####
    openai_manager = OpenAIManager()
    prompt = openai_manager.preparePrompt(html_table)
    response = openai_manager.call(prompt)
    header_region, entries_region = openai_manager.parseResponse(response)
    print(header_region)
    print(entries_region)
    