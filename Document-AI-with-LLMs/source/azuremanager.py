# import libraries

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import pickle

class AzureManager:
    def __init__(self):
        with open('E:/Git/TableUnderstanding/api_keys/azure_keys_and_endpoint.txt', 'r') as file:
            key = file.readline().strip()
            key2 = file.readline().strip()
            endpoint = file.readline().strip()
        self.client = DocumentAnalysisClient(
            endpoint = endpoint,
            credential = AzureKeyCredential(key)
        )

    # API call
    def analyzeDocument(self, pdf_path):
        with open(pdf_path, "rb") as pdf:
            poller = self.client.begin_analyze_document("prebuilt-layout", document = pdf)
        return poller.result()

    # parse all tables found in the document
    def parseResultTables(self, result):
        keys_to_keep = ['row_index', 'column_index', 'column_span', 'row_span', 'content']
        tables = []
        for table in result.tables:
            table = table.to_dict()
            tables.append({
                'page_number': table['bounding_regions'][0]['page_number'],
                'cells': [{key: cell[key] for key in keys_to_keep if key in cell} for cell in table['cells']]       
            })
        return tables


if __name__ == "__main__":
    azure_manager = AzureManager()
    result = azure_manager.analyzeDocument("E:/Git/TableUnderstanding/TESTE/1.pdf")
    tables = azure_manager.parseResultTables(result)
    # get one table, and send the cells to physical structure

    with open('azure_tables.pkl', 'wb') as f:
        pickle.dump(tables, f)

    
