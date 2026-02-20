from flask import Flask, jsonify, request

app = Flask(__name__)

livros = [
    {
        
        "id": 1,
        "titulo": 'O senhor dos anéis - A Sociedade do Anel',
        'autor': 'J.R.R. Tolkien'
    },
    {
        
        'id': 2,
        'titulo': 'Percy Jackson - O ladrão de Raios',
        'autor': 'Rick Riordan'
    },
    {
        
        'id': 3,
        'titulo':  'Harry Potter - A pedra filosofal',
        'autor': 'J.K. Rowling'
    },
]

# Consultar todos


@app.route('/livros', methods=['GET'])
def obter_livros():
    return jsonify(livros)

# Consultar por ID


@app.route("/livros/<int:id>", methods=['GET'])
def obter_livro_por_id(id):
    for livro in livros:
        if livro.get('id') == id:
            return jsonify(livro)
    return jsonify({"erro": "Livro não encontrado"}), 404

# Editar por ID


@app.route('/livros/<int:id>', methods=['PUT'])
def editar_livro_por_id(id):
    livro_alterado = request.get_json()
    for indice, livro in enumerate(livros):
        if livro.get('id') == id:
            livros[indice].update(livro_alterado)
            return jsonify(livros[indice])
    return jsonify({"erro": "Livro não encontrado"}), 404

# Criar novo livro


@app.route('/livros', methods=['POST'])
def incluir_novo_livro():
    novo_livro = request.get_json()
    livros.append(novo_livro)
    return jsonify(livros), 201

# Excluir livro


@app.route('/livros/<int:id>', methods=["DELETE"])
def excluir_livros(id):
    for indice, livro in enumerate(livros):
        if livro.get('id') == id:
            del livros[indice]
            return jsonify(livros)
    return jsonify({"erro": "Livro não encontrado"}), 404


if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
