# -------------------------------------------------------------------------
# Non-production code.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to analyze documents.
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md#extract-layout

USAGE:
    python doit.py
    set the environment variables in file secrets.env
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult, ContentFormat
 

## Function to call Document Intelligence endpoint to analyze documents
def analyze_doc(client, doc):

    print("[START analyze_docs() using Document Intelligence]...")

    with open(doc, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout", 
            output_content_format=ContentFormat.MARKDOWN,
            analyze_request=f, 
            locale="en-US", 
            # pages="1",
            features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
            content_type="application/octet-stream",
        )

    result: AnalyzeResult = poller.result()
    return result.content

    
## Function to call AOAI GPT model to get business insights
def retrieve_insights(client, engine, data):

    print("\n[START retrieve_insights() using Azure OpenAI]...\n")

    # Modify system and user prompts based on the use case.
        
    # BASE_PROMPT = f"You are an AI assistant that helps people understand the given table data and extract required information in a pre-defined JSON format with key-value pair."

    # USER_PROPMT = f"give me the data points for Financial Year 2020 [Cash and Cash Equivalents, Total Assets, Goodwill & Intangible Assets, Total Assets, Net Worth or Net Equity, Total Liabilities, Debt (Short-term & Long-term), Total Liabilities, Net Income] from the following data contents. If exact data point names are not found, try to use the closest. If no similar data point names at all, then give a value null. Also provide a brief sreport of the financial report including summary of what happened, and potential risks with recommendations. Look for any references of the financial year that is requested. when returning results, format the results such that the financial year is in the top of each result sectiion."

    BASE_PROMPT = f"You are an Oil and Gas Worker executing welding job on a facility location that requires a hot work permit."

    USER_PROPMT = f"Could you please help me identify the step by step process in the job, potential hazards, and recommended PPE to be used in the process?"


    request_content = "\n==== data contents ====\n" + str(data)

    conversation = [{"role":"system", "content": BASE_PROMPT}]
    conversation.append({"role": "user", "content": USER_PROPMT + request_content})

    response = client.chat.completions.create(
        model=engine,
        messages=conversation,
        max_tokens=4096,
    )

    response_message = response.choices[0].message

    print("\n\nBASE_PROMPT: " + BASE_PROMPT)
    print("\n========\n")
    print(response_message.content)

if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        env_path = Path('.') / 'secrets.env'
        load_dotenv(dotenv_path=env_path)

        aoai_client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),  
            api_version="2023-12-01-preview",
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
        chat_engine =os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

        di_client = DocumentIntelligenceClient(
            endpoint=os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"], 
            credential=AzureKeyCredential(os.environ["AZURE_DOCUMENT_INTELLIGENCE_API_KEY"]),
            api_version="2023-10-31-preview"
        )

        path_to_sample_documents = os.path.abspath(
            os.path.join("./docs/x.pdf",
            )
        )

        content = analyze_doc(di_client, path_to_sample_documents)
        insights = retrieve_insights(aoai_client, chat_engine, content)

    except HttpResponseError as error:
        print(f"Uh-oh! Seems there was an invalid request: {error}")