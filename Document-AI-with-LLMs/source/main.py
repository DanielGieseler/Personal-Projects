from table import PhysicalStructure, LogicalStructure
from azuremanager import AzureManager
from openaimanager import OpenAIManager
import pickle
import imgkit

if __name__ == "__main__":
    TESTE = False
    if TESTE:
        print("Step 1: Import Segmentation")
        physical_structure = PhysicalStructure.from_spreadsheet('E:/Git/TableUnderstanding/example_files/header.xlsx')
    else:
        print("Step 1: Azure Segmentation")
        file_name, file_extension = "3", "pdf"
        azure_manager = AzureManager()
        result = azure_manager.analyzeDocument(f'E:/Git/TableUnderstanding/TEST/{file_name}.{file_extension}')
        tables = azure_manager.parseResultTables(result)
        physical_structure = PhysicalStructure.from_azure(tables[-1]["cells"])
    html_table = physical_structure.to_HTML()
    ###
    print("Step 2: LLM Functional Analysis")
    openai_manager = OpenAIManager()
    prompt = openai_manager.preparePrompt(html_table)
    response = openai_manager.call(prompt)
    header_region, entries_region = openai_manager.parseResponse(response)
    ###
    print("Step 3: Algorithmic Structural Analysis")
    try:
        logical_structure = LogicalStructure(physical_structure, header_region, entries_region)
        logical_structure.parse()
        df = logical_structure.to_dataframe()
    except:
        df = None
    ###
    with open(f'E:/Git/TableUnderstanding/TEST/log_{file_name}.pkl', 'wb') as f:
        pickle.dump({
            "tables_response": tables,
            "physical_structure": physical_structure,
            "functional_analysis_response": response,
            "dataframe": df
        }, f)
    print("End.")

