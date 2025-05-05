from .sex import Sex as Sex
from peak_utility.enumeration.parsing_enum import ParsingEnum

class Gender(ParsingEnum):
    FOAL: int
    YEARLING: int
    COLT: int
    FILLY: int
    STALLION: int
    MARE: int
    GELDING: int
    RIG: int
    C = COLT
    F = FILLY
    S = STALLION
    M = MARE
    G = GELDING
    R = RIG
    FOALS = FOAL
    YEARLINGS = YEARLING
    COLTS = COLT
    FILLIES = FILLY
    STALLIONS = STALLION
    MARES = MARE
    GELDINGS = GELDING
    RIGS = RIG
    @property
    def sex(self): ...
    @staticmethod
    def determine(official_age: int, sex: Sex | None = None, **kwargs): ...
