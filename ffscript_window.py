

import customtkinter as ctk


ctk.set_appearance_mode("dark")

PANEL_BG = "#0b1020"     # deep navy
CARD_BG = "#111827"      # dark card
ACCENT = "#38bdf8"       # cyan-blue
TEXT = "#e5e7eb"
MUTED = "#9ca3af"


class ScriptWindow:
    def __init__(self, root):
        self.root = root
        self.script_text = None

        # Window
        self.win = ctk.CTkToplevel(self.root)
        self.win.geometry("860x620+200+100")
        self.win.configure(fg_color=PANEL_BG)
        self.win.update_idletasks()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.96)

        # Drag support
        self.win.bind("<ButtonPress-1>", self._start_move)
        self.win.bind("<B1-Motion>", self._do_move)

        # ESC closes
        self.win.bind("<Escape>", lambda e: self.win.destroy())

        # Container
        container = ctk.CTkFrame(
            self.win,
            fg_color=PANEL_BG,
            corner_radius=16
        )
        container.pack(fill="both", expand=True, padx=24, pady=24)

      
        ctk.CTkLabel(
            container,
            text="Script Input",
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=8, pady=(0, 4))

        ctk.CTkLabel(
            container,
            text="Paste or type your presentation script below",
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=8, pady=(0, 14))

        
        card = ctk.CTkFrame(
            container,
            fg_color=CARD_BG,
            corner_radius=16
        )
        card.pack(fill="both", expand=True, padx=4, pady=(0, 18))

        self.textbox = ctk.CTkTextbox(
            master=card,
            fg_color=CARD_BG,
            text_color=TEXT,
            font=ctk.CTkFont(size=13),
            wrap="word",
            scrollbar_button_color="#1f2937",
            scrollbar_button_hover_color=ACCENT,
        )
        self.textbox.pack(fill="both", expand=True, padx=18, pady=18)

        footer = ctk.CTkFrame(container, fg_color=PANEL_BG)
        footer.pack(fill="x", padx=4)

        self.start_btn = ctk.CTkButton(
            footer,
            text="Start Presentation",
            fg_color=ACCENT,
            text_color="#0b1020",
            hover_color="#60a5fa",
            height=44,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._finish,
        )
        self.start_btn.pack(fill="x", padx=6)
        self.win.focus_force()
        self.textbox.focus_set()


    def _finish(self):
        text = self.textbox.get("1.0", "end").strip()
        if not text:
            return
        self.script_text = text
        self.win.destroy()

    
    def _start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _do_move(self, event):
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.win.geometry(f"+{x}+{y}")
