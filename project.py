from pypdf import PdfReader
import re
from nlp import get_keywords,most_com

def extract_pages(path: str) -> list[dict]:
    """
    Read a PDF and return a list of dictionary.
    Each dictionary is of form: {'pg_no': int, 'text': str}
    """
    reader=PdfReader(path)
    data=[]
    for pg_no,page in enumerate(reader.pages,start=1):
        data.append({'pg_no':pg_no,'text':page.extract_text()})
    return data


def get_page_stats(page_text: str) -> dict:
    """Stats for ONE page."""
    ch=len(page_text)
    w=len(page_text.split())
    s = len(re.findall(r'[.!?]+', page_text))
    return {'words':w,'sentences':s,'characters':ch}


def get_document_stats(pages: list[dict]) -> list[dict]:
    """
    Compute statistics for the given PDF.

    Args:
        pages: List of dicts:{'page_number': int, 'text': str}

    Returns:
        dictionary with statistics for total document and each page.

    """
    stat={}
    l=[]
    total_words=0
    total_sentances=0
    total_chars=0
    for page in pages:
        v=get_page_stats(page['text'])
        v['pg_no']=page['pg_no']
        v['page_keywords']=get_keywords(page['text'])
        total_words+=v['words']
        total_sentances+=v['sentences']
        total_chars+=v['characters']
        l.append(v)

    total_text=' '.join(page['text'] for page in pages)
    total_stat={}
    total_stat['total_pages']=len(pages)
    total_stat['total_words']=total_words
    total_stat['total_sentances']=total_sentances
    total_stat['total_characters']=total_chars
    total_stat['document_keyword']=most_com(pages)
    total_stat['avg_words_per_page']=round(total_stat['total_words']/total_stat['total_pages'],1)
    total_stat['reading_time_minutes']=total_stat['total_words']/200

    stat['total']=total_stat
    stat['per_page']=l

    return stat

def main():
    ...

if __name__=='__main__':
    main()
