import customtkinter as ctk

PANEL_BG = "#0b1020"
CARD_BG = "#111827"
ACCENT = "#38bdf8"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"


class GhostSummaryWindow:
    def __init__(self, root, summary):
        self.root = root

        self.win = ctk.CTkToplevel(root)
        self.win.geometry("760x560+260+140")
        self.win.configure(fg_color=PANEL_BG)
        self.win.overrideredirect(True)
        self.win.title("Ghost Summary")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.93)

        self.win.focus_force()
        # Escape = exit app
        self.win.bind("<Escape>", lambda e: self.win.destroy())

        container = ctk.CTkFrame(
            self.win, fg_color=PANEL_BG, corner_radius=16
        )
        container.pack(fill="both", expand=True, padx=24, pady=24)

        # Header
        ctk.CTkLabel(
            container,
            text="👻 Ghost Summary",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            container,
            text="Session review",
            font=ctk.CTkFont(size=13),
            text_color=MUTED,
        ).pack(anchor="w", pady=(2, 18))

        # Sections
        self._section(
            container,
            title="✔ Strong Coverage",
            items=summary.get("strong", []),
            accent="#22c55e",
        )

        self._section(
            container,
            title="⚠ Missed / Weak Areas",
            items=summary.get("missed", []),
            accent="#ef4444",
        )

        suggestions = summary.get("suggestions", [])
        if suggestions:
            self._section(
                container,
                title="💡 Suggestions",
                items=suggestions,
                accent=ACCENT,
            )

        # Show message if no data available
        strong_count = len(summary.get("strong", []))
        missed_count = len(summary.get("missed", []))
        if strong_count == 0 and missed_count == 0:
            ctk.CTkLabel(
                container,
                text="No summary data available yet. Continue your presentation to generate a summary.",
                wraplength=660,
                justify="center",
                text_color=MUTED,
                font=ctk.CTkFont(size=13),
            ).pack(anchor="center", pady=20)

        ctk.CTkButton(
            container,
            text="Exit",
            height=44,
            fg_color=ACCENT,
            text_color="#0b1020",
            hover_color="#0ea5e9",
            command=self.root.destroy,
        ).pack(fill="x", pady=(22, 0))

        self.win.focus_force()

    def _section(self, parent, title, items, accent):
        if not items:
            return

        card = ctk.CTkFrame(
            parent, fg_color=CARD_BG, corner_radius=14
        )
        card.pack(fill="x", pady=10)

        # Section title
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=accent,
        ).pack(anchor="w", padx=18, pady=(14, 8))

        # Bullet items
        for item in items[:5]:
            text = item["text"] if isinstance(item, dict) else item
            ctk.CTkLabel(
                card,
                text=f"• {text}",
                wraplength=660,
                justify="left",
                text_color=MUTED,
                font=ctk.CTkFont(size=12),
            ).pack(anchor="w", padx=22, pady=4)
