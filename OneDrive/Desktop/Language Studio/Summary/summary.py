from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Replace with your Azure Text Analytics subscription key and region
subscription_key = "8f7e5a654f6849f295e19c92cbdf1999"
service_region = "eastus"

def authenticate_text_analytics_client():
    endpoint = f"https://{service_region}.api.cognitive.microsoft.com/"
    ta_credential = AzureKeyCredential(subscription_key)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

def summarize_text(text):
    client = authenticate_text_analytics_client()
    
    # Perform text summarization
    poller = client.begin_extract_summary(documents=[text])
    summary_results = poller.result()
    print("Summary:")
    for result in summary_results:
        for sentence in result.sentences:
            print(sentence.text)

# Example text to summarize
text_to_summarize = """
At any given moment, turnaround coordinators for German airline Lufthansa CityLine have their eyes glued to monitors displaying more than half a dozen video feeds of airplanes parked at gates around the airport. The coordinators’ job is to ensure that the planes are unloaded, refueled, cleaned, restocked and reloaded so that every passenger reaches their destination safely, on time and with their luggage.

            Minutes lost here or there in the turnaround process can add up, costing airlines millions of dollars a year. As many in the industry note, airplanes only make money while in the air.

            “Think of a pitstop in a car race, and this is pretty much the same that happens in a turnaround for an aircraft,” said Philipp Grindemann, head of business development and project management for Lufthansa CityLine. “All the processes need to be on time, need to be fast, need to be lean.”

            Lufthansa CityLine is a subsidiary of Lufthansa, one of the world’s major airline groups with a network that spans the globe. Lufthansa maintains hubs in Frankfurt and Munich, Germany. Lufthansa CityLine connects passengers with destinations around Europe to and from these hubs, flying more than 300 flights per day. Ontime arrivals and departures are essential for customer satisfaction and Lufthansa’s bottom line.

            Outside of weather, delays stem from missteps during the tightly choreographed turnaround process. Like most industry players, Lufthansa CityLine relies on manual timestamps to understand when each step of the turnaround process starts and ends and uses that manual timestamp data to glean insights on where to make adjustments for faster, leaner turnarounds.

            In a pilot phase, the airline partnered with zeroG, a Lufthansa Group consulting company founded by Lufthansa Systems to accelerate the tangible impact of artificial intelligence in operational and commercial processes at airlines around the world. One example is improving turnaround management with AI.

            ZeroG’s Deep Turnaround solution leverages Azure Video Analyzer, a new offering from Microsoft that combines capabilities from Live Video Analytics and Azure Video Indexer. For Lufthansa, it generates automatic timestamps from the video feeds and issues alerts when the turnaround goes off script.

            “With that transparency of Deep Turnaround – knowing when the caterer arrives, knowing when the bridge arrives in order to deboard the aircraft – the airline can steer the process and have much leaner processes than before,” said Manuel van Esch, lead consultant for zeroG.

            For example, when a fuel truck arrives later than predicted, Deep Turnaround alerts the turnaround coordinators and other ground operations personnel. The alert kicks off a hunt for a solution that prevents a delay, such as dispatching a second fuel truck to the plane.

            Applied AI Services
            Azure Video Analyzer is among a handful of Azure Applied AI Services that Microsoft highlighted on Tuesday during Build, the company’s annual conference for developers. These services – Azure Video Analyzer, Azure Metrics Advisor, Azure Bot Service, Azure Cognitive Search, Azure Form Recognizer and Azure Immersive Reader – accelerate the development of scenario-specific AI solutions.

            Azure Applied AI Services are built on top of AI models at the core of Azure AI products and services. That includes Azure Cognitive Services, which offer customizable AI models and tools for building AI solutions that help customers extract meaning from text, integrate speech into apps and services, identify and analyze content within images and videos, and make decisions.

            Customers can also customize these services and extend them with their own custom models from Azure Machine Learning to meet the specific needs of their business.

            Customers routinely tell Microsoft that while they see the potential of AI, building solutions are harder than they anticipated, said Eric Boyd, corporate vice president of Microsoft Azure AI in Redmond, Washington.

            “The goal with Azure Applied AI Services is to provide a bit more packaging and structure to really accelerate the development of AI solutions for common business processes,” he said.

            The Azure Video Analyzer service, for example, brings together Computer Vision from Azure Cognitive Services and an automatic captioning model along with capabilities for integrating existing closed circuit video feeds and video management systems, which make it easier for businesses to build video analytics solutions.

            Microsoft created the Azure Applied AI Services category to target common business scenarios that Boyd’s Azure AI team has seen customers repeatedly build from scratch. For example, Azure Form Recognizer builds on optical character recognition, a computer vision technology that recognizes text and is key to many business solutions from reading receipts to pulling data from intake forms.
"""

# Call the function to summarize text
summarize_text(text_to_summarize)

