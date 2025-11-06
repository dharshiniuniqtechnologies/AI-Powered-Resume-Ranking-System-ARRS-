from sentence_transformers import SentenceTransformer, util
import spacy
import re
from collections import Counter

model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load('en_core_web_sm')

# Comprehensive skill keywords database
TECHNICAL_SKILLS = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin', 'swift'],
    'web': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'fastapi', 'spring'],
    'data': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'pandas', 'numpy'],
    'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform'],
    'tools': ['git', 'jira', 'agile', 'scrum', 'rest api', 'graphql', 'microservices']
}

SOFT_SKILLS = ['leadership', 'communication', 'teamwork', 'problem solving', 'analytical', 
               'creative', 'adaptable', 'organized', 'detail-oriented', 'collaborative']

def extract_skills(text):
    """Advanced skill extraction using both NER and keyword matching"""
    text_lower = text.lower()
    skills = set()
    
    # Keyword-based extraction
    all_skills = []
    for category, skill_list in TECHNICAL_SKILLS.items():
        all_skills.extend(skill_list)
    all_skills.extend(SOFT_SKILLS)
    
    for skill in all_skills:
        if skill in text_lower:
            skills.add(skill)
    
    # NLP-based extraction for additional context
    doc = nlp(text_lower)
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
            # Filter technical-sounding nouns
            if any(tech in token.text for tech in ['tech', 'dev', 'eng', 'soft', 'data', 'web']):
                skills.add(token.text)
    
    return list(skills)

def extract_experience_years(text):
    """Extract years of experience from resume"""
    # Patterns like "5 years", "5+ years", "5-7 years"
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)'
    ]
    
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    years.append(int(match[0]))
                else:
                    years.append(int(match))
    
    return max(years) if years else 0

def extract_education(text):
    """Extract education level"""
    education_keywords = {
        'phd': 5,
        'doctorate': 5,
        'master': 4,
        'mba': 4,
        'bachelor': 3,
        'associate': 2,
        'diploma': 1
    }
    
    text_lower = text.lower()
    for degree, score in education_keywords.items():
        if degree in text_lower:
            return score
    return 0

def calculate_similarity(job_description, resume_text):
    """Compute semantic similarity between job and resume"""
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(job_embedding, resume_embedding)
    return float(similarity)

def calculate_skill_match(job_skills, resume_skills):
    """Calculate percentage of job skills present in resume"""
    if not job_skills:
        return 0.0
    
    job_skills_set = set([s.lower() for s in job_skills])
    resume_skills_set = set([s.lower() for s in resume_skills])
    
    matched_skills = job_skills_set.intersection(resume_skills_set)
    match_percentage = len(matched_skills) / len(job_skills_set) if job_skills_set else 0
    
    return match_percentage

def calculate_keyword_density(job_description, resume_text):
    """Calculate how many job keywords appear in resume"""
    # Extract meaningful keywords from job description
    job_doc = nlp(job_description.lower())
    job_keywords = [token.lemma_ for token in job_doc 
                   if token.pos_ in ['NOUN', 'VERB', 'ADJ'] 
                   and not token.is_stop 
                   and len(token.text) > 3]
    
    if not job_keywords:
        return 0.0
    
    resume_lower = resume_text.lower()
    matched_keywords = sum(1 for keyword in job_keywords if keyword in resume_lower)
    
    return matched_keywords / len(job_keywords)

def rank_resume(job_description, resume_text, job_experience_required=0):
    """
    Comprehensive resume ranking with multiple factors
    Returns a score between 0-100
    """
    # Extract features
    job_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)
    resume_experience = extract_experience_years(resume_text)
    resume_education = extract_education(resume_text)
    
    # Calculate individual scores
    semantic_score = calculate_similarity(job_description, resume_text) * 100
    skill_match_score = calculate_skill_match(job_skills, resume_skills) * 100
    keyword_density_score = calculate_keyword_density(job_description, resume_text) * 100
    
    # Experience scoring (with diminishing returns)
    if job_experience_required > 0:
        if resume_experience >= job_experience_required:
            experience_score = 100
        elif resume_experience > 0:
            experience_score = (resume_experience / job_experience_required) * 100
        else:
            experience_score = 50  # No experience mentioned
    else:
        experience_score = 75  # Neutral if not specified
    
    # Education score (normalized to 100)
    education_score = (resume_education / 5) * 100 if resume_education else 50
    
    # Weighted final score
    weights = {
        'semantic': 0.30,
        'skill_match': 0.30,
        'keyword_density': 0.20,
        'experience': 0.15,
        'education': 0.05
    }
    
    final_score = (
        semantic_score * weights['semantic'] +
        skill_match_score * weights['skill_match'] +
        keyword_density_score * weights['keyword_density'] +
        experience_score * weights['experience'] +
        education_score * weights['education']
    )
    
    return {
        'final_score': round(final_score, 2),
        'semantic_similarity': round(semantic_score, 2),
        'skill_match': round(skill_match_score, 2),
        'keyword_density': round(keyword_density_score, 2),
        'experience_score': round(experience_score, 2),
        'education_score': round(education_score, 2),
        'matched_skills': list(set([s.lower() for s in job_skills]) & set([s.lower() for s in resume_skills])),
        'resume_skills': resume_skills[:15],  # Top 15 skills
        'missing_skills': list(set([s.lower() for s in job_skills]) - set([s.lower() for s in resume_skills]))[:10]
    }

def batch_rank_resumes(job_description, resumes_data, job_experience_required=0):
    """
    Rank multiple resumes and return sorted list
    resumes_data: list of dicts with 'id' and 'text' keys
    """
    ranked_resumes = []
    
    for resume in resumes_data:
        score_data = rank_resume(job_description, resume['text'], job_experience_required)
        ranked_resumes.append({
            'resume_id': resume.get('id'),
            'name': resume.get('name', 'Unknown'),
            'score': score_data['final_score'],
            'details': score_data
        })
    
    # Sort by score descending
    ranked_resumes.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rank position
    for idx, resume in enumerate(ranked_resumes, 1):
        resume['rank'] = idx
    
    return ranked_resumes