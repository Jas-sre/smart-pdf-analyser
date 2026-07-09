import re
import math
from collections import Counter

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'about', 'other', 'some', 'such', 'than', 'then', 'these',
    'those', 'very', 'when', 'where', 'which', 'while', 'will',
    'with', 'you', 'your', 'they', 'their', 'them', 'this', 'that','from', 'into', 'more', 'most', 'also', 'any', 'all', 'each'
}

def normalize_word(word: str) -> str:
    """Simple stemming: strip trailing 's' for plurals (if word is long enough)."""

    word = word.strip('.,!?;:()[]{}"\'-')

    if not re.match(r'^[a-z]+$', word):
        return ''

    if len(word) > 3 and word.endswith('s'):
        word = word[:-1]
    return word

def get_keywords(text: str) -> list:
    words = text.lower().split()
    filtered = [normalize_word(w) for w in words if normalize_word(w) and normalize_word(w) not in STOP_WORDS]
    return Counter(filtered).most_common(5)

def compute_tfidf(pages: list[dict]) -> list:
    """
    Compute TF-IDF for all words across all pages.

    Return the dictionary containing word and its tf_idf.
    """
    words=set()
    tf={}
    idf={}
    tf_idf={}
    l=0
    
    for page in pages:
        useful_words=[normalize_word(w) for w in page['text'].lower().split() if normalize_word(w) and normalize_word(w) not in STOP_WORDS]
        for x in useful_words:
            words.add(x)
            if x not in tf:
                tf[x]=1
            else:
                tf[x]+=1

        clean_text = re.sub(r'http[s]?://\S+', 'URL_LINK', page['text'])
        sentences=re.split(r'[.!?]+',clean_text)
        l+=len(sentences)
        for sentence in sentences:
            for word in words:
                if word in sentence.lower():
                    if word not in idf:
                        idf[word]=idf.get(word,0)+1
    for x in tf:
        tf[x]=1+math.log(tf[x])

    for word in words:
        tf_idf[word]=round(tf[word]*(math.log(l/idf.get(word,1))+1),4)

    return tf_idf

def most_com_keyword(pages):
    return Counter(compute_tfidf(pages)).most_common(5)

def text_to_sentences(pages: list[dict]) -> list[dict]:
    """
    Split all pages into sentences, keeping page numbers.

    Returns: [{'sentence': '...', 'pg_no': ...},...]
    """
    l=[]
    for page in pages:
        clean_text = re.sub(r'http[s]?://\S+', 'URL_LINK', page['text'])
        sentences=re.split(r'[.!?]+',clean_text)
        for sentence in sentences:
            if sentence.strip():
                l.append({'sentence':sentence,'pg_no':page['pg_no']})
    return l

def bm25_search(pages: list[dict], question: str, top_n: int = 1,
                k1: float = 1.5, b: float = 0.75) -> list[dict]:
    """
    BM25 search algorithm — industry standard for ranking.

    Returns top N sentences with their BM25 scores.
    """
    sentences = text_to_sentences(pages)
    tokenized = []  # will be a list(list)
    for s in sentences:
        words = [normalize_word(w) for w in s['sentence'].lower().split() if normalize_word(w) and normalize_word(w) not in STOP_WORDS]
        tokenized.append(words)

    N = len(tokenized)
    if N == 0:
        return []
    df = {}
    for words in tokenized:
        for word in set(words):
            df[word] = df.get(word, 0) + 1

    avgl = sum(len(w) for w in tokenized) / N

    query_words = [normalize_word(w) for w in question.lower().split() if normalize_word(w) and normalize_word(w) not in STOP_WORDS]
    if not query_words:
        return []

    #bm25 algorithm
    results = []
    for i, sent_words in enumerate(tokenized):
        if not sent_words:
            continue
        tf = Counter(sent_words)
        sent_len = len(sent_words)
        score = 0.0

        for word in query_words:
            if word not in tf:
                continue

            #IDF with smoothing
            idf = math.log((N - df[word] + 0.5) / (df[word] + 0.5) + 1)

            #TF normalization
            tf_norm = (tf[word] * (k1 + 1)) / (
                tf[word] + k1 * (1 - b + b * sent_len / avgl))

            score += idf * tf_norm

        results.append({
            'sentence': sentences[i]['sentence'],
            'pg_no': sentences[i]['pg_no'],
            'score': round(score, 4)
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    return results[:top_n]

def get_key_sentences(pages: list[dict], top_n: int = 3) -> list[dict]:
    """
    Extract key sentences based on keyword overlap.
    Sentences with more top-keywords are likely more important.
    """

    tfidf_scores = compute_tfidf(pages)
    top_keywords = [word for word, score in Counter(tfidf_scores).most_common(10)]

    sentences = text_to_sentences(pages)

    results = []
    for sent in sentences:
        sent_words = set(normalize_word(w) for w in sent['sentence'].lower().split())

        overlap = sum(1 for kw in top_keywords if kw in sent_words)

        results.append({
            'sentence': sent['sentence'],
            'pg_no': sent['pg_no'],
            'keyword_count': overlap,
        })

    results.sort(key=lambda x: x['keyword_count'], reverse=True)

    return results[:top_n]
