
from sentence_transformers import SentenceTransformer

class VietnameseEmbeddingFunction:
    def __init__(self):
        self.model = SentenceTransformer("AITeamVN/Vietnamese_Embedding")

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()


def get_embedding_function():
    return VietnameseEmbeddingFunction()
