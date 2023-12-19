from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Smartphone(Base):
    __tablename__ = "tblhandphone"
    no = Column(Integer, primary_key=True)
    nama_handphone = Column(String(255))
    kamera = Column(String(255))
    baterai = Column(String(255))
    ram = Column(String(255))
    memori = Column(String(255))
    harga = Column(String(255))

    def __init__(self, nama_handphone, kamera, baterai, ram, memori, harga):
        self.nama_handphone = nama_handphone
        self.kamera = kamera
        self.baterai = baterai
        self.ram = ram
        self.memori = memori
        self.harga = harga

    def calculate_score(self, dev_scale):
        score = 0
        score += self.kamera * dev_scale['kamera']
        score += self.baterai * dev_scale['baterai']
        score += self.ram * dev_scale['ram']
        score += self.memori * dev_scale['memori']
        score -= self.harga * dev_scale['harga']
        return score

    def __repr__(self):
        return f"Smartphone(nama_handphone={self.nama_handphone!r}, kamera={self.kamera!r}, baterai={self.baterai!r}, ram={self.ram!r}, memori={self.memori!r}, harga={self.harga!r})"
