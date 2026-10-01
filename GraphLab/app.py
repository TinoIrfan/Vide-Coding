from flask import Flask, render_template, request
import numpy as np
import sympy as sp

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

app = Flask(__name__)


# =========================================================
# SYMBOL
# =========================================================

x, y = sp.symbols("x y")


# =========================================================
# FUNGSI MATEMATIKA YANG DIDUKUNG
# =========================================================

ALLOWED_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "cot": sp.cot,
    "sec": sp.sec,
    "csc": sp.csc,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "abs": sp.Abs,
    "pi": sp.pi,
    "e": sp.E,
}


TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)


# =========================================================
# PARSE EKSPRESI
# =========================================================

def parse_expression(expression):

    expression = expression.strip()

    if not expression:
        raise ValueError("Persamaan tidak boleh kosong.")

    # Mendukung:
    # y = x^2
    # f(x) = x^2
    # x^2 + 2x + 1

    if "=" in expression:

        left, right = expression.split("=", 1)

        left = left.strip().lower()

        if left in ["y", "f(x)", "f"]:

            expression = right.strip()

        else:

            expression = right.strip()

    try:

        expr = parse_expr(
            expression,

            local_dict={
                "x": x,
                "y": y,
                **ALLOWED_FUNCTIONS
            },

            transformations=TRANSFORMATIONS,

            evaluate=True
        )

        return expr

    except Exception as e:

        raise ValueError(
            f"Persamaan tidak valid: {expression}"
        ) from e


# =========================================================
# HITUNG DATA GRAFIK 2D
# =========================================================

def calculate_2d(expression, x_min, x_max):

    expr = parse_expression(expression)

    X = np.linspace(
        x_min,
        x_max,
        1000
    )

    function = sp.lambdify(
        x,
        expr,
        modules=["numpy"]
    )

    Y = function(X)

    Y = np.asarray(
        Y,
        dtype=float
    )

    Y = np.where(
        np.isfinite(Y),
        Y,
        np.nan
    )

    Y = np.where(
        np.abs(Y) < 1e8,
        Y,
        np.nan
    )

    return {
        "x": X.tolist(),
        "y": Y.tolist(),
        "name": expression
    }


# =========================================================
# HITUNG DATA GRAFIK 3D
# =========================================================

def calculate_3d(expression, x_min, x_max, y_min, y_max):

    expr = parse_expression(expression)

    resolution = 100

    X = np.linspace(
        x_min,
        x_max,
        resolution
    )

    Y = np.linspace(
        y_min,
        y_max,
        resolution
    )

    X, Y = np.meshgrid(
        X,
        Y
    )

    function = sp.lambdify(
        (x, y),
        expr,
        modules=["numpy"]
    )

    Z = function(
        X,
        Y
    )

    Z = np.asarray(
        Z,
        dtype=float
    )

    Z = np.where(
        np.isfinite(Z),
        Z,
        np.nan
    )

    Z = np.where(
        np.abs(Z) < 1e8,
        Z,
        np.nan
    )

    return {
        "x": X[0].tolist(),
        "y": Y[:, 0].tolist(),
        "z": Z.tolist(),
        "name": expression
    }


# =========================================================
# HALAMAN UTAMA
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# GRAFIK 2D
# =========================================================

@app.route(
    "/2d",
    methods=["GET", "POST"]
)
def graph2d():

    expression = ""

    x_min = -10
    x_max = 10

    graph = None

    error = None

    if request.method == "POST":

        expression = request.form.get(
            "expression",
            ""
        )

        try:

            x_min = float(
                request.form.get(
                    "x_min",
                    -10
                )
            )

            x_max = float(
                request.form.get(
                    "x_max",
                    10
                )
            )

            if x_min >= x_max:

                raise ValueError(
                    "X minimum harus lebih kecil dari X maksimum."
                )

            graph = calculate_2d(
                expression,
                x_min,
                x_max
            )

        except Exception as e:

            error = str(e)

    return render_template(
        "graph2d.html",

        expression=expression,

        x_min=x_min,
        x_max=x_max,

        graph=graph,

        error=error
    )


# =========================================================
# GRAFIK 3D
# =========================================================

@app.route(
    "/3d",
    methods=["GET", "POST"]
)
def graph3d():

    expressions = [
        "",
        "",
        "",
        "",
        ""
    ]

    x_min = -10
    x_max = 10

    y_min = -10
    y_max = 10

    z_min = -10
    z_max = 10

    surfaces = []

    errors = []

    if request.method == "POST":

        try:

            x_min = float(
                request.form.get(
                    "x_min",
                    -10
                )
            )

            x_max = float(
                request.form.get(
                    "x_max",
                    10
                )
            )

            y_min = float(
                request.form.get(
                    "y_min",
                    -10
                )
            )

            y_max = float(
                request.form.get(
                    "y_max",
                    10
                )
            )

            z_min = float(
                request.form.get(
                    "z_min",
                    -10
                )
            )

            z_max = float(
                request.form.get(
                    "z_max",
                    10
                )
            )

            if x_min >= x_max:

                raise ValueError(
                    "X minimum harus lebih kecil dari X maksimum."
                )

            if y_min >= y_max:

                raise ValueError(
                    "Y minimum harus lebih kecil dari Y maksimum."
                )

            if z_min >= z_max:

                raise ValueError(
                    "Z minimum harus lebih kecil dari Z maksimum."
                )

        except Exception as e:

            errors.append(
                str(e)
            )

        for i in range(1, 6):

            expression = request.form.get(
                f"function_{i}",
                ""
            ).strip()

            expressions[i - 1] = expression

            if not expression:
                continue

            try:

                surface = calculate_3d(
                    expression,
                    x_min,
                    x_max,
                    y_min,
                    y_max
                )

                surfaces.append(
                    surface
                )

            except Exception as e:

                errors.append(
                    str(e)
                )

    return render_template(
        "graph3d.html",

        expressions=expressions,

        surfaces=surfaces,

        errors=errors,

        x_min=x_min,
        x_max=x_max,

        y_min=y_min,
        y_max=y_max,

        z_min=z_min,
        z_max=z_max
    )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )