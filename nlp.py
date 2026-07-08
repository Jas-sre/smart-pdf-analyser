import re
import math
from collections import Counter

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'about', 'other', 'some', 'such', 'than', 'then', 'these',
    'those', 'very', 'when', 'where', 'which', 'while', 'will',
    'with', 'you', 'your', 'they', 'their', 'them', 'this', 'that',
    'from', 'into', 'more', 'most', 'also', 'any', 'all', 'each'
}


def normalize_word(word: str) -> str:
    """Simple stemming: strip trailing 's' for plurals (if word is long enough)."""
    word = word.strip('.,!?;:()[]{}"\'-')
    if len(word) > 3 and word.endswith('s'):
        word = word[:-1]
    return word

def get_keywords(text: str) -> list:
    words = text.lower().split()
    filtered = [normalize_word(w) for w in words if normalize_word(w) not in STOP_WORDS]
    return Counter(filtered).most_common(2)

def compute_tfidf(pages: list[dict]) -> list:
    """
    Compute TF-IDF for all words across all pages.

    Return the dictionary containing word and its tf_idf.
    """
    words=set()
    tf={}
    idf={}
    tf_idf={}

    for page in pages:
        useful_words=[normalize_word(w) for w in page['text'].lower().split() if normalize_word(w) not in STOP_WORDS]
        for x in useful_words:
            words.add(x)
            if x not in tf:
                tf[x]=1
            else:
                tf[x]+=1

        for x in tf:
            tf[x]=1+math.log(tf[x])

        clean_text = re.sub(r'http[s]?://\S+', 'URL_LINK', page['text'])
        sentences=re.split(r'[.!?]+',clean_text)
        l=len(sentences)
        for sentence in sentences:
            for word in words:
                if word in sentence.lower():
                    if word not in idf:
                        idf[word]=idf.get(word,0)+1

    for word in words:
        tf_idf[word]=round(tf[word]*(math.log(l/idf.get(word,1))+1),4)

    return tf_idf

def most_com(pages):
    return Counter(compute_tfidf(pages)).most_common(5)
