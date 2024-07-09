from repository.database import db

#MODEL
class Payment(db.Model):
    # criando a tabela de pagamentos
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    bank_payment_id = db.Column(db.String(200), nullable=True)
    qr_code = db.Column(db.String(100), nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=False) #Fri, 28 Jun 2024 16:15:06 GMT

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'paid': self.paid,
            'bank_payment_id': self.bank_payment_id,
            'qr_code': self.qr_code,
            'expiration_date': self.expiration_date
        }