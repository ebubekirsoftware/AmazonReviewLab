import requests
import ollama
from dotenv import load_dotenv


class ReviewSummarizer:
    """
    ReviewSummarizer, verilen sınıflandırılmış yorumları özetleyen bir sınıftır.

    Methods:
        summarize_reviews(review_data): Verilen yorumları ve kategorileri özetler.
    """

    def __init__(self) -> None:
        load_dotenv()

    def ollama_generate(self, prompt):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        return response.json()["response"].strip()

    def summarize_reviews(self, kategori_yorumlari: dict) -> str:
        """
        Verilen yorumları ve kategorileri özetler.

        Args:
            kategori_yorumlari (dict): Kategorilere göre gruplandırılmış yorumları içeren sözlük.

        Returns:
            str: Tüm yorumların özetlendiği metin.
        """
        kategori_yorum_metni = "\n".join(
            [f"{kategori}: " + " | ".join(yorumlar) for kategori, yorumlar in kategori_yorumlari.items()]
        )

        prompt = f"""
        Sen [Türkçe] AI yorum özetleme asistanısın. Verdiğin yanıt tamamen Türkçe olmalıdır. [Dil: Türkçe]
        Aşağıdaki farklı kategorilere ait kullanıcı yorumlarını analiz et ve her kategori için duygu analizi yaparak ortalama bir puan hesapla. 
        Ardından her kategori için ayrı ayrı değerlendirme hazırla.
        Değerlendirmelerin açık, sade ve düzgün bir Türkçe ile yazılmasını sağla. Her kategorinin analizini ayrı bir başlık altında belirt. 
        Son olarak, tüm kategoriler için genel bir sonuç çıkar.

        Lütfen şu formatta sonucu belirtin:

        <format>
        Yorumların Puanları:
        1. Ürün Kalitesi:(puan/10)(Bu kategori için puanlama)
        2. Paketleme/Teslimat:(puan/10)(Bu kategori için puanlama)
        3. Ürün Tasarımı:(puan/10)(Bu kategori için puanlama)
        4. Fiyat/Performans:(puan/10)(Bu kategori için puanlama)
        5. Genel Sonuç:(puan/10)(Bu kategori için puanlama)

        Yorum Özetleri:
        1. Ürün Kalitesi: (Bu kategori için değerlendirme)
        2. Paketleme/Teslimat: (Bu kategori için değerlendirme)
        3. Ürün Tasarımı: (Bu kategori için değerlendirme)
        4. Fiyat/Performans: (Bu kategori için değerlendirme)
        \n
        \n
        \n
        5. Genel Sonuç: (Tüm kategoriler için genel değerlendirme)
        <format>

        Yorumlar:
        {kategori_yorum_metni}

        """
        try:
            response = self.ollama_generate(prompt)
            return response
        except Exception as e:
            print(f"Özetleme işlemi sırasında bir hata oluştu: {str(e)}")
            return ""
