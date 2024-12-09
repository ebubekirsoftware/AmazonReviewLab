import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
import nltk


class DataPreparation:
    """
    DataPreparation, bir veri setini hazırlamak ve ön işleme tabi tutmak için kullanılan bir sınıftır.

    Attributes:
        input_path (str): Girdi veri setinin yolu.
        output_path (str): İşlenmiş veri setinin kaydedileceği yol.
        dataset (pd.DataFrame): Yüklenmiş ve işlenmekte olan veri seti.

    Methods:
        load_data(): Veriyi yükler.
        preprocess(): Veriyi ön işleme tabi tutar ve kategorileri düzenler.
        save_data(): İşlenmiş veriyi belirtilen yola kaydeder.
    """

    def __init__(self, input_path: str, output_path: str) -> None:
        """
        DataPreparation sınıfını başlatır ve gerekli bileşenleri yükler.

        Args:
            input_path (str): Girdi veri setinin yolu.
            output_path (str): İşlenmiş veri setinin kaydedileceği yol.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.dataset = None

    def load_data(self) -> None:
        """
        Veriyi CSV dosyasından yükler.
        """
        self.dataset = pd.read_csv(self.input_path)
        print("Veri başarıyla yüklendi.")

    def preprocess(self) -> None:
        """
        Veriyi ön işleme tabi tutar ve gerekli düzenlemeleri yapar.
        """
        if self.dataset is None:
            raise ValueError("Veri seti yüklenmedi. Lütfen load_data() fonksiyonunu önce çağırın.")

        # Genel kategoriyi çıkarma
        if 'GENEL' in self.dataset.columns:
            self.dataset = self.dataset.drop(columns=['GENEL'])

        # Yorumla ilgili kategorileri belirleme-encoding
        columns_to_normalize = ['KALITE', 'BOYUT', 'TASARIM', 'PAKETLEME', 'FIYAT']
        for col in columns_to_normalize:
            if col in self.dataset.columns:
                self.dataset[col] = self.dataset[col].apply(lambda x: 1 if x in [1, -1] else 0)

        # Boyut ve Tasarım kategorilerini birleştirme
        if 'BOYUT' in self.dataset.columns and 'TASARIM' in self.dataset.columns:
            self.dataset['URUN_TASARIMI'] = self.dataset.apply(
                lambda row: 1 if row['BOYUT'] == 1 or row['TASARIM'] == 1 else 0, axis=1
            )
            self.dataset = self.dataset.drop(columns=['BOYUT', 'TASARIM'])

        # Kategori isimlendirmelerini düzenleme
        self.dataset.columns = ['YORUM', 'URUN_KALITESI', 'PAKETLEME/TESLIMAT', 'FIYAT/PERFORMANS', 'URUN_TASARIMI']

        # Belirli sütunları float tipine dönüştürme
        columns_to_convert = ['URUN_KALITESI', 'PAKETLEME/TESLIMAT', 'FIYAT/PERFORMANS', 'URUN_TASARIMI']
        self.dataset[columns_to_convert] = self.dataset[columns_to_convert].astype(float)

        print("Veri ön işleme tamamlandı.")

    def save_data(self) -> None:
        """
        İşlenmiş veriyi belirtilen yola kaydeder.
        """
        if self.dataset is None:
            raise ValueError("Veri seti işlenmedi. Lütfen preprocess() fonksiyonunu çağırın.")
        self.dataset.to_csv(self.output_path, index=False)
        print(f"İşlenmiş veri başarıyla {self.output_path} konumuna kaydedildi.")


if __name__ == "__main__":
    input_path = "dataset/trendyol_comments_10k_encoded.csv"
    output_path = "dataset/comment_categorized.csv"
    data_preparation = DataPreparation(input_path=input_path, output_path=output_path)
    data_preparation.load_data()
    data_preparation.preprocess()
    data_preparation.save_data()