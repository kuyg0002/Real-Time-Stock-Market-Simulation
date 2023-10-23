from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_notification')
def send_notification():
    updated_stock_data = {"ticker": "AAPL", "price": 150.25}
    target_session_id = 'some_actual_session_id_here' # replace with an actual session ID
    socketio.emit('stock_update', updated_stock_data, room=target_session_id)
    return "Notification Sent!"

if __name__ == "__main__":
    socketio.run(app, debug=True)
