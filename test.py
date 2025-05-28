import tkinter as tk
import pandas as pd
import random
import difflib
import json
import os

file_path = "ALC WORDS (SO).xlsx"
xls = pd.ExcelFile(file_path)

excluded_sheets = ["Book - 11", "Blok-11 Grammer"]
included_sheets = [sheet for sheet in xls.sheet_names if sheet not in excluded_sheets]

word_pairs = []
for sheet in included_sheets:
    df = xls.parse(sheet)
    for _, row in df.iterrows():
        try:
            if pd.notna(row[1]) and pd.notna(row[2]):
                eng = str(row[1]).strip()
                tr = str(row[2]).strip()
                if eng and tr:
                    word_pairs.append((eng, tr))
        except Exception:
            continue

def generate_question(word_list):
    correct = random.choice(word_list)
    correct_tr = correct[1]

    def similar_words(target, words, n=10, cutoff=0.6):
        # difflib.get_close_matches hedef kelimeyi words içindeki benzerlerden bulur
        # Burada words içi sadece türkçe karşılıklar
        tr_words = [w[1] for w in words if w != correct]
        close_tr = difflib.get_close_matches(target, tr_words, n=n, cutoff=cutoff)
        close = [w for w in words if w[1] in close_tr]
        return close

    similar_options = similar_words(correct_tr, word_list)

    choices = [correct]
    while len(choices) < 4:
        if similar_options:
            opt = random.choice(similar_options)
            if opt not in choices:
                choices.append(opt)
                similar_options.remove(opt)
        else:
            opt = random.choice(word_list)
            if opt != correct and opt not in choices:
                choices.append(opt)
    random.shuffle(choices)
    return (correct[0], correct_tr, [choice[1] for choice in choices])

class QuizApp:
    def __init__(self, root, word_list):
        self.root = root
        self.root.title("Vocabulary Quiz")
        self.root.geometry("820x620")

        self.word_list = word_list
        self.questions = [generate_question(word_list) for _ in range(min(100, len(word_list)))]
        self.q_index = 0
        self.answers = {}

        self.answers_file = "answers.json"
        self.load_answers()

        self.question_label = tk.Label(root, font=('Times New Roman', 18), wraplength=750, justify="center")
        self.question_label.pack(pady=30)

        self.buttons = []
        for i in range(4):
            btn = tk.Button(root, font=('Times New Roman', 16), width=60, anchor='w',
                            command=lambda i=i: self.check_answer(i))
            btn.pack(pady=12)
            self.buttons.append(btn)

        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=20)
        self.back_btn = tk.Button(nav_frame, text="← Geri", font=('Times New Roman', 16), width=15, command=self.prev_question)
        self.back_btn.grid(row=0, column=0, padx=40)
        self.next_btn = tk.Button(nav_frame, text="İleri →", font=('Times New Roman', 16), width=15, command=self.next_question)
        self.next_btn.grid(row=0, column=1, padx=40)

        self.status_label = tk.Label(root, text="", font=('Times New Roman', 14))
        self.status_label.pack(pady=12)

        self.score_label = tk.Label(root, text="", font=('Times New Roman', 18))
        self.score_label.pack()

        # Platform bağımsız varsayılan renkler
        self.default_bg = self.buttons[0].cget("background")
        self.default_fg = self.buttons[0].cget("foreground")

        self.load_question()

    def load_answers(self):
        if os.path.exists(self.answers_file):
            try:
                with open(self.answers_file, "r", encoding="utf-8") as f:
                    self.answers = json.load(f)
                    # json keys string, index için int'e çevirelim
                    self.answers = {int(k): v for k, v in self.answers.items()}
            except Exception:
                self.answers = {}
        else:
            self.answers = {}

    def save_answers(self):
        try:
            with open(self.answers_file, "w", encoding="utf-8") as f:
                json.dump(self.answers, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cevap kaydedilemedi: {e}")

    def load_question(self):
        self.display_question()
        self.update_score()

    def display_question(self):
        eng, correct_tr, options = self.questions[self.q_index]
        self.correct_answer = correct_tr
        self.question_label.config(text=f"Soru {self.q_index + 1}: '{eng}' kelimesinin anlamı nedir?")
        self.status_label.config(text=f"{self.q_index + 1} / {len(self.questions)}")

        selected = self.answers.get(self.q_index, None)
        for i, option in enumerate(options):
            self.buttons[i].config(text=option, state="normal", bg=self.default_bg, fg=self.default_fg)
            if selected:
                if option == self.correct_answer:
                    self.buttons[i].config(bg="#6FCF97", fg="white")  # Pastel yeşil
                elif option == selected:
                    self.buttons[i].config(bg="#EB5757", fg="white")  # Pastel kırmızı
                else:
                    self.buttons[i].config(bg=self.default_bg, state="disabled", fg=self.default_fg)

    def check_answer(self, choice_index):
        selected = self.buttons[choice_index].cget("text")
        self.answers[self.q_index] = selected
        self.save_answers()

        for btn in self.buttons:
            if btn.cget("text") == self.correct_answer:
                btn.config(bg="#6FCF97", fg="white")  # Pastel yeşil
            elif btn.cget("text") == selected:
                btn.config(bg="#EB5757", fg="white")  # Pastel kırmızı
            else:
                btn.config(bg=self.default_bg, fg=self.default_fg)
            btn.config(state="disabled")

        self.update_score()
        # 1 saniye sonra otomatik sonraki soruya geç
        self.root.after(1000, self.auto_next)

    def auto_next(self):
        if self.q_index < len(self.questions) - 1:
            self.q_index += 1
            self.load_question()

    def next_question(self):
        if self.q_index < len(self.questions) - 1:
            self.q_index += 1
            self.load_question()

    def prev_question(self):
        if self.q_index > 0:
            self.q_index -= 1
            self.load_question()

    def update_score(self):
        correct_count = sum(1 for i, ans in self.answers.items() if i < len(self.questions) and ans == self.questions[i][1])
        total_answered = len(self.answers)
        self.score_label.config(
            text=f"✔️ Doğru: {correct_count}    ❌ Yanlış: {total_answered - correct_count}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root, word_pairs)
    root.mainloop()
