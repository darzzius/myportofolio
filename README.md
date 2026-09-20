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

### Tugas 3
1. Alasan Menggunakan ModelForm:
- ModelForm secara otomatis memetakan field input form berdasarkan definisi kolom yang sudah ada di models.py. Jadi tidak diperlukan menulis tag <input>, tipe data, dan atributnya satu per satu di HTML.

- Validasi tipe data, panjang string (max_length), nilai unik (unique=True), hingga status required langsung diturunkan dari model. form.is_valid() dipanggil, otomatis memeriksa integritas data dan membersihkan input.

- Data yang lolos validasi dapat langsung disimpan ke database tanpa perlu mengekstrak request.POST.get('field') secara manual satu per satu.

- Django otomatis mengaitkan pesan kesalahan ke field yang bermasalah jika pengisian form tidak valid, sehingga mudah ditampilkan kembali kepada pengguna di halaman web.

Tag {% csrf_token %} berfungsi melindungi aplikasi dari serangan CSRF.
CSRF adalah serangan ketika situs jahat pihak ketiga memanfaatkan sesi autentikasi/cookie pengguna yang masih aktif untuk mengeksekusi permintaan HTTP (seperti POST untuk menghapus atau mengubah data) tanpa izin sadar dari pengguna. Django menyematkan token acak rahasia yang unik pada form. Saat form dikirimkan lewat metode POST, middleware Django mencocokkan token di payload dengan token pada sesi browser. Jika token tidak cocok atau absen, Django langsung memblokir permintaan tersebut dengan status 403 Forbidden.

2.  XML menggunakan tag  berulang seperti (<title>Judul</title>), sedangkan JSON memakai format key-value ({"title": "Judul"}). Payload JSON jauh lebih kecil, sehingga transmisi data melalui jaringan berlangsung lebih cepat.

JSON kompatibel langsung dengan ekosistem browser. Data JSON dapat diparsing langsung menjadi objek JavaScript menggunakan JSON.parse(), sedangkan XML membutuhkan DOMParser yang memakan lebih banyak memori dan proses komputasi.

JSON mendukung tipe data standar secara langsung (string, number, boolean, array, object, dan null). Pada XML, semua nilai pada dasarnya dianggap sebagai teks (string), sehingga developer harus mengonversi tipe datanya secara manual di sisi frontend.

Bahasa pemrograman modern dan framework frontend dirancang untuk mengonsumsi data berstruktur JSON.

3. - HTTP Request 
  Klien mengirimkan permintaan GET ke endpoint URL tertentu (misalnya /experience/json/).

- Routing 
Django membaca URL yang masuk dan memanggil fungsi view yang sesuai (misalnya show_experience_json).

- Pengambilan Data
View mengeksekusi query database menggunakan Django ORM, menghasilkan kumpulan objek berupa QuerySet.

- Serialization
QuerySet tersebut dimasukkan ke modul serializer Django untuk dikonversi menjadi representasi teks JSON

- HTTP Response
Data string JSON tersebut dibungkus ke dalam HttpResponse dengan header content_type="application/json", lalu dikirimkan kembali ke klien sebagai respons HTTP 200 OK.