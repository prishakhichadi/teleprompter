from sentence_transformers import SentenceTransformer, util

class SemanticMatcher:
    def __init__(self, bullet_points, threshold=0.55):
        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded.")

        self.bullets = bullet_points
        self.bullet_embeddings = self.model.encode(self.bullets, convert_to_tensor=True)
        self.threshold = threshold
        self.covered = set()

    def update_bullets(self, bullet_points):
        self.bullets = bullet_points
        self.bullet_embeddings = self.model.encode(self.bullets, convert_to_tensor=True)
        self.covered = set()

    def process_text(self, spoken_text):
        if not spoken_text.strip():
            return None, None

        spoken_emb = self.model.encode(spoken_text, convert_to_tensor=True)
        cos_scores = util.cos_sim(spoken_emb, self.bullet_embeddings)[0]

        best_idx = int(cos_scores.argmax())
        best_score = float(cos_scores[best_idx])

        if best_score >= self.threshold:
            covered_bullet = self.bullets[best_idx]
            self.covered.add(covered_bullet)
        else:
            covered_bullet = None

        missed = [b for b in self.bullets if b not in self.covered]

        return covered_bullet, missed


