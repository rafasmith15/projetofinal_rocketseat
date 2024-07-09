from flask import Flask, jsonify, request, send_file, render_template
from repository.database import db
from db_models.payments import Payment
from datetime import datetime, timedelta
from payments.pix import Pix
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' ##sqlite é o banco de dados em arquivo, e n cm gerenciamento de banco de dados
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'

db.init_app(app)
socketio = SocketIO(app)

@app.route('/payments/pix', methods=['POST'])
def create_pix_payment():
    data = request.get_json()

    if 'value' not in data:
        return jsonify({'message': 'Invalid value'}), 400
    
    expiration_date = datetime.now() + timedelta(minutes=30)

    new_payment = Payment(value=data['value'], expiration_date=expiration_date)
    
    pix_obj = Pix()
    data_payment_pix = pix_obj.create_payment()
    new_payment.bank_payment_id = data_payment_pix['bank_payment_id'] 
    new_payment.qr_code = data_payment_pix["qr_code_path"]

    db.session.add(new_payment) #adiciona o pagamento no banco de dados
    db.session.commit() #salva o pagamento no banco de dados

    return jsonify({'message': 'Pix payment created!',
                    'payment': new_payment.to_dict()}), 201


@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return render_template('404.html')
    
    if payment.paid:
        return render_template('confirmed_payment.html',
                                payment_id=payment.id, #dados dinâmicos
                                value=payment.value,
                                qr_code=payment.qr_code)

    return render_template('payment.html',
                            payment_id=payment.id, #dados dinâmicos
                            value=payment.value,
                            host="http://127.0.0.1:5000",
                            qr_code=payment.qr_code) #renderiza o template html


@app.route('/payments/pix/qr_code/<file_name>', methods=['GET'])
def get_img(file_name):

    if not file_name:
        return jsonify({'message': 'Invalid file name'}), 400
    
    return send_file(f'static/img/{file_name}.png', mimetype='image/png')


@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    data =request.get_json()

    # Verifica se o bank_payment_id e value estão no json que vem da requisição do user
    if "bank_payment_id" not in data and "value" not in data:
        return jsonify({'message': 'Invalid bank_payment_id'}), 400

    payment = Payment.query.filter_by(bank_payment_id=data.get('bank_payment_id')).first() #recupera o 1º pagamento com o bank_payment_id pq pode retornar mais de um valor

    # Verifica se o pagamento foi encontrado
    if not payment or payment.paid:
        return jsonify({'message': 'Payment not found'}), 404

    # Verifica se o valor do pagamento é igual ao valor que veio no json do user
    if data.get("value") != payment.value:
        return jsonify({'message': 'Invalid value'}), 400
    
    payment.paid = True #No SQLite, True é 1 e False é 0
    db.session.commit()
    socketio.emit(f'payment-confirmed-{payment.id}') #emite um evento para o socketio
    return jsonify({'message': 'Pix payment confirmed!'}), 200

#websockets
# Rota que será executada quando receber um evento de conexão do user ao servidor
# a info do tipo de evento vem pelo protocolo websocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('message', {'message': 'Connected!'})

# quando o user se desconecta do servidor
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True) #roda o servidor
