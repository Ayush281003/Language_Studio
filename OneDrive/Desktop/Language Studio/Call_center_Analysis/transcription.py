import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Replace with your Azure Speech and Text Analytics subscription keys and regions
speech_subscription_key = "4381a7a89c85440c95036c074ad58949"
speech_service_region = "eastus"
text_analytics_subscription_key = "8f7e5a654f6849f295e19c92cbdf1999"
text_analytics_service_region = "eastus"

def authenticate_text_analytics_client():
    endpoint = f"https://{text_analytics_service_region}.api.cognitive.microsoft.com/"
    ta_credential = AzureKeyCredential(text_analytics_subscription_key)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

def transcribe_audio(audio_file_path):
    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_subscription_key, region=speech_service_region)
    
    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
    # Create a speech recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("Transcribing...")
    result = speech_recognizer.recognize_once_async().get()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Transcription: " + result.text)
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {0}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {0}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {0}".format(cancellation_details.error_details))
    
    return None

def analyze_text(text):
    client = authenticate_text_analytics_client()
    
    # Perform sentiment analysis
    sentiment_result = client.analyze_sentiment(documents=[text])[0]
    print("Sentiment analysis:")
    print(f"Overall sentiment: {sentiment_result.sentiment}")
    print(f"Positive score: {sentiment_result.confidence_scores.positive}")
    print(f"Neutral score: {sentiment_result.confidence_scores.neutral}")
    print(f"Negative score: {sentiment_result.confidence_scores.negative}")
    
    # Perform PII analysis
    pii_result = client.recognize_pii_entities(documents=[text])[0]
    print("PII analysis:")
    for entity in pii_result.entities:
        print(f"Entity: {entity.text}, Category: {entity.category}, Sub-category: {entity.subcategory}, Confidence score: {entity.confidence_score}")

        # Perform text summarization
    poller = client.begin_extract_summary(documents=[text])
    summary_result = poller.result()  # This is an ItemPaged object

    print("Summary:")
    for document in summary_result:
        for sentence in document.sentences:
            print(sentence.text)

# Provide the path to your audio file
audio_file_path = "harvard.wav"

# Call the function to transcribe audio
transcription_result = transcribe_audio(audio_file_path)

if transcription_result:
    analyze_text(transcription_result)
