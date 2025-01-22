from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
import json

app = Flask(__name__)
CORS(app)

TENDER_TYPES = [
    "Zamówienie udzielane jest w trybie podstawowym na podstawie: art. 275 pkt 1 ustawy",
    "Zamówienie udzielane jest w trybie przetargu nieograniczonego na podstawie: art. 132 ustawy",
    "Zamówienie udzielane jest w trybie przetargu ograniczonego na podstawie: art. 140 ustawy",
    "Zamówienie udzielane jest w trybie negocjacji z ogłoszeniem na podstawie: art. 153 pkt 5 ustawy",
    "Zamówienie udzielane jest w trybie dialogu konkurencyjnego na podstawie: art. 169 ustawy w zw. z art. 153 pkt 2 ustawy",
    "Zamówienie udzielane jest w trybie partnerstwa innowacyjnego na podstawie: art. 189 ustawy"
]

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/notices')
def get_notices():
    base_url = "http://ezamowienia.gov.pl/mo-board/api/v1/notice"
    try:
        params = {
            # "PageSize": 20,
            # "PageNumber": request.args.get('page', 1, type=int),
            "TenderType": request.args.get('tenderType'),
            # "PublicationDateFrom": request.args.get('dateFrom'),
            # "PublicationDateTo": request.args.get('dateTo')
        }
        
        response = requests.get(base_url, params=params)
        response_text = response.text
        
        # Check if response is XML
        if response_text.startswith('<?xml'):
            root = ET.fromstring(response_text)
            items = []
            for item in root.findall('.//SearchTenderReportModel'):
                tender = {}
                for child in item:
                    tender[child.tag] = child.text
                items.append(tender)
            return jsonify({"items": items})
        else:
            return jsonify({"items": []})
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400
    except ET.ParseError as e:
        return jsonify({"error": f"XML parsing error: {str(e)}"}), 400

@app.route('/api/tender-types')
def get_tender_types():
    return jsonify(TENDER_TYPES)

if __name__ == '__main__':
    app.run(debug=True)
