import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np


class ModelValidator:
    """
    ModelValidator, bir sınıflandırma modelinin performansını doğrulamak için kullanılan bir sınıftır.

    Attributes:
        model_checkpoint_path (str): Eğitilmiş modelin yolu.
        val_data_path (str): Doğrulama veri setinin yolu.
        model (AutoModelForSequenceClassification): Yüklenmiş sınıflandırma modeli.
        tokenizer (AutoTokenizer): Metinleri işlemek için kullanılan tokenizer.
        val_data (pd.DataFrame): Doğrulama veri seti.

    Methods:
        load_data(): Doğrulama verisini yükler.
        tokenize_data(): Veriyi tokenleştirir.
        predict(): Model ile tahmin yapar.
        compute_metrics(): Performans metriklerini hesaplar.
        validate(): Modeli doğrular ve sonuçları döndürür.
    """

    def __init__(self, model_checkpoint_path: str, val_data_path: str) -> None:
        """
        ModelValidator sınıfını başlatır ve gerekli bileşenleri yükler.

        Args:
            model_checkpoint_path (str): Eğitilmiş modelin yolu.
            val_data_path (str): Doğrulama veri setinin yolu.
        """
        self.model_checkpoint_path = model_checkpoint_path
        self.val_data_path = val_data_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_checkpoint_path)
        self.val_data = None
        self.encoded_inputs = None
        self.predictions = None

    def load_data(self) -> None:
        """
        Doğrulama verisini CSV dosyasından yükler.
        """
        self.val_data = pd.read_csv(self.val_data_path)
        print("Doğrulama verisi başarıyla yüklendi.")

    def tokenize_data(self) -> None:
        """
        Doğrulama verisini tokenleştirir.
        """
        if self.val_data is None:
            raise ValueError("Doğrulama verisi yüklenmedi. Lütfen load_data() fonksiyonunu önce çağırın.")

        texts = self.val_data["text"].tolist()
        self.encoded_inputs = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        print("Doğrulama verisi başarıyla tokenleştirildi.")

    def predict(self) -> None:
        """
        Model ile doğrulama verisi üzerinde tahmin yapar.
        """
        if self.encoded_inputs is None:
            raise ValueError("Veri tokenleştirilmedi. Lütfen tokenize_data() fonksiyonunu önce çağırın.")

        with torch.no_grad():
            outputs = self.model(**self.encoded_inputs)
            logits = outputs.logits
            self.predictions = torch.sigmoid(logits).numpy()
        print("Model ile tahminler başarıyla yapıldı.")

    def compute_metrics(self) -> dict:
        """
        Performans metriklerini hesaplar.

        Returns:
            dict: Performans metriklerini içeren sözlük.
        """
        if self.predictions is None:
            raise ValueError("Tahminler yapılmadı. Lütfen predict() fonksiyonunu önce çağırın.")

        true_labels = self.val_data[["URUN_KALITESI", "PAKETLEME/TESLIMAT", "FIYAT/PERFORMANS", "URUN_TASARIMI"]].values
        preds = (self.predictions > 0.5).astype(int)

        # Genel metrikler
        accuracy = accuracy_score(true_labels, preds)
        precision = precision_score(true_labels, preds, average='macro')
        recall = recall_score(true_labels, preds, average='macro')
        f1 = f1_score(true_labels, preds, average='macro')

        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

        # Kategori bazında metrikler
        category_metrics = {}
        category_names = ["URUN_KALITESI", "PAKETLEME/TESLIMAT", "FIYAT/PERFORMANS", "URUN_TASARIMI"]
        for idx, category in enumerate(category_names):
            category_accuracy = accuracy_score(true_labels[:, idx], preds[:, idx])
            category_precision = precision_score(true_labels[:, idx], preds[:, idx], zero_division=1)
            category_recall = recall_score(true_labels[:, idx], preds[:, idx], zero_division=1)
            category_f1 = f1_score(true_labels[:, idx], preds[:, idx], zero_division=1)
            category_metrics[category] = {
                'accuracy': category_accuracy,
                'precision': category_precision,
                'recall': category_recall,
                'f1': category_f1
            }

        metrics['category_metrics'] = category_metrics
        return metrics

    def validate(self) -> None:
        """
        Modeli doğrular ve performans metriklerini ekrana yazdırır.
        """
        self.load_data()
        self.tokenize_data()
        self.predict()
        metrics = self.compute_metrics()
        print("Performans Metrikleri:")
        for key, value in metrics.items():
            if key == 'category_metrics':
                print("Kategori Bazlı Metrikler:")
                for category, cat_metrics in value.items():
                    print(f"  {category}:")
                    for metric_name, metric_value in cat_metrics.items():
                        print(f"    {metric_name}: {metric_value:.4f}")
            else:
                print(f"{key}: {value:.4f}")


# Kullanım örneği
if __name__ == "__main__":
    model_checkpoint_path = "src/models/finetuned_class_model"
    val_data_path = "dataset/validation_df(random_state_42).csv"
    validator = ModelValidator(model_checkpoint_path=model_checkpoint_path, val_data_path=val_data_path)
    validator.validate()