# GraphLab — Mini Desmos dengan Python + HTML + CSS

Website grafik fungsi 2D yang dibuat tanpa JavaScript.

## Teknologi

- Python
- Flask
- SymPy — membaca dan menghitung persamaan
- NumPy — membuat titik-titik grafik
- Matplotlib — menggambar grafik
- HTML
- CSS

## Fitur

- Hingga 5 fungsi dalam satu grafik
- `y = x^2`
- `y = sin(x)`
- `y = 2*x + 5`
- `y = sqrt(x)`
- `y = log(x)`
- Trigonometri
- Grid koordinat
- Sumbu X dan Y
- Legend fungsi
- Pengaturan X minimum/maksimum
- Pengaturan Y minimum/maksimum
- Tampilan dark mode
- Responsive untuk layar kecil
- Grafik dikirim sebagai SVG dari Python

## Cara menjalankan

Buka terminal VS Code di folder project:

```bash
pip install -r requirements.txt
python app.py
```

Kemudian buka:

http://127.0.0.1:5000

## Catatan

Karena proyek sengaja tidak menggunakan JavaScript, interaksi seperti drag/zoom real-time ala Desmos belum tersedia. Perubahan grafik dilakukan setelah tombol "Gambar Grafik" ditekan.

Versi ini cocok sebagai fondasi untuk dikembangkan menjadi graphing calculator yang lebih lengkap.
