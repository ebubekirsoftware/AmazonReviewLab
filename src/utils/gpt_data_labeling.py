import openai
import pandas as pd
import time
import re


class GPTDataLabeling:
    """
    GPTDataLabeling, GPT-4 kullanarak yorumları etiketlemek için kullanılan bir sınıftır.

    Attributes:
        api_key (str): OpenAI API anahtarı.
        dataset_path (str): İşlenecek veri setinin yolu.
        client (openai.OpenAI): GPT-4 API istemcisi.
        dataset (pd.DataFrame): Yüklenmiş veri seti.
        labeled_data (list): Etiketlenmiş yorumların listesi.

    Methods:
        load_data(): Veriyi yükler ve gerekli temizleme işlemlerini yapar.
        gpt_labeling(comment, index): Bir yorumu GPT-4 ile etiketler.
        label_data(): Veri setindeki tüm yorumları etiketler.
        save_data(output_path): Etiketlenmiş veriyi belirtilen yola kaydeder.
    """

    def __init__(self, api_key: str, dataset_path: str) -> None:
        """
        GPTDataLabeling sınıfını başlatır ve gerekli bileşenleri yükler.

        Args:
            api_key (str): OpenAI API anahtarı.
            dataset_path (str): İşlenecek veri setinin yolu.
        """
        self.api_key = api_key
        openai.api_key = self.api_key
        self.dataset_path = dataset_path
        self.dataset = None
        self.labeled_data = []

    def load_data(self) -> None:
        """
        Veriyi CSV dosyasından yükler ve gerekli temizleme işlemlerini yapar.
        """
        self.dataset = pd.read_csv(self.dataset_path, sep=";", encoding="utf-8")
        self.dataset.drop_duplicates(subset=["Metin"], inplace=True)
        self.dataset.reset_index(drop=True, inplace=True)
        print("Veri başarıyla yüklendi ve temizlendi.")

    def gpt_labeling(self, comment: str, index: int) -> str:
        """
        Bir yorumu GPT-4 ile etiketler.

        Args:
            comment (str): Etiketlenecek yorum.
            index (int): Yorumun indeksi.

        Returns:
            str: Etiketlenmiş yorum.
        """
        messages = [
            {
                "role": "user",
                "content": f"""
                Yorum: "{comment}"

                Bu yorumu aşağıdaki etiketlere göre değerlendir:
                1. Kalite
                2. Boyut
                3. Tasarım
                4. Paketleme
                5. Fiyat
                6. Genel

                Eğer etikete göre olumlu ise pozitif, olumsuz ise negatif etiketi ver. Eğer etiket hakkında bir bilgi olmadığını düşünüyorsan nötr etiketi ver. Her bir etiket için sadece tek kelimelik bir yanıt ver: pozitif, negatif veya nötr.
                """
            }
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4", messages=messages, max_tokens=150, temperature=0.7
            )
            labeled_comment = response.choices[0].message.content.strip()
            print(f"Yorum {index}: {comment} için etiketleme yapıldı.")
            return labeled_comment
        except Exception as e:
            print(f"Yorum {index} için etiketleme sırasında bir hata oluştu: {e}")
            return ""

    def label_data(self) -> None:
        """
        Veri setindeki tüm yorumları etiketler ve sonuçları labeled_data listesine ekler.
        """
        for index, comment in enumerate(self.dataset['Metin']):
            response = self.gpt_labeling(comment, index)
            if response:
                self.labeled_data.append(response)
            time.sleep(2)  # API oran sınırını aşmamak için gecikme

        print("Tüm veriler etiketlendi.")

    def save_data(self, output_path: str) -> None:
        """
        Etiketlenmiş veriyi belirtilen yola kaydeder.

        Args:
            output_path (str): Kaydedilecek dosya yolu.
        """
        if not self.labeled_data:
            raise ValueError("Etiketlenmiş veri bulunmuyor. Lütfen label_data() fonksiyonunu çağırın.")

        # Etiketleri sütunlara ayırma
        labeled_df = pd.DataFrame(columns=['Kalite', 'Boyut', 'Tasarım', 'Paketleme', 'Fiyat', 'Genel'])
        for index, response in enumerate(self.labeled_data):
            labels = response.split('\n')
            for label in labels:
                key, value = label.split(': ')
                key = key.split('. ')[1]  # '1. Kalite' -> 'Kalite'
                labeled_df.at[index, key] = value

        combined_df = pd.concat([self.dataset, labeled_df], axis=1)
        combined_df.to_csv(output_path, index=False)
        print(f"Etiketlenmiş veri başarıyla {output_path} konumuna kaydedildi.")


# Kullanım örneği
if __name__ == "__main__":
    api_key = ""
    dataset_path = "dataset/veri_seti_200k.csv"
    output_path = "dataset/trendyol_comments_10k_labeled.csv"
    gpt_labeling = GPTDataLabeling(api_key=api_key, dataset_path=dataset_path)
    gpt_labeling.load_data()
    gpt_labeling.label_data()
    gpt_labeling.save_data(output_path)
