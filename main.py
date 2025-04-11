
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import dateparser
import requests
import os

app = Flask(__name__)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route("/", methods=["POST"])
def agendar():
    data = request.json
    comando = data.get("comando", "")
    
    if not comando:
        return jsonify({"erro": "Campo 'comando' não enviado."}), 400

    hora = dateparser.parse(comando, settings={"PREFER_DATES_FROM": "future"})
    if not hora:
        return jsonify({"erro": "Data/hora não reconhecida no comando."}), 400

    titulo = comando.split("agenda", 1)[1].split("para")[0].strip().capitalize() if "agenda" in comando.lower() else "Compromisso"

    duracao = 30
    if "por" in comando.lower() and "min" in comando.lower():
        try:
            parte = comando.lower().split("por")[1]
            duracao = int(''.join(filter(str.isdigit, parte)))
        except:
            pass

    local = ""
    if "local:" in comando.lower():
        local = comando.lower().split("local:")[1].split("descrição:")[0].strip().capitalize()

    descricao = ""
    if "descrição:" in comando.lower():
        descricao = comando.lower().split("descrição:")[1].strip().capitalize()

    inicio = hora
    fim = inicio + timedelta(minutes=duracao)

    payload = {
        "summary": titulo,
        "start_time": inicio.isoformat(),
        "end_time": fim.isoformat(),
        "description": descricao,
        "location": local
    }

    resposta = requests.post(WEBHOOK_URL, json=payload)

    if resposta.status_code == 200:
        return jsonify({
            "status": "ok",
            "mensagem": "Evento enviado com sucesso.",
            "titulo": titulo,
            "inicio": inicio.strftime('%d/%m %H:%M'),
            "duracao_min": duracao
        })
    else:
        return jsonify({"status": "erro", "mensagem": resposta.text}), 500

@app.route('/')
def home():
    return "Deco online!"

@app.route('/gmail/last', methods=['GET'])
def get_last_email():
    return jsonify({
        "from": "cojepemec.secretaria@tjsc.jus.br",
        "subject": "Pauta Concentrada - Atualização de Disponibilidades",
        "received": "11.04.2025 09h44",
        "summary": "Mediadores enviaram novas disponibilidades, já atualizadas na planilha."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

