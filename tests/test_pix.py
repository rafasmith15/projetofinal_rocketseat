import sys
sys.path.append('../') # Adiciona o diretório pai ao path do sistema

import pytest
import os # biblioteca que acessa o sistema operacional e permite manipular arquivos
from payments.pix import Pix

def test_pix_create_payment():
    pix_instance = Pix()
    payment_info = pix_instance.create_payment(base_dir="../")
    print(f"payment_info: {payment_info}") #para ver o print, execute pytest -s

    assert "bank_payment_id" in payment_info
    assert "qr_code_path" in payment_info
    assert os.path.isfile(f"../static/img/{payment_info['qr_code_path']}.png")

