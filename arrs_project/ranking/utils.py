from sentence_transformers import SentenceTransformer, util
import spacy

model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load('en_core_web_sm')

def extract_skills(text):
    """Simple keyword-based skill extractor"""
    skills = []
    doc = nlp(text.lower())
    for token in doc:
        if token.pos_ == "NOUN":
            skills.append(token.text)
    return list(set(skills))

def calculate_similarity(job_description, resume_text):
    """Compute semantic similarity between job and resume"""
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(job_embedding, resume_embedding)
    return float(similarity)
