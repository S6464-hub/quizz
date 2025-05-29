import streamlit as st
import pandas as pd
import random
import difflib

# Başlık
st.title("📚 Vocabulary Quiz")

# Excel dosyasını yükle
@st.cache_data
def load_words(file_path):
    xls = pd.ExcelFile(file_path)
    excluded_sheets = ["Book - 11", "Blok-11 Grammer"]
    included_sheets = [sheet for sheet in xls.sheet_names if sheet not in excluded_sheets]

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

# Dosya yükleme
uploaded_file = st.file_uploader("📂 Lütfen kelime dosyanızı (.xlsx) yükleyin", type=["xlsx"])

if uploaded_file:
    words = load_words(uploaded_file)

    # Session State ile quiz durumu
    if 'q_index' not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.questions = []
        st.session_state.score = {'correct': 0, 'wrong': 0}
        st.session_state.answers = {}

    def generate_question(word_list):
        correct = random.choice(word_list)
        correct_tr = correct[1]

        def similar_words(target, words, threshold=0.5):
            return [w for w in words if w != correct and difflib.SequenceMatcher(None, target, w[1]).ratio() > threshold]

        choices = [correct]
        similar = similar_words(correct_tr, word_list)
        while len(choices) < 4:
            opt = random.choice(similar if similar else word_list)
            if opt not in choices:
                choices.append(opt)
        random.shuffle(choices)
        return (correct[0], correct[1], [choice[1] for choice in choices])

    # Soru listesi oluştur
    if not st.session_state.questions:
        st.session_state.questions = [generate_question(words) for _ in range(min(100, len(words)))]

    # Şu anki soru
    q = st.session_state.questions[st.session_state.q_index]
    eng, correct_tr, options = q

    st.markdown(f"### {st.session_state.q_index + 1}. '{eng}' kelimesinin Türkçesi nedir?")
    selected = st.radio("Seçenekler:", options)

    if st.button("Cevabı Kontrol Et"):
        if st.session_state.q_index not in st.session_state.answers:
            st.session_state.answers[st.session_state.q_index] = selected
            if selected == correct_tr:
                st.session_state.score['correct'] += 1
                st.success("✔️ Doğru!")
            else:
                st.session_state.score['wrong'] += 1
                st.error(f"❌ Yanlış! Doğru cevap: {correct_tr}")

    # Sonraki soru
    if st.button("➡️ Sonraki Soru"):
        if st.session_state.q_index < len(st.session_state.questions) - 1:
            st.session_state.q_index += 1
        else:
            st.info("🎉 Quiz bitti!")

    # Skor durumu
    st.write("---")
    st.markdown(f"**✅ Doğru:** {st.session_state.score['correct']} &nbsp;&nbsp;&nbsp;&nbsp; ❌ Yanlış: {st.session_state.score['wrong']}")
