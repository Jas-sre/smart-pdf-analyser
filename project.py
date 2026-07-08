from pypdf import PdfReader
import re

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

def main():
    ...
    
if __name__=='__main__':
    main()
