import requests
import os
import math
from dotenv import load_dotenv


class AmazonAPI:
    """
    AmazonAPI, Amazon'dan ürün yorumlarını çeken bir sınıftır.

    Attributes:
        api_key (str): API erişimi için kullanılan RapidAPI anahtarı.

    Methods:
        get_amazon_reviews(asin): Amazon ürün yorumlarını çeker ve liste olarak döner.
    """

    def __init__(self) -> None:
        """
        AmazonAPI sınıfını başlatır ve gerekli ortam değişkenlerini yükler.
        """

        # .env dosyasının tam yolunu belirle
        dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')

        # .env dosyasını yükle
        load_dotenv(dotenv_path=dotenv_path)

        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError(
                "RAPIDAPI_KEY .env dosyasından yüklenemedi. Lütfen .env dosyanızı kontrol edin ve RAPIDAPI_KEY değerini ekleyin.")
        self.host = "real-time-amazon-data.p.rapidapi.com"

    def calculate_page_count(self, total_reviews: int) -> int:
        """
        Toplam yorum sayısına göre gerekli sayfa sayısını hesaplayan bir fonksiyon.

        Args:
            total_reviews (int): Ürünün toplam yorum sayısı.

        Returns:
            int: Gerekli sayfa sayısı.
        """
        return math.ceil(total_reviews / 10)

    def get_amazon_reviews(self, asin: str) -> list:
        """
        Amazon ürün yorumlarını tüm sayfalar boyunca API'den çeken bir fonksiyon.

        Args:
            asin (str): Ürüne ait ASIN kodu.

        Returns:
            list: Tüm sayfalardan gelen yorumları içeren bir liste.
        """
        url = f"https://{self.host}/product-reviews"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host
        }

        # İlk sayfa sorgusu ile toplam yorum sayısını öğren
        querystring = {
            "asin": asin,
            "country": "TR",
            "sort_by": "TOP_REVIEWS",
            "star_rating": "ALL",
            "verified_purchases_only": "false",
            "images_or_videos_only": "false",
            "current_format_only": "false",
            "page": "1"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code != 200:
            print(f"API çağrısı başarısız oldu. Status code: {response.status_code}, Hata mesajı: {response.text}")
            return []

        data = response.json()
        if 'data' not in data or 'total_reviews' not in data['data']:
            print(
                "Toplam yorum sayısı bilgisi bulunamadı. API yanıt formatı değişmiş olabilir, lütfen API dökümantasyonunu kontrol edin.")
            return []

        total_reviews = data['data']['total_reviews']
        page_count = self.calculate_page_count(total_reviews)

        all_reviews = []

        # İlk sayfanın verilerini işleyin
        if 'reviews' in data['data']:
            reviews_list = data['data']['reviews']
            all_reviews.extend([
                review.get('review_comment', 'No Comment')
                for review in reviews_list
            ])

        # Kalan sayfalar için veri çekme
        for page in range(2, page_count + 1):
            querystring["page"] = str(page)
            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code != 200:
                print(
                    f"Page {page} için API çağrısı başarısız oldu. Status code: {response.status_code}, Hata mesajı: {response.text}")
                continue

            try:
                data = response.json()
                if 'data' in data and 'reviews' in data['data']:
                    reviews_list = data['data']['reviews']
                    all_reviews.extend([
                        review.get('review_comment', 'No Comment')
                        for review in reviews_list
                    ])
                else:
                    print(
                        f"Page {page} verileri alınamadı. API yanıt formatı değişmiş olabilir, lütfen API dökümantasyonunu kontrol edin.")
            except json.JSONDecodeError as e:
                print(f"Page {page} yanıtı çözülürken bir hata oluştu: {str(e)}")

        return all_reviews if all_reviews else []
