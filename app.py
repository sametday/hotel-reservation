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
    # Güvenli Tutar Çevirme Fonksiyonu (Crash Önleyici)
    def safe_float(val):
        try:
            return float(str(val).replace(',', '').replace(' TL', '').strip() or 0)
        except:
            return 0.0

    pipeline = [
        {"$lookup": {"from": "rooms", "localField": "room_id", "foreignField": "_id", "as": "room_info"}},
        {"$unwind": {"path": "$room_info", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "hotels", "localField": "room_info.hotel_id", "foreignField": "_id", "as": "hotel_info"}},
        {"$unwind": {"path": "$hotel_info", "preserveNullAndEmptyArrays": True}},
        {"$sort": {"created_at": -1}}
    ]
    
    bookings_cursor = db.bookings.aggregate(pipeline)
    all_bookings = []
    total_revenue = 0.0
    
    for b in bookings_cursor:
        room = b.get('room_info') or {}
        hotel = b.get('hotel_info') or {}
        
        b['room_info'] = room if room.get('room_type') else {"room_type": "Silinmiş Oda", "room_number": "-"}
        b['hotel_name'] = hotel.get('name', 'Bilinmeyen Otel')
        
        price = safe_float(b.get('total_price', 0))
        b['total_price'] = price
        total_revenue += price
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
    
    conflict_bookings = list(bookings_col.find({
        "check_in": {"$lt": checkout},
        "check_out": {"$gt": checkin}
    }, {"room_id": 1}))
    occupied_room_ids = [b['room_id'] for b in conflict_bookings]

    query = {}
    if city: query['city'] = city
    if district: query['district'] = {"$regex": district, "$options": "i"} 
    
    matching_hotels = list(hotels_col.find(query))
    hotel_ids = [h['_id'] for h in matching_hotels]

    if not matching_hotels:
        flash("Seçtiğiniz kriterlerde otel bulunamadı.", "info")
        return redirect(url_for('index'))

    available_rooms_cursor = list(rooms_col.find({
        "hotel_id": {"$in": hotel_ids},
        "_id": {"$nin": occupied_room_ids}
    }))

    room_capacities = {"Standart Oda": 2, "Deluxe Oda": 3, "Aile Süiti": 5, "Kral Dairesi": 4}
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

    return render_template('hotels.html', hotels=final_hotels, checkin=checkin, checkout=checkout, city=city, total_guests=total_guests)

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
        room = b.get('room_details') or {}
        hotel = b.get('hotel_info') or {}
        b['room_details'] = room if room.get('room_type') else {"room_type": "Silinmiş Oda", "room_number": "-"}
        b['hotel_name'] = hotel.get('name', 'Bilinmeyen Otel')
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
        email = current_user.email if current_user.is_authenticated else request.form.get('email')
        phone = request.form.get('phone')

        booking_doc = {
            "customer_name": customer_name, "email": email, "phone": phone,
            "hotel_name": hotel['name'], "room_id": room['_id'],
            "room_info": {"room_type": room['room_type'], "room_number": room['room_number']},
            "check_in": checkin, "check_out": checkout_date,
            "total_price": total_price, "created_at": datetime.now()
        }
        db.bookings.insert_one(booking_doc)

        flash(f"Ödeme Başarılı! Rezervasyon bilgileriniz {email} adresine gönderildi.", "success")
        return redirect(url_for('index'))

    return render_template('checkout.html', room=room, hotel=hotel, checkin=checkin, checkout=checkout_date, days=days, total_price=total_price)

# ==============================================================
#                 4. REST API ROTALARI
# ==============================================================

def serialize_doc(doc):
    if not doc: return None
    for key, value in doc.items():
        if isinstance(value, ObjectId): doc[key] = str(value)
        elif isinstance(value, datetime): doc[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    return doc

@app.route('/api/v1/locations', methods=['GET'])
def api_get_locations():
    locations = list(db.locations.find({}, {"_id": 0}))
    location_dict = {loc["city"]: loc["districts"] for loc in locations}
    return jsonify({"status": "success", "data": location_dict}), 200

@app.route('/api/v1/get_rooms/<hotel_id>', methods=['GET'])
@login_required
@admin_required
def api_get_rooms(hotel_id):
    try:
        rooms = list(db.rooms.find({"hotel_id": ObjectId(hotel_id)}))
        room_data = [{"_id": str(r["_id"]), "room_type": r["room_type"], "room_number": r["room_number"], "price": r["price"]} for r in rooms]
        return jsonify({"status": "success", "data": room_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route('/api/v1/get_hotels_by_city/<city>', methods=['GET'])
@login_required
@admin_required
def api_get_hotels_by_city(city):
    try:
        hotels = list(db.hotels.find({"city": city}))
        hotel_data = [{"_id": str(h["_id"]), "name": h["name"]} for h in hotels]
        return jsonify({"status": "success", "data": hotel_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ==============================================================
#                 5. STATE-MACHINE OOP CHATBOT
# ==============================================================

class HolidayBotManager:
    """Spagetti if-else bloklarını çözen temiz, state-machine tabanlı Chatbot Sınıfı"""
    def __init__(self, db_conn):
        self.db = db_conn
        self.city_aliases = {
            "afyon": "Afyonkarahisar", "urfa": "Şanlıurfa", "antep": "Gaziantep", 
            "maraş": "Kahramanmaraş", "izmit": "Kocaeli", "adapazarı": "Sakarya", 
            "içel": "Mersin", "hatay": "Hatay", "antakya": "Hatay", "kıbrıs": "Girne"
        }

    def get_intents(self, lang):
        if lang == 'tr':
            return {
                "cheap": ["ucuz", "uygun", "ekonomik", "kampanya", "indirim", "fırsat", "bütçe", "hesaplı"],
                "luxury": ["lüks", "5 yıldız", "kral", "pahalı", "kaliteli", "premium", "deluxe", "harika"],
                "pool": ["havuz", "deniz", "sahil", "plaj", "yüzme", "kum", "aqua", "su", "termal", "kaplıca"],
                "family": ["aile", "çocuk", "bebek", "geniş", "kalabalık", "büyük"],
                "romantic": ["balayı", "romantik", "sevgili", "eş", "çift", "aşk"],
                "food": ["kahvaltı", "yemek", "her şey", "büfe", "restoran"],
                "my_bookings": ["rezervasyonum", "rezervasyonlarım", "bilet", "sipariş", "biletlerim"],
                "auth": ["giriş yap", "üye ol", "kayıt ol", "hesabım", "giriş"]
            }
        return {
            "cheap": ["cheap", "affordable", "economic", "discount", "budget", "sale"],
            "luxury": ["luxury", "5 star", "expensive", "quality", "premium", "deluxe", "great", "king"],
            "pool": ["pool", "sea", "beach", "swim", "sand", "aqua", "water", "thermal"],
            "family": ["family", "child", "children", "baby", "large", "big"],
            "romantic": ["honeymoon", "romantic", "couple", "wife", "husband", "love"],
            "my_bookings": ["my bookings", "my reservation", "my ticket", "my tickets"],
            "auth": ["login", "sign in", "register", "sign up", "my account"]
        }

    def get_chitchat(self, lang):
        if lang == 'tr':
            return {
                "nasılsın": "Teşekkür ederim, harikayım! Size en iyi tatili bulmak için buradayım.",
                "kimsin": "Ben 36Otel'in akıllı tatil asistanıyım.",
                "teşekkür": "Rica ederim! Size yardımcı olabildiysem ne mutlu bana."
            }
        return {
            "how are you": "Thank you, I'm doing great! I'm here to find the best vacation for you.",
            "who are you": "I'm 36Otel's smart Holiday Assistant.",
            "thank": "You're welcome! I'm glad I could help."
        }

    def extract_city(self, text):
        words = text.split()
        valid_cities = self.db.hotels.distinct("city")
        valid_lower = {c.lower(): c for c in valid_cities}

        for w in words:
            if w in self.city_aliases and self.city_aliases[w] in valid_cities: return self.city_aliases[w]
        for c_lower, c_orig in valid_lower.items():
            if c_lower in text: return c_orig
        for w in words:
            if len(w) >= 4:
                matches = difflib.get_close_matches(w, list(valid_lower.keys()), n=1, cutoff=0.75)
                if matches: return valid_lower[matches[0]]
        return None

    def process_booking_confirmation(self, text, lang, context, user):
        yes_words = ["evet", "olur", "yap", "onaylıyorum", "tamam"] if lang == 'tr' else ["yes", "ok", "confirm"]
        no_words = ["hayır", "istemiyorum", "vazgeç"] if lang == 'tr' else ["no", "cancel"]

        if any(w in text for w in yes_words):
            if not user.is_authenticated:
                return ("Hızlı rezervasyon için lütfen sayfadan <b>Giriş Yapın</b>." if lang == 'tr' else "Please <b>Login</b> for quick booking.")
            
            checkin = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            checkout = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            
            self.db.bookings.insert_one({
                "customer_name": user.name, "email": user.email, "phone": "Chatbot Hızlı İşlem",
                "room_id": ObjectId(context.get('proposed_room_id')),
                "check_in": checkin, "check_out": checkout,
                "total_price": context.get('proposed_price', 0), "created_at": datetime.now()
            })
            
            context['state'] = 'browsing'
            context['city'] = None
            return f"🎉 <b>İşlem Başarılı!</b><br>{context.get('proposed_hotel_name')} için rezervasyonunuz tamamlandı." if lang == 'tr' else "🎉 <b>Success!</b> Booking completed."

        elif any(w in text for w in no_words):
            context['state'] = 'browsing'
            return "İşlemi iptal ettim. Nereye bakalım?" if lang == 'tr' else "Canceled. Where else?"
        return "Lütfen 'Evet' veya 'Hayır' yazın." if lang == 'tr' else "Please say 'Yes' or 'No'."

    def respond(self, msg, lang, user, context):
        text = re.sub(r'[^\w\s]', ' ', msg.lower())

        # 1. Booking Confirmation State
        if context.get('state') == 'offering_booking':
            reply = self.process_booking_confirmation(text, lang, context, user)
            return reply, context

        # 2. Extract Intent and Entities
        city = self.extract_city(text)
        if city: context['city'] = city

        detected_intents = [k for k, v in self.get_intents(lang).items() if any(kw in text for kw in v)]
        for i in detected_intents:
            if i not in context['intents']: context['intents'].append(i)

        # 3. Handle Direct Commands (Auth / Bookings)
        if "auth" in detected_intents:
            return "<a href='/login' class='btn btn-warning w-100 fw-bold'>Giriş Yap / Üye Ol</a>" if lang == 'tr' else "<a href='/login' class='btn btn-warning w-100'>Login / Register</a>", context
        
        if "my_bookings" in detected_intents:
            if not user.is_authenticated: return "Lütfen Giriş Yapın." if lang == 'tr' else "Please Login.", context
            bookings = list(self.db.bookings.find({"email": user.email}))
            if not bookings: return "Aktif rezervasyonunuz yok." if lang == 'tr' else "No active bookings.", context
            b = bookings[-1]
            return f"En son rezervasyonunuz: <b>{b['check_in']}</b> - <b>{b['check_out']}</b>." if lang == 'tr' else f"Latest booking: <b>{b['check_in']}</b> - <b>{b['check_out']}</b>.", context

        # 4. State Machine: Offer a Hotel if City is known
        if context['city']:
            hotel_count = self.db.hotels.count_documents({"city": context['city']})
            if hotel_count == 0:
                bad_city = context['city']
                context['city'] = None
                return f"Maalesef {bad_city} bölgesinde otel kalmamış." if lang == 'tr' else f"No hotels in {bad_city}.", context

            if not context['intents']:
                return f"{context['city']} şehrinde {hotel_count} otelimiz var. Konseptiniz nedir? (Lüks, Ucuz vs.)" if lang == 'tr' else f"We have {hotel_count} hotels in {context['city']}. What concept?", context
            else:
                city_hotels = list(self.db.hotels.find({"city": context['city']}, {"_id": 1}))
                cheapest_room = self.db.rooms.find_one({"hotel_id": {"$in": [h['_id'] for h in city_hotels]}}, sort=[("price", 1)])
                
                if cheapest_room:
                    hotel = self.db.hotels.find_one({"_id": cheapest_room['hotel_id']})
                    context['proposed_room_id'] = str(cheapest_room['_id'])
                    context['proposed_hotel_name'] = hotel['name']
                    context['proposed_price'] = cheapest_room['price'] * 3
                    context['state'] = 'offering_booking'
                    return f"Mükemmel! {hotel['name']} otelini buldum. Fiyat: {context['proposed_price']} TL. Hemen hızlı rezervasyon yapayım mı? (Evet/Hayır)" if lang == 'tr' else f"Found {hotel['name']}. Confirm booking? (Yes/No)", context
                else:
                    context['state'] = 'browsing'
                    context['city'] = None
                    return f"{context['city']} bölgesinde size uygun {hotel_count} otel buldum. Butona tıklayın." if lang == 'tr' else "Found hotels for you.", context

        # 5. Fallback & Chit-Chat
        chitchat = next((v for k, v in self.get_chitchat(lang).items() if k in text), None)
        if chitchat: return chitchat, context

        if context['intents']:
            return "Harika! Peki hangi bölgeye veya şehre gitmek istersiniz?" if lang == 'tr' else "Great! Which city?", context

        greet_words = ["merhaba", "selam", "hey", "iyi"] if lang == 'tr' else ["hello", "hi", "hey"]
        if any(w in text for w in greet_words):
            return "Merhaba! Tatil hayalinizi gerçekleştirmek için buradayım. Nereye gitmek istersiniz?" if lang == 'tr' else "Hello! Where to?", context

        return "Söylediğinizi anlayamadım. Sadece tatil ve şehir terimlerini algılayabiliyorum." if lang == 'tr' else "I only understand travel and city terms.", context

# Initialize Bot
bot_manager = HolidayBotManager(db)

@app.route('/api/v1/chat', methods=['POST'])
def api_chat():
    lang = request.cookies.get('lang', 'tr')
    msg = request.get_json().get('message', '').lower()
    
    reset_words = ["baştan", "iptal", "sıfırla"] if lang == 'tr' else ["reset", "cancel", "clear"]
    if any(w in msg for w in reset_words):
        session['chat_context'] = {"city": None, "intents": [], "state": "browsing"}
        return jsonify({"reply": "Sıfırladım. Nereye gitmek istersiniz?" if lang == 'tr' else "Reset. Where to?"})
        
    if 'chat_context' not in session:
        session['chat_context'] = {"city": None, "intents": [], "state": "browsing"}
        
    context = session['chat_context']
    if 'state' not in context: context['state'] = "browsing"

    # OOP Bot'a yönlendiriyoruz (Bütün çöp kod buradan temizlendi!)
    reply_text, updated_context = bot_manager.respond(msg, lang, current_user, context)
    
    session['chat_context'] = updated_context
    session.modified = True
    return jsonify({"reply": reply_text})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)