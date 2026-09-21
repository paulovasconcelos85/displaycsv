import os
from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # limite de 5 MB por upload


def ler_csv(stream):
    """Tenta UTF-8 (com ou sem BOM do Excel) e cai para Latin-1.
    sep=None detecta automaticamente ';' ou ','."""
    for enc in ("utf-8-sig", "latin-1"):
        try:
            stream.seek(0)
            return pd.read_csv(stream, sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Não foi possível decodificar o arquivo.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/display", methods=["POST"])
def display_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template("index.html", erro="Selecione um arquivo CSV."), 400
    try:
        df = ler_csv(file.stream)
    except Exception as e:
        return render_template("index.html", erro=f"Erro ao ler o CSV: {e}"), 400

    tabela = df.to_html(classes="data", index=False, na_rep="")
    return render_template("display.html", tabela=tabela)


@app.errorhandler(413)
def arquivo_grande(_):
    return render_template("index.html", erro="Arquivo maior que 5 MB."), 413


if __name__ == "__main__":
    # Só roda localmente. No Azure, quem sobe a app é o gunicorn.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")