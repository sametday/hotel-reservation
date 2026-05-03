from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import difflib
import re
import random

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "pasha_hotels_secret_2026") 

# Veritabanı Bağlantısı
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['otel_db']
hotels_col = db['hotels']
rooms_col = db['rooms']
bookings_col = db['bookings']

# ==============================================================
#                 ÇOKLU DİL (i18n) MOTORU
# ==============================================================
TRANSLATIONS = {
    'tr': {
        'home': 'Ana Sayfa', 'my_bookings': 'Rezervasyonlarım', 'login': 'Giriş Yap', 'register': 'Kayıt Ol', 'logout': 'Çıkış Yap',
        'hero_title': 'Türkiye\'nin 81 İlini Keşfet', 'hero_desc': 'Binlerce otel arasından sana en uygun olanı anında bul.',
        'city': 'İl', 'district': 'İlçe', 'checkin': 'Giriş', 'checkout': 'Çıkış', 'adults': 'Yetişkin', 'children': 'Çocuk', 'search_btn': 'BUL',
        'email': 'E-POSTA', 'password': 'ŞİFRE', 'name_surname': 'AD SOYAD', 'login_btn': 'GİRİŞ YAP', 'register_btn': 'HESAP OLUŞTUR',
        'no_account': 'Henüz hesabınız yok mu?', 'have_account': 'Zaten hesabınız var mı?', 'register_now': 'Hemen Kaydolun', 'login_now': 'Giriş Yapın',
        'filters': 'Filtreler', 'price_range': 'Fiyat Aralığı', 'stars': 'Yıldız', 'amenities': 'Tesis Özellikleri', 'all_stars': 'Tüm Yıldızlar',
        'night': 'Gece', 'total_price': 'Toplam Tutar', 'book_now': 'HEMEN YER AYIRT', 'no_hotels_found': 'Otel bulunamadı.',
        'checkout_title': 'Rezervasyonu Tamamla', 'stay_summary': 'Konaklama Özeti', 'room_type': 'Oda Tipi', 'guest_info': 'Misafir Bilgileri',
        'phone': 'Telefon Numarası', 'pay_now': 'GÜVENLİ ÖDEME YAP', 'credit_card': 'Kredi Kartı', 'card_name': 'Kart Üzerindeki İsim', 'card_no': 'Kart Numarası',
        'past_bookings': 'Tüm konaklama detaylarınız.', 'cancel_booking': 'İptal Et', 'no_bookings': 'Henüz bir rezervasyonunuz yok.',
        'view_rooms': 'ODALARI İNCELE', 'total_paid': 'Toplam Ödenen:', 'transaction': 'İşlem:', 'select': 'Seçiniz', 'select_city_first': 'Önce İl Seçin',
        'search_results': 'Arama Sonuçları', 'hotels_in_region': 'bölgesindeki oteller', 'all_hotels': 'Tüm bölgelerdeki oteller',
        'selected_dates': 'Seçili Tarihler', 'narrow_results': 'Sonuçları Daralt', 'max_budget': 'Maksimum Bütçe', 'star_count': 'Yıldız Sayısı',
        'free_wifi': 'Ücretsiz Wi-Fi', 'pool': 'Yüzme Havuzu', 'spa': 'Spa & Masaj', 'parking': 'Otopark', 'breakfast': 'Kahvaltı',
        'facilities_found': 'adet tesis bulundu.', 'sort_by': 'Sırala:', 'recommended': 'Önerilen', 'price_lowest': 'Fiyata Göre (En Düşük)',
        'price_highest': 'Fiyata Göre (En Yüksek)', 'stars_highest': 'Yıldıza Göre (Önce 5 Yıldız)', 'available': 'Müsait',
        'starting_from': 'Gecelik başlayan fiyatlarla', 'available_rooms_here': 'Bu Tesisteki Müsait Odalar', 'room_no': 'Oda No:',
        'per_night': '/gece', 'select_btn': 'Seç', 'no_hotels_criteria': 'Aradığınız kriterlerde otel bulunamadı.', 'try_again': 'Lütfen farklı tarihler veya farklı bir bölge seçerek tekrar deneyin.',
        'back_to_search': 'Aramaya Geri Dön', 'payment_info': 'Ödeme Bilgileri', 'customer_info': 'Müşteri Bilgileri', 'email_desc': 'E-Posta Adresi (Onay Maili İçin)',
        'card_info': 'Kart Bilgileri', 'exp_date': 'Son Kullanma (Ay/Yıl)', 'secure_pay': 'Güvenli Ödeme Yap', 'dates': 'Tarihler', 'duration': 'Süre',
        'all_districts': 'Tüm İlçeler', 'view_on_map': 'Haritada Gör'
    },
    'en': {
        'home': 'Home', 'my_bookings': 'My Bookings', 'login': 'Login', 'register': 'Register', 'logout': 'Logout',
        'hero_title': 'Discover 81 Cities of Turkey', 'hero_desc': 'Find the perfect hotel among thousands instantly.',
        'city': 'City', 'district': 'District', 'checkin': 'Check-in', 'checkout': 'Check-out', 'adults': 'Adults', 'children': 'Children', 'search_btn': 'SEARCH',
        'email': 'EMAIL', 'password': 'PASSWORD', 'name_surname': 'FULL NAME', 'login_btn': 'LOGIN', 'register_btn': 'CREATE ACCOUNT',
        'no_account': 'Don\'t have an account?', 'have_account': 'Already have an account?', 'register_now': 'Register Now', 'login_now': 'Login Now',
        'filters': 'Filters', 'price_range': 'Price Range', 'stars': 'Stars', 'amenities': 'Amenities', 'all_stars': 'All Stars',
        'night': 'Night', 'total_price': 'Total Price', 'book_now': 'BOOK NOW', 'no_hotels_found': 'No hotels found.',
        'checkout_title': 'Complete Booking', 'stay_summary': 'Stay Summary', 'room_type': 'Room Type', 'guest_info': 'Guest Information',
        'phone': 'Phone Number', 'pay_now': 'SECURE PAYMENT', 'credit_card': 'Credit Card', 'card_name': 'Name on Card', 'card_no': 'Card Number',
        'past_bookings': 'Your stay details.', 'cancel_booking': 'Cancel Booking', 'no_bookings': 'You have no bookings yet.',
        'view_rooms': 'VIEW ROOMS', 'total_paid': 'Total Paid:', 'transaction': 'Transaction:', 'select': 'Select', 'select_city_first': 'Select City First',
        'search_results': 'Search Results', 'hotels_in_region': 'hotels in this region', 'all_hotels': 'Hotels in all regions',
        'selected_dates': 'Selected Dates', 'narrow_results': 'Narrow Results', 'max_budget': 'Maximum Budget', 'star_count': 'Star Rating',
        'free_wifi': 'Free Wi-Fi', 'pool': 'Swimming Pool', 'spa': 'Spa & Massage', 'parking': 'Parking', 'breakfast': 'Breakfast',
        'facilities_found': 'properties found.', 'sort_by': 'Sort By:', 'recommended': 'Recommended', 'price_lowest': 'Price (Lowest)',
        'price_highest': 'Price (Highest)', 'stars_highest': 'Stars (5 Stars First)', 'available': 'Available',
        'starting_from': 'Prices starting from', 'available_rooms_here': 'Available Rooms in This Property', 'room_no': 'Room No:',
        'per_night': '/night', 'select_btn': 'Select', 'no_hotels_criteria': 'No hotels found matching your criteria.', 'try_again': 'Please try again with different dates or a different region.',
        'back_to_search': 'Back to Search', 'payment_info': 'Payment Information', 'customer_info': 'Customer Information', 'email_desc': 'Email Address (For Confirmation)',
        'card_info': 'Card Information', 'exp_date': 'Expiry Date (MM/YY)', 'secure_pay': 'Secure Payment', 'dates': 'Dates', 'duration': 'Duration',
        'all_districts': 'All Districts', 'view_on_map': 'View on Map'
    }
}

@app.context_processor
def inject_translations():
    lang = request.cookies.get('lang', 'tr')
    def t(key):
        return TRANSLATIONS.get(lang, TRANSLATIONS['tr']).get(key, key)
    return dict(t=t, current_lang=lang)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    resp = redirect(request.referrer or url_for('index'))
    resp.set_cookie('lang', lang, max_age=60*60*24*30) 
    return resp

# Flask-Login Ayarları
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Bu sayfayı görmek için lütfen giriş yapın."
login_manager.login_message_category = "warning"

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data['name']
        self.is_admin = user_data.get('is_admin', False)

@login_manager.user_loader
def load_user(user_id):
    u = db.users.find_one({"_id": ObjectId(user_id)})
    if u: return User(u)
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        
        if db.users.find_one({"email": email}):
            flash("Bu e-posta adresi zaten kullanımda!", "danger")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        db.users.insert_one({"name": name, "email": email, "password": hashed_pw})
        
        flash("Kaydınız başarıyla oluşturuldu, giriş yapabilirsiniz.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        user_data = db.users.find_one({"email": email})
        
        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(user_data)
            login_user(user_obj)
            flash(f"Hoş geldiniz, {user_obj.name}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Geçersiz e-posta veya şifre!", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for('index'))

# ==============================================================
#                 2. ADMİN ROTALARI
# ==============================================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # TIRT MANTIK TEMİZLENDİ! 
    # MongoDB Atlas Aggregation kullanarak veritabanı seviyesinde JOIN işlemleri yapıyoruz.
    pipeline = [
        {"$lookup": {"from": "rooms", "localField": "room_id", "foreignField": "_id", "as": "room_info"}},
        {"$unwind": {"path": "$room_info", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "hotels", "localField": "room_info.hotel_id", "foreignField": "_id", "as": "hotel_info"}},
        {"$unwind": {"path": "$hotel_info", "preserveNullAndEmptyArrays": True}},
        {"$sort": {"created_at": -1}}
    ]
    
    bookings_cursor = db.bookings.aggregate(pipeline)
    all_bookings = []
    total_revenue = 0
    
    for b in bookings_cursor:
        room = b.get('room_info', {})
        hotel = b.get('hotel_info', {})
        b['room_info'] = room if room else {"room_type": "Silinmiş Oda", "room_number": "-"}
        b['hotel_name'] = hotel.get('name', 'Bilinmeyen Otel') if hotel else "Bilinmeyen Otel"
        total_revenue += float(b.get('total_price', 0))
        all_bookings.append(b)

    all_rooms = list(db.rooms.find())
    all_hotels = list(db.hotels.find())
    
    hotel_dict = {h['_id']: h['name'] for h in all_hotels}
    for r in all_rooms:
        r['hotel_name'] = hotel_dict.get(r.get('hotel_id'), "Bağlantısız Oda")

    return render_template('admin/dashboard.html', 
                           bookings=all_bookings, 
                           rooms=all_rooms, 
                           hotels=all_hotels, 
                           revenue=total_revenue)

@app.route('/admin/add-hotel', methods=['POST'])
@login_required
@admin_required
def add_hotel():
    new_hotel = {
        "name": request.form.get('name'),
        "city": request.form.get('city'),
        "district": request.form.get('district'),
        "stars": int(request.form.get('stars')),
        "description": request.form.get('description'),
        "image_url": request.form.get('image_url') or "https://images.unsplash.com/photo-1566073771259-6a8506099945"
    }
    db.hotels.insert_one(new_hotel)
    flash(f"{new_hotel['name']} başarıyla eklendi!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-hotel/<hotel_id>', methods=['POST'])
@login_required
@admin_required
def delete_hotel(hotel_id):
    db.hotels.delete_one({"_id": ObjectId(hotel_id)})
    db.rooms.delete_many({"hotel_id": ObjectId(hotel_id)})
    flash("Otel ve otele bağlı tüm odalar sistemden silindi.", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-room', methods=['POST'])
@login_required
@admin_required
def add_room():
    hotel_id = request.form.get('hotel_id')
    new_room = {
        "hotel_id": ObjectId(hotel_id), 
        "room_number": request.form.get('room_number'),
        "room_type": request.form.get('room_type'),
        "price": float(request.form.get('price')),
        "is_available": True
    }
    db.rooms.insert_one(new_room)
    flash("Yeni oda başarıyla eklendi!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-room/<room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    db.rooms.delete_one({"_id": ObjectId(room_id)})
    flash("Oda sistemden silindi.", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-booking', methods=['POST'])
@login_required
@admin_required
def admin_add_booking():
    room_id = request.form.get('room_id')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    
    d1 = datetime.strptime(check_in, "%Y-%m-%d")
    d2 = datetime.strptime(check_out, "%Y-%m-%d")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if d1 < today:
        flash("Hata: Geçmiş bir tarihe rezervasyon oluşturulamaz!", "danger")
        return redirect(url_for('admin_dashboard'))
    if d1 >= d2:
        flash("Hata: Çıkış tarihi, giriş tarihinden sonra olmalıdır!", "danger")
        return redirect(url_for('admin_dashboard'))

    room = db.rooms.find_one({"_id": ObjectId(room_id)})
    nights = max((d2 - d1).days, 1)
    
    new_booking = {
        "customer_name": request.form.get('customer_name'),
        "email": request.form.get('email', '-'),
        "phone": request.form.get('phone', '-'),
        "room_id": ObjectId(room_id),
        "check_in": check_in,
        "check_out": check_out,
        "total_price": nights * room['price'],
        "created_at": datetime.now()
    }
    db.bookings.insert_one(new_booking)
    flash("Manuel rezervasyon eklendi!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-booking/<booking_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_booking(booking_id):
    db.bookings.delete_one({"_id": ObjectId(booking_id)})
    flash("Rezervasyon iptal edildi.", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-room/<room_id>', methods=['POST'])
@login_required
@admin_required
def update_room(room_id):
    new_price = request.form.get('price')
    if new_price:
        db.rooms.update_one({"_id": ObjectId(room_id)}, {"$set": {"price": float(new_price)}})
        flash("Oda fiyatı başarıyla güncellendi!", "success")
    else:
        flash("Geçersiz fiyat girdiniz.", "danger")
    return redirect(url_for('admin_dashboard'))

# ==============================================================
#                 3. MÜŞTERİ (VİTRİN) ROTALARI
# ==============================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        city = request.form.get('city')
        district = request.form.get('district')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        adults = int(request.form.get('adults', 1))
        children = int(request.form.get('children', 0))
        
        session['last_search'] = {
            'city': city, 'district': district, 'checkin': checkin,
            'checkout': checkout, 'adults': adults, 'children': children
        }
    else:
        s = session.get('last_search')
        if not s: return redirect(url_for('index'))
        city, district = s.get('city'), s.get('district')
        checkin, checkout = s.get('checkin'), s.get('checkout')
        adults, children = s.get('adults', 1), s.get('children', 0)

    total_guests = adults + children

    if not checkin or not checkout or checkin >= checkout:
        flash("Geçersiz tarih aralığı!", "danger")
        return redirect(url_for('index'))
    
    # 1. ÖNCE ÇAKIŞAN REZERVASYONLARI BUL (Sadece room_id çekerek RAM'i koruyoruz)
    conflict_bookings = list(bookings_col.find({
        "check_in": {"$lt": checkout},
        "check_out": {"$gt": checkin}
    }, {"room_id": 1}))
    occupied_room_ids = [b['room_id'] for b in conflict_bookings]

    # 2. ŞEHİR/İLÇEYE GÖRE OTELLERİ BUL
    query = {}
    if city: query['city'] = city
    if district: query['district'] = {"$regex": district, "$options": "i"} 
    
    matching_hotels = list(hotels_col.find(query))
    hotel_ids = [h['_id'] for h in matching_hotels]

    if not matching_hotels:
        flash("Seçtiğiniz kriterlerde otel bulunamadı.", "info")
        return redirect(url_for('index'))

    # 3. VERİTABANINA "DOLU OLMAYANLARI GETİR" DİYORUZ (Atlas'ın gücü ile N+1 RAM katliamına son)
    available_rooms_cursor = list(rooms_col.find({
        "hotel_id": {"$in": hotel_ids},
        "_id": {"$nin": occupied_room_ids}
    }))

    room_capacities = {"Standart Oda": 2, "Deluxe Oda": 3, "Aile Süiti": 5, "Kral Dairesi": 4}

    # Sadece kapasitesi yetenleri filtrele
    available_rooms = [r for r in available_rooms_cursor if room_capacities.get(r.get('room_type'), 2) >= total_guests]

    valid_hotel_ids = set([r['hotel_id'] for r in available_rooms])
    final_hotels = [h for h in matching_hotels if h['_id'] in valid_hotel_ids]

    amenities_list = [
        {"id": "wifi", "name": "Ücretsiz Wi-Fi", "icon": "bi-wifi"},
        {"id": "pool", "name": "Yüzme Havuzu", "icon": "bi-water"},
        {"id": "spa", "name": "Spa & Masaj", "icon": "bi-flower1"},
        {"id": "parking", "name": "Ücretsiz Otopark", "icon": "bi-p-circle"},
        {"id": "breakfast", "name": "Kahvaltı Dahil", "icon": "bi-cup-hot"}
    ]

    for hotel in final_hotels:
        hash_val = sum(ord(c) for c in str(hotel['_id']))
        hotel['amenities'] = []
        for i, am in enumerate(amenities_list):
            if (hash_val + i) % 2 == 0:
                hotel['amenities'].append(am)
        if not hotel['amenities']:
            hotel['amenities'] = [amenities_list[0], amenities_list[4]]
            
        hotel['available_rooms'] = [r for r in available_rooms if r['hotel_id'] == hotel['_id']]
        if hotel['available_rooms']:
            hotel['starting_price'] = min(r['price'] for r in hotel['available_rooms'])

    return render_template('hotels.html', 
                           hotels=final_hotels, 
                           checkin=checkin, 
                           checkout=checkout, 
                           city=city, 
                           total_guests=total_guests)

@app.route('/booking/<room_id>')
def booking_page(room_id):
    room = rooms_col.find_one({"_id": ObjectId(room_id)})
    hotel = hotels_col.find_one({"_id": room['hotel_id']}) if room else None
    
    checkin, checkout = request.args.get('checkin'), request.args.get('checkout')
    d1, d2 = datetime.strptime(checkin, "%Y-%m-%d"), datetime.strptime(checkout, "%Y-%m-%d")
    nights = max((d2 - d1).days, 1)
    
    return render_template('booking.html', room=room, hotel=hotel, checkin=checkin, checkout=checkout, nights=nights, total=nights * room['price'])

@app.route('/confirm_booking/<room_id>', methods=['POST'])
@login_required
def confirm_booking(room_id):
    customer_name = request.form.get('fullname')
    checkin = request.form.get('checkin') or request.args.get('checkin')
    checkout = request.form.get('checkout') or request.args.get('checkout')
    total_price = request.form.get('total_price') or request.args.get('total_price')

    booking_doc = {
        "customer_name": customer_name,
        "email": current_user.email, 
        "phone": request.form.get('phone'),
        "room_id": ObjectId(room_id),
        "check_in": checkin,
        "check_out": checkout,
        "total_price": total_price,
        "created_at": datetime.now()
    }
    
    db.bookings.insert_one(booking_doc)
    return render_template('success.html', name=customer_name)

@app.route('/my-bookings')
@login_required
def my_bookings():
    clean_email = current_user.email.strip()
    # TIRT MANTIK TEMİZLENDİ! Yine Aggregation kullanıyoruz.
    pipeline = [
        {"$match": {"email": {"$regex": f"^{clean_email}$", "$options": "i"}}},
        {"$lookup": {"from": "rooms", "localField": "room_id", "foreignField": "_id", "as": "room_details"}},
        {"$unwind": {"path": "$room_details", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "hotels", "localField": "room_details.hotel_id", "foreignField": "_id", "as": "hotel_info"}},
        {"$unwind": {"path": "$hotel_info", "preserveNullAndEmptyArrays": True}},
        {"$sort": {"created_at": -1}}
    ]
    
    user_bookings_cursor = list(db.bookings.aggregate(pipeline))
    user_bookings = []
    
    for b in user_bookings_cursor:
        room = b.get('room_details', {})
        hotel = b.get('hotel_info', {})
        b['room_details'] = room if room else {"room_type": "Silinmiş Oda", "room_number": "-"}
        b['hotel_name'] = hotel.get('name', 'Bilinmeyen Otel') if hotel else "Bilinmeyen Otel"
        user_bookings.append(b)
            
    return render_template('my_bookings.html', bookings=user_bookings)

@app.route('/cancel-booking/<booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    if db.bookings.find_one({"_id": ObjectId(booking_id), "email": current_user.email}):
        db.bookings.delete_one({"_id": ObjectId(booking_id)})
        flash("Rezervasyonunuz iptal edildi.", "success")
    else:
        flash("İptal işlemi başarısız.", "danger")
    return redirect(url_for('my_bookings'))

@app.route('/checkout/<room_id>', methods=['GET', 'POST'])
def checkout(room_id):
    room = db.rooms.find_one({"_id": ObjectId(room_id)})
    hotel = db.hotels.find_one({"_id": room['hotel_id']})

    checkin = request.args.get('checkin')
    checkout_date = request.args.get('checkout')

    d1 = datetime.strptime(checkin, '%Y-%m-%d')
    d2 = datetime.strptime(checkout_date, '%Y-%m-%d')
    days = (d2 - d1).days
    total_price = days * room['price']

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        if current_user.is_authenticated:
            email = current_user.email
        else:
            email = request.form.get('email')
        phone = request.form.get('phone')

        booking_doc = {
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "hotel_name": hotel['name'],
            "room_id": room['_id'],
            "room_info": {"room_type": room['room_type'], "room_number": room['room_number']},
            "check_in": checkin,
            "check_out": checkout_date,
            "total_price": total_price,
            "created_at": datetime.now()
        }
        db.bookings.insert_one(booking_doc)

        flash(f"Ödeme Başarılı! Rezervasyon bilgileriniz {email} adresine gönderildi.", "success")
        return redirect(url_for('index'))

    return render_template('checkout.html', room=room, hotel=hotel, checkin=checkin, checkout=checkout_date, days=days, total_price=total_price)

# ==============================================================
#                 4. REST API ROTALARI
# ==============================================================

def serialize_doc(doc):
    if not doc:
        return None
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    return doc

@app.route('/api/v1/hotels', methods=['GET'])
def api_get_hotels():
    hotels = list(db.hotels.find())
    serialized_hotels = [serialize_doc(h) for h in hotels]
    
    return jsonify({
        "status": "success",
        "message": "Oteller başarıyla getirildi.",
        "count": len(serialized_hotels),
        "data": serialized_hotels
    }), 200

@app.route('/api/v1/hotels/<hotel_id>', methods=['GET'])
def api_get_hotel_details(hotel_id):
    try:
        hotel = db.hotels.find_one({"_id": ObjectId(hotel_id)})
        if not hotel:
            return jsonify({"status": "error", "message": "Otel bulunamadı!"}), 404
        
        rooms = list(db.rooms.find({"hotel_id": ObjectId(hotel_id)}))
        hotel = serialize_doc(hotel)
        hotel['rooms'] = [serialize_doc(r) for r in rooms] 
        
        return jsonify({"status": "success", "data": hotel}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Geçersiz ID formatı"}), 400

@app.route('/api/v1/search', methods=['POST'])
def api_search_hotels():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Arama verisi eksik!"}), 400

    city = data.get('city')
    district = data.get('district')
    
    query = {}
    if city: query['city'] = city
    if district: query['district'] = {"$regex": district, "$options": "i"}
    
    matching_hotels = list(db.hotels.find(query))
    
    return jsonify({
        "status": "success",
        "count": len(matching_hotels),
        "data": [serialize_doc(h) for h in matching_hotels]
    }), 200

@app.route('/api/v1/get_rooms/<hotel_id>', methods=['GET'])
@login_required
@admin_required
def api_get_rooms(hotel_id):
    try:
        rooms = list(db.rooms.find({"hotel_id": ObjectId(hotel_id)}))
        room_data = []
        for r in rooms:
            room_data.append({
                "_id": str(r["_id"]),
                "room_type": r["room_type"],
                "room_number": r["room_number"],
                "price": r["price"]
            })
        return jsonify({"status": "success", "data": room_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route('/api/v1/get_hotels_by_city/<city>', methods=['GET'])
@login_required
@admin_required
def api_get_hotels_by_city(city):
    try:
        hotels = list(db.hotels.find({"city": city}))
        hotel_data = []
        for h in hotels:
            hotel_data.append({
                "_id": str(h["_id"]),
                "name": h["name"]
            })
        return jsonify({"status": "success", "data": hotel_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/admin/hotels', methods=['POST'])
def api_add_hotel():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('city'):
        return jsonify({"status": "error", "message": "Otel adı ve şehri zorunludur!"}), 400
    
    new_hotel = {
        "name": data.get('name'),
        "city": data.get('city'),
        "district": data.get('district', ''),
        "stars": int(data.get('stars', 3)),
        "description": data.get('description', ''),
        "image_url": data.get('image_url', '')
    }
    result = db.hotels.insert_one(new_hotel)
    return jsonify({"status": "success", "message": "Yeni otel sisteme başarıyla eklendi.", "hotel_id": str(result.inserted_id)}), 201

@app.route('/api/v1/admin/hotels/<hotel_id>', methods=['DELETE'])
def api_delete_hotel(hotel_id):
    try:
        result = db.hotels.delete_one({"_id": ObjectId(hotel_id)})
        if result.deleted_count == 0:
            return jsonify({"status": "error", "message": "Silinecek otel bulunamadı!"}), 404
        db.rooms.delete_many({"hotel_id": ObjectId(hotel_id)})
        return jsonify({"status": "success", "message": "Otel ve bağlı odalar sistemden tamamen silindi."}), 200
    except:
        return jsonify({"status": "error", "message": "Geçersiz ID formatı"}), 400

@app.route('/api/v1/admin/bookings', methods=['GET'])
def api_get_all_bookings():
    bookings = list(db.bookings.find())
    return jsonify({"status": "success", "count": len(bookings), "data": [serialize_doc(b) for b in bookings]}), 200

@app.route('/api/v1/admin/bookings/<booking_id>', methods=['DELETE'])
def api_delete_booking(booking_id):
    try:
        result = db.bookings.delete_one({"_id": ObjectId(booking_id)})
        if result.deleted_count == 0:
            return jsonify({"status": "error", "message": "Rezervasyon bulunamadı!"}), 404
        return jsonify({"status": "success", "message": "Rezervasyon başarıyla iptal edildi."}), 200
    except:
        return jsonify({"status": "error", "message": "Geçersiz ID formatı"}), 400
    
@app.route('/api/v1/locations', methods=['GET'])
def api_get_locations():
    locations = list(db.locations.find({}, {"_id": 0}))
    location_dict = {loc["city"]: loc["districts"] for loc in locations}
    return jsonify({"status": "success", "data": location_dict}), 200

@app.route('/api/v1/chat', methods=['POST'])
def api_chat():
    lang = request.cookies.get('lang', 'tr')
    data = request.get_json()
    msg = data.get('message', '').lower()
    
    # --- BAĞLAM (CONTEXT) YÖNETİMİ ---
    reset_words = ["baştan", "iptal", "vazgeçtim", "sıfırla", "başka", "temizle"] if lang == 'tr' else ["reset", "cancel", "start over", "clear", "another", "new"]
    if any(w in msg for w in reset_words):
        session['chat_context'] = {"city": None, "intents": [], "state": "browsing"}
        reply = "Nasıl isterseniz, her şeyi sıfırladım. Yeni bir tatil rotası çizelim. Nereye gitmek istersiniz?" if lang == 'tr' else "As you wish, everything is reset. Let's plan a new trip. Where would you like to go?"
        return jsonify({"reply": reply})
        
    if 'chat_context' not in session:
        session['chat_context'] = {"city": None, "intents": [], "state": "browsing"}
        
    context = session['chat_context']
    if 'state' not in context:
        context['state'] = "browsing"

    msg_clean = re.sub(r'[^\w\s]', ' ', msg)
    if context.get('state') == 'offering_booking':
        yes_words = ["evet", "olur", "yap", "onaylıyorum", "tamam", "istiyorum", "tabii"] if lang == 'tr' else ["yes", "yeah", "sure", "ok", "okay", "confirm", "do it"]
        no_words = ["hayır", "istemiyorum", "vazgeç", "yok", "kalsın"] if lang == 'tr' else ["no", "nope", "cancel", "don't", "stop"]
        
        if any(w in msg_clean for w in yes_words):
            if not current_user.is_authenticated:
                reply = "Hızlı rezervasyon yapabilmem için lütfen sayfadan <b>Giriş Yapın</b> veya <b>Kayıt Olun</b>." if lang == 'tr' else "Please <b>Login</b> or <b>Register</b> first so I can make a quick booking for you."
                return jsonify({"reply": reply})
                
            room_id = context.get('proposed_room_id')
            hotel_name = context.get('proposed_hotel_name')
            total_price = context.get('proposed_price', 0)
            
            if not room_id:
                context['state'] = 'browsing'
                session['chat_context'] = context
                reply = "Bir hata oluştu, lütfen baştan başlayalım. Hangi şehre gitmek istersiniz?" if lang == 'tr' else "An error occurred, let's start over. Which city would you like to go?"
                return jsonify({"reply": reply})
                
            checkin_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            checkout_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            
            new_booking = {
                "customer_name": current_user.name,
                "email": current_user.email,
                "phone": "Chatbot Hızlı İşlem",
                "room_id": ObjectId(room_id),
                "check_in": checkin_date,
                "check_out": checkout_date,
                "total_price": total_price,
                "created_at": datetime.now()
            }
            db.bookings.insert_one(new_booking)
            
            context['state'] = 'browsing'
            context['city'] = None
            context['intents'] = []
            session['chat_context'] = context
            
            reply = f"🎉 <b>İşlem Başarılı!</b><br>{hotel_name} oteli için ({checkin_date} - {checkout_date}) tarihleri arasında rezervasyonunuzu anında tamamladım. Detayları 'Rezervasyonlarım' sayfasından görebilirsiniz." if lang == 'tr' else f"🎉 <b>Success!</b><br>I have completed your booking for {hotel_name} between ({checkin_date} - {checkout_date}). You can see details in 'My Reservations'."
            return jsonify({"reply": reply})
            
        elif any(w in msg_clean for w in no_words):
            context['state'] = 'browsing'
            session['chat_context'] = context
            reply = "Anladım, işlemi iptal ettim. Size farklı şehirlerdeki seçenekleri göstermeye devam edebilirim. Nereye bakalım?" if lang == 'tr' else "Understood, I canceled the operation. I can keep showing you options in other cities. Where to?"
            return jsonify({"reply": reply})
        else:
            reply = "Lütfen işlemi onaylamak için sadece <b>'Evet'</b> veya iptal etmek için <b>'Hayır'</b> yazın." if lang == 'tr' else "Please just type <b>'Yes'</b> to confirm or <b>'No'</b> to cancel."
            return jsonify({"reply": reply})
            
    words = msg_clean.split()
    city_aliases = {
        "afyon": "Afyonkarahisar", "urfa": "Şanlıurfa", "antep": "Gaziantep", 
        "maraş": "Kahramanmaraş", "izmit": "Kocaeli", "adapazarı": "Sakarya", 
        "içel": "Mersin", "hatay": "Hatay", "antakya": "Hatay", "kıbrıs": "Girne"
    }
    valid_cities = db.hotels.distinct("city")
    valid_lower = {c.lower(): c for c in valid_cities}
    found_city = None
    
    for w in words:
        if w in city_aliases and city_aliases[w] in valid_cities:
            found_city = city_aliases[w]
            break
    if not found_city:
        for c_lower, c_orig in valid_lower.items():
            if c_lower in msg_clean:
                found_city = c_orig
                break
    if not found_city:
        all_cities_list = list(valid_lower.keys())
        for w in words:
            if len(w) >= 4:
                matches = difflib.get_close_matches(w, all_cities_list, n=1, cutoff=0.75)
                if matches:
                    found_city = valid_lower[matches[0]]
                    break

    if found_city:
        context['city'] = found_city

    if lang == 'tr':
        intents = {
            "cheap": ["ucuz", "uygun", "ekonomik", "kampanya", "indirim", "fırsat", "bütçe", "hesaplı"],
            "luxury": ["lüks", "5 yıldız", "kral", "pahalı", "kaliteli", "premium", "deluxe", "harika"],
            "pool": ["havuz", "deniz", "sahil", "plaj", "yüzme", "kum", "aqua", "su", "termal", "kaplıca"],
            "family": ["aile", "çocuk", "bebek", "geniş", "kalabalık", "büyük"],
            "romantic": ["balayı", "romantik", "sevgili", "eş", "çift", "aşk"],
            "food": ["kahvaltı", "yemek", "her şey", "büfe", "restoran"],
            "my_bookings": ["rezervasyonum", "rezervasyonlarım", "bilet", "sipariş", "biletlerim"],
            "auth": ["giriş yap", "üye ol", "kayıt ol", "hesabım", "giriş"]
        }
    else:
        intents = {
            "cheap": ["cheap", "affordable", "economic", "discount", "budget", "sale"],
            "luxury": ["luxury", "5 star", "expensive", "quality", "premium", "deluxe", "great", "king"],
            "pool": ["pool", "sea", "beach", "swim", "sand", "aqua", "water", "thermal"],
            "family": ["family", "child", "children", "baby", "large", "big"],
            "romantic": ["honeymoon", "romantic", "couple", "wife", "husband", "love"],
            "food": ["breakfast", "food", "all inclusive", "buffet", "restaurant"],
            "my_bookings": ["my bookings", "my reservation", "my reservations", "my ticket", "my tickets"],
            "auth": ["login", "sign in", "register", "sign up", "my account"]
        }
    
    detected_intents = []
    for intent, keywords in intents.items():
        if any(kw in msg_clean for kw in keywords):
            detected_intents.append(intent)
            
    for i in detected_intents:
        if i not in context['intents']:
            context['intents'].append(i)
            
    if "my_bookings" in detected_intents:
        if not current_user.is_authenticated:
            reply = "Rezervasyonlarınızı görebilmem için lütfen önce sisteme <b>Giriş Yapın</b>." if lang == 'tr' else "Please <b>Login</b> first so I can check your reservations."
            return jsonify({"reply": reply})
        else:
            user_bookings = list(db.bookings.find({"email": current_user.email}))
            if not user_bookings:
                reply = "Şu an aktif bir rezervasyonunuz bulunmuyor. Sizin için yeni bir tatil planlayalım mı?" if lang == 'tr' else "You don't have any active reservations. Shall we plan a new trip?"
            else:
                b = user_bookings[-1]
                reply = f"En son rezervasyonunuz: <b>{b['check_in']}</b> ile <b>{b['check_out']}</b> tarihleri arasında.<br>Detayları görmek için 'Rezervasyonlarım' paneline gidebilirsiniz." if lang == 'tr' else f"Your latest booking is between <b>{b['check_in']}</b> and <b>{b['check_out']}</b>.<br>You can check the details in 'My Reservations' panel."
            return jsonify({"reply": reply})
            
    if "auth" in detected_intents:
        reply = "<a href='/login' class='btn btn-warning w-100 text-dark fw-bold'>Giriş Yap / Üye Ol</a>" if lang == 'tr' else "<a href='/login' class='btn btn-warning w-100 text-dark fw-bold'>Login / Register</a>"
        return jsonify({"reply": reply})

    session['chat_context'] = context
    session.modified = True

    if lang == 'tr':
        chit_chat_responses = {
            "nasılsın": "Teşekkür ederim, harikayım! Size en iyi tatili bulmak için buradayım. Siz nasılsınız?",
            "iyi misin": "Teşekkür ederim, sistemlerim tam performans çalışıyor! Size tatil planlamada yardımcı olmak için sabırsızlanıyorum.",
            "naber": "İyiyim, teşekkürler! Sizin için tatil fırsatlarını tarıyorum. Nasıl bir yer arıyorsunuz?",
            "kimsin": "Ben 36Otel'in Yapay Zeka destekli tatil asistanıyım. Türkiye'nin dört bir yanındaki binlerce oteli saniyeler içinde sizin için analiz edebilirim.",
            "adın ne": "Benim özel bir ismim yok, bana kısaca 'Asistan' diyebilirsiniz. Önceliğim size harika bir tatil bulmak!",
            "yapay zeka": "Evet, Doğal Dil İşleme yetenekleriyle donatılmış bir yapay zekayım. Cümlelerinizi analiz edip size en uygun oteli bulabilirim.",
            "fiyatlar nasıl": "Fiyatlar seçtiğiniz şehre ve otel tipine göre değişiyor ancak sistemimizde her bütçeye uygun (800 TL'den başlayan) seçenekler mevcut.",
            "pahalı": "Her bütçeye uygun otellerimiz var. İsterseniz 'Ucuz' veya 'Ekonomik' diyerek en uygun fiyatlı olanları görebilirsiniz.",
            "hangi şehirler": "Türkiye'nin 81 ilinin tamamında otel ağımız var! Antalya, İzmir, Trabzon, Van... Nereye gitmek istersiniz?",
            "indirim": "En güncel indirimleri ve kampanya fırsatlarını yakalamak için bana gitmek istediğiniz şehri söylemeniz yeterli.",
            "fıkra": "Tatil planlamaktan fıkra ezberlemeye pek vaktim olmadı maalesef 😊 Ama size harika bir tatil bularak yüzünüzü güldürebileceğime eminim!",
            "teşekkür": "Rica ederim! Size yardımcı olabildiysem ne mutlu bana. Başka bir sorunuz var mı?",
            "sağol": "Rica ederim, her zaman buradayım! Şimdiden harika bir tatil dilerim.",
            "hava": "Hava durumunu anlık olarak bilemiyorum ama Akdeniz sahilleri yazları her zaman harikadır! Sıcak bir sahil tatili ister misiniz?",
            "iptal": "Rezervasyonlarınızı sisteme giriş yaptıktan sonra 'Rezervasyonlarım' sayfasından kolayca iptal edebilirsiniz. Her şey çok esnek!",
            "iletişim": "Bize destek@36otel.com adresinden ulaşabilirsiniz.",
            "yaşın kaç": "Ben dijital bir varlığım, yaşım yok. Ancak tecrübem on binlerce rezervasyon verisine dayanıyor!",
            "günaydın": "Günaydın! Harika bir gün ve harika bir tatil planlamak için buradayım.",
            "iyi akşamlar": "İyi akşamlar! Günün yorgunluğunu atacağınız harika bir tatil planlamaya ne dersiniz?",
            "iyi geceler": "İyi geceler! Yarın harika bir tatil rotası çizmek için burada olacağım."
        }
    else:
        chit_chat_responses = {
            "how are you": "Thank you, I'm doing great! I'm here to find the best vacation for you. How are you?",
            "what's up": "I'm good, thanks! Scanning vacation deals for you. What kind of place are you looking for?",
            "who are you": "I'm 36Otel's AI Holiday Assistant. I can analyze thousands of hotels across Turkey in seconds.",
            "your name": "I don't have a specific name, you can just call me 'Assistant'. My priority is finding you a great vacation!",
            "ai": "Yes, I am an AI equipped with NLP. I can understand your sentences and find the best hotel.",
            "prices": "Prices vary depending on the city and hotel type, but we have affordable options starting from 800 TL.",
            "expensive": "We have hotels for every budget. You can say 'cheap' or 'economic' to see the most affordable ones.",
            "cities": "We have hotels in all 81 provinces of Turkey! Antalya, Izmir, Trabzon... Where would you like to go?",
            "discount": "To catch the latest discounts, just tell me which city you want to go to.",
            "joke": "I haven't had much time to memorize jokes 😊 But finding you a great holiday will make you smile!",
            "thank": "You're welcome! I'm glad I could help. Do you have any other questions?",
            "weather": "I don't know the weather exactly, but the Mediterranean coast is always wonderful in summer!",
            "cancel": "You can easily cancel your reservations from the 'My Reservations' page.",
            "contact": "You can reach us at support@36otel.com.",
            "age": "I'm a digital entity, I don't have an age. But my experience is vast!",
            "good morning": "Good morning! I'm here to plan a wonderful vacation.",
            "good evening": "Good evening! Let's plan a great vacation to relieve your tiredness.",
            "good night": "Good night! I'll be here tomorrow to draw a great vacation route."
        }

    chit_chat_reply = None
    for key, val in chit_chat_responses.items():
        if key in msg_clean:
            chit_chat_reply = val
            break

    reply = ""
    checkin_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    checkout_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    
    if context['city']:
        hotel_count = db.hotels.count_documents({"city": context['city']})
        if hotel_count == 0:
            bad_city = context['city']
            context['city'] = None
            session['chat_context'] = context
            reply = f"Maalesef şu an {bad_city} bölgesinde sistemimize kayıtlı otel kalmamış. Ege sahilleri veya Antalya harika alternatifler. İlgilenir misiniz?" if lang == 'tr' else f"Unfortunately, we don't have any hotels registered in {bad_city} right now. How about Aegean coast or Antalya?"
            return jsonify({"reply": reply})
            
        if not context['intents']:
            if chit_chat_reply:
                reply = chit_chat_reply + (f"<br><br>Bu arada {context['city']} tatiliniz için nasıl bir konsept aradığınızı düşünmeye devam ediyor musunuz? (Lüks, Ucuz)" if lang == 'tr' else f"<br><br>By the way, are you still thinking about what concept you want for your {context['city']} vacation? (Luxury, Cheap)")
                return jsonify({"reply": reply})

            if lang == 'tr':
                responses = [
                    f"Harika bir seçim! {context['city']} şehrinde tam {hotel_count} otelimiz var. Peki nasıl bir konsept arıyorsunuz? (Örn: Lüks, Ucuz, Havuzlu, Aile)",
                    f"{context['city']} tatili için sizi arama zahmetinden kurtarayım. Bütçe dostu mu olsun, yoksa 5 yıldızlı lüks bir yer mi arıyorsunuz?",
                    f"{context['city']} bölgesini sizin için taradım. Bana kiminle gideceğinizi (Örn: Eşimle, Çocuklarla) söylerseniz size en uygun oteli bulabilirim."
                ]
                btn_text = f"Sadece Tüm {context['city']} Otellerini Gör"
            else:
                responses = [
                    f"Great choice! We have {hotel_count} hotels in {context['city']}. What concept are you looking for? (e.g. Luxury, Cheap, Pool, Family)",
                    f"Let me save you the trouble for {context['city']}. Do you want a budget-friendly place or a 5-star luxury hotel?",
                    f"I scanned {context['city']} for you. If you tell me who you are going with (e.g. Spouse, Children), I can find the best hotel."
                ]
                btn_text = f"See All {context['city']} Hotels"
                
            reply = random.choice(responses)
            reply += f"<br><form action='/search' method='POST' class='mt-2'><input type='hidden' name='city' value='{context['city']}'><input type='hidden' name='checkin' value='{checkin_date}'><input type='hidden' name='checkout' value='{checkout_date}'><button type='submit' class='btn btn-sm btn-outline-warning text-white w-100'>{btn_text}</button></form>"
            return jsonify({"reply": reply})
            
        else:
            city_hotels = list(db.hotels.find({"city": context['city']}, {"_id": 1}))
            hotel_ids = [h['_id'] for h in city_hotels]
            cheapest_room = db.rooms.find_one({"hotel_id": {"$in": hotel_ids}}, sort=[("price", 1)])
            
            if cheapest_room:
                proposed_hotel = db.hotels.find_one({"_id": cheapest_room['hotel_id']})
                nights = 3
                total_price = cheapest_room['price'] * nights
                
                context['proposed_room_id'] = str(cheapest_room['_id'])
                context['proposed_hotel_name'] = proposed_hotel['name']
                context['proposed_price'] = total_price
                context['state'] = 'offering_booking'
                session['chat_context'] = context
                
                reply = f"Mükemmel! {context['city']} bölgesinde tam aradığınız gibi bir yer buldum: <b>{proposed_hotel['name']}</b>.<br>Gelecek hafta 3 gecelik toplam fiyat: {total_price} TL.<br><br>Sizin adınıza şu an hemen <b>hızlı rezervasyon</b> yapmamı onaylıyor musunuz? (Evet / Hayır)" if lang == 'tr' else f"Perfect! I found exactly what you're looking for in {context['city']}: <b>{proposed_hotel['name']}</b>.<br>Total price for 3 nights next week: {total_price} TL.<br><br>Do you confirm me to make a <b>quick booking</b> for you right now? (Yes / No)"
            else:
                reply = f"Harika! {context['city']} bölgesinde size uygun {hotel_count} otel buldum. Hemen inceleyebilirsiniz." if lang == 'tr' else f"Great! I found {hotel_count} suitable hotels in {context['city']}. You can review them now."
                btn_text = "Otelleri Göster" if lang == 'tr' else "Show Hotels"
                reply += f"<form action='/search' method='POST' class='mt-3'><input type='hidden' name='city' value='{context['city']}'><input type='hidden' name='checkin' value='{checkin_date}'><input type='hidden' name='checkout' value='{checkout_date}'><button type='submit' class='btn btn-sm btn-primary text-white fw-bold w-100'>{btn_text}</button></form>"
                
                session['chat_context'] = {"city": None, "intents": [], "state": "browsing"}
                
            return jsonify({"reply": reply})

    else:
        if context['intents']:
            if chit_chat_reply:
                return jsonify({"reply": chit_chat_reply + (" Bu arada tatiliniz için şehir kararı verdiniz mi?" if lang == 'tr' else " By the way, have you decided on a city for your vacation?")})

            if lang == 'tr':
                intent_map = {"cheap": "Bütçe dostu ekonomik", "luxury": "Ultra lüks 5 yıldızlı", "pool": "Havuzlu ve ferah", "family": "Çocuk dostu aile", "romantic": "Romantik ve sessiz"}
                primary_intent = context['intents'][-1]
                reply = f"{intent_map.get(primary_intent, 'Harika')} bir tatil aradığınızı anlıyorum. Türkiye'nin 81 ilinde seçeneklerimiz var. Öncelikli olarak hangi <b>bölgeye veya şehre</b> (Örn: Antalya, İzmir) gitmek istersiniz?"
            else:
                intent_map = {"cheap": "Budget-friendly", "luxury": "Ultra luxury 5-star", "pool": "Refreshing with a pool", "family": "Family-friendly", "romantic": "Romantic and quiet"}
                primary_intent = context['intents'][-1]
                reply = f"I understand you are looking for a {intent_map.get(primary_intent, 'great')} vacation. We have options in all 81 provinces. Which <b>region or city</b> (e.g. Antalya, Izmir) would you prefer?"
            return jsonify({"reply": reply})
        else:
            if chit_chat_reply:
                return jsonify({"reply": chit_chat_reply})
            
            greet_words_tr = ["merhaba", "selam", "hey", "hi", "iyi", "günler"]
            greet_words_en = ["hello", "hi", "hey", "good"]
            greet_words = greet_words_tr if lang == 'tr' else greet_words_en
            
            if any(w in msg_clean for w in greet_words):
                reply = "Merhaba! Ben 36Otel Yapay Zeka Asistanı. Sizinle sohbet ederek hayalinizdeki tatili bulabilirim. Nereye gitmek istersiniz?" if lang == 'tr' else "Hello! I am 36Otel AI Assistant. I can help you find your dream vacation. Where would you like to go?"
                return jsonify({"reply": reply})
            else:
                if lang == 'tr':
                    responses = [
                        "Söylediğinizi tam olarak kavrayamadım. Bir yapay zeka olarak alanım sadece tatil, otel ve seyahattir. Lütfen gitmek istediğiniz ŞEHRİ (Örn: Muğla) yazın.",
                        "Anlamakta zorluk çektim 😊 Kararsızsanız bana sadece 'Havuzlu', 'Ucuz' veya 'Antalya' gibi anahtar kelimeler yazmanız yeterli.",
                        "Derin öğrenme algoritmalarım şu an için sadece Tatil ve Konaklama terimlerini algılayabiliyor. Lütfen bana aradığınız otel konseptini veya şehri belirtir misiniz?"
                    ]
                else:
                    responses = [
                        "I couldn't quite grasp what you said. As an AI, my expertise is limited to travel and hotels. Please type the CITY you want to visit.",
                        "I had trouble understanding 😊 If you are undecided, just type keywords like 'Pool', 'Cheap' or 'Antalya'.",
                        "My deep learning algorithms can only understand Travel and Accommodation terms right now. Could you please specify a hotel concept or city?"
                    ]
                return jsonify({"reply": random.choice(responses)})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)