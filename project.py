import pandas as pd
import streamlit as st
from pypdf import PdfReader
import re
import base64
from nlp import get_keywords,most_com_keyword,bm25_search,get_key_sentences

def extract_pages(file) -> list[dict]:
    """
    Read a PDF and return a list of dictionary.
    Each dictionary is of form: {'pg_no': int, 'text': str}
    """
    reader=PdfReader(file)
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
    total_sentences=0
    total_chars=0
    for page in pages:
        v=get_page_stats(page['text'])
        v['pg_no']=page['pg_no']
        v['page_keywords']=' , '.join([item for item, count in get_cached_keywords(page['text'])])
        total_words+=v['words']
        total_sentences+=v['sentences']
        total_chars+=v['characters']
        l.append(v)

    total_stat={}
    total_stat['total_pages']=len(pages)
    total_stat['total_words']=total_words
    total_stat['total_sentences']=total_sentences
    total_stat['total_characters']=total_chars
    total_stat['document_keyword']=' , '.join([item for item, count in get_cached_doc_keyword(pages)])
    total_stat['avg_words_per_page']=round(total_stat['total_words']/total_stat['total_pages'],1)
    total_stat['reading_time_minutes']=total_stat['total_words']/200

    stat['total']=total_stat
    stat['per_page']=l

    return stat

def format_reading_time(minutes: float) -> str:
    """Convert minutes to a friendly string."""
    if minutes < 1:
        seconds = int(round(minutes * 60))
        return f"{seconds} sec"
    elif minutes < 60:
        return f"{minutes:.1f} min"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"

def show_pdf_preview(pdf_bytes: bytes, height: int = 600):
    
    """Display the uploaded PDF in an embedded iframe."""

    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Embed using HTML iframe with data URL
    pdf_display = f'''
    <div style="
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 5px;
        background-color: #f8f8f8;
    ">
        <iframe
            src="data:application/pdf;base64,{base64_pdf}#view=FitH"
            width="100%"
            height="{height}"
            type="application/pdf"
            style="border: none; border-radius: 5px;"
        >
        </iframe>
    </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)





#cache processing

@st.cache_data  
def get_cached_stats(pages):
    """Compute stats once"""
    return get_document_stats(pages)

@st.cache_data
def get_cached_key_sentences(pages,top_n=5):
    """Get key sentences once"""
    return get_key_sentences(pages,top_n)

@st.cache_data
def cached_bm25_search(pages, question, top_n=1):
    """Cache search results per question"""
    return bm25_search(pages, question, top_n)

@st.cache_data
def get_cached_keywords(page_text):
    """get Keyword once"""
    return get_keywords(page_text)

@st.cache_data
def get_cached_doc_keyword(pages):
    """Get Keyword once"""
    return most_com_keyword(pages)







def show_stat(pages):
    st.header('📊 Statistics')
    
    stats=get_cached_stats(pages)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Pages", stats['total']['total_pages'])
    with col2:
        st.metric("📝 Words", f"{stats['total']['total_words']:,}")  # commas!
    with col3:
        st.metric("💬 Sentences", stats['total']['total_sentences'])
    with col4:
        st.metric("⏱️ Reading Time", format_reading_time(stats['total']['reading_time_minutes']))
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("🔤 Characters", f"{stats['total']['total_characters']:,}")
    with col6:
        st.metric("📊 Avg Words Per Page", stats['total']['avg_words_per_page'])
    
    
    st.subheader("🏷️ Top Document Keywords")
    st.info(stats['total']['document_keyword'])
    
    
    with st.expander("📋 View Per-Page Statistics"):
        st.dataframe(pd.DataFrame(stats['per_page']).set_index('pg_no'))


def show_search(pages):
    st.header('🔍 Smart Search')
    st.write('Ask any question about the document and get the most relevant sentences!')
    
    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_input(
            'Enter your question:',
            placeholder='e.g., "What is real estate?"'
        )
    with col2:
        n_results = st.selectbox(
            'Results to show:',
            [1, 2, 3, 4, 5],
            index=0
        )
    
    search_clicked = st.button('🔎 Search', type='primary', use_container_width=True)
    
    if search_clicked:
        if not question.strip():
            st.warning('⚠️ Please enter a question first!')
        else:
            with st.spinner('🔍 Searching for answers...'):
                results = cached_bm25_search(pages, question, top_n=n_results)
            
            if not results or results[0]['score'] == 0:
                st.warning('😕 No matching sentences found. Try a different question.')
            else:
                st.success(f'✅ Found {len(results)} relevant sentence(s)!')
                st.divider()
                
                for i, r in enumerate(results, 1):
                    st.markdown(f"### #{i}")
                    
                    st.info(f'💬 "{r["sentence"]}"')
                    st.success(f"Found from 📄 Page {r['pg_no']}")

                    if i < len(results):
                        st.divider()

def show_key_sent(pages):
    st.header('🌟 Key Sentences')
    st.write('Gives the sentence with most keywords')
    col1,col2=st.columns([1,3])
    with col1:
        n = st.selectbox(
                'Results to show:',
                range(1,16),
                index=0
            )
    results=get_cached_key_sentences(pages,n)
    for i,x in enumerate(results, 1):
        st.markdown(f"### #{i}")
        
        st.info(f'💬 "{x["sentence"]}"')
        st.success(f"Found from 📄 Page {x['pg_no']}")
        
        if i < len(results):
            st.divider()




def main_page():
    st.set_page_config(
    page_title="Smart PDF Analyser",
    page_icon="📚",
    layout="wide" )

    st.title('📚 Smart Pdf Analyser')

    st.header('Upload your PDF')
    st.write('\n\n\n\n')
    uploaded=st.file_uploader('Choose a file',type='pdf')
    st.write('\n\n\n\n')

    if uploaded is not None:
        st.success(f"✅ Uploaded: {uploaded.name}")
        st.write('\n\n\n\n')
        if st.button('🔍 Analyse PDF', type='primary'):
            with st.spinner('Reading PDF...'):
                pages = extract_pages(uploaded)
                st.session_state['pages'] = pages
                st.session_state['filename'] = uploaded.name
                st.session_state['pdf_bytes'] = uploaded.getvalue()
                st.session_state['analysis_done'] = True
            st.rerun()


def analysis_page():
    pages=st.session_state['pages']
    fn=st.session_state['filename']
    pdf_bytes = st.session_state['pdf_bytes']
    col1,col2=st.columns(2)
    with col1:    
        st.title('📚 Smart Pdf Analyser')
        st.write('\n\n')
    with col2:        
        st.write('\n\n')
        if st.button('🔄 New Analysis',icon_position='right',use_container_width=True):
                st.session_state.clear()
                st.rerun()
    
    col1,col2=st.columns([3,1])
    with col1:
        st.subheader(f'📄 {fn}')
        st.write('\n\n')
    with col2:
        if st.button('🗑️ Clear Cache'):
            st.cache_data.clear()
            st.rerun()

    with st.expander("📄 View PDF Document", expanded=False):
        show_pdf_preview(pdf_bytes)
    st.write('\n\n')

    view = st.radio(
    "Select view:",
    ['📊 Statistics', '🔍 Smart Search', '🌟 Key Sentences'],
    horizontal=True,
    label_visibility="hidden")

    if view == '📊 Statistics':
        show_stat(pages)
    elif view == '🔍 Smart Search':
        show_search(pages)
    elif view == '🌟 Key Sentences':
        show_key_sent(pages)
        
def main():
    if 'analysis_done' in st.session_state:
        analysis_page()
    else:
        main_page()

if __name__=='__main__':
    main()
