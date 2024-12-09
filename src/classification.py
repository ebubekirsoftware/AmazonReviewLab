
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv


class ReviewClassifier:
    """
    ReviewClassifier, verilen yorumları önceden eğitilmiş bir sınıflandırma modeli kullanarak sınıflandıran bir sınıftır.

    Attributes:
        model_checkpoint_path (str): Modelin kontrol noktası yolu.
        tokenizer (AutoTokenizer): Yorumları işlemek için kullanılan tokenizer.
        model (AutoModelForSequenceClassification): Yorumları sınıflandırmak için kullanılan model.

    Methods:
        classify_reviews(review_list): Yorumları sınıflandırır ve sonuçları döndürür.
    """

    def __init__(self, model_checkpoint_path: str) -> None:
        """
        Args:
            model_checkpoint_path (str): Modelin kontrol noktası yolu.
        """
        load_dotenv()
        self.model_checkpoint_path = model_checkpoint_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_checkpoint_path)
        self.categories = ["URUN_KALITESI", "PAKETLEME/TESLIMAT", "FIYAT/PERFORMANS", "URUN_TASARIMI"]
        print("Model ve tokenizer başarıyla yüklendi.")

    def classify_reviews(self, review_list: list, threshold: float = 0.5) -> list:
        """
        Verilen yorumları sınıflandırır ve sınıflandırma sonuçlarını döndürür.

        Args:
            review_list (list): Sınıflandırılacak yorumların listesi.
            threshold (float): Sınıflandırma için eşik değeri. Varsayılan olarak 0.5.

        Returns:
            list: Her yorumun sınıflandırma sonuçlarını içeren liste.
        """

        encoded_inputs = self.tokenizer(
            review_list,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**encoded_inputs)
            predictions = torch.sigmoid(outputs.logits).numpy()

        classification_results = []
        for i, prediction in enumerate(predictions):
            classified_categories = [
                category for j, category in enumerate(self.categories)
                if prediction[j] >= threshold
            ]
            classification_results.append({
                "review": review_list[i],
                "categories": classified_categories
            })
        return classification_results

