#========================================================================================
# Document Analysis using Azure Document Intelligence Service
# Author: Manish Choudhari
# Prerequisites: Install  pip install azure-ai-formrecognizer azure-core pyodbc    
#========================================================================================

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pyodbc

# Azure Document Intelligence details
endpoint = "Add your endpoint here/"   # Your Endpoint
key = "Add your key here"  # Your Azure key
local_file_path = r"Add your input file path here\InputDoc.jpeg"  # Input scanned file

# Fields you want to extract
fields_to_extract = ["Employee Code", "Name", "Date of Birth", "Age", "Area of service", "Blood Group", "Marital Status", "Work Expereince", "Emergency Contact Number"]

# Use set to prevent duplicates
added_values = set()

# SQL Server connection string
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=SONALI;"
    "Database=test;"
    "Trusted_Connection=yes;"
)

def run_analysis():
    # Create Azure client
    credential = AzureKeyCredential(key)
    client = DocumentAnalysisClient(endpoint=endpoint, credential=credential)

    # Open document
    with open(local_file_path, "rb") as f:
        print("Analyzing document...")
        poller = client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result()

    # Connect to SQL Server
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Loop through key-value pairs
    for kvp in result.key_value_pairs:
        key_text = kvp.key.content if kvp.key else ""
        val_text = kvp.value.content if kvp.value else ""

        # Clean value
        cleaned_value = val_text.lstrip(": ").strip()

        for keyword in fields_to_extract:
            if keyword.lower() in key_text.lower():
                if cleaned_value not in added_values:
                    insert_query = """
                        INSERT INTO ExtractedFields (FieldName, FieldValue)
                        VALUES (?, ?)
                    """
                    cursor.execute(insert_query, keyword, cleaned_value)
                    conn.commit()

                    added_values.add(cleaned_value)

    conn.close()

    print("Document analysis completed! Data inserted into SQL Server table.")

if __name__ == "__main__":
    run_analysis()
