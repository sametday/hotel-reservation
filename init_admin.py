from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['otel_db']

def create_admin():
    email = input("Admin Email: ").strip().lower()
    password = input("Admin Şifre: ")
    name = input("Admin İsim: ")

    if db.users.find_one({"email": email}):
        print("Hata: Bu e-posta ile kayıtlı bir kullanıcı zaten var!")
        return

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    admin_user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "is_admin": True  # En kritik kısım!
    }

    db.users.insert_one(admin_user)
    print(f"Başarılı! {email} adresiyle admin yetkili kullanıcı oluşturuldu.")

if __name__ == "__main__":
    create_admin()
