"""
Models package initialization.

This package contains all Django models for the travel booking system.
"""

from .destino import Destino
from .factura import Factura
from .fatura_linha import FacturaLinha
from .feedback import Feedback
from .hotel import Hotel
from .pacote import Pacote
from .pacote_destino import PacoteDestino
from .pacote_hotel import PacoteHotel
from .pacote_voo import PacoteVoo
from .pagamento import Pagamento
from .compra import Compra
from .tipo_user import TipoUser
from .utilizador import Utilizador
from .voos import Voo

__all__ = [
    'Destino',
    'Factura',
    'FacturaLinha',
    'Feedback',
    'Hotel',
    'Pacote',
    'PacoteDestino',
    'PacoteHotel',
    'PacoteVoo',
    'Pagamento',
    'Compra',
    'TipoUser',
    'Utilizador',
    'Voo',
]