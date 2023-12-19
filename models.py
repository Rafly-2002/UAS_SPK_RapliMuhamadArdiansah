from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Smartphone(Base):
    __tablename__ = "tblhandphone" 
    no = Column(Integer, primary_key=True)
    nama_handphone = Column(String)
    kamera = Column(String)
    baterai = Column(String)
    ram = Column(String)
    memori = Column(String)
    harga = Column(String)

    def __repr__(self):
        return f"Smartphone(nama_handphone={self.nama_handphone!r}, kamera={self.kamera!r}, baterai={self.baterai!r}, ram={self.ram!r}, memori={self.memori!r}, harga={self.harga!r})"
