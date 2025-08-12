from flask import Flask, jsonify, request, url_for, make_response
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed
from threading import Lock

app = Flask(__name__)

_livros = [
    {"id": 1, "titulo": "O senhor dos anéis - A Sociedade do Anel",
        "autor": "J.R.R. Tolkien"},
    {"id": 2, "titulo": "Percy Jackson - O ladrão de Raios", "autor": "Rick Riordan"},
    {"id": 3, "titulo": "Harry Potter - A pedra filosofal", "autor": "J.K. Rowling"},
]
_lock = Lock()


def _json_error(message, code):
    return jsonify({"error": {"code": code, "message": message}}), code


@app.errorhandler(BadRequest)
def handle_400(e):
    return _json_error(str(e.description or "Requisição inválida"), 400)


@app.errorhandler(NotFound)
def handle_404(e):
    return _json_error("Recurso não encontrado", 404)


@app.errorhandler(MethodNotAllowed)
def handle_405(e):
    return _json_error("Método não permitido", 405)


def _require_json():
    if not request.is_json:
        raise BadRequest("Content-Type deve ser application/json")
    try:
        return request.get_json()
    except Exception:
        raise BadRequest("JSON inválido")


def _next_id():
    with _lock:
        return (max((l["id"] for l in _livros), default=0) + 1)


@app.get("/livros")
def listar_livros():
    # filtros simples
    autor = request.args.get("autor")
    titulo = request.args.get("titulo")
    data = _livros
    if autor:
        data = [l for l in data if autor.lower() in l["autor"].lower()]
    if titulo:
        data = [l for l in data if titulo.lower() in l["titulo"].lower()]
    return jsonify(data), 200


@app.get("/livros/<int:id>")
def obter_livro(id: int):
    for l in _livros:
        if l["id"] == id:
            return jsonify(l), 200
    raise NotFound()


@app.post("/livros")
def criar_livro():
    body = _require_json()
    titulo = body.get("titulo")
    autor = body.get("autor")
    if not titulo or not autor:
        raise BadRequest("Campos obrigatórios: titulo, autor")
    novo = {"id": _next_id(), "titulo": titulo, "autor": autor}
    with _lock:
        _livros.append(novo)
    resp = make_response(jsonify(novo), 201)
    resp.headers["Location"] = url_for(
        "obter_livro", id=novo["id"], _external=False)
    return resp


@app.put("/livros/<int:id>")
def substituir_livro(id: int):
    body = _require_json()
    # PUT: substituição (exige todos os campos)
    titulo = body.get("titulo")
    autor = body.get("autor")
    if not titulo or not autor:
        raise BadRequest("PUT exige os campos: titulo, autor")
    with _lock:
        for i, l in enumerate(_livros):
            if l["id"] == id:
                _livros[i] = {"id": id, "titulo": titulo, "autor": autor}
                return jsonify(_livros[i]), 200
    raise NotFound()


@app.patch("/livros/<int:id>")
def atualizar_parcial(id: int):
    body = _require_json()
    if "id" in body:
        raise BadRequest("Campo 'id' não pode ser alterado")
    with _lock:
        for i, l in enumerate(_livros):
            if l["id"] == id:
                _livros[i] = {
                    **l, **{k: v for k, v in body.items() if k in ("titulo", "autor")}}
                return jsonify(_livros[i]), 200
    raise NotFound()


@app.delete("/livros/<int:id>")
def excluir_livro(id: int):
    with _lock:
        for i, l in enumerate(_livros):
            if l["id"] == id:
                del _livros[i]
                return "", 204
    raise NotFound()


if __name__ == "__main__":
    # Para dev; em produção use um WSGI (gunicorn/uwsgi) e 0.0.0.0 se for docker
    app.run(host="127.0.0.1", port=5000, debug=True)
