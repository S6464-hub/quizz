import streamlit as st
import pandas as pd
import random
import difflib

st.set_page_config(page_title="Kelime Quiz", layout="centered")

st.title("📘 İngilizce-Türkçe Kelime Testi")
st.write("Lütfen .xlsx formatında kelime dosyanızı yükleyin. İkinci sütun İngilizce, üçüncü sütun Türkçe olmalıdır.")

uploaded_file = st.file_uploader("📂 Dosya Seç", type=["xlsx"])

@st.cache_data
def load_words(file):
    xls = pd.ExcelFile(file)
    excluded_sheets = ["Book - 11", "Blok-11 Grammer"]
    included_sheets = [s for s in xls.sheet_names if s not in excluded_sheets]

    word_pairs = []
    for sheet in included_sheets:
        df = xls.parse(sheet)
        for _, row in df.iterrows():
            try:
                eng = str(row[1]).strip()
                tr = str(row[2]).strip()
                if eng and tr and eng.lower() != 'nan':
                    word_pairs.append((eng, tr))
            except:
                continue
    return word_pairs

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
        if similar_options:
            opt = random.choice(similar_options)
            if opt not in choices:
                choices.append(opt)
        else:
            opt = random.choice(word_list)
            if opt != correct and opt not in choices:
                choices.append(opt)
    random.shuffle(choices)
    return correct[0], correct_tr, [opt[1] for opt in choices]

if uploaded_file:
    words = load_words(uploaded_file)
    if 'q_index' not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.answers = {}

    questions = [generate_question(words) for _ in range(20)]
    q_index = st.session_state.q_index
    current = questions[q_index]
    st.subheader(f"Soru {q_index + 1}")
    st.write(f"'{current[0]}' kelimesinin Türkçesi nedir?")

    for idx, choice in enumerate(current[2]):
        if st.button(choice, key=f"btn_{q_index}_{idx}"):
            st.session_state.answers[q_index] = choice
            st.session_state.q_index += 1
            st.rerun()

    with st.sidebar:
        st.markdown("### 📊 Sonuçlar")
        correct = sum(1 for i, ans in st.session_state.answers.items() if ans == questions[i][1])
        total = len(st.session_state.answers)
        st.write(f"✔️ Doğru: {correct}")
        st.write(f"❌ Yanlış: {total - correct}")

        if st.button("🔄 Yeniden Başla"):
            st.session_state.q_index = 0
            st.session_state.answers = {}
            st.rerun()
