import fitz
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def rank_resumes(job_description, resume_paths):
    job_clean = preprocess(job_description)
    resumes = []
    names = []
    for path in resume_paths:
        text = extract_text_from_pdf(path)
        resumes.append(preprocess(text))
        names.append(os.path.basename(path))

    corpus = [job_clean] + resumes
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    ranked = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
    return [(name, round(float(score)*100, 2)) for name, score in ranked]