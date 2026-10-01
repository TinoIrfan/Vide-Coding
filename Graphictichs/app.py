from flask import Flask, render_template, request
import io
import base64

import numpy as np
import sympy as sp

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)


app = Flask(__name__)


# ============================================================
# KONFIGURASI PARSER MATEMATIKA
# ============================================================

x = sp.Symbol("x")

TRANSFORMATIONS = (
    standard_transformations
    + (convert_xor,)
    + (implicit_multiplication_application,)
)

MATH_FUNCTIONS = {
    "x": x,

    # Trigonometri
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "cot": sp.cot,
    "sec": sp.sec,
    "csc": sp.csc,

    # Fungsi matematika
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "abs": sp.Abs,

    # Konstanta
    "pi": sp.pi,
    "e": sp.E,
}


# ============================================================
# MEMBACA PERSAMAAN
# ============================================================

def parse_function(function_text):
    """
    Mengubah input seperti:

        y = sin(x)
        y = x^2 + 2sin(x)

    menjadi ekspresi SymPy.
    """

    if not function_text:
        return None

    text = function_text.strip()

    if not text:
        return None

    # Hilangkan spasi
    text = text.replace(" ", "")

    # Jika pengguna menulis "y = ..."
    if "=" in text:
        left, right = text.split("=", 1)

        # Kita hanya mendukung bentuk y = ...
        if left.lower() in ["y", "f(x)", "f"]:
            text = right
        else:
            raise ValueError(
                "Gunakan format seperti: y = sin(x)"
            )

    if not text:
        raise ValueError("Persamaan kosong.")

    try:
        expression = parse_expr(
            text,
            local_dict=MATH_FUNCTIONS,
            transformations=TRANSFORMATIONS,
            evaluate=True
        )

        return expression

    except Exception:
        raise ValueError(
            f"Persamaan tidak dapat dibaca: {function_text}"
        )


# ============================================================
# MEMBUAT GRAFIK
# ============================================================

def create_graph(functions, xmin, xmax, ymin, ymax):

    # Pastikan range valid
    if xmin >= xmax:
        raise ValueError("X minimum harus lebih kecil dari X maksimum.")

    if ymin >= ymax:
        raise ValueError("Y minimum harus lebih kecil dari Y maksimum.")

    # Membuat titik x
    x_values = np.linspace(xmin, xmax, 2000)

    # Membuat figure
    fig, ax = plt.subplots(
        figsize=(10, 7),
        dpi=120
    )

    # Background
    fig.patch.set_facecolor("#080d1c")
    ax.set_facecolor("#080d1c")

    # ========================================================
    # GAMBAR SETIAP FUNGSI
    # ========================================================

    for index, function_text in enumerate(functions):

        if not function_text.strip():
            continue

        expression = parse_function(function_text)

        # Ubah ekspresi SymPy menjadi fungsi NumPy
        function = sp.lambdify(
            x,
            expression,
            modules=["numpy"]
        )

        try:
            y_values = function(x_values)

            # Pastikan hasil menjadi array NumPy
            y_values = np.asarray(y_values, dtype=float)

            # Tangani nilai tak valid
            y_values = np.where(
                np.isfinite(y_values),
                y_values,
                np.nan
            )

            # Gambar grafik
            ax.plot(
                x_values,
                y_values,
                linewidth=2.2,
                label=function_text
            )

        except Exception as error:
            raise ValueError(
                f"Fungsi '{function_text}' tidak dapat dihitung: {error}"
            )

    # ========================================================
    # SUMBU KOORDINAT
    # ========================================================

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # Grid
    ax.grid(
        True,
        linestyle="--",
        linewidth=0.6,
        alpha=0.25
    )

    # Sumbu X
    ax.axhline(
        0,
        linewidth=1,
        alpha=0.8
    )

    # Sumbu Y
    ax.axvline(
        0,
        linewidth=1,
        alpha=0.8
    )

    # Warna tulisan
    ax.tick_params(
        colors="#cbd5e1",
        labelsize=9
    )

    # Warna garis border
    for spine in ax.spines.values():
        spine.set_color("#27314a")

    # Label
    ax.set_xlabel(
        "x",
        color="#cbd5e1"
    )

    ax.set_ylabel(
        "y",
        color="#cbd5e1"
    )

    # Legend
    if any(f.strip() for f in functions):
        legend = ax.legend(
            loc="upper right",
            fontsize=9,
            framealpha=0.85
        )

        legend.get_frame().set_facecolor("#11182b")
        legend.get_frame().set_edgecolor("#27314a")

        for text in legend.get_texts():
            text.set_color("#e2e8f0")

    plt.tight_layout()

    # ========================================================
    # UBAH GRAFIK MENJADI SVG
    # ========================================================

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="svg",
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )

    plt.close(fig)

    buffer.seek(0)

    svg_data = buffer.getvalue().decode("utf-8")

    return svg_data


# ============================================================
# HALAMAN UTAMA
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():

    # Lima slot fungsi
    functions = [""] * 5

    # Nilai default range
    xmin = -10
    xmax = 10
    ymin = -10
    ymax = 10

    graph_svg = None
    error = None

    # ========================================================
    # JIKA TOMBOL "GAMBAR GRAFIK" DITEKAN
    # ========================================================

    if request.method == "POST":

        # Ambil semua fungsi dari HTML
        functions = request.form.getlist("function")

        # Pastikan selalu tersedia 5 slot
        while len(functions) < 5:
            functions.append("")

        # Ambil range
        try:
            xmin = float(
                request.form.get("xmin", "-10").replace(",", ".")
            )

            xmax = float(
                request.form.get("xmax", "10").replace(",", ".")
            )

            ymin = float(
                request.form.get("ymin", "-10").replace(",", ".")
            )

            ymax = float(
                request.form.get("ymax", "10").replace(",", ".")
            )

        except ValueError:
            error = "Nilai rentang grafik harus berupa angka."

        # ====================================================
        # BUAT GRAFIK
        # ====================================================

        if error is None:

            try:

                # Hanya fungsi yang diisi
                active_functions = [
                    f.strip()
                    for f in functions
                    if f.strip()
                ]

                if not active_functions:
                    error = "Masukkan minimal satu fungsi."

                else:
                    graph_svg = create_graph(
                        active_functions,
                        xmin,
                        xmax,
                        ymin,
                        ymax
                    )

            except Exception as e:
                error = str(e)

    # ========================================================
    # RENDER HTML
    # ========================================================

    return render_template(
        "index.html",
        functions=functions,
        xmin=xmin,
        xmax=xmax,
        ymin=ymin,
        ymax=ymax,
        graph_svg=graph_svg,
        error=error
    )


# ============================================================
# MENJALANKAN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )