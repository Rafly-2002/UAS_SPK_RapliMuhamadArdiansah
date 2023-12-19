import sys
from colorama import Fore, Style
from models import Base, Smartphone
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(Smartphone)
    for phone in session.scalars(query):
        print(phone)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'kamera': 3, 'baterai': 4,
                            'ram': 4, 'memori': 5, 'harga': 5}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Smartphone.no, Smartphone.nama_handphone, Smartphone.kamera, Smartphone.baterai,
                       Smartphone.ram, Smartphone.memori, Smartphone.harga)
        result = session.execute(query).fetchall()
        return [{'no': phone.no, 'nama_handphone': phone.nama_handphone, 'kamera': phone.kamera, 'baterai': phone.baterai,
                 'ram': phone.ram, 'memori': phone.memori, 'harga': phone.harga} for phone in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        kamera_values = []  # max
        baterai_values = []  # max
        ram_values = []  # max
        memori_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # Kamera
            kamera_spec = data['kamera']
            numeric_values = [int(value.split()[0]) for value in kamera_spec.split(
                ',') if value.split()[0].isdigit()]
            max_kamera_value = max(numeric_values) if numeric_values else 1
            kamera_values.append(max_kamera_value)

            # Baterai
            baterai_spec = data['baterai']
            baterai_numeric_values = [int(
                value.split()[0]) for value in baterai_spec.split() if value.split()[0].isdigit()]
            max_baterai_value = max(
                baterai_numeric_values) if baterai_numeric_values else 1
            baterai_values.append(max_baterai_value)

            # RAM
            ram_spec = data['ram']
            ram_numeric_values = [
                int(value) for value in ram_spec.split() if value.isdigit()]
            max_ram_value = max(
                ram_numeric_values) if ram_numeric_values else 1
            ram_values.append(max_ram_value)

            # Memori
            memori_value = DEV_SCALE['memori'].get(data['memori'], 1)
            memori_values.append(memori_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

        return [
            {'no': data['no'],
             'kamera': kamera_value / max(kamera_values),
             'baterai': baterai_value / max(baterai_values),
             'ram': ram_value / max(ram_values),
             'memori': memori_value / max(memori_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             }
            for data, kamera_value, baterai_value, ram_value, memori_value, harga_value
            in zip(self.data, kamera_values, baterai_values, ram_values, memori_values, harga_values)
        ]


class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['kamera']**self.weight['kamera'] *
                row['baterai']**self.weight['baterai'] *
                row['ram']**self.weight['ram'] *
                row['memori']**self.weight['memori'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'kamera': product['produk'] / self.weight['kamera'],
                'baterai': product['produk'] / self.weight['baterai'],
                'ram': product['produk'] / self.weight['ram'],
                'memori': product['produk'] / self.weight['memori'],
                'harga': product['produk'] / self.weight['harga'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data


class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['no']:
                  round(row['kamera'] * weight['kamera'] +
                        row['baterai'] * weight['baterai'] +
                        row['ram'] * weight['ram'] +
                        row['memori'] * weight['memori'] +
                        row['harga'] * weight['harga'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['No', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')
