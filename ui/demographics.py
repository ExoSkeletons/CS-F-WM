from typing import Any

import ttkbootstrap as ttk

from ui.app import WidgetFrame
from ui.survey import DataCollector
from ui.theme import pady, Fonts, padx, pad_l


class DemoPage(WidgetFrame, DataCollector):
    def decline_button(self, master: Any, var: ttk.StringVar) -> ttk.Radiobutton:
        decline_text = "Decline to State"
        decline_style = "secondary" + self.r_style_b

        b = ttk.Radiobutton(
            master=master,
            text=decline_text, value="-",
            variable=var,
            bootstyle=decline_style
        )
        b.pack(side="left", padx=padx)
        return b

    def _create_widgets(self):
        self.title_font = Fonts.h1
        self.subtitle_font = Fonts.small
        self.q_font = Fonts.h3
        self.r_style_b = "-outline-toolbutton"
        self.r_style = "info" + self.r_style_b

        self.config(padding=(padx, pady))

        self.bind_all("<ButtonRelease>", lambda event: self.event_generate("<<PageValidityChanged>>"))

        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=pady)
        ttk.Label(
            title_frame,
            text="Demographic Information", font=self.title_font
        ).grid(row=0, column=0)
        # ttk.Label(
        #     title_frame,
        #     text="(This page is optional)", font=self.subtitle_font
        # ).grid(row=0, column=1, padx=padx, sticky="sw")

        self.gender_var = ttk.StringVar(value=None)
        self.deg_level_var = ttk.StringVar(value=None)
        self.deg_field_var = ttk.StringVar(value=None)
        self.eng_level_var = ttk.StringVar(value=None)
        self.age_var = ttk.StringVar(value=None)
        self.ai_use_var = ttk.StringVar(value=None)

        answers_frame = ttk.Frame(self)
        answers_frame.pack(fill="both", expand=True)

        gender_frame = ttk.Frame(answers_frame)
        gender_frame.pack(fill="x", pady=pady)
        ttk.Label(gender_frame, text="Gender", font=self.q_font).pack(anchor="w", pady=pady)
        gender_opts = ttk.Frame(gender_frame)
        gender_opts.pack(anchor="w", padx=padx)
        self.decline_button(gender_opts, self.gender_var)
        for text, value in [
            ("Male", "m"),
            ("Female", "f"),
            ("Other", "o"),
        ]:
            ttk.Radiobutton(
                gender_opts,
                text=text, value=value,
                variable=self.gender_var,
                bootstyle=self.r_style
            ).pack(side="left", padx=padx)

        age_frame = ttk.Frame(answers_frame)
        age_frame.pack(fill="x", pady=pady)
        ttk.Label(age_frame, text="Age", font=self.q_font).pack(anchor="w", pady=pady)
        age_opts = ttk.Frame(age_frame)
        age_opts.pack(anchor="w", padx=padx)
        min_age = 20
        max_age = 50
        step = 5
        ar = [f"{age + 1}-{age + step}" for age in range(min_age, max_age, step)]
        ar.insert(0, f"18 or below")
        ar.insert(1, f"18-{min_age}")
        ar.append(f"{max_age + 1} or above")
        # self.decline_button(age_opts, self.age_var)
        for r in ar:
            ttk.Radiobutton(
                age_opts,
                text=r, value=r,
                variable=self.age_var,
                bootstyle=self.r_style
            ).pack(side="left", padx=padx)

        edu_frame = ttk.Frame(answers_frame)
        edu_frame.pack(fill="x", pady=pady)
        edu_level = ttk.Frame(edu_frame)
        edu_level.grid(row=0, column=0)
        ttk.Label(
            edu_level,
            text="What Degree are you currently pursuing?",
            font=self.q_font
        ).pack(anchor="w", pady=pady)
        edu_opts = ttk.Frame(edu_level)
        edu_opts.pack(anchor="w", padx=padx)
        # self.decline_button(edu_opts, self.deg_level_var)
        for text, value, color in [
            ("BSc", "bsc", "success"),
            ("MSc", "msc", "warning"),
            ("PhD", "phd", "danger"),
        ]:
            ttk.Radiobutton(
                edu_opts,
                text=text, value=value,
                variable=self.deg_level_var,
                bootstyle=color + self.r_style_b
            ).pack(side="left", padx=padx)

        edu_field_frame = ttk.Frame(edu_frame)
        edu_field_frame.grid(row=0, column=1, padx=pad_l)
        ttk.Label(
            edu_field_frame,
            text="What is the field of your Degree?",
            font=self.q_font
        ).pack(anchor="w", pady=pady)
        edu_field_text = ttk.Entry(edu_field_frame, textvariable=self.deg_field_var, bootstyle="info")
        edu_field_text.pack(anchor="w", padx=padx)

        eng_frame = ttk.Frame(answers_frame)
        eng_frame.pack(fill="x", pady=pady)
        eng_level = ttk.Frame(eng_frame)
        eng_level.grid(row=0, column=0)
        ttk.Label(
            eng_level,
            text="How would you rate your English comprehension?",
            font=self.q_font
        ).pack(anchor="w", pady=pady)
        eng_opts = ttk.Frame(eng_level)
        eng_opts.pack(anchor="w", padx=padx)
        # self.decline_button(eng_opts, self.eng_level_var)
        c_range = ['danger', 'warning', 'info', 'success']
        n = 6
        for i in range(1, n):
            ttk.Radiobutton(
                eng_opts,
                text=str(i), value=str(i),
                variable=self.eng_level_var,
                bootstyle=c_range[int((float(i) / n) * len(c_range))] + self.r_style_b
            ).pack(side="left", padx=padx)

        ai_use_frame = ttk.Frame(answers_frame)
        ai_use_frame.pack(fill="x", pady=pady)
        ttk.Label(
            ai_use_frame,
            text="Do you use AI tools? If so, how often?",
            font=self.q_font
        ).pack(anchor="w", pady=pady)
        ai_opts = ttk.Frame(ai_use_frame)
        ai_opts.pack(anchor="w", padx=padx)
        # self.decline_button(ai_opts, self.ai_use_var)
        for text, value, color in [
            ("No", False, "danger"),
            ("Several times a Day", "several times a day", "success"),
            ("On a Daily basis", "daily", "info"),
            ("On a Weekly basis", "weekly", "info"),
            ("On a Monthly basis", "monthly", "warning"),
            ("On a Yearly basis", "yearly", "secondary"),
        ]:
            ttk.Radiobutton(
                ai_opts,
                text=text, value=value,
                variable=self.ai_use_var,
                bootstyle=color + self.r_style_b if color is not None else self.r_style
            ).pack(side="left", padx=padx)

        super()._create_widgets()

    def get_data(self) -> dict:
        return {
            "gender": self.gender_var.get() or None,
            "edu_pursuing": self.deg_level_var.get() or None,
            "edu_field": self.deg_field_var.get() or None,
            "age": self.age_var.get() or None,
            "ai_use_freq": self.ai_use_var.get() or None,
        }

    def is_valid(self) -> bool:
        return bool(
                self.gender_var.get() and
                self.deg_level_var.get() and
                self.eng_level_var.get() and
                self.age_var.get() and
                self.ai_use_var.get() and
                True
        )
