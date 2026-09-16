from sentence_transformers import SentenceTransformer, util
import torch

class SlideSentenceTracker:
    def __init__(self, slide_sentences, threshold=0.45):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = threshold
        self.finalized_slides = set()
        self.summary = []

        self.slide_sentences = slide_sentences

        # Pre-embed ONLY text
        self.slide_embeddings = {
            k: self.model.encode(
                [s["text"] for s in v],
                convert_to_tensor=True
            )
            for k, v in slide_sentences.items()
        }

        self.last_seen = {k: -1 for k in slide_sentences}
        self.missed_callback = None

    def set_missed_callback(self, fn):
        self.missed_callback = fn

    def update(self, spoken_text, current_slide):
        if current_slide not in self.slide_sentences:
            return
        if len(spoken_text.strip()) < 5:
            return

        spoken_emb = self.model.encode(spoken_text, convert_to_tensor=True)
        emb = self.slide_embeddings[current_slide]

        scores = util.cos_sim(spoken_emb, emb)[0]

        # 🔑 weighted score
        weighted_scores = []
        for i, score in enumerate(scores):
            sent = self.slide_sentences[current_slide][i]
            combined = float(score) * sent["weight"]
            weighted_scores.append(combined)

        best_idx = int(torch.argmax(torch.tensor(weighted_scores)))
        best_score = weighted_scores[best_idx]

        if best_score < self.threshold:
            return

        last = self.last_seen[current_slide]

        if best_idx > last + 1 and self.missed_callback:
            for i in range(last + 1, best_idx):
                missed = self.slide_sentences[current_slide][i]
                self.missed_callback(
                    missed["text"],
                    current_slide
                )
        self.slide_sentences[current_slide][best_idx]["spoken"] = True
        self.last_seen[current_slide] = max(last, best_idx)

    def current_sentence(self, current_slide):
        idx = self.last_seen.get(current_slide, -1)
        if idx >= 0:
            return self.slide_sentences[current_slide][idx]["text"]
        return None
    
    
    def finalize_slide(self, slide_index):
        if slide_index in self.finalized_slides:
            return

        self.finalized_slides.add(slide_index)

        for sent in self.slide_sentences.get(slide_index, []):
            if sent["spoken"]:
                # Add to ghost summary
                self.summary.append({
                    "slide": slide_index,
                    "text": sent["text"],
                    "source": sent["source"]
                })
            else:
                # Mark as missed and notify UI
                sent["missed"] = True
                if self.missed_callback:
                    self.missed_callback(sent["text"], slide_index)

    def get_summary_data(self):
        summary = []

        for slide, sentences in self.slide_sentences.items():
            for idx, sent in enumerate(sentences):
                # Check if this sentence was matched (spoken)
                matched = sent.get("spoken", False) or (idx <= self.last_seen.get(slide, -1))
                summary.append({
                    "slide": slide,
                    "text": sent["text"],
                    "source": sent["source"],
                    "weight": sent.get("weight", 0.5),
                    "matched": matched
                })

        return summary

