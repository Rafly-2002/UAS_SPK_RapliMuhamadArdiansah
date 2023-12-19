from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import Smartphone as SmartphoneModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'nama_handphone':3, 'kamera': 5, 'baterai':3,'ram': 4, 
                           'memori': 5, 'harga': 4}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(SmartphoneModel.no, SmartphoneModel.nama_handphone, SmartphoneModel.kamera, SmartphoneModel.baterai,
                       SmartphoneModel.ram, SmartphoneModel.memori, SmartphoneModel.harga)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no': Smartphone.no,'nama_handphone': Smartphone.nama_handphone, 'kamera': Smartphone.kamera,
                'baterai': Smartphone.baterai, 'ram': Smartphone.ram, 'memori': Smartphone.memori, 'harga': Smartphone.harga} for Smartphone in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        nama_handphone_values = [] #max
        kamera_values = [] # max
        baterai_values = []  # max
        ram_values = []  # max
        memori_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # Nama_handphone
            nama_handphone_spec = data['nama_handphone']
            numeric_values = [int(value.split()[0]) for value in nama_handphone_spec.split(
                ',') if value.split()[0].isdigit()]
            max_nama_handphone_value = max(numeric_values) if numeric_values else 1
            nama_handphone_values.append(max_nama_handphone_value)

            # Kamera
            kamera_spec = data['kamera']
            kamera_numeric_values = [int(
                value.split()[0]) for value in kamera_spec.split() if value.split()[0].isdigit()]
            max_kamera_value = max(
                kamera_numeric_values) if kamera_numeric_values else 1
            kamera_values.append(max_kamera_value)

            # Baterai
            baterai_spec = data['baterai']
            baterai_numeric_values = [int(
                value.split()[0]) for value in baterai_spec.split() if value.split()[0].isdigit()]
            max_baterai_value = max(
                baterai_numeric_values) if baterai_numeric_values else 1
            baterai_values.append(max_baterai_value)

            # Ram
            ram_spec = data['ram']
            ram_numeric_values = [float(value.split()[0]) for value in ram_spec.split(
            ) if value.replace('.', '').isdigit()]
            max_ram_value = max(
                ram_numeric_values) if ram_numeric_values else 1
            ram_values.append(max_ram_value)

            # Memori
            memori_spec = data['memori']
            memori_numeric_values = [
                int(value) for value in memori_spec.split() if value.isdigit()]
            max_memori_value = max(
                memori_numeric_values) if memori_numeric_values else 1
            memori_values.append(max_memori_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in str(data['harga']) if char.isdigit())
            harga_values.append(float(harga_cleaned) if harga_cleaned else 0)  # Convert to float

        return [
    {
        'no': data['no'],
        'nama_handphone': nama_handphone_value / max(nama_handphone_values),
        'kamera': kamera_value / max(kamera_values),
        'baterai': baterai_value / max(baterai_values),
        'ram': ram_value / max(ram_values),
        'memori': memori_value / max(memori_values),
        'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0,
        
    }
    for data, nama_handphone_value, kamera_value, ram_value, memori_value, baterai_value, harga_value
    in zip(self.data, nama_handphone_values, kamera_values, ram_values, memori_values, harga_values, baterai_values)
]


    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['nama_handphone']**self.weight['nama_handphone'] *
                row['kamera']**self.weight['kamera'] *
                row['ram']**self.weight['ram'] *
                row['memori']**self.weight['memori'] *
                row['baterai']**self.weight['baterai'] *
                row['harga']**self.weight['harga'],
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['no'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'handphone': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['no'],
                'Score': round(row['nama_handphone'] * weight['nama_handphone'] +
                               row['kamera'] * weight['kamera'] +
                               row['ram'] * weight['ram'] +
                               row['memori'] * weight['memori'] +
                               row['baterai'] * weight['baterai'] +
                               row['harga'] * weight['harga'], 2)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'handphone': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class Smartphone(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(SmartphoneModel).order_by(SmartphoneModel.no)
        result_set = query.all()
        data = [{'no': row.no, 'nama_handphone': row.nama_handphone, 'kamera': row.kamera,
                 'ram': row.ram, 'baterai': row.baterai, 'memori': row.memori, 'harga': row.harga }
                for row in result_set]
        return self.get_paginated_result('handphone/', data, request.args), 200


api.add_resource(Smartphone, '/handphone')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)