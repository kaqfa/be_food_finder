## Backend Food Finder

Aplikasi backend untuk aplikasi pencarian makanan pada restoran yang tercantum pada aplikasi.

Cara menggunakan:

- Pastikan sudah terinstall docker dengan baik di komputer anda.
- Setelah clone, jalankan beberapa perintah di bawah ini:

```
docker-compose up -d
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py make_rsa
docker-compose exec -it django python manage.py createsuperuser
```

- Sekarang anda bisa masuk ke halaman admin dan menambahkan user beserta restorannya.

NB: 1 user hanya bisa menambahkan 1 restoran.