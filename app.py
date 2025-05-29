import streamlit as st
import pandas as pd
import random
import difflib

st.set_page_config(page_title="Kelime Quiz", layout="centered")
st.title("📘 İngilizce Kelime Quiz Uygulaması")

@st.cache_data
def load_words():
    file_path = "ALC_WORDS_SO.xlsx"  # GitHub'da aynı klasöre koy
    xls = pd.ExcelFile(file_path)
    excluded_sheets = ["Book - 11", "Blok-11 Grammer"]
    included_sheets = [s for s in xls.sheet_names if s not in excluded_sheets]

    words = []
    for sheet in included_sheets:
        df = xls.parse(sheet)
        for _, row in df.iterrows():
            try:
                eng = str(row[1]).strip()
                tr = str(row[2]).strip()
                if eng and tr and eng.lower() != 'nan':
                    words.append((eng, tr))
            except:
                continue
    return words

def generate_question(word_list):
    correct = random.choice(word_list)
    correct_tr = correct[1]

    def similar_words(target, words, threshold=0.5):
        close = []
        for w in words:
            if w == correct:
                continue
            seq = difflib.SequenceMatcher(None, target, w[1])
            if seq.ratio() > threshold:
                close.append(w)
        return close

    similar_options = similar_words(correct_tr, word_list)

    choices = [correct]
    while len(choices) < 4:
        opt = random.choice(similar_options if similar_options else word_list)
        if opt not in choices:
            choices.append(opt)
            if opt in similar_options:
                similar_options.remove(opt)
    random.shuffle(choices)
    return correct[0], correct_tr, [c[1] for c in choices]

# Uygulama başlat
words = load_words()
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.answers = {}

questions = [generate_question(words) for _ in range(min(100, len(words)))]

def show_question(index):
    eng, correct_tr, options = questions[index]
    st.markdown(f"### Soru {index+1}: **{eng}** kelimesinin anlamı nedir?")
    selected = st.radio("Seçiminiz:", options, key=index)
    if st.button("Cevabı Kontrol Et", key=f"check_{index}"):
        st.session_state.answers[index] = selected
        if selected == correct_tr:
            st.success("Doğru ✅")
        else:
            st.error(f"Yanlış ❌ Doğru cevap: {correct_tr}")

show_question(st.session_state.q_index)

col1, col2 = st.columns(2)
with col1:
    if st.session_state.q_index > 0 and st.button("← Geri"):
        st.session_state.q_index -= 1
with col2:
    if st.session_state.q_index < len(questions) - 1 and st.button("İleri →"):
        st.session_state.q_index += 1

correct_count = sum(1 for i, ans in st.session_state.answers.items() if ans == questions[i][1])
total_answered = len(st.session_state.answers)
st.markdown(f"#### ✔️ Doğru: {correct_count}    ❌ Yanlış: {total_answered - correct_count}")
