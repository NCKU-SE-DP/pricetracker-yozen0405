from .prompts import EXTRACT_KEYWORDS_PROMPT, GENERATE_SUMMARY_PROMPT, RELEVANCE_CHECK_PROMPT
from .utils import generate_ai_response

def generate_summary(content):
    return generate_ai_response(content, GENERATE_SUMMARY_PROMPT)

def extract_search_keywords(content):
    return generate_ai_response(content, EXTRACT_KEYWORDS_PROMPT)

def relevance_check(content):
    return generate_ai_response(content, RELEVANCE_CHECK_PROMPT)

