# e-Maktab uslubidagi IT Savodxonlar to‘garagi jurnali

Flask + SQLAlchemy asosidagi o‘quv loyihasi. Rasmiy e-Maktab/Kundalik.com mahsuloti emas; faqat ko‘k-oq rangli maktab boshqaruv paneli uslubidan ilhomlangan.

## Lokal ishga tushirish (Windows)
1. Python 3.11 yoki yangiroq versiyasini o‘rnating.
2. Loyihani ochib, terminalda:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
3. Brauzerda `http://127.0.0.1:5000` manzilini oching. SQLite bazasi avtomatik yaratiladi.

## GitHub va Render
1. GitHub’da yangi repository yarating.
2. Ushbu papkadagi fayllarni repository’ga yuklang (`app.py`, `models.py`, `templates/`, `requirements.txt`, `Procfile`, `render.yaml` va boshqalar).
3. Render’da **New + → Blueprint** ni tanlab, GitHub repository’ni ulang. `render.yaml` web service va PostgreSQL yaratishni ta’riflaydi. Yoki qo‘lda Web Service va PostgreSQL yarating.
4. Blueprint usulida Render `DATABASE_URL` ni bazaning connection string qiymatiga bog‘laydi. Qo‘lda yaratishda Web Service → Environment ichida `DATABASE_URL` nomli variable yarating va PostgreSQL sahifasidagi **Internal Database URL** qiymatini kiriting (ikkalasi bir Render regionida bo‘lsin).
5. Build command: `pip install -r requirements.txt`; Start command: `gunicorn app:app`.
6. `SECRET_KEY` environment variable yarating (uzun tasodifiy qiymat) yoki Blueprint yaratgan qiymatdan foydalaning.
7. Deploy tugagach, Render bergan `https://...onrender.com` URL’ni oching.

## Muhim eslatmalar
- Render’ning bepul tariflari, PostgreSQL mavjudligi va limitlari vaqt o‘tishi bilan o‘zgarishi mumkin; yaratish paytida Render panelidagi joriy shartlarni tekshiring.
- SQLite lokalda, `DATABASE_URL` berilganda PostgreSQL ishlatiladi.
- Bu boshlang‘ich versiyada login/rol va CSRF himoyasi yo‘q. Internetga ochiq haqiqiy maktab ma’lumotlari uchun autentifikatsiya, rollar, CSRF himoyasi, zaxira nusxalari va maxfiylik siyosatini qo‘shing. Hozircha haqiqiy o‘quvchi ma’lumotlari o‘rniga test ma’lumotlaridan foydalaning.
- `db.create_all()` yangi jadvallarni yaratadi, lekin mavjud bazaning sxemasini migratsiya qilmaydi. Keyingi versiyalarda Flask-Migrate ishlatish tavsiya etiladi.
