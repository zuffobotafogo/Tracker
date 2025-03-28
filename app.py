from flask import Flask, render_template, jsonify
from dashboard import create_dashboard
import requests
import pandas as pd
import pdfkit

app = Flask(__name__)

# Criar dashboard
app = create_dashboard(app)

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para buscar informações de um voo específico
@app.route('/flight_info/<icao24>')
def flight_info(icao24):
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    data = response.json()

    for flight in data["states"]:
        if flight[0] == icao24:
            return jsonify({
                "Aeronave": flight[1],
                "País": flight[2],
                "Latitude": flight[6],
                "Longitude": flight[5],
                "Altitude": flight[7]
            })

    return jsonify({"Erro": "Voo não encontrado"}), 404

# Rota para gerar um relatório em PDF
@app.route('/generate_report')
def generate_report():
    df = pd.read_json("data/flight_history.json")  # Simulação de histórico de voos
    report_html = df.to_html()

    pdfkit.from_string(report_html, "reports/generated_report.pdf")
    return "Relatório gerado com sucesso!", 200

if __name__ == '__main__':
    app.run(debug=True)
