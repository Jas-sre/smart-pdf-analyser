# 📚 Smart PDF Analyzer

#### Description:

The ***Smart PDF Analyzer*** is a web application I built from scratch using **Python**. It lets users upload any PDF file and instantly get useful insights about its content — including document statistics, top keywords, an smart Q&A search engine, and auto-generation of key sentences.

The most interesting part of this project is that all the **_Natural Language Processing (NLP)_ algorithms are implemented by me from the base**.I did not use any *AI APIs, embedding models, or pre-trained language models*. Instead, I implemented classical NLP techniques — **Term Frequency - Inverse Document Frequency (TF-IDF)** and **BM25** (the ranking algorithm used by most production search engines).



## 🌐 Live Demo

Try the live app here: [https://smart-pdf-analyser.streamlit.app](https://smart-pdf-analyser.streamlit.app/)



## ✨ Features

### The application has three main capabilities:

1. ### 📊Statistics

* **Document Statistics** - Displays total pages, words, sentences, and characters of the entire document. It also estimates average reading time and average word per page.

* **Page Statistics** - Displays total words , sentence , character and keywords of each page

* **🏷️Top Document Keywords** — Identifies the most important words in the document using the classic TF-IDF algorithm.

2. ### 🔍 Intelligent Search (BM25 algorithm)
    Users can ask questions about the document, and the application finds the most relevant sentences matching the question using BM25, the industry-standard ranking algorithm.*The search handles term frequency saturation, document length normalization, and IDF smoothing — the same techniques used by major search engines*.

3. ### 🌟 Auto-Summary (Key Sentences)
    Displays the most important sentences of the document based on keyword overlap with the document's top TF-IDF keywords.

4. ### Other Features
    * We can see the **pdf uploaded** using a expander.
    * The New Analysis function triggers the main page.
    * The is a option to clear cache , useful if the cache data accumulates to a large extent. 



## 🛠️ Technology Stack

- **Python 3** — The programming language
- **Streamlit** — The module of Python used for Web UI framework (chosen for its simplicity)
- **pypdf** — Lightweight library for extracting text from PDF files
- **pandas** — For displaying per-page statistics in a clean table format(used for the purpose of converting data into dataframe)
- **pytest** — For unit testing the core functions




## 📁 Project Structure

**The project contains 3 major python files :**

### `nlp.py` — Core NLP Algorithms

This file contains all the **Natural Language Processing** logic.

- **`normalize_word(word)`** — Cleans a word by stripping punctuation, filtering out non-alphabetic tokens (preventing numbers and symbols from appearing as keywords), and applying simple stemming (i.e removing the trailing zeros).

- **`STOP_WORDS`** — A curated set of 57 common English words that are filtered out before processing. This prevents stop words (eg. is , the...) from being treated as keywords.

- **`get_keywords(text)`** — Returns the top 5 most frequent meaningful words from a text.

- **`compute_tfidf(pages)`** — Implements the full TF-IDF algorithm across all pages. Uses sublinear TF scaling (`1 + log(count)`) to prevent high-frequency words from dominating. I used Sentence-level IDF ,treating each sentence as a "document" so the algorithm works correctly even on single-page PDFs.

- **`bm25_search(pages, question)`** — Implements the BM25 ranking algorithm with the standard parameters `k1=1.5` and `b=0.75`(found to produce best result after testing on large databases). This is the same algorithm used by Elasticsearch and other major search engines for ranking search results.

- **`get_key_sentences(pages, top_n)`** — Returns the top_n sentences ranked by how many of the document's TF-IDF keywords they contain. Acts as a simple summary.


### `project.py` — Streamlit Web Application

This file contains the **UI logic** using Python's Streamlit module:

#### **Functions**

- **`extract_pages(file)`** — Reads an uploaded PDF file and extracts text from each page, preserving page numbers.

- **`get_page_stats(page_text)`** — Computes statistics (words, sentences, characters) for a single page.

- **`get_document_stats(pages)`** — Aggregates stats across all pages, plus per-page breakdown.

- **`format_reading_time(minutes)`** — Smart formatting: shows time in seconds for average reading time under 1 minute, in minutes for average reading time under 1 hour, and in hours+minutes for even longer documents.

#### **Working**

- **Main flow** — Uses `st.session_state` to manage a multi-page experience: first the upload page, then the analysis page with three view modes (Statistics, Smart Search, Key Sentences) accessible via a horizontal radio selector.

- **`@st.cache_data` decorators** — Memoize expensive computations like TF-IDF and BM25 search, so the app stays responsive even with complex queries.This is needed because on each response the streamlit tend to run the entire script from start till end , this will cause the program to rash on multiple immediate use of functionality and hence maintaining cache data is necessary.


### `test_pdf_analyzer.py` — Unit Tests

- I wrote 5 pytest unit tests covering the core functions: `normalize_word`, `format_reading_time`, `get_keywords`, `get_page_stats` and `get_document_stats` . These tests verify edge cases like empty inputs, special characters, plural stemming, time formatting, and proper filtering of numbers and stop words. 
- The tests helped me catch and fix several bugs during development — particularly around number filtering and the page-level TF-IDF logic.

### `requirements.txt` — Dependencies

-Lists all Python packages needed: `pypdf`, `streamlit`, `pandas`, `pytest`.

-Run `pip install -r requirements.txt` in command prompt to run the dependencies. 



## 🎯 Design Decisions

### Why Classical NLP Instead of AI APIs?

I wanted to build a final project on my owm form the **scratch** . If I had used OpenAI's GPT API or sentence-transformers embeddings, the actual "intelligence" would be a black box I don't know about. By implementing TF-IDF and BM25 myself, I can explain exactly how relevance scoring works mathematically and So I using API , making the project self-contained and free to run.

### Why Streamlit?

Streamlit let me build a beautiful, professional UI using only Python.It was simple and beginner friendly , so i found it really easy and comfortable to design the webpage.

### Why BM25 Instead of Just TF-IDF?

During development, I first used basic TF-IDF + cosine similarity and it had a critical flaw: a single high-frequency word could dominate the similarity score, causing wrong sentences to win search results.
BM25 fixed this with two key features — **sublinear TF scaling** (diminishing returns for word frequency) and **document length normalization** (short sentences don't unfairly win). Implementing BM25 was a significant upgrade that made the search engine genuinely useful.

### Why Simple Plural Stemming Instead of Porter Stemmer?

I implemented a basic stemmer (`forms` → `form`) instead of using NLTK's Porter Stemmer or lemmatizer.My stemmer handles 90% of cases correctly, is only 3 lines of code, and avoids an external dependency.As I said I wanted the algorithm to be my own and hence made this decision

### Why Caching?

BM25 search and TF-IDF computation are O(N) operations. Without caching, every widget interaction would trigger a full recomputation, making the app feel slow. With `@st.cache_data`, results are memoized — the second time a user asks the same question, the answer is instant.



## ⚠️ Known Limitations

- **Single PDF at a time** — The session only holds one uploaded PDF. Multi-PDF support would require storing multiple vector indexes.
- **English text only** — The stop words list is English-specific, and word stemming only handles basic English plural patterns.
- **Text-only PDFs** — Scanned PDFs (image-based) won't work because there's no OCR.
- **Sentence splitting is basic** — I use a simple regex-based sentence splitter that doesn't handle complex cases like "Dr. Smith" or "U.S.A." perfectly.



## 🚀 How To Run locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Jas-sre/smart-pdf-analyser.git
   cd smart-pdf-analyser
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run projet.py
   ```

4. Open your browser to `http://localhost:8501` and upload any PDF!

5. To run the tests:
   ```bash
   pytest tests/ -v

   ```

## 🎓 What I Learned

This project taught me a lot about:
- **Classical NLP algorithms** — TF-IDF and BM25 are surprisingly elegant once you implement them.
- **Algorithm debugging** — Finding the bug where I iterated over characters instead of words was a real lesson.
- **Caching strategies** — Streamlit's `@st.cache_data` taught me about memoization in practice.
- **UI/UX considerations** — Things like the reading-time formatter (showing "17 sec" instead of "0.3 min") made the app feel professional.



## 📜 License

This project is open source and available under the MIT License.



##  Acknowledgments

- **CS50** — For the inspiration and structured learning path
- **The BM25 paper** — Robertson, S. & Zaragoza, H. (2009). "The Probabilistic Relevance Framework: BM25 and Beyond"
