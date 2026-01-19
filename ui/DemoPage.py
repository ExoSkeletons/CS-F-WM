import tkinter as tk
from tkinter import ttk

from ui.app import WidgetFrame


class DemoPage(WidgetFrame):
    def _create_widgets(self):
        # --- Page title ---
        ttk.Label(
            self,
            text="Optional Demographic Information",
        ).pack(anchor="w", pady=(0, 10))
        ttk.Label(
            self,
            text="(This page is optional.)",
        ).pack(anchor="w", pady=(0, 15))

        self.gender_var = tk.StringVar(value=None)
        self.deg_level_var = tk.StringVar(value=None)
        self.age_var = tk.StringVar(value=None)
        self.ai_use_var = tk.StringVar(value=None)

        answers_frame = ttk.Frame(self)
        answers_frame.pack(fill="both", expand=True)

        gender_frame = ttk.Frame(answers_frame)
        gender_frame.pack(fill="x", pady=5)
        ttk.Label(gender_frame, text="Gender:").pack(anchor="w")
        gender_opts = ttk.Frame(gender_frame)
        gender_opts.pack(anchor="w", padx=10)

        for text, value in [
            ("Male", "m"),
            ("Female", "f"),
            ("Other", "o"),
        ]:
            ttk.Radiobutton(
                gender_opts,
                text=text, value=value,
                variable=self.gender_var
            ).pack(side="left", padx=5)

        edu_level = ttk.Frame(answers_frame)
        edu_level.pack(fill="x", pady=5)
        ttk.Label(edu_level, text="What degree are you currently pursuing?").pack(anchor="w")
        edu_opts = ttk.Frame(edu_level)
        edu_opts.pack(anchor="w", padx=10)
        for text, value in [
            ("BSc", "bsc"),
            ("MSc", "msc"),
            ("PhD", "phd"),
        ]:
            ttk.Radiobutton(
                edu_opts,
                text=text, value=value,
                variable=self.deg_level_var
            ).pack(side="left", padx=5)

        age_frame = ttk.Frame(answers_frame)
        age_frame.pack(fill="x", pady=5)
        ttk.Label(age_frame, text="Age:").pack(anchor="w")
        age_opts = ttk.Frame(age_frame)
        age_opts.pack(anchor="w", padx=10)
        min_age = 20
        max_age = 50
        step = 5
        ar = [f"{age + 1}-{age + step}" for age in range(min_age, max_age, step)]
        ar.insert(0, f"18 or below")
        ar.insert(1, f"18-{min_age}")
        ar.append(f"{max_age + 1} or above")
        for r in ar:
            ttk.Radiobutton(age_opts, text=r, value=r, variable=self.age_var).pack(side="left", padx=5)

        ai_frame = ttk.Frame(answers_frame)
        ai_frame.pack(fill="x", pady=5)
        ttk.Label(ai_frame, text="Do you use AI tools often?").pack(anchor="w")
        ai_opts = ttk.Frame(ai_frame)
        ai_opts.pack(anchor="w", padx=10)
        for text, value in [
            ("Yes", True),
            ("No", False),
        ]:
            ttk.Radiobutton(
                ai_opts,
                text=text,
                value=value,
                variable=self.ai_use_var
            ).pack(side="left", padx=5)

        super()._create_widgets()

    def get_data(self) -> dict:
        return {
            "gender": self.gender_var.get() or None,
            "edu_pursuing": self.deg_level_var.get() or None,
            "age": self.age_var.get() or None,
            "uses_ai_often": self.ai_use_var.get() or None,
        }
