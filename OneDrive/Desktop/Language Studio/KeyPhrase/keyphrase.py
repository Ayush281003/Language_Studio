from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Your endpoint and API key
endpoint = "https://mynewresourcegpii.cognitiveservices.azure.com/"
api_key = "8f7e5a654f6849f295e19c92cbdf1999"

# Authenticate the client
def authenticate_client():
    ta_credential = AzureKeyCredential(api_key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client

# Function to extract key phrases
def key_phrase_extraction(client, documents):
    response = client.extract_key_phrases(documents=documents)
    for idx, doc in enumerate(response):
        if not doc.is_error:
            print(f"\nDocument {idx + 1} key phrases:")
            for phrase in doc.key_phrases:
                print(f"\t{phrase}")
        else:
            print(f"\nDocument {idx + 1} has an error: {doc.error}")

if __name__ == "__main__":
    client = authenticate_client()
    
    # Example documents
    documents = [
        "My cat might need to see a veterinarian.",
        "The weather is amazing today.",
        "The quick brown fox jumps over the lazy dog."
    ]
    
    key_phrase_extraction(client, documents)
