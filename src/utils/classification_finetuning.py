import os
import pandas as pd
import numpy as np
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer


class ClassificationFineTuner:
    """
    ClassificationFineTuner, bir veri seti üzerinde önceden eğitilmiş bir dil modelini çoklu etiket sınıflandırma için ince ayar yapmak için kullanılan bir sınıftır.

    Attributes:
        model_name (str): Kullanılacak önceden eğitilmiş modelin ismi.
        dataset_path (str): Yorumların bulunduğu CSV veri setinin yolu.
        model (AutoModelForSequenceClassification): Yüklenmiş dil modeli.
        tokenizer (AutoTokenizer): Metinleri işlemek için kullanılan tokenizer.

    Methods:
        load_and_prepare_data(): Veriyi yükler, hazırlar ve eğitim ile doğrulama setlerine böler.
        tokenize_function(example): Veriyi tokenize eder.
        train(): Modeli eğitir.
    """

    def __init__(self, model_name: str, dataset_path: str) -> None:
        """
        ClassificationFineTuner sınıfını başlatır ve gerekli bileşenleri yükler.

        Args:
            model_name (str): Kullanılacak önceden eğitilmiş modelin ismi.
            dataset_path (str): CSV formatındaki veri setinin yolu.
        """
        self.model_name = model_name
        self.dataset_path = dataset_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=4)
        self.model.config.problem_type = "multi_label_classification"
        self.train_dataset = None
        self.val_dataset = None

    def load_and_prepare_data(self) -> None:
        """
        Veriyi yükler, temizler ve eğitim ve doğrulama setlerine böler.
        """
        dataset = pd.read_csv(self.dataset_path)
        dataset = dataset.dropna(subset=['YORUM'])
        dataset.loc[:, 'YORUM'] = dataset['YORUM'].astype(str)

        # Yorumları ve etiketleri ayırma
        texts = dataset['YORUM'].tolist()
        labels = dataset[['URUN_KALITESI', 'PAKETLEME/TESLIMAT', 'FIYAT/PERFORMANS', 'URUN_TASARIMI']].values

        # Eğitim ve doğrulama seti ayırma
        X_train, X_val, y_train, y_val = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Eğitim ve doğrulama setlerini Hugging Face Dataset formatına dönüştürme
        self.train_dataset = Dataset.from_dict({'text': X_train, 'labels': y_train.tolist()})
        self.val_dataset = Dataset.from_dict({'text': X_val, 'labels': y_val.tolist()})

        # Veriseti kontroller
        print("Eğitim ve doğrulama verileri hazırlandı.")
        print(f"Eğitim seti örnek veri: {self.train_dataset[0]}")
        print(f"Doğrulama seti örnek veri: {self.val_dataset[0]}")

        # Tokenize edilmiş veri seti oluşturma
        self.train_dataset = self.train_dataset.map(self.tokenize_function, batched=True)
        self.val_dataset = self.val_dataset.map(self.tokenize_function, batched=True)

        # Text sütununu kaldırma (artık gerekli değil)
        self.train_dataset = self.train_dataset.remove_columns(["text"])
        self.val_dataset = self.val_dataset.remove_columns(["text"])

        # Tensor formatına çevirme (PyTorch için gerekli)
        self.train_dataset.set_format("torch")
        self.val_dataset.set_format("torch")

    def tokenize_function(self, example: dict) -> dict:
        """
        Veriyi tokenize eden fonksiyon.

        Args:
            example (dict): Tokenize edilecek örnek veri.

        Returns:
            dict: Tokenize edilmiş veri.
        """
        return self.tokenizer(
            example['text'],
            truncation=True,
            padding='max_length',
            max_length=128
        )

    def train(self) -> None:
        """
        Modeli eğitir.
        """
        training_args = TrainingArguments(
            output_dir="./results",
            evaluation_strategy="steps",
            eval_steps=100,
            save_strategy="steps",
            save_steps=500,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=5,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="none",
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            tokenizer=self.tokenizer,
        )

        print("Model eğitimi başlatılıyor...")
        trainer.train()
        print("Model eğitimi tamamlandı.")


if __name__ == "__main__":
    model_name = "dbmdz/bert-base-turkish-uncased"
    dataset_path = "dataset/comment_categorized_10k.csv"
    fine_tuner = ClassificationFineTuner(model_name=model_name, dataset_path=dataset_path)
    fine_tuner.load_and_prepare_data()
    fine_tuner.train()
