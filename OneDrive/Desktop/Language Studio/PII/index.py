from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


# Replace with your own values
endpoint = "https://mynewresourcegpii.cognitiveservices.azure.com/"
key = "8f7e5a654f6849f295e19c92cbdf1999"


def detect_pii(text):
    credential = AzureKeyCredential(key)
    client = TextAnalyticsClient(endpoint, credential)
    
    key_phrases_result = client.extract_key_phrases([text], language="en")
    print("Key Phrases:", key_phrases_result[0].key_phrases)
    
    sentiment_result = client.analyze_sentiment([text], language="en")
    print("Sentiment:", sentiment_result[0].sentiment)


    language_result = client.detect_language([text])
    print("Detected Language:", language_result[0].primary_language.name)


    response = client.recognize_pii_entities([text])
    for doc in response:
        for entity in doc.entities:
            print(f"Detected PII: {entity.text} (Category: {entity.category})")
    



if __name__ == "__main__":
    input_text = "ACCOUNT TRANSFER REQUESTTo, From: Name: Mustafa AbdulThe Branch Manager Address: 2201 C Street NW I Washington, DC 20520Bank of America Phone No.: 202-555-0129Madam/ Dear Sir,Request for my /our SB/RD/Term Deposit Account TransferA/c No. GL28 0219 2024 5014 48From (Branch Name- Code) to (Branch Name- Code)1. I hold the above account/accounts with branch code: BOFAUS3N.2. I request you to transfer the captioned account. The new address proof is enclosed/ shall beprovided within 6 months at the transferee branch.3. I request you to transfer the CIF.4. I understand that if CIF is not transferred, my Home Branch will continue to remain the same.Please arrange accordingly.Yours faithfully,"
    detect_pii(input_text)

