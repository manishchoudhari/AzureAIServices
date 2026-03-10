"""
pip install azure-ai-textanalytics
pip install azure-core
pip install nltk
pip install pdfplumber
pip install pandas
pip install scikit-learn

Author : Manish Choudhari

Processed Text:
primary care visit usd 25 copay visit deductible specialist visit usd 40 copay annual deductible usd 1000 individual usd 2000 family coinsurance 20 deductible

Extracted Entities:
{'text': '$25', 'category': 'Quantity'}
{'text': '$40', 'category': 'Quantity'}
{'text': '$1000', 'category': 'Quantity'}
{'text': '$2000', 'category': 'Quantity'}
{'text': '20%', 'category': 'Percentage'}

Structured Plan Output:
{'Service': 'Primary Care Visit', 'Copay': 25, 'Deductible': True, 'Coinsurance': 20}

Final Output:
{
 'Service': 'Primary Care Visit',
 'Copay': 25,
 'Deductible': True,
 'Coinsurance': 20,
 'Cluster': 0
}

"""

import re
import nltk
import pdfplumber
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# -------------------------------
# Download nltk packages
# -------------------------------
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# -------------------------------
# Azure Language Service Config
# -------------------------------
endpoint = "YOUR_AZURE_LANGUAGE_ENDPOINT"
key = "YOUR_AZURE_LANGUAGE_KEY"

credential = AzureKeyCredential(key)
text_analytics_client = TextAnalyticsClient(endpoint, credential)

# -------------------------------
# Input Layer - Read PDF
# -------------------------------
def extract_text_from_pdf(file_path):

    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "

    return text


document_text = """
Primary care visit: $25 copay per visit after deductible.
Specialist visit: $40 copay.
Annual deductible: $1000 individual / $2000 family.
Coinsurance: 20% after deductible.
"""

# If using PDF
# document_text = extract_text_from_pdf("policy.pdf")


# -------------------------------
# Text Preprocessing Layer
# -------------------------------

# Normalization
text = document_text.lower()

# Remove punctuation
text = re.sub(r'[^\w\s$%]', '', text)

# Currency normalization
text = re.sub(r'\$', ' usd ', text)

# -------------------------------
# Tokenization
# -------------------------------
tokens = word_tokenize(text)

# -------------------------------
# Stopword Removal
# -------------------------------
stop_words = set(stopwords.words('english'))

tokens = [w for w in tokens if w not in stop_words]

# -------------------------------
# Stemming
# -------------------------------
stemmer = PorterStemmer()
stemmed_tokens = [stemmer.stem(w) for w in tokens]

# -------------------------------
# Lemmatization
# -------------------------------
lemmatizer = WordNetLemmatizer()
lemmatized_tokens = [lemmatizer.lemmatize(w) for w in tokens]

processed_text = " ".join(lemmatized_tokens)

print("\nProcessed Text:")
print(processed_text)

# -------------------------------
# Azure AI Language - NER
# -------------------------------
documents = [document_text]

response = text_analytics_client.recognize_entities(documents)

entities = []

for doc in response:
    for entity in doc.entities:
        entities.append({
            "text": entity.text,
            "category": entity.category,
            "confidence": entity.confidence_score
        })

print("\nExtracted Entities:")
for e in entities:
    print(e)

# -------------------------------
# Plan Attribute Extraction
# -------------------------------
plan = {}

if "primary care visit" in text:
    plan["Service"] = "Primary Care Visit"

copay_match = re.search(r'(\d+)\s?usd', text)
if copay_match:
    plan["Copay"] = int(copay_match.group(1))

if "deductible" in text:
    plan["Deductible"] = True

coinsurance_match = re.search(r'(\d+)%', text)
if coinsurance_match:
    plan["Coinsurance"] = int(coinsurance_match.group(1))
else:
    plan["Coinsurance"] = None

print("\nStructured Plan Output:")
print(plan)

# -------------------------------
# Feature Vector Creation
# -------------------------------
documents = [processed_text]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)

print("\nFeature Vector:")
print(X.toarray())

# -------------------------------
# Clustering Plans
# (For large dataset e.g. 800 plans)
# -------------------------------
kmeans = KMeans(n_clusters=3)

clusters = kmeans.fit_predict(X)

print("\nCluster Assignment:")
print(clusters)

# -------------------------------
# Final Output
# -------------------------------
final_output = {
    "Service": plan.get("Service"),
    "Copay": plan.get("Copay"),
    "Deductible": plan.get("Deductible"),
    "Coinsurance": plan.get("Coinsurance"),
    "Cluster": int(clusters[0])
}

print("\nFinal Output:")
print(final_output)