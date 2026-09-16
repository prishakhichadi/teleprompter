
import customtkinter as ctk
import tkinter as tk
import queue
import textwrap
import threading
import time


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PANEL_BG = "#0b1020"   
CARD_BG = "#111827"       
ACCENT = "#38bdf8"        
ACCENT_SOFT = "#1f2937"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
ALERT = "#ef4444"


class FloatingOverlay:

    def toggle_overlay_visibility(self, event=None):
        self.overlay_hidden = not self.overlay_hidden

        if self.overlay_hidden:
            self.win.withdraw()
        else:
            self.win.deiconify()

    def __init__(self, root, stop_event, on_summary=None, width=980, height=620):
        self.root = root
        self.stop_event = stop_event
        self.width = width
        self.height = height
        self.queue = queue.Queue()
        self.slide_controller = None

        self.win = ctk.CTkToplevel(self.root)
        self.win.geometry(f"{width}x{height}+120+80")
        self.win.configure(fg_color=PANEL_BG)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.93)
        self.overlay_hidden = False

        self.win.bind("<ButtonPress-1>", self._start_move)
        self.win.bind("<B1-Motion>", self._do_move)
        self.win.focus_force()
        self.win.bind("<Escape>", self._quit_all)
        self.root.bind("<Escape>", self._quit_all)

        self._build_layout()
        self._poll_queue()
        self.on_summary = on_summary

    def set_tracker(self, tracker):
        self.tracker = tracker


    def _build_layout(self):
        self.container = ctk.CTkFrame(
            self.win, fg_color=PANEL_BG, corner_radius=14
        )
        self.container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Top bar
        top_bar = ctk.CTkFrame(self.container, fg_color=PANEL_BG)
        top_bar.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            top_bar,
            text="AI Assistant",
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="normal"),
        ).pack()

        self.lbl_current = ctk.CTkLabel(
            top_bar,
            text="Slide — / —",
            text_color=MUTED,
            font=ctk.CTkFont(size=11),
        )
        self.lbl_current.pack(pady=(2, 0))
        self.lbl_current.pack_forget()


        split = ctk.CTkFrame(self.container, fg_color=PANEL_BG)
        split.pack(fill="both", expand=True, padx=16, pady=(6, 14))


        left_w = int(self.width * 0.32)
        self.left_frame = ctk.CTkFrame(
            split, width=left_w, fg_color=CARD_BG, corner_radius=14
        )
        self.left_frame.pack(side="left", fill="y", padx=(0, 16))
        self.left_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.left_frame,
            text="LIVE TRANSCRIPT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="nw", padx=18, pady=(16, 8))

        self.current_text = ctk.CTkLabel(
            self.left_frame,
            text="Listening…",
            wraplength=left_w - 40,
            justify="left",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.current_text.pack(anchor="nw", padx=18, pady=(4, 10))

        self.current_sub = ctk.CTkLabel(
            self.left_frame,
            text="",
            wraplength=left_w - 40,
            justify="left",
            text_color=MUTED,
            font=ctk.CTkFont(size=11),
        )
        self.current_sub.pack(anchor="nw", padx=18, pady=(0, 14))

  
        self.right_frame = ctk.CTkFrame(split, fg_color=PANEL_BG)
        self.right_frame.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(self.right_frame, fg_color=PANEL_BG)
        header.pack(fill="x", padx=6, pady=(4, 8))

        ctk.CTkLabel(
            header,
            text="Missed Content",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT,
        ).pack(side="left", padx=6)


        self.cards_canvas = tk.Canvas(
            self.right_frame, bg=PANEL_BG, highlightthickness=0
        )
        self.cards_canvas.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.cards_scrollbar = ctk.CTkScrollbar(
            self.right_frame,
            orientation="vertical",
            command=self.cards_canvas.yview,
        )
        self.cards_scrollbar.pack(side="right", fill="y", padx=(0, 6))

        self.cards_canvas.configure(yscrollcommand=self.cards_scrollbar.set)

        self.cards_inner = ctk.CTkFrame(self.cards_canvas, fg_color=PANEL_BG)
        self.cards_window = self.cards_canvas.create_window(
            (0, 0), window=self.cards_inner, anchor="nw"
        )

        self.cards_inner.bind("<Configure>", self._on_frame_configure)
        self.cards_canvas.bind("<Configure>", self._on_canvas_configure)

        self.missed_count = 0

        # Controls
        self._build_controls()


    def _build_controls(self):
        ctrl = ctk.CTkFrame(self.container, fg_color=PANEL_BG)
        ctrl.place(relx=0.5, rely=0.93, anchor="s")

        self.btn_prev = ctk.CTkButton(
            ctrl, text="◀ Prev", width=90, command=self.on_prev_slide
        )
        self.btn_prev.pack(side="left", padx=6)

        self.btn_summary = ctk.CTkButton(
            ctrl,
            text="Review",
            width=110,
            fg_color="#EDEFF3",
            text_color="#1B1B1B",
            hover_color="#DADDE3",
            command=self.on_ghost_summary
        )
        self.btn_summary.pack(side="left", padx=8)

        self.btn_next = ctk.CTkButton(
            ctrl, text="Next ▶", width=90, command=self.on_next_slide
        )
        self.btn_next.pack(side="left", padx=6)

        self.status_lbl = ctk.CTkLabel(
            ctrl,
            text="Listening…",
            text_color=ACCENT,
            font=ctk.CTkFont(size=11, slant="italic"),
        )
        self.status_lbl.pack(side="left", padx=16)

        self.btn_next = ctk.CTkButton(
            ctrl, text="Next ▶", width=90, command=self.on_next_slide
        )
        self.btn_next.pack(side="left", padx=6)

   
    def set_slide_controller(self, slide_controller):
        self.slide_controller = slide_controller
        self.update_slide_label()

    def on_next_slide(self):
        if self.slide_controller:
            # 1. finalize CURRENT slide first
            self.tracker.finalize_slide(self.slide_controller.current_slide)

            # 2. then move to next slide
            self.slide_controller.next_slide()

            # 3. sync tracker slide index
            self.tracker.current_slide = self.slide_controller.current_slide

            self.update_slide_label()



    def on_prev_slide(self):
        if self.slide_controller:
            self.tracker.finalize_slide(self.slide_controller.current_slide)
            self.slide_controller.prev_slide()
            self.tracker.current_slide = self.slide_controller.current_slide
            self.update_slide_label()



    def update_slide_label(self):
        if not self.slide_controller:
            return
        self.lbl_current.configure(
            text=f"Slide {self.slide_controller.current_slide + 1} / "
                 f"{self.slide_controller.total_slides}"
        )

    def set_current(self, text):
        main, _, rest = text.partition("\n\n")
        self.current_text.configure(
            text=textwrap.fill(main.strip(), 60) or "Listening…"
        )
        self.current_sub.configure(
            text=textwrap.fill(rest.strip(), 50) if rest.strip() else ""
        )

    def display_missed(self, missed):
        self.missed_count += 1

        slide = missed["slide"]
        text = missed["text"]

        header_text = f"Slide {slide + 1} · Missed #{self.missed_count}"

        card = ctk.CTkFrame(
            self.cards_inner,
            fg_color=CARD_BG,
            corner_radius=14
        )
        card.pack(fill="x", padx=14, pady=8)

        # Header
        ctk.CTkLabel(
            card,
            text=header_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        # Body (the actual missed sentence)
        ctk.CTkLabel(
            card,
            text=text.strip(),
            wraplength=self.width - 420,
            justify="left",
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=14, pady=(0, 12))



    def _poll_queue(self):
        try:
            while True:
                typ, payload = self.queue.get_nowait()
                if typ == "current":
                    self.set_current(payload)
                elif typ == "missed":
                    self.display_missed(payload)
        except queue.Empty:
            pass
        self.win.after(120, self._poll_queue)

    
    def _on_frame_configure(self, _):
        self.cards_canvas.configure(
            scrollregion=self.cards_canvas.bbox("all")
        )

    def _on_canvas_configure(self, event):
        self.cards_canvas.itemconfig(self.cards_window, width=event.width)

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.win.geometry(f"+{x}+{y}")

    def set_current_async(self, text):
        self.queue.put(("current", text))

    def display_missed_async(self, missed):
        self.queue.put(("missed", missed))

    def _quit_all(self, event=None):
        try:
            self.stop_event.set()
        except:
            pass
        try:
            self.win.destroy()
        except:
            pass
        try:
            self.root.after(50, self.root.destroy)
        except:
            pass

    def run(self):
        self.root.mainloop()

    def on_ghost_summary(self):
        if self.on_summary:
            self.on_summary()

