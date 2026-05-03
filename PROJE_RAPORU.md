# 36Otel Rezervasyon Sistemi - Proje Teknik Raporu ve Sunum Rehberi

**Ders:** Web Programlama  
**Tarih:** Mayıs 2026  
**Proje Ekibi:** Hüseyin, Furkan, Samet, Deniz  

---

## 1. Proje Özeti ve Vizyon
**36Otel**, geleneksel otel rezervasyon sistemlerini modern bir yaklaşımla ele alan, NoSQL veritabanı mimarisi üzerine kurulu ve **Yapay Zeka (NLP) destekli Chatbot** ile güçlendirilmiş tam kapsamlı bir web uygulamasıdır. Proje, sadece otel listelemekle kalmayıp, kullanıcının niyetini (intent) algılayarak ona özel teklifler sunan ve sohbet üzerinden doğrudan rezervasyon yapabilen yenilikçi bir mimariye sahiptir.

## 2. Kullanılan Teknoloji Yığını ve Nedenleri
*   **Backend (Sunucu):** Python & Flask. *Neden?* Mikro framework yapısı sayesinde sadece ihtiyacımız olan modülleri kullanarak sistemi hafif ve hızlı tuttuk.
*   **Veritabanı:** MongoDB & PyMongo. *Neden?* Otel ve oda özellikleri (havuz, wifi, manzara vb.) değişkendir. NoSQL'in esnek JSON (BSON) yapısı sayesinde ilişkisel veritabanlarının hantal tablolarından kurtulduk.
*   **Frontend (Önyüz):** HTML5, Vanilla JS, Bootstrap 5, Jinja2. *Neden?* Dark-Mode Glassmorphism tasarımı ile modern bir UI/UX sağlandı. Vanilla JS ile sayfa yenilenmeden dinamik asenkron işlemler yapıldı.
*   **Güvenlik:** Flask-Login & Werkzeug. Şifreler düz metin yerine Bcrypt hash algoritmalarıyla şifrelenerek veri güvenliği sağlandı.

## 3. Projenin Öne Çıkan İnovatif Özelliği: State-Machine Chatbot
Piyasadaki standart öğrenci projelerinden farklı olarak bu projede **Bağlam Farkındalığına Sahip (Context-Aware) Çift Dilli NLP Chatbot** kodlanmıştır.
*   **Fuzzy Matching (Bulanık Eşleştirme):** Kullanıcı "istnbul" yazsa bile sistem harf dizilimi yakınlığından bunun "İstanbul" olduğunu anlar.
*   **Intent Detection (Niyet Algılama):** Kullanıcı "ailemle gideceğim" dediğinde, "family" niyetini algılar ve geniş odalı aile otellerini filtreler.
*   **Oturum Hafızası:** Kullanıcının bir önceki mesajını hafızada tutarak sohbeti devam ettirir ve sohbet ekranı üzerinden tek tıkla veritabanına **rezervasyon (INSERT)** kaydı atabilir.

---

## 4. Ekip Sorumlulukları ve Hocanın Sorabileceği Mülakat Soruları

Sunum sırasında hocanızın (jürinin) projeyi kimin ne kadar anladığını ölçmek için sorabileceği muhtemel sorular ve cevap anahtarları aşağıdadır:

### 👤 SAMET (Frontend Geliştirici & UX & Proje Yönetimi)
**Sorumluluk:** Jinja2 şablonları, Bootstrap 5 UI, oda ve otel listeleme ekranları, genel entegrasyon.
*   **Hocanın Sorusu:** *"Jinja2 nedir? Neden direkt HTML yazmadın da Jinja2 kullandın?"*
    *   **Cevap:** Standart HTML statiktir, veritabanından gelen otel listesini HTML'de dinamik olarak dönemeyiz. Jinja2, Python'dan gelen listeleri `{% for hotel in hotels %}` döngüleriyle sayfa yenilenirken HTML koduna çevirmemizi sağlayan bir şablonlama (template) motorudur.
*   **Hocanın Sorusu:** *"Bootstrap grid sistemi nasıl çalışıyor? Sitenin mobilde düzgün görünmesini nasıl sağladın?"*
    *   **Cevap:** Bootstrap'in 12 sütunlu ızgara yapısını kullandım. Örneğin `col-md-6 col-12` sınıflarını kullanarak, div'lerin bilgisayarda yan yana (6 birim), mobilde ise alt alta (12 birim) düşmesini sağlayarak responsive bir yapı kurdum.

### 👤 FURKAN (Backend Geliştirici & Güvenlik)
**Sorumluluk:** Flask-Login, Werkzeug, Şifre Hashleme, Oturum (Session) Yönetimi, Admin/Müşteri rol ayrımı.
*   **Hocanın Sorusu:** *"Kullanıcı şifrelerini veritabanında nasıl tutuyorsun? Düz metin olarak kaydetmek neden tehlikeli?"*
    *   **Cevap:** Şifreleri kesinlikle düz metin kaydetmiyoruz. Werkzeug kütüphanesinin `generate_password_hash` fonksiyonunu kullanarak tek yönlü şifreledik. Veritabanı çalınsa bile hackerlar şifrelerin orijinal halini göremez. Giriş yaparken `check_password_hash` ile kullanıcının girdiği şifreyle hash'i karşılaştırıyoruz.
*   **Hocanın Sorusu:** *"Session (Oturum) nedir ve login required dekoratörü nasıl çalışıyor?"*
    *   **Cevap:** Session, kullanıcı giriş yaptığında tarayıcıya bırakılan şifreli bir çerezdir. `@login_required` dekoratörü, kullanıcının session'ını kontrol eder; eğer geçerli bir oturum yoksa fonksiyonun çalışmasını durdurur ve anında login sayfasına yönlendirir. Böylece admin paneline linki bilerek girilmesini engelleriz.

### 👤 HÜSEYİN (Frontend Geliştirici & JavaScript UX)
**Sorumluluk:** Vanilla JS ile tarih doğrulamaları, dinamik ilçe seçimi, AJAX etkileşimleri.
*   **Hocanın Sorusu:** *"Kullanıcı şehir seçtiğinde sayfa yenilenmeden sadece o şehrin ilçeleri nasıl geliyor?"*
    *   **Cevap:** Frontend tarafında JavaScript'in `fetch` API'sini (veya DOM event listener) kullandım. 'Şehir' select box'ı değiştiğinde (`onchange` eventi), JS ile yakalayıp JSON objesindeki o şehre ait ilçeleri döngüyle okuyor ve 'İlçe' select box'ının içine dinamik olarak HTML `<option>` etiketleri ekliyoruz. Bu sayede sunucuya gereksiz yük bindirmeden UX'i akıcı tutuyoruz.
*   **Hocanın Sorusu:** *"Tarih doğrulamasını JS ile client-side yapmak yerine neden Python ile server-side yapmadık?"*
    *   **Cevap:** İkisini de yapmak en güvenlisidir. JavaScript ile frontend'de (geçmiş tarihi engellemek, çıkış tarihinin girişten sonra olmasını sağlamak) anlık doğrulama yaparak kullanıcı deneyimini artırıyoruz. Eğer form yanlış gönderilirse kullanıcıyı sayfa yenilenmeden uyarabiliyoruz.

### 👤 DENİZ (Backend Mimarı & Veritabanı & NLP Chatbot)
**Sorumluluk:** Flask mimarisi, MongoDB şemaları, PyMongo sorguları, Rezervasyon iş mantığı, Chatbot state-machine algoritması.
*   **Hocanın Sorusu:** *"Neden MySQL gibi ilişkisel bir SQL veritabanı yerine MongoDB (NoSQL) tercih ettiniz?"*
    *   **Cevap:** Otel rezervasyon sistemlerinde veri şemaları değişkendir. Bir otelin özellikleri (havuz, wifi) ile diğerininki farklı olabilir. MongoDB verileri JSON dokümanları halinde tuttuğu için Python dict yapısıyla mükemmel uyum sağlar. JOIN işlemleri yerine "Embedding" (odaları otel belgesine gömme) veya "Referencing" yaparak hızı artırdık.
*   **Hocanın Sorusu:** *"Chatbot'un hafızası var diyorsunuz, bu bot önceki yazdıklarımı nasıl hatırlıyor?"*
    *   **Cevap:** Chatbot, bir "State-Machine" (Durum Makinesi) mimarisine sahip. Flask'ın `session` objesini kullanarak sohbet bağlamını (`chat_context`) sakladım. Kullanıcı ilk mesajda sadece niyetini (Örn: Havuzlu) söylüyorsa, bunu session'a kaydediyoruz. İkinci mesajda sadece "Antalya" dediğinde, sistem eski session verisini okuyarak aramanın "Antalya + Havuzlu" olduğunu anlıyor ve MongoDB sorgusunu buna göre atıyor.

---

## 5. Projeyi Canlıya Alma (Deployment) Rehberi

Elinizdeki projeyi yerel makineden çıkarıp gerçek bir domain (Hostinger) ile dünyaya açmak için sunum öncesi şu adımları izleyebilirsiniz:

### A. Render.com Kullanarak (En İyi Ücretsiz Yöntem)
Hostinger'da sadece alan adınız (domain) var ve VPS'iniz yoksa, Python uygulamanızı barındırmak için **Render.com** (ücretsiz katmanı) mükemmeldir.

1. **GitHub'a Yükleme:** Proje klasörünü Github hesabınıza (gizli veya açık) Pushlayın.
2. **Render.com Kurulumu:**
   * Render.com'a GitHub ile giriş yapın.
   * `New Web Service` butonuna tıklayın ve GitHub deponuzu bağlayın.
   * Ayarlara şunları girin:
     * **Environment:** Python 3
     * **Build Command:** `pip install -r requirements.txt` (Bu komut için `gunicorn` kütüphanesi eklendi)
     * **Start Command:** `gunicorn app:app`
     * **Instance Type:** Free ($0/month)
3. **Environment Variables (.env):** Ayarlar sekmesinde MongoDB bağlantı URI'nizi (`MONGO_URI`) ve `FLASK_SECRET_KEY` değerlerinizi girin.
4. **Deploy:** Oluştur tuşuna basın. Birkaç dakika içinde siteniz `https://xxx.onrender.com` olarak canlıya çıkacaktır.

### B. Hostinger Domainini Siteye Bağlama
Siteniz Render üzerinde çalışmaya başladıktan sonra Hostinger'daki alan adınızı buraya yönlendirmeniz gerekir:
1. Render panosunda "Settings" sekmesine gidin.
2. **Custom Domains** bölümünü bulun ve Hostinger'dan aldığınız alanı adını (Örn: `benimotelim.com`) ekleyin.
3. Render size 2 adet DNS kaydı verecektir: Biri **A Kaydı (IP adresi)**, diğeri **CNAME**.
4. **Hostinger** kontrol panelinize gidin, DNS Yönlendirme (DNS Zone Editor) kısmını açın.
5. Sadece IP adresini A kaydı olarak, CNAME bilgisini de www için kaydedin. (Render'ın size verdiği IP adresini yazmanız yeterlidir).
6. İşlem tamam! 1-2 saat içinde DNS oturacak ve projenize direkt kendi alan adınızdan erişilecektir.

---
**Sonuç:** Bu proje standart bir okul ödevinin çok ötesine geçerek, gerçek hayat senaryolarını çözen, kullanıcı dostu ve yapay zeka destekli bir platform olmuştur. Başarılar dileriz!
