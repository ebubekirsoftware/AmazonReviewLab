import streamlit as st
import requests
import pandas as pd
import re

# Sayfa Yapılandırması
st.set_page_config(page_title="Amazon Ürün Yorum Analizi", layout="centered")

# Stil ekleme (CSS)
def add_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .sidebar .sidebar-content {{
            background-color: rgba(0, 0, 0, 0.2);
        }}
        h1, h2, h3, h4, h5, h6 {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 5px;
        }}
        .block-container {{
            font-size: 1.4em;
        }}
        div[data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.2);
        }}
        .element-container > div {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 5px;
        }}
        button[kind="primary"] {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    # Uygulama sayfalarını ayırma
    if "api_response" not in st.session_state:
        st.session_state["api_response"] = None
    page = st.sidebar.radio("Sayfa Seçimi", ["Link Girişi", "Sonuçlar"])

    if page == "Link Girişi":
        link_input_page()
    elif page == "Sonuçlar":
        results_page()

def link_input_page():
    # Başlık
    st.title("AMAZON Ürün Yorum Analizi (TR)")

    # Link giriş alanı
    st.write("Amazon ürün linkini aşağıya girin ve 'Analiz Et' butonuna tıklayın.")
    link = st.text_input("Amazon Ürün Linki", placeholder="https://www.amazon.com.tr/...")

    # Analiz Et butonu
    if st.button("Analiz Et"):
        if not link:
            st.error("Lütfen bir Amazon ürün linki girin.")
            return

        # API isteği gönderme
        url = "http://127.0.0.1:4000/predict/"
        data = {"link": link}

        try:
            with st.spinner("Analiz ediliyor, lütfen bekleyin..."):
                response = requests.post(url, json=data)
                result = response.json()

                if response.status_code != 200:
                    st.error("API'den geçerli bir yanıt alınamadı.")
                    return

                # API yanıtını session state'e kaydetme
                st.session_state["api_response"] = result
                st.success("Analiz tamamlandı! Sol taraftaki menüden 'Sonuçlar' sayfasına geçebilirsiniz.")

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

def results_page():
    # Sayfa Başlığı
    st.title("Amazon Ürün Yorum Analizi - Sonuçlar")

    # API yanıtı kontrolü
    if "api_response" not in st.session_state or st.session_state["api_response"] is None:
        st.warning("Henüz bir analiz yapılmadı. Lütfen 'Link Girişi' sayfasına giderek bir ürün linki girin.")
        return

    # API yanıtını yükle
    response_data = st.session_state["api_response"]

    # Yorumların Puanları Bölümü
    st.subheader("Yorumların Puanları")

    # Gelen yanıt metninden puanları çekme
    conclusion_text = response_data.get('conclusion', '')
    categories = ["Ürün Kalitesi", "Paketleme/Teslimat", "Ürün Tasarımı", "Fiyat/Performans", "Genel Sonuç"]
    scores = {}
    lines = conclusion_text.split("\n")
    for line in lines:
        for category in categories:
            if category.lower() in line.lower():
                match_score = re.search(r"(\d+(?:[,.]\d+)?)/10", line)
                if match_score:
                    scores[category] = float(match_score.group(1).replace(",", "."))

    for category in categories:
        score = scores.get(category, None)
        if score is not None:
            st.write(f"**{category}:**")
            progress_color = get_color(score)
            st.markdown(
                f"""<div style='background-color: {progress_color}; border-radius: 10px; height: 25px; width: {score * 10}%;'></div>""",
                unsafe_allow_html=True,
            )
            st.write(f"Puan: {score:.1f}/10")

    # Yorum Özetleri Bölümü
    st.subheader("Yorum Özetleri")
    summary_start = None
    lines = conclusion_text.split("\n")
    for i, line in enumerate(lines):
        if "yorum özetleri:".lower() in line.lower():
            summary_start = i + 1
            break

    if summary_start is not None:
        summaries_text = "\n".join(lines[summary_start:])
        st.markdown(summaries_text)

    # Kategori Yorumları
    st.subheader("Kategori Yorumları")
    category_comments = response_data.get("categories", {})
    if not category_comments:
        st.write("Kategori yorumları bulunamadı.")
    else:
        for category, comments in category_comments.items():
            if st.button(f"{category} Yorumları"):
                if comments:
                    st.write(f"### {category} Yorumları")
                    df = pd.DataFrame(comments, columns=["Yorumlar"])
                    st.dataframe(df)
                else:
                    st.write(f"{category} için yorum bulunamadı.")

    # Yeni Analiz Başlat Butonu
    if st.button("Yeni Analiz Başlat"):
        # Session state'i sıfırla
        st.session_state.clear()
        # Kullanıcıyı yönlendir
        st.experimental_rerun()

def get_color(score):
    if score <= 6.9:
        return "#FF4B4B"  # Kırmızı
    elif score <= 7.9:
        return "#FFA500"  # Turuncu
    elif score <= 8.9:
        return "#32CD32"  # Yeşil
    else:
        return "#0000CD"  # Koyu Mavi

if __name__ == "__main__":
    # Arka plan resmi ekle
    add_background_image("https://images.unsplash.com/photo-1662947368791-8630979e964b?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8YW1hem9uJTIwbG9nbyUyMDNkfGVufDB8fDB8fHww")
    main()
