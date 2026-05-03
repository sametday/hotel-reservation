import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['otel_db']

def generate_fake_data():
    print("Mevcut veriler temizleniyor...")
    db.hotels.delete_many({})
    db.rooms.delete_many({})
    
    locations = list(db.locations.find())
    if not locations:
        print("Hata: db.locations boş. Önce konum_ekle.py çalıştırılmalı.")
        return

    # Çok daha kaliteli ve lüks görseller
    premium_images = [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
        "https://images.unsplash.com/photo-1551882547-ff40c0d12c56?w=800&q=80",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",
        "https://images.unsplash.com/photo-1542314831-c6a4d27eceb0?w=800&q=80",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&q=80"
    ]

    # Gerçekçi sahte isim şablonları
    chain_brands = [
        "Hilton Garden Inn {district}",
        "Ramada Plaza by Wyndham {city}",
        "Anemon {city} Hotel",
        "Divan {district}",
        "Dedeman {city}",
        "DoubleTree by Hilton {city}",
        "Novotel {district}",
        "Ibis {city}",
        "Park Inn by Radisson {city}",
        "Grand {district} Resort & Spa",
        "Royal {city} Palace",
        "Premium {district} Suites",
        "The {city} Edition"
    ]

    print("[*] 81 il geneline rastgele 2000 adet GERÇEKÇİ lüks otel dağıtılıyor...")
    
    for _ in range(2000):
        loc = random.choice(locations)
        city = loc['city']
        district = random.choice(loc['districts']) if loc['districts'] else "Merkez"
        
        hotel_name = random.choice(chain_brands).format(city=city, district=district)
        stars = random.randint(3, 5)
        
        hotel_doc = {
            "name": hotel_name,
            "city": city,
            "district": district,
            "stars": stars,
            "description": f"{city} şehrinin göz bebeği {district} ilçesinde, konforlu ve unutulmaz bir konaklama deneyimi sizi bekliyor.",
            "image_url": random.choice(premium_images)
        }
        inserted_hotel = db.hotels.insert_one(hotel_doc)
        
        room_types = [
            ("Standart Oda", 1500, 2500), 
            ("Deluxe Oda", 3000, 5000), 
            ("Aile Süiti", 5500, 8000),
            ("Kral Dairesi", 10000, 25000)
        ]
        
        for i in range(random.randint(2, 5)):
            rtype, min_price, max_price = random.choice(room_types)
            room_doc = {
                "hotel_id": inserted_hotel.inserted_id,
                "room_number": f"{random.randint(1,9)}0{random.randint(1,9)}",
                "room_type": rtype,
                "price": random.randint(min_price, max_price),
                "is_available": True
            }
            db.rooms.insert_one(room_doc)
            
    print("[+] BAŞARILI! Toplam 2000 adet çok kaliteli sahte otel veritabanına eklendi.")

if __name__ == "__main__":
    generate_fake_data()
