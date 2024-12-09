
# Amazon Review Lab

## Genel Bakış

Amazon Review Lab, Amazon ürün yorumlarını analiz etmek için geliştirilmiş güçlü bir uygulamadır. Kullanıcılar, bir Amazon ürün linki girerek yorumlardan kategorize edilmiş, özetlenmiş ve duygu analiziyle desteklenmiş bilgiler elde edebilir. Bu uygulama, yorum analizi sürecini kolaylaştırarak hızlı ve etkili izlenimler sunar.

## Özellikler

- **Yorum Kategorilendirme**: Yorumları Ürün Kalitesi, Paketleme/Teslimat, Fiyat/Performans ve Ürün Tasarımı gibi ön tanımlı kategorilere otomatik olarak sınıflandırır.
- **Özetleme**: Her kategori için temel konuları vurgulayan kısa özetler sunar.
- **Duygu Analizi**: Her kategoriye duygu puanları atar ve genel bir duygu puanı hesaplar.
- **Kullanıcı Dostu Arayüz**: Web tabanlı bir arayüz ve FastAPI uç noktalarıyla kolay bir deneyim sunar.

## Uygulama Akışı

1. **Kullanıcı Girişi**: Uygulamaya Amazon ürün linki girilir.
2. **Veri Çekimi**: Amazon API'si kullanılarak yorumlar elde edilir.
3. **Yorum Sınıflandırma**: Yorumlar, önceden eğitilmiş bir model kullanılarak kategorilere ayrılır.
4. **Özetleme**: Gelişmiş doğal dil işleme teknikleriyle kategorize edilmiş yorumlar özetlenir.
5. **Sonuç Görüntüleme**: Sonuçlar, her kategoriyi detaylıca inceleme imkânıyla bir panoda sunulur.

![Schema](https://github.com/ebubekirsoftware/AmazonReviewLab/raw/main/pics/schema.png)


## Uygulama Mimarisi

Uygulama aşağıdaki yapıyı kullanır:

- **Önyüz**: Etkileşimli bir kullanıcı deneyimi için Streamlit ile geliştirilmiştir.
- **Arka Uç**: API isteklerini ve model çıkarımlarını yönetmek için FastAPI kullanılmıştır.
- **Veri Boru Hattı**: Veri toplama, işleme ve görüntüleme için birden fazla bileşen entegre edilmiştir.

### Dosya Yapısı

```
.
|-- app.py
|-- requirements.txt
|-- amazon-ui/
|   |-- amazon_streamlit.py
|-- config/
|   |-- .env
|-- dataset/
|   |-- comment_categorized_10k.csv
|   |-- reviews_200k.csv
|   |-- validation_df(random_state_42).csv
|-- src/
|   |-- amazon_api.py
|   |-- classification.py
|   |-- main.py
|   |-- summarization.py
|   |-- logs/
|   |   |-- classifier_trainer_state.json
|   |-- models/
|   |   |-- finetuned_class_model
|   |-- utils/
|   |   |-- classification_finetuning.py
|   |   |-- data_prep.py
|   |   |-- gpt_data_labeling.py
|   |-- __pycache__/
|-- tests/
|   |-- classification_model_validation.py
|   |-- metrics.txt
|   |-- test_api.py
```

### Temel Bileşenler

#### 1. **Önyüz (Streamlit)**

- Kullanıcı etkileşimlerini yönetir.
- Amazon ürün linklerini girmek için form sunar.
- Kategori puanları, özetler ve detaylı yorumlar dahil olmak üzere analiz sonuçlarını görüntüler.
- Dosya: `amazon-ui/amazon_streamlit.py`.

#### 2. **Arka Uç (FastAPI)**

- Sınıflandırma ve özetleme için API uç noktaları sağlar.
- Kullanıcı girdilerini işler ve veri çekimi ile model çıkarımlarını yönetir.
- Dosya: `app.py`.

#### 3. **Amazon API**

- RapidAPI entegrasyonu kullanarak yorumları çeker.
- Sayfalama işlemleri ile 200k'ye kadar yorumu alır.
- Dosya: `src/amazon_api.py`.

#### 4. **Sınıflandırma**

- Yorumları sınıflandırmak için ince ayarlanmış bir transformer tabanlı model kullanır.
- Kategoriler: Ürün Kalitesi, Paketleme/Teslimat, Fiyat/Performans, Ürün Tasarımı.
- Dosya: `src/classification.py`.

#### 5. **Özetleme**

- NLP modeli (Llama3 gibi) kullanarak kategori bazında özetler ve genel sonuçlar oluşturur.
- Dosya: `src/summarization.py`.

### Docker Entegrasyonu

- **Konteynerler**: Uygulama iki Docker konteyneriyle yönetilir—biri ana API, diğeri ise özetleme modeli içindir.
- **Çekme Komutu**: İlgili Docker imajını çekmek için:
  ```
  docker pull ebubekirsoftware/amazonreviewlab
  ```

## Kurulum

### Gereksinimler

- Python 3.11 veya daha yenisi
- Docker yüklenmiş olmalı
- `.env` dosyası RapidAPI kimlik bilgileriyle yapılandırılmış olmalı

### Adımlar

1. Depoyu klonlayın.
   ```
   git clone https://github.com/your-repo/amazon-review-lab.git
   ```
2. Proje dizinine gidin.
   ```
   cd amazon-review-lab
   ```
3. Bağımlılıkları yükleyin.
   ```
   pip install -r requirements.txt
   ```
4. Uygulamayı başlatın.
   ```
   python app.py
   ```

## Kullanım

### Streamlit Arayüzü

1. Streamlit uygulamasını çalıştırın.
   ```
   streamlit run amazon-ui/amazon_streamlit.py
   ```
2. Bir Amazon ürün linki girin ve `Analyze` butonuna tıklayın.
3. Kategorize edilmiş sonuçları ve özetleri görüntüleyin.

### FastAPI Uç Noktaları

1. FastAPI sunucusunu başlatın.
   ```
   uvicorn app:app --reload
   ```
2. API dokümantasyonuna erişin: `http://127.0.0.1:8000/docs`.

## Örnek Çıktılar

- **Kategorilendirme**: Kategorilere ayrılmış yorumlar ve duygu puanları.
- **Özetleme**: Yorumlara dayalı kısa ve kullanılabilir içgörüler.

## Özel Not: Docker ile Çalıştırma Yapılandırmaları

Amazon Review Lab uygulamasını Streamlit üzerinden çalıştırırken aşağıdaki Docker yapılandırmalarını uygulamanız gereklidir.

### Ortak Ağ Üzerinde Çalışma Gerekliliği

Bu uygulamanın doğru şekilde çalışabilmesi için, **ollama2** konteyneri (Llama3 modelini barındırır) ile aynı Docker ağı üzerinde bulunması gerekir.

#### Ortak Ağ Oluşturma

1. Docker ağı oluşturun:
   ```bash
   docker network create amazonreviewlab-network
   ```
2. Ollama konteynerini çalıştırırken ağı belirtin:
   ```bash
   docker run -d --network amazonreviewlab-network --name ollama2 ollama/ollama
   ```
3. Amazon Review Lab konteynerini çalıştırırken aynı ağı kullanın:
   ```bash
   docker run -d -p 8000:8000 --network amazonreviewlab-network --name amazonreviewlab ebubekirsoftware/amazonreviewlab
   ```

#### Ağ Durumunu Kontrol Etme

Ağ yapılandırmalarını doğrulamak için şu komutu çalıştırabilirsiniz:

```bash
docker network inspect amazonreviewlab-network
```

## Gelecek Planları

- Ek kategorilerle sınıflandırma modelini geliştirin.
- Çok dilli desteğini iyileştirin.
- Daha derin içgörüler için gelişmiş görünteleme seçenekleri ekleyin.

## Katkı Sağlayanlar

- **Ebubekir Tosun** - Geliştirici ve Bakımcı
