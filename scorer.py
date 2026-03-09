import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from parser import clean_text, detect_sections, extract_contact_info


COMMON_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "you", "your", "are",
    "was", "were", "will", "have", "has", "had", "our", "their", "they", "them",
    "job", "role", "team", "work", "working", "candidate", "including", "using",
    "years", "year", "plus", "etc", "about", "into", "able", "such", "more",
    "very", "also", "well", "within", "across", "through", "other", "than",
    "those", "these", "must", "required", "preferred", "strong", "minimum",
    "knowledge", "experience", "good", "clear"
}

# Curated phrase bank to make output more meaningful
IMPORTANT_PHRASES = [
    "power bi",
    "tableau",
    "advanced excel",
    "excel reporting",
    "sql",
    "python",
    "dashboard development",
    "data visualization",
    "business intelligence",
    "data validation",
    "data cleansing",
    "data transformation",
    "data extraction",
    "trend analysis",
    "variance analysis",
    "kpi tracking",
    "reporting automation",
    "financial analysis",
    "transaction data",
    "predictive analytics",
    "machine learning",
    "cross functional collaboration",
    "stakeholder communication",
    "business insights",
    "data driven decisions",
    "large datasets",
    "reporting workflows",
    "enterprise reporting",
    "problem solving",
    "decision making",
    "requirements gathering",
    "report design",
    "sql queries",
    "data models",
    "reporting accuracy",
    "metric definitions",
]


def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def tokenize(text):
    text = clean_text(text)
    words = text.split()
    filtered_words = [w for w in words if len(w) > 2 and w not in COMMON_STOPWORDS]

    tokens = []

    # Single words
    for w in filtered_words:
        tokens.append(w)

    # 2-word phrases
    for i in range(len(filtered_words) - 1):
        phrase = filtered_words[i] + " " + filtered_words[i + 1]
        tokens.append(phrase)

    # 3-word phrases
    for i in range(len(filtered_words) - 2):
        phrase = (
            filtered_words[i]
            + " "
            + filtered_words[i + 1]
            + " "
            + filtered_words[i + 2]
        )
        tokens.append(phrase)

    return tokens


def extract_meaningful_phrases(text):
    lowered = clean_text(text)
    found = []

    for phrase in IMPORTANT_PHRASES:
        if phrase in lowered:
            found.append(phrase)

    return sorted(set(found))


def exact_keyword_score(resume_text, jd_text):
    resume_phrase_set = set(extract_meaningful_phrases(resume_text))
    jd_phrase_set = set(extract_meaningful_phrases(jd_text))

    # fallback if curated phrase coverage is too low
    if not jd_phrase_set:
        resume_tokens = set(tokenize(resume_text))
        jd_tokens = set(tokenize(jd_text))
        matched = sorted(resume_tokens.intersection(jd_tokens))
        missing = sorted(jd_tokens.difference(resume_tokens))
        matched = [m for m in matched if len(m) > 4][:20]
        missing = [m for m in missing if len(m) > 4][:20]
        score = (len(matched) / max(len(jd_tokens), 1)) * 100
        return round(score, 2), matched, missing

    matched = sorted(resume_phrase_set.intersection(jd_phrase_set))
    missing = sorted(jd_phrase_set.difference(resume_phrase_set))

    score = (len(matched) / max(len(jd_phrase_set), 1)) * 100
    return round(score, 2), matched[:20], missing[:20]


def semantic_similarity_score(resume_text, jd_text):
    model = get_embedding_model()
    embeddings = model.encode([resume_text, jd_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100
    return round(score, 2)


def tfidf_similarity_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100
    return round(score, 2)


def extract_required_phrases(jd_text):
    lines = re.split(r"[.\n•\-]+", jd_text)
    triggers = (
        "required",
        "must",
        "minimum",
        "proficient",
        "experience in",
        "experience with",
        "knowledge of",
        "ability to",
        "strong",
    )

    required = []
    for line in lines:
        cleaned = line.strip()
        lowered = cleaned.lower()
        if any(trigger in lowered for trigger in triggers) and len(cleaned) > 8:
            required.append(cleaned)

    return required[:20]


def required_coverage_score(resume_text, jd_text):
    required_items = extract_required_phrases(jd_text)

    if not required_items:
        return 50.0, []

    resume_lower = clean_text(resume_text)
    covered = []

    for item in required_items:
        item_lower = clean_text(item)
        overlap_count = 0

        for phrase in IMPORTANT_PHRASES:
            if phrase in item_lower and phrase in resume_lower:
                overlap_count += 1

        if overlap_count > 0:
            covered.append(item)

    score = (len(covered) / len(required_items)) * 100
    return round(score, 2), covered[:10]


def parsing_quality_score(resume_text):
    score = 0
    warnings = []

    sections = detect_sections(resume_text)
    contact = extract_contact_info(resume_text)

    if len(resume_text.strip()) > 300:
        score += 30
    else:
        warnings.append("Resume text seems too short. The PDF may not have parsed properly.")

    if contact["email_found"]:
        score += 15
    else:
        warnings.append("Add your email clearly near the top of the resume.")

    if contact["phone_found"]:
        score += 15
    else:
        warnings.append("Add your phone number clearly near the top of the resume.")

    if any(s in sections for s in ["skills", "technical skills"]):
        score += 15
    else:
        warnings.append("Add a clear Skills or Technical Skills heading.")

    if any(s in sections for s in ["experience", "work experience", "employment"]):
        score += 15
    else:
        warnings.append("Add a clear Experience or Work Experience heading.")

    if any(s in sections for s in ["education"]):
        score += 10
    else:
        warnings.append("Add a clear Education heading so ATS can detect your academic background.")

    return min(score, 100), warnings, sections


def categorize_missing_keywords(missing_keywords):
    technical = []
    business = []
    soft = []

    technical_terms = {
        "python", "sql", "excel", "power bi", "tableau", "dashboard development",
        "data visualization", "machine learning", "predictive analytics",
        "business intelligence", "data transformation", "data extraction",
        "kpi tracking", "variance analysis", "sql queries", "data models",
        "reporting automation", "data validation", "data cleansing"
    }

    soft_terms = {
        "cross functional collaboration", "stakeholder communication",
        "problem solving", "decision making"
    }

    for item in missing_keywords:
        lowered = item.lower()

        if lowered in technical_terms:
            technical.append(item)
        elif lowered in soft_terms:
            soft.append(item)
        else:
            business.append(item)

    return technical[:8], business[:8], soft[:8]


def generate_feedback(results):
    feedback = []

    overall = results["overall_score"]
    exact_score = results["exact_score"]
    semantic_score = results["semantic_score"]
    required_score = results["required_score"]
    warnings = results["warnings"]

    matched = results["matched_keywords"]
    missing = results["missing_keywords"]

    if overall >= 80:
        feedback.append("Your resume is strongly aligned with this job description overall.")
    elif overall >= 60:
        feedback.append("Your resume is moderately aligned with this job description, but still needs stronger tailoring.")
    else:
        feedback.append("Your resume is currently weakly aligned with this job description and needs more direct role-specific language.")

    if exact_score >= 60:
        feedback.append("A strong number of important job phrases already appear in your resume.")
    elif exact_score >= 40:
        feedback.append("Your resume includes some relevant role phrases, but important job language is still missing.")
    else:
        feedback.append("Your resume is missing many important job phrases from the description.")

    if semantic_score < 70:
        feedback.append("The wording in your resume differs significantly from the job description, so your relevance may not be obvious to ATS systems or recruiters.")

    if matched:
        feedback.append(f"Strongest matching areas: {', '.join(matched[:6])}.")

    if missing:
        feedback.append(f"Most important missing phrases: {', '.join(missing[:6])}.")

    if required_score < 60:
        feedback.append("Your resume does not yet cover enough of the job's required qualification language.")

    if warnings:
        feedback.append("ATS formatting/readability issues detected: " + " ".join(warnings))

    return feedback


def generate_specific_improvements(results):
    improvements = []

    technical_missing = results["technical_missing"]
    business_missing = results["business_missing"]
    soft_missing = results["soft_missing"]
    warnings = results["warnings"]

    if technical_missing:
        top_tech = ", ".join(technical_missing[:3])
        improvements.append(
            f"Add these technical phrases where truthful: {top_tech}. Best places: Skills section, summary, and project bullets."
        )

    if business_missing:
        top_business = ", ".join(business_missing[:3])
        improvements.append(
            f"Add more business-focused role language such as: {top_business}. Best place: work experience bullets."
        )

    if soft_missing:
        top_soft = ", ".join(soft_missing[:3])
        improvements.append(
            f"Show these soft-skill ideas directly in achievements: {top_soft}. Mention collaboration, communication, or stakeholder-facing work if you truly did it."
        )

    if warnings:
        for warning in warnings:
            improvements.append(warning)

    # Resume-specific stronger guidance
    improvements.append(
        "Add 2–3 bullets that mention dashboard development, KPI tracking, reporting accuracy, or data validation if those reflect your real work."
    )
    improvements.append(
        "Mention SQL more directly in your experience or projects if you have used it, not just in the skills section."
    )
    improvements.append(
        "If the job description emphasizes business partnership, add wording like 'supported business decisions', 'translated data into insights', or 'collaborated with cross-functional teams' where truthful."
    )
    improvements.append(
        "Rewrite weak general phrases into stronger ones. Example: replace 'analyzed data' with 'performed trend analysis, validated data accuracy, and built reporting views to support decision-making' if accurate."
    )
    improvements.append(
        "Make sure your Education section is clearly labeled as 'Education' so ATS systems detect it correctly."
    )

    return improvements[:10]


def overall_score(resume_text, jd_text):
    exact_score, matched_keywords, missing_keywords = exact_keyword_score(resume_text, jd_text)
    semantic_score = semantic_similarity_score(resume_text, jd_text)
    tfidf_score = tfidf_similarity_score(resume_text, jd_text)
    required_score, covered_requirements = required_coverage_score(resume_text, jd_text)
    parse_score, warnings, sections = parsing_quality_score(resume_text)

    technical_missing, business_missing, soft_missing = categorize_missing_keywords(missing_keywords)

    final_score = (
        exact_score * 0.35
        + semantic_score * 0.20
        + tfidf_score * 0.10
        + required_score * 0.20
        + parse_score * 0.15
    )

    results = {
        "overall_score": round(final_score, 2),
        "exact_score": round(exact_score, 2),
        "semantic_score": round(semantic_score, 2),
        "tfidf_score": round(tfidf_score, 2),
        "required_score": round(required_score, 2),
        "parse_score": round(parse_score, 2),
        "matched_keywords": matched_keywords[:20],
        "missing_keywords": missing_keywords[:20],
        "technical_missing": technical_missing,
        "business_missing": business_missing,
        "soft_missing": soft_missing,
        "covered_requirements": covered_requirements,
        "warnings": warnings,
        "sections_found": sections,
    }

    results["feedback"] = generate_feedback(results)
    results["specific_improvements"] = generate_specific_improvements(results)
    return results