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

# Function to find linked entities
def find_linked_entities(client, documents):
    response = client.recognize_linked_entities(documents=documents)
    for idx, doc in enumerate(response):
        if not doc.is_error:
            print(f"\nDocument {idx + 1}:")
            for entity in doc.entities:
                print(f"\tName: {entity.name}")
                print(f"\tURL: {entity.url}")
                print(f"\tData Source: {entity.data_source}")
                print("\tMatches:")
                for match in entity.matches:
                    print(f"\t\tText: {match.text}")
                    print(f"\t\tConfidence Score: {match.confidence_score:.2f}")
                    print(f"\t\tOffset: {match.offset}")
                    print(f"\t\tLength: {match.length}")
        else:
            print(f"\nDocument {idx + 1} has an error: {doc.error}")

if __name__ == "__main__":
    client = authenticate_client()
    
    # Example documents
    documents = [
        "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.",
        "The Mona Lisa is a half-length portrait painting by Italian artist Leonardo da Vinci."
    ]
    
    find_linked_entities(client, documents)
