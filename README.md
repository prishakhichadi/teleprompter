Real-Time Presentation Co-Pilot

A low-latency desktop assistant that tracks live speech against a slide script in real time. It uses semantic matching to detect missed points and displays them through a non-intrusive overlay, helping presenters stay on track without breaking flow.

Tech Stack & Components

Speech-to-Text (STT)

OpenAI Whisper (local, CPU-only, VAD enabled)

Natural Language Processing

SentenceTransformers

Cosine similarity for paraphrase-aware matching

Tracking Logic

Greedy forward-only progress tracking (no backtracking)

UI

Tkinter / CustomTkinter

Always-on-top overlay window

Audio

SoundDevice

Architecture
Audio Pipeline

Microphone input → Whisper (CPU) → Transcribed text

Script Extraction

Extracts text from PPT slides and speaker notes

Applies weighted priority to emphasize key content

Semantic Alignment

Converts both script sentences and live speech into embeddings

Handles heavy paraphrasing and non-verbatim delivery

State Tracking

A greedy progress algorithm advances through the script

Identifies skipped or missed sentences in real time

Setup & Execution
Install Dependencies
pip install -r requirements.txt

Run Application
python ffmain.py

Core Logic Snippets
Semantic Matching
# Script sentences are embedded once; speech is embedded live
similarity = util.cos_sim(speech_embedding, script_embeddings)
best_match_idx = torch.argmax(similarity)

Greedy Tracker
# Prevents backtracking and identifies skipped content
if current_match_idx > last_match_idx:
    missed_sentences = script[last_match_idx + 1 : current_match_idx]
    update_overlay(missed_sentences)

Key Features

Local Processing
Runs entirely on CPU with no cloud dependencies.

Weighted Context Awareness
Combines slide text and speaker notes with configurable importance.

Adaptive Thresholds
Similarity thresholds adjust dynamically based on recent speaker confidence.
