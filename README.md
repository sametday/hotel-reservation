# 36Otels - Modern Hotel Reservation Platform

Bu proje, Flask ve MongoDB kullanılarak geliştirilmiş, uçtan uca çalışabilen, premium "Dark Mode Glassmorphism" tasarıma sahip bir otel rezervasyon sistemidir.

## 🚀 Projeyi Nasıl Başlatacaksın?

Sıfırdan projeyi çalıştırmak için terminalde şu adımları izlemelisin:

### 1. Sanal Ortamı Aktif Et
Projenin kök dizininde (VS Code terminalinde) şu komutu çalıştırarak Python sanal ortamını aktif hale getir:
```powershell
.\.venv\Scripts\activate
```
*(Aktif olduğunda terminal satırının başında `(.venv)` yazısını göreceksin.)*

### 2. Veritabanını Doldur (İsteğe Bağlı)
Eğer MongoDB veritabanın boşsa veya sıfırlamak istiyorsan, sisteme yapay zeka ile oluşturulmuş 81 il için 2000 adet gerçekçi otel ve on binlerce oda eklemek için şu dosyayı çalıştır:
```powershell
python veri_cogalt.py
```
*(Bu işlem 5-10 saniye sürebilir, tamamlandığında sana bilgi verecektir.)*

### 3. Sunucuyu Başlat
Tüm hazırlıklar tamamsa projeyi yayına almak için ana dosyayı çalıştır:
```powershell
python app.py
```

### 4. Siteye Giriş
Tarayıcını aç ve şu adrese git: **http://127.0.0.1:5000**

---

## 🔑 Yönetici (Admin) Paneli
Site üzerinden veya `/admin/dashboard` adresinden yönetici paneline erişmek için, veritabanında `is_admin: true` olan bir kullanıcıya ihtiyacın vardır. İlk kurulumda yönetici yetkisi almak için admin yapmak istediğin hesabın e-postasını `init_admin.py` içine yazıp çalıştırabilirsin.

## 🛠 Kullanılan Teknolojiler
- **Backend:** Python, Flask, Flask-Login, PyMongo
- **Frontend:** HTML5, Vanilla CSS, Bootstrap 5, Jinja2
- **Database:** MongoDB
- **UI Design:** Dark Mode, Glassmorphism, Responsive Grid

## ✨ Öne Çıkan Özellikler
- 81 il ve 973 ilçe destekli Dinamik API Arama Motoru.
- Çift dilli (Türkçe & İngilizce) kalıcı çeviri (i18n) sistemi.
- Tarih çakışmalarını (Müsaitlik) önleyen akıllı MongoDB sorgu algoritması.
- Otel, oda, rezervasyon ekleme/silme yapılabilen şifreli Admin paneli.
