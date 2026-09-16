import re
from sentence_transformers import SentenceTransformer, util


class SentenceTracker:
    def __init__(self, script_text, threshold=0.55):
        self.threshold = threshold
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Parse script
        self.sentences = []   # list of dicts
        self._parse_script(script_text)

        # Precompute embeddings
        self.embeddings = self.model.encode(
            [s["text"] for s in self.sentences],
            convert_to_tensor=True
        )

        self.covered = set()
        self.on_skip_callback = None
        self.last_seen_idx = -1

    def set_callback(self, fn):
        self.on_skip_callback = fn

   
    def _parse_script(self, text):
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for p_idx, para in enumerate(paragraphs):
            sents = re.split(r'(?<=[.!?])\s+', para)
            for s_idx, sent in enumerate(sents):
                sent = sent.strip()
                if sent:
                    self.sentences.append({
                        "text": sent,
                        "para_idx": p_idx,
                        "sent_idx": s_idx
                    })

    def update(self, spoken_text):
        if not spoken_text.strip():
            return

        spoken_emb = self.model.encode(spoken_text, convert_to_tensor=True)
        scores = util.cos_sim(spoken_emb, self.embeddings)[0]

        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        print(f"[DEBUG] sentence match idx={best_idx}, score={best_score:.3f}")

        if best_score < self.threshold:
            return

        # Accept sentence
        if best_idx <= self.last_seen_idx:
            return

        # Detect skipped sentences
        skipped = []
        for idx in range(self.last_seen_idx + 1, best_idx):
            if idx not in self.covered:
                skipped.append(self.sentences[idx])

        # Emit skipped sentences
        if skipped and self.on_skip_callback:
            for s in skipped:
                self.on_skip_callback("• " + s["text"])

        # Mark current sentence covered
        self.covered.add(best_idx)
        self.last_seen_idx = best_idx

    def current_sentence(self):
        if self.last_seen_idx >= 0:
            return self.sentences[self.last_seen_idx]["text"]
        return None

#hi
