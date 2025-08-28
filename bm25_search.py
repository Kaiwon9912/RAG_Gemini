from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# nltk.download('punkt')

def bm25_filter(query: str, text: str, chunk_size: int = 2, top_k: int = 3):
    from rank_bm25 import BM25Okapi
    from nltk.tokenize import word_tokenize, sent_tokenize
    # import nltk

    # nltk.download('punkt')

    sentences = sent_tokenize(text)
    query_tokens = word_tokenize(query.lower())

    chunks = [" ".join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
    tokenized_chunks = [word_tokenize(chunk.lower()) for chunk in chunks]

    bm25 = BM25Okapi(tokenized_chunks)
    scores = bm25.get_scores(query_tokens)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    
    return [chunk for chunk, _ in ranked[:top_k]]
