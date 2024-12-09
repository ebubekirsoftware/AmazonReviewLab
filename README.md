
# Amazon Review Lab

![Schema](https://github.com/ebubekirsoftware/AmazonReviewLab/blob/main/pics/amazon.avif)

## Genel Bakış

Amazon Review Lab, Amazon ürün yorumlarını analiz etmek için geliştirilmiş güçlü bir uygulamadır. Kullanıcılar, bir Amazon ürün linki girerek yorumlardan kategorize edilmiş, özetlenmiş ve duygu analiziyle desteklenmiş bilgiler elde edebilir. Bu uygulama, yorum analizi sürecini kolaylaştırarak hızlı ve etkili izlenimler sunar.

## Özellikler

- **Yorum Kategorilendirme**: Yorumları Ürün Kalitesi, Paketleme/Teslimat, Fiyat/Performans ve Ürün Tasarımı gibi ön tanımlı kategorilere otomatik olarak sınıflandırır.
- **Özetleme**: Her kategori için temel konuları vurgulayan kısa özetler sunar.
- **Duygu Analizi**: Her kategoriye duygu puanları atar ve genel bir duygu puanı hesaplar.
- **Kullanıcı Dostu Arayüz**: Web tabanlı bir arayüz ve FastAPI uç noktalarıyla kolay bir deneyim sunar.

## Uygulama İş Akışı

1. **Kullanıcı Girişi**: Uygulamaya Amazon ürün linki girilir.
2. **Veri Çekimi**: Amazon API'si kullanılarak yorumlar elde edilir.
3. **Yorum Sınıflandırma**: Yorumlar, önceden eğitilmiş bir model kullanılarak kategorilere ayrılır.
4. **Özetleme**: Kategorize edilmiş yorumlar Ollama ile kurulan yerel llama3 modeli ile özetlenir.
5. **Sonuç Görüntüleme**: Sonuçlar, her kategoriyi detaylıca inceleme imkânıyla bir panoda sunulur.

![Schema](https://github.com/ebubekirsoftware/AmazonReviewLab/raw/main/pics/schema.png)


## Uygulama Mimarisi

Uygulama aşağıdaki yapıyı kullanır:

- **Frontend**: Etkileşimli bir kullanıcı deneyimi için Streamlit ile geliştirilmiştir.
- **Backend**: API isteklerini ve model çıkarımlarını yönetmek için FastAPI kullanılmıştır. Docker entegrasyonuyla güçlü bir altyapı kurulmuştur. Tüm backend süreçlerinde dosya formatı JSON kullanılmıştır.
- **Data Pipeline**: Veri toplama, işleme ve görüntüleme için birden fazla bileşen entegre edilmiştir.

### Dosya Yapısı
Bu proje, modüler tasarlanmış bir dosya yapısına sahiptir. Her bir dizin ve dosya, belirli bir işlevi yerine getirmek üzere organize edilmiştir. Bu yapının amacı, kodun okunabilirliğini artırmak, sürdürmeyi kolaylaştırmak ve geliştirme sürecini daha verimli hale getirmektir.


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

#### 1. **Frontend (Streamlit)**

- Kullanıcı etkileşimlerini yönetir.
- Amazon ürün linklerini girmek için bir alan sunar.
- Kategori puanları, özetler ve detaylı yorumlar dahil olmak üzere analiz sonuçlarını görüntüler.
- Dosya: `amazon-ui/amazon_streamlit.py`.

#### 2. **Backend (FastAPI)**

- Sınıflandırma ve özetleme için API endpointleri sağlar.
- Kullanıcı girdilerini işler ve veri çekimi ile model çıkarımlarını yönetir.
- Dosya: `app.py`.

#### 3. **Amazon API**

- RapidAPI 'Amazon Real Data API' entegrasyonu kullanarak yorumları çeker.
- Dosya: `src/amazon_api.py`.

#### 4. **Sınıflandırma (Classification)**

- Yorumları sınıflandırmak için etiketlenmiş review dataset ile fine-tuning yapılmış bir transformer tabanlı model kullanır.
- Kategoriler: Ürün Kalitesi, Paketleme/Teslimat, Fiyat/Performans, Ürün Tasarımı.
- Dosya: `src/classification.py`.

#### 5. **Özetleme (Summerization)**

- Bir llm modeli olan Llama3 kullanarak kategori bazında özetler ve genel sonuçlar oluşturur. Model local bir şekilde Ollama üzerinden kullanılır.
- Dosya: `src/summarization.py`.

### Llama3 ile Özetleme için Ollama Kullanımı

Ollama, büyük dil modellerinin (LLM) yerel olarak çalıştırılması için tasarlanmış bir framework’tür. Llama3 ile özetleme yaparken Ollama’yı tercih etmemizin nedenleri şunlardır:

1. **Yerel Çalıştırma**: Llama3’ü yerelde çalıştırarak veri gizliliği ve güvenliği sağlar.
2. **Performans Optimizasyonu**: Büyük modellerde bile yüksek performans sunar. CPU ve GPU optimizasyonuyla hızlı yanıt üretir.
3. **Kolay Kullanım**: Geliştirici dostu araçlarla entegrasyonu kolaylaştırır.

![Schema](https://github.com/ebubekirsoftware/AmazonReviewLab/blob/main/pics/llama.jpg)



# Kurulum

### Gereksinimler

- Python 3.11 veya daha yenisi
- Docker ve Ollama yüklenmiş olmalı
- `.env` dosyası RapidAPI kimlik bilgileriyle yapılandırılmış olmalı


## Docker Entegrasyonu ve Manuel Çalıştırma

### Docker ile Çalıştırma
Amazon Review Lab uygulamasını Docker üzerinden çalıştırmak için iki konteyner yapılandırılması gerekmektedir. Bu konteynerler aynı Docker ağı üzerinde olmalıdır. Aşağıda adım adım kurulum ve yapılandırma talimatları verilmiştir:

##### Gerekli Konteynerler
1. **Amazon Review Lab API Konteyneri**:
   - Docker Hub'dan ilgili imajı çekmek için:
     ```bash
     docker pull ebubekirsoftware/amazonreviewlab
     ```
2. **Ollama Konteyneri**:
   - Ollama konteynerini çekmek için aşağıdaki komutu kullanın:
     ```bash
     docker pull ollama/ollama
     ```
   - Ollama konteyneri başlatıldıktan sonra Llama3 modelini indirmek için şu komutu çalıştırın:
     ```bash
     ollama pull llama3
     ```

##### Ortak Ağ Oluşturma ve Konteynerlerin Çalıştırılması
1. Docker ağı oluşturun:
   ```bash
   docker network create amazonreviewlab-network
   ```
2. Ollama konteynerini ağı belirterek başlatın:
   ```bash
   docker run -d --network amazonreviewlab-network --name ollama ollama/ollama
   ```
   - Ollama konteyneri başlatıldıktan sonra Llama3 modelini indirin ve yapılandırın.
3. Amazon Review Lab API konteynerini aynı ağ üzerinde çalıştırın:
   ```bash
   docker run -d -p 4000:4000 --network amazonreviewlab-network --name amazonreviewlab ebubekirsoftware/amazonreviewlab
   ```

##### Uygulamanın Başlatılması
- Docker konteynerleri başlatıldıktan sonra, `amazon-ui` klasöründe bulunan `amazon_streamlit.py` dosyasını çalıştırarak uygulamayı başlatabilirsiniz:
  ```bash
  streamlit run amazon-ui/amazon_streamlit.py
  ```
- Port numaralarının görseldeki gibi yapılandırıldığından emin olun:
  - Amazon API Konteyneri: `4000:4000`
  - Ollama Konteyneri: `11434:11434`

### Manuel Kurulum (Docker Kullanılmadan)
Docker kullanmadan Amazon Review Lab uygulamasını çalıştırmak için aşağıdaki adımları takip edin:

##### Gerekli Adımlar
1. GitHub reposunu klonlayın:
   ```bash
   git clone https://github.com/your-repo/amazon-review-lab.git
   ```
2. Proje dizinine gidin:
   ```bash
   cd amazon-review-lab
   ```
3. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. Uygulamayı FastAPI üzerinden çalıştırın:
   ```bash
   uvicorn app:app --port 4000
   ```

##### Uygulamanın Başlatılması
- FastAPI çalıştıktan sonra, `amazon-ui` klasöründeki `amazon_streamlit.py` dosyasını çalıştırarak uygulamaya bağlanabilirsiniz:
  ```bash
  streamlit run amazon-ui/amazon_streamlit.py
  ```

Her iki yöntemle de uygulama aynı şekilde çalışacaktır. Docker ile çalıştırma, özellikle bağımlılıkların izolasyonu ve dağıtım kolaylığı açısından önerilir.


## Kullanım

### Streamlit Arayüzü

1. Streamlit uygulamasını çalıştırın.
   ```
   streamlit run amazon-ui/amazon_streamlit.py
   ```
2. Bir Amazon ürün linki girin ve `Analyze` butonuna tıklayın.
3. Kategorize edilmiş sonuçları ve özetleri görüntüleyin.


## Örnek Çıktılar

- **Kategorilendirme**: Kategorilere ayrılmış yorumlar ve duygu puanları.
- **Özetleme**: Yorumlara dayalı kısa ve kullanılabilir içgörüler.
![Schema](https://github.com/ebubekirsoftware/AmazonReviewLab/blob/main/pics/points.png))

Ağ yapılandırmalarını doğrulamak için şu komutu çalıştırabilirsiniz:

```bash
docker network inspect amazonreviewlab-network
```


## Geliştirici

- **Ebubekir Tosun** - Geliştirici ve Bakımcı


