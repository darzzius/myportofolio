Name : Rafael Darius Sagala

NPM : 2506584275

Class : PBP A

Keterangan : Ganteng

Tidak menggunakan AI
### Tugas 1

1.Pada Tutorial dan Tugas 1, ya saya mengguanakan <section>, elemen tersebut membantu saya dalam memisahkan 
bagian-bagian di portofolio saya

2. iya benar, terutama pada bagian pengalaman, saya harus menghabiskan banyak waktu untuk berfikir karena terganti terus menerus untuk membuat kotak yang baru karena tidak sesuai dengan ekspektasi saya jika diubah kedalam view mobilephone. saya juga menghabiskan waktu sangat banyak untuk mengedit bagian gelombang menyerupai gurun karena hal tersebut adalah ekspektasi saya pada awalnya

3. Saya merasa terbatas karena kekurangan saya yaitu kurang fokus, sehingga banyak sekali redudasi. saya juga merasa untuk ngecek apakah hasilnya sesuai atau tidak sesuai sedikit 'ribet' karena harus secara manual. 

### Tugas 2

1. Alur dimulai ketika pengguna mengakses URL . Browser mengirimkan HTTP GET Request ke server Django.
urls.py berperan sebagai awal dari Django pertama kali memeriksa berkas konfigurasi URL utama proyek. Di sini, pola URL dicocokkan dan diteruskan ke aplikasi terkait menggunakan fungsi include() ( ke main.urls).

urls.py digunakan sebagai aplikasi berkas URL di dalam aplikasi mencocokkan rute spesifik yang diminta dengan fungsi view yang bertugas menanganinya (misalnya path('experience/', show_experience, name='show_experience')).

views.py bertindak sebagai pengendali logika (seperti controler). Jika halaman memerlukan data dinamis, view memanggil model melalui Django ORM (contoh: Experience.objects.all()).

models.py berinteraksi dengan database untuk mengambil atau memanipulasi data sesuai query yang diminta oleh view, kemudian mengembalikan objek data tersebut ke view.

templates/ berfungsi untuk membungkus data dari model ke dalam sebuah dictionary dan memanggil template HTML yang sesuai menggunakan fungsi render(). Django memproses tag/variabel (seperti perulangan {% for %}) dan menggabungkannya dengan struktur HTML.

HTTP Response, view menghasilkan objek HttpResponse berupa dokumen HTML utuh yang sudah dirender dan mengirimkannya kembali ke browser untuk ditampilkan kepada pengguna.

2. a. memudahkan dalam memisahkan tanggung jawab, dimana tamplate digunakan untuk tampilan(UI)
b. memudahkan dalam pemeliaraan
c. memudahkan dalam efisiensi, karena data yang disimpan di model bersifat dinamis
d. fleksibilitas, memudahkan fitur lanjutan di masa mendatang karena datanya terstruktur

3. makemigrations: Berfungsi untuk mendeteksi perubahan skema yang dilakukan pada berkas models.py dan menyusun berkas migrasi baru (file Python di dalam folder migrations/). Perintah ini bertindak mencatat histori perubahan, tetapi belum mengubah struktur database fisik.

migrate: Berfungsi untuk mengeksekusi berkas migrasi yang belum dijalankan ke database nyata (misalnya SQLite atau PostgreSQL). Perintah ini menerjemahkan ke dalam perintah SQL (seperti CREATE TABLE atau ALTER TABLE) dan memperbarui skema tabel secara permanen.
   Contoh Kasus:
     - Misalkan pada model Experience, saya ingin menambahkan atribut tanggal mulai kerja (start_date):
       class Experience(models.Model):
           start_date = models.DateField(null=True, blank=True)
       
     - Setelah menambahkan field tersebut di models.py:
       1. Jalankan python manage.py makemigrations untuk membuat berkas migrasi baru (misalnya 0002_experience_start_date.py).
       2. Jalankan python manage.py migrate untuk menerapkan kolom baru start_date tersebut ke dalam tabel database.