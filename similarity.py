import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import hashlib

from preprocessing import preprocess


class CoretaxChatbot:
    def __init__(self, dataset_path, threshold=0.65, cache_path=None):
        self.threshold = threshold
        self.df = pd.read_excel(dataset_path)

        cache_path = cache_path or (dataset_path + ".cache.pkl")
        dataset_hash = self._hash_file(dataset_path)
        cached = self._load_cache(cache_path, dataset_hash)

        if cached is not None:
            self.df["clean_question"] = cached["clean_question"]
            self.vectorizer = cached["vectorizer"]
            self.tfidf_matrix = cached["tfidf_matrix"]
        else:
            self.df["clean_question"] = self.df["Pertanyaan (Q)"].apply(preprocess)
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df["clean_question"])
            self._save_cache(cache_path, dataset_hash)

    @staticmethod
    def _hash_file(path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _load_cache(self, cache_path, dataset_hash):
        if not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
            if data.get("dataset_hash") != dataset_hash:
                return None
            return data
        except Exception:
            return None

    def _save_cache(self, cache_path, dataset_hash):
        try:
            with open(cache_path, "wb") as f:
                pickle.dump({
                    "dataset_hash": dataset_hash,
                    "clean_question": self.df["clean_question"],
                    "vectorizer": self.vectorizer,
                    "tfidf_matrix": self.tfidf_matrix,
                }, f)
        except Exception:
            pass

    def get_response(self, user_question):
        clean_q = preprocess(user_question)
        user_vector = self.vectorizer.transform([clean_q])

        scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        best_idx = scores.argmax()
        best_score = scores[best_idx]

        if best_score < self.threshold:
            return {
                "found": False,
                "answer": "Maaf, saya belum menemukan jawaban yang sesuai.",
                "score": float(best_score),
                "category": None
            }

        return {
            "found": True,
            "answer": self.df.iloc[best_idx]["Jawaban (A)"],
            "score": float(best_score),
            "category": self.df.iloc[best_idx]["Kategori"]
        }
