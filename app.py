import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

from classification import ReviewClassifier
from amazon_api import AmazonAPI
from summarization import ReviewSummarizer

app = FastAPI()
model_checkpoint_path = os.path.abspath("src/models/finetuned_class_model")
amazon_api = AmazonAPI()
classifier = ReviewClassifier(model_checkpoint_path)
summarizer = ReviewSummarizer()

class TextRequest(BaseModel):
    link: str

def get_asin_from_link(link) -> dict:
    asin_match = re.search(r"/dp/([A-Z0-9]{10})|rd_i=([A-Z0-9]{10})", link, re.IGNORECASE)
    if asin_match:
        asin_code_1 = asin_match.group(1)
        asin_code_2 = asin_match.group(2)
        test_asin = asin_code_1 if asin_code_1 else asin_code_2
        print(f"Ürün bulundu. Ürünün ASIN numarası: {test_asin}")
        return test_asin
    else:
        return {"message":'Geçerli bir ASIN numarası bulunamadı.'}


@app.post("/classify")
def classify(link):
    asin = get_asin_from_link(link)

    # 1. Amazon yorumlarını çekme
    reviews = amazon_api.get_amazon_reviews(asin)
    if not reviews:
        return {"message": "Yorumlar alınamadı. İşlem sonlandırıldı."}

    # 2. Yorumları sınıflandırma
    print("Yorumlar sınıflandırılıyor...")
    classified_reviews = classifier.classify_reviews(reviews, threshold=0.5)

    if not classified_reviews:
        return {"message": 'Sınıflandırma sonuçları alınamadı. İşlem sonlandırıldı.'}
    return {"classified_reviews": classified_reviews}


@app.post("/predict")
def predict(request: TextRequest):
    asin = get_asin_from_link(request.link)

    # 1. Amazon yorumlarını çekme
    reviews = amazon_api.get_amazon_reviews(asin)
    if not reviews:
        return {"message": "Yorumlar alınamadı. İşlem sonlandırıldı."}

    # 2. Yorumları sınıflandırma
    print("Yorumlar sınıflandırılıyor...")
    classified_reviews = classifier.classify_reviews(reviews, threshold=0.5)

    if not classified_reviews:
        return {"message": 'Sınıflandırma sonuçları alınamadı. İşlem sonlandırıldı.'}

    # 3. Yorumları kategori bazında grupla
    print("Yorumlar kategorilere göre gruplanıyor...")
    kategori_yorumlari = {}
    for item in classified_reviews:
        for kategori in item["categories"]:
            kategori_yorumlari.setdefault(kategori, []).append(item["review"])
    print("Yorumlar kategorilere göre başarıyla gruplanmıştır.")

    # 4. Özetleme işlemi
    print("Yorumlar özetleniyor...")
    summary = summarizer.summarize_reviews(kategori_yorumlari)
    if summary:
        return {"conclusion": summary, "categories": kategori_yorumlari}
    else:
        return {"message": "Özetleme işlemi başarısız oldu."}
