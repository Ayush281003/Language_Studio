import json
import time
import uuid
from typing import Tuple, List, Dict, Any

class TranscriptionPhrase:
    def __init__(self, id: int, text: str, itn: str, lexical: str, speaker_number: int, offset: str, offset_in_ticks: float):
        self.id = id
        self.text = text
        self.itn = itn
        self.lexical = lexical
        self.speaker_number = speaker_number
        self.offset = offset
        self.offset_in_ticks = offset_in_ticks

class SentimentAnalysisResult:
    def __init__(self, speaker_number: int, offset_in_ticks: float, document: dict):
        self.speaker_number = speaker_number
        self.offset_in_ticks = offset_in_ticks
        self.document = document

class ConversationAnalysisForSimpleOutput:
    def __init__(self, summary: List[Tuple[str, str]], pii_analysis: List[List[Tuple[str, str]]]):
        self.summary = summary
        self.pii_analysis = pii_analysis

class CombinedRedactedContent:
    def __init__(self, channel: int):
        self.channel = channel
        self.lexical = []
        self.itn = []
        self.display = []

# Constants
WAIT_SECONDS = 10
SPEECH_TRANSCRIPTION_PATH = "speechtotext/v3.1/transcriptions"
SENTIMENT_ANALYSIS_PATH = "language/:analyze-text"
SENTIMENT_ANALYSIS_QUERY = "api-version=2022-05-01"
CONVERSATION_ANALYSIS_PATH = "/language/analyze-conversations/jobs"
CONVERSATION_ANALYSIS_QUERY = "api-version=2022-10-01-preview"
CONVERSATION_SUMMARY_MODEL_VERSION = "latest"

def create_transcription(input_audio_url: str, speech_endpoint: str, speech_subscription_key: str, locale: str) -> str:
    uri = f"{speech_endpoint}/{SPEECH_TRANSCRIPTION_PATH}"
    content = {
        "contentUrls": [input_audio_url],
        "properties": {
            "diarizationEnabled": False,
            "timeToLive": "PT30M"
        },
        "locale": locale,
        "displayName": f"call_center_{time.strftime('%Y-%m-%d-%H-%M-%S')}"
    }
    response = send_post(uri, json.dumps(content), speech_subscription_key, [201])
    transcription_id = json.loads(response.content)["self"].split("/")[-1]
    return transcription_id

def get_transcription_status(transcription_id: str, speech_endpoint: str, speech_subscription_key: str) -> bool:
    uri = f"{speech_endpoint}/{SPEECH_TRANSCRIPTION_PATH}/{transcription_id}"
    response = send_get(uri, speech_subscription_key, [200])
    status = json.loads(response.content)["status"]
    return status.lower() == "succeeded"

def wait_for_transcription(transcription_id: str, speech_endpoint: str, speech_subscription_key: str):
    while True:
        print(f"Waiting {WAIT_SECONDS} seconds for transcription to complete.")
        time.sleep(WAIT_SECONDS)
        if get_transcription_status(transcription_id, speech_endpoint, speech_subscription_key):
            break

def get_transcription_files(transcription_id: str, speech_endpoint: str, speech_subscription_key: str) -> dict:
    uri = f"{speech_endpoint}/{SPEECH_TRANSCRIPTION_PATH}/{transcription_id}/files"
    response = send_get(uri, speech_subscription_key, [200])
    return json.loads(response.content)

def get_transcription_uri(transcription_files: dict) -> str:
    for value in transcription_files["values"]:
        if value["kind"] == "Transcription":
            return value["links"]["contentUrl"]
    raise Exception("Transcription file not found")

def get_transcription(transcription_uri: str) -> dict:
    response = send_get(transcription_uri, "", [200])
    return json.loads(response.content)

def get_transcription_phrases(transcription: dict) -> List[TranscriptionPhrase]:
    phrases = []
    for i, phrase in enumerate(transcription["recognizedPhrases"]):
        best = phrase["nBest"][0]
        if "speaker" in phrase:
            speaker_number = phrase["speaker"] - 1
        elif "channel" in phrase:
            speaker_number = phrase["channel"]
        else:
            raise Exception("nBest item contains neither channel nor speaker attribute.")
        phrases.append(TranscriptionPhrase(
            i, best["display"], best["itn"], best["lexical"], speaker_number,
            phrase["offset"], phrase["offsetInTicks"]
        ))
    return phrases

def delete_transcription(transcription_id: str, speech_endpoint: str, speech_subscription_key: str):
    uri = f"{speech_endpoint}/{SPEECH_TRANSCRIPTION_PATH}/{transcription_id}"
    send_delete(uri, speech_subscription_key)

def get_sentiment_analysis(phrases: List[TranscriptionPhrase], language_endpoint: str, language_subscription_key: str, language: str) -> List[SentimentAnalysisResult]:
    uri = f"{language_endpoint}/{SENTIMENT_ANALYSIS_PATH}?{SENTIMENT_ANALYSIS_QUERY}"
    phrase_data = {}
    documents_to_send = []
    for phrase in phrases:
        phrase_data[phrase.id] = (phrase.speaker_number, phrase.offset_in_ticks)
        documents_to_send.append({
            "id": str(phrase.id),
            "language": language,
            "text": phrase.text
        })
    
    results = []
    for chunk in [documents_to_send[i:i+10] for i in range(0, len(documents_to_send), 10)]:
        content = {
            "kind": "SentimentAnalysis",
            "analysisInput": {
                "documents": chunk
            }
        }
        response = send_post(uri, json.dumps(content), language_subscription_key, [200])
        for doc in json.loads(response.content)["results"]["documents"]:
            speaker_number, offset_in_ticks = phrase_data[int(doc["id"])]
            results.append(SentimentAnalysisResult(speaker_number, offset_in_ticks, doc))
    return results

def get_sentiments_for_simple_output(sentiment_analysis_results: List[SentimentAnalysisResult]) -> List[str]:
    return [result.document["sentiment"] for result in sorted(sentiment_analysis_results, key=lambda x: x.offset_in_ticks)]

def get_sentiment_confidence_scores(sentiment_analysis_results: List[SentimentAnalysisResult]) -> List[dict]:
    return [result.document["confidenceScores"] for result in sorted(sentiment_analysis_results, key=lambda x: x.offset_in_ticks)]

def merge_sentiment_confidence_scores_into_transcription(transcription: dict, sentiment_confidence_scores: List[dict]) -> dict:
    recognized_phrases = transcription["recognizedPhrases"]
    for i, phrase in enumerate(recognized_phrases):
        for nBest_item in phrase["nBest"]:
            nBest_item["sentiment"] = sentiment_confidence_scores[i]
        recognized_phrases[i] = nBest_item
    transcription["recognizedPhrases"] = recognized_phrases
    return transcription

def transcription_phrases_to_conversation_items(transcription_phrases: List[TranscriptionPhrase]) -> List[dict]:
    return [
        {
            "id": phrase.id,
            "text": phrase.text,
            "itn": phrase.itn,
            "lexical": phrase.lexical,
            "role": "Agent" if phrase.speaker_number == 0 else "Customer",
            "participantId": phrase.speaker_number
        }
        for phrase in transcription_phrases
    ]

def request_conversation_analysis(conversation_items: List[dict], language_endpoint: str, language_subscription_key: str) -> str:
    uri = f"{language_endpoint}/{CONVERSATION_ANALYSIS_PATH}?{CONVERSATION_ANALYSIS_QUERY}"
    content = {
        "displayName": f"call_center_{time.strftime('%Y-%m-%d-%H-%M-%S')}",
        "analysisInput": {
            "conversations": [
                {
                    "id": "conversation1",
                    "language": "en-US",
                    "modality": "transcript",
                    "conversationItems": conversation_items
                }
            ]
        },
        "tasks": [
            {
                "taskName": "summary_1",
                "kind": "ConversationalSummarizationTask",
                "parameters": {
                    "modelVersion": CONVERSATION_SUMMARY_MODEL_VERSION,
                    "summaryAspects": ["Issue", "Resolution"]
                }
            },
            {
                "taskName": "PII_1",
                "kind": "ConversationalPIITask",
                "parameters": {
                    "piiCategories": ["All"]
                }
            }
        ]
    }
    response = send_post(uri, json.dumps(content), language_subscription_key, [202])
    return response.headers["operation-location"]

def get_conversation_analysis_status(conversation_analysis_url: str, language_subscription_key: str) -> bool:
    response = send_get(conversation_analysis_url, language_subscription_key, [200])
    status = json.loads(response.content)["status"]
    return status.lower() == "succeeded"

def wait_for_conversation_analysis(conversation_analysis_url: str, language_subscription_key: str):
    while True:
        print(f"Waiting {WAIT_SECONDS} seconds for conversation analysis to complete.")
        time.sleep(WAIT_SECONDS)
        if get_conversation_analysis_status(conversation_analysis_url, language_subscription_key):
            break

def get_conversation_analysis(conversation_analysis_url: str, language_subscription_key: str) -> dict:
    response = send_get(conversation_analysis_url, language_subscription_key, [200])
    return json.loads(response.content)

def get_conversation_analysis_for_simple_output(conversation_analysis: dict) -> ConversationAnalysisForSimpleOutput:
    tasks = conversation_analysis["tasks"]["items"]
    summary_task = next(task for task in tasks if task["taskName"] == "summary_1")
    conversation_summary = summary_task["results"]["conversations"][0]["summaries"]
    pii_task = next(task for task in tasks if task["taskName"] == "PII_1")
    conversation_pii_analysis = pii_task["results"]["conversations"][0]["conversationItems"]
    return ConversationAnalysisForSimpleOutput(
        [(summary["aspect"], summary["text"]) for summary in conversation_summary],
        [[
            (entity["category"], entity["text"])
            for entity in document["entities"]
        ] for document in conversation_pii_analysis]
    )

def send_post(uri: str, content: str, subscription_key: str, expected_status_codes: List[int]) -> Any:
    # Implement HTTP POST request logic here
    pass

def send_get(uri: str, subscription_key: str, expected_status_codes: List[int]) -> Any:
    # Implement HTTP GET request logic here
    pass

def send_delete(uri: str, subscription_key: str) -> None:
    # Implement HTTP DELETE request logic here
    pass