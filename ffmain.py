import threading
import time
import customtkinter as ctk
from tkinter import filedialog
from slide_controller import SlideController
from ffscript_window import ScriptWindow
from ffoverlay_tk import FloatingOverlay
from ffparagraph_tracker import SentenceTracker
from ffslide_sentence_tracker import SlideSentenceTracker
import ffstt
from ffweights import SOURCE_WEIGHTS, intrinsic_weight

from ffghost_summary import build_ghost_summary, format_ghost_summary
from ffghost_summary_window import GhostSummaryWindow


ctk.set_appearance_mode("light")

root = ctk.CTk()
root.withdraw()

sw = ScriptWindow(root)


root.wait_window(sw.win)

script = sw.script_text
if not script:
    print("No script provided — exiting.")
    raise SystemExit


# Select PowerPoint

ppt_path = filedialog.askopenfilename(
    title="Select PowerPoint file",
    filetypes=[("PowerPoint files", "*.pptx")]
)

if not ppt_path:
    print("No PPT selected - exiting.")
    raise SystemExit

def split_script_by_slide(script_text):
    return [
        block.strip()
        for block in script_text.split("\n\n")
        if block.strip()
    ]


def sentences_from_block(block):
    return [s.strip() for s in block.split(".") if s.strip()]


script_blocks = split_script_by_slide(script)

script_sentences = {}
for slide_idx, block in enumerate(script_blocks):
    script_sentences[slide_idx] = sentences_from_block(block)


slide_controller = SlideController(ppt_path)

slide_sentences = {}

for i in range(slide_controller.total_slides):
    combined = []

    for s in script_sentences.get(i, []):
        iw = intrinsic_weight(s)
        combined.append({
        "text": s,
        "source": "script",   # or "slide"
        "weight": iw * SOURCE_WEIGHTS["script"],
        "spoken": False,
        "missed": False
})


    # PPT sentences for this slide
    for s in slide_controller.get_slide_sentences(i):
        iw = intrinsic_weight(s)
        combined.append({
            "text": s,
            "source": "slide",
            "weight": iw * SOURCE_WEIGHTS["slide"]
        })

    slide_sentences[i] = combined
-

tracker = SlideSentenceTracker(slide_sentences, threshold=0.45)


def show_ghost_summary():
    summary_data = tracker.get_summary_data()
    summary = build_ghost_summary(summary_data)
    text = format_ghost_summary(summary)
    GhostSummaryWindow(root, text)


stop_event = threading.Event()

overlay = FloatingOverlay(
    root,
    stop_event,
    on_summary=show_ghost_summary
)
overlay.set_slide_controller(slide_controller)


tracker.set_missed_callback(
    lambda sent, slide: overlay.display_missed_async({
        "slide": slide,
        "text": sent,
        "ts": time.time()
    })
)


# STT

_last_ui_update = 0

def stt_callback(text):
    global _last_ui_update

    if len(text.strip()) < 5:
        return

    now = time.time()
    if now - _last_ui_update < 0.4:
        return

    _last_ui_update = now

    cur_slide = slide_controller.current_slide
    tracker.update(text, cur_slide)

    cur = tracker.current_sentence(cur_slide)
    overlay.set_current_async(cur if cur else "Listening…")

#stt thread begins

threading.Thread(
    target=ffstt.stt_loop,
    args=(stt_callback, stop_event),
    daemon=True
).start()



root.mainloop()

summary_data = tracker.get_summary_data()
print(format_ghost_summary(build_ghost_summary(summary_data)))
print("Application exited cleanly.")
