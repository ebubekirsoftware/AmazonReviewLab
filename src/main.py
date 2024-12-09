import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

from amazon_api import AmazonAPI
from classification import ReviewClassifier
from summarization import ReviewSummarizer

class MainApp:
    """
    MainApp, Amazon ürün yorumlarını çekme, sınıflandırma ve özetleme işlemlerini gerçekleştiren sınıftır.

    Methods:
        run(asin): Verilen ASIN koduna göre tüm işlemleri yürütür.
    """

    def __init__(self, model_checkpoint_path) -> None:
        """
        MainApp sınıfını başlatır ve gerekli sınıf örneklerini oluşturur.
        """
        self.amazon_api = AmazonAPI()
        self.classifier = ReviewClassifier(model_checkpoint_path)
        self.summarizer = ReviewSummarizer()
        self.categories = ["URUN_KALITESI", "PAKETLEME/TESLIMAT", "FIYAT/PERFORMANS", "URUN_TASARIMI"]

    def run(self, asin: str) -> None:
        """
        Verilen ASIN koduna göre Amazon'dan yorumları çekme, sınıflandırma ve özetleme işlemlerini gerçekleştirir.

        Args:
            asin (str): Ürüne ait ASIN kodu.
        """
        # 1. Amazon yorumlarını çekme
        print("Yorumlar çekiliyor...")
        reviews = self.amazon_api.get_amazon_reviews(asin)
        if not reviews:
            print("Yorumlar alınamadı. İşlem sonlandırıldı.")
            return
        print("Yorumlar başarıyla çekildi.")

        # 2. Yorumları sınıflandırma
        print("Yorumlar sınıflandırılıyor...")
        self.classifier.categories = self.categories  # Kategorileri sınıflandırıcıya aktarma
        classified_reviews = self.classifier.classify_reviews(reviews, threshold=0.5)
        if not classified_reviews:
            print("Sınıflandırma sonuçları alınamadı. İşlem sonlandırıldı.")
            return
        print("Yorumlar başarıyla sınıflandırıldı.")

        # 3. Yorumları kategori bazında grupla
        print("Yorumlar kategorilere göre gruplanıyor...")
        kategori_yorumlari = {}
        for item in classified_reviews:
            for kategori in item["categories"]:
                kategori_yorumlari.setdefault(kategori, []).append(item["review"])
        print("Yorumlar kategorilere göre başarıyla gruplanmıştır.")

        # 4. Özetleme işlemi
        print("Yorumlar özetleniyor...")
        summary = self.summarizer.summarize_reviews(kategori_yorumlari)
        if summary:
            print("Yorumların Özeti:")
            print(summary)
        else:
            print("Özetleme işlemi başarısız oldu.")

    def get_asin_from_link(self) -> str:
        """
        Kullanıcıdan Amazon ürün linki alarak ASIN kodunu ayıklar.

        Returns:
            str: Geçerli ASIN kodu.
        """
        while True:
            user_input = input("Lütfen Amazon ürün linkini giriniz: ")
            asin_match = re.search(r"/dp/([A-Z0-9]{10})|rd_i=([A-Z0-9]{10})", user_input, re.IGNORECASE)
            if asin_match:
                asin_code_1 = asin_match.group(1)
                asin_code_2 = asin_match.group(2)
                test_asin = asin_code_1 if asin_code_1 else asin_code_2
                print(f"Ürün bulundu. Ürünün ASIN numarası: {test_asin}")
                return test_asin
            else:
                print("Geçerli bir ASIN numarası bulunamadı. Lütfen geçerli bir Amazon ürün linki girin.")

# Uygulama çalıştırma
if __name__ == "__main__":
    model_path = os.path.abspath("models/finetuned_class_model")
    main_app = MainApp(model_checkpoint_path=model_path)
    asin_code = main_app.get_asin_from_link()
    main_app.run(asin_code)
