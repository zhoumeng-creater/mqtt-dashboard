
from flask import Flask, request, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import threading
import json
import time
import random
import datetime
import sqlite3


app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"], supports_credentials=True)

mqtt_client = None
received_messages = {}

def on_connect(client, userdata, flags, rc):
    print("连接结果: " + mqtt.connack_string(rc))

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        payload_dict = json.loads(payload_str)
        topic = msg.topic

        payload_dict['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if topic not in received_messages:
            received_messages[topic] = []
        received_messages[topic].append(payload_dict)

        if topic == "device/fps":
            save_fps_to_db(payload_dict["fps"], payload_dict["timestamp"])
        elif topic == "device/surveillance_camera":  # 新增此分支
            save_surveillance_camera_to_db(payload_dict["status"], payload_dict["timestamp"])
        
        print(f"[收到消息] 主题: {topic}, 内容: {payload_dict}")
    except Exception as e:
        print(f"[错误] 解析消息失败: {e}")

        print(f"[收到消息] 主题: {topic}, 内容: {payload_dict}")
  


def init_db():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temperature_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_user_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            id_number TEXT,
            home_address TEXT,
            company TEXT,
            company_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_water_heater_db():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_heater_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_light_control_db():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS light_control_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intensity REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_fps_db():
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fps REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
def init_surveillance_camera_db():
    conn = sqlite3.connect('surveillance_camera.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveillance_camera_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(value, timestamp):
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO temperature_data (value, timestamp) VALUES (?, ?)', (value, timestamp))
    conn.commit()
    conn.close()

def save_water_heater_to_db(temperature, status, timestamp):
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO water_heater_data (temperature, status, timestamp) VALUES (?, ?, ?)', (temperature, status, timestamp))
    conn.commit()
    conn.close()

def save_light_control_to_db(intensity, status, timestamp):
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO light_control_data (intensity, status, timestamp) VALUES (?, ?, ?)',
                   (intensity, status, timestamp))
    conn.commit()
    conn.close()

def save_fps_to_db(fps, timestamp):
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fps_data (fps, timestamp) VALUES (?, ?)', (fps, timestamp))
    conn.commit()
    conn.close()
    
def save_surveillance_camera_to_db(status, timestamp):
    conn = sqlite3.connect('surveillance_camera.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO surveillance_camera_data (status, timestamp) VALUES (?, ?)', (status, timestamp))
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('idNumber')
    home_address = data.get('homeAddress')
    company = data.get('company')
    company_address = data.get('companyAddress')

    if not username or not password:
        return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password, phone, email, id_number, home_address, company, company_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, phone, email, id_number, home_address, company, company_address))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
    finally:
        conn.close()

    return jsonify({'status': 'success', 'message': '注册成功'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'message': '登录成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

@app.route('/api/user', methods=['GET'])
def get_user_info():
    username = request.args.get('username')

    if not username:
        return jsonify({'status': 'error', 'message': '用户名不能为空'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_info = {
            'username': user[1],
            'phone': user[3],
            'email': user[4],
            'idNumber': user[5],
            'homeAddress': user[6],
            'company': user[7],
            'companyAddress': user[8]
        }
        return jsonify({'status': 'success', 'data': user_info})
    else:
        return jsonify({'status': 'error', 'message': '用户未找到'}), 404

@app.route('/api/user', methods=['PUT'])
def update_user_info():
    data = request.get_json()

    username = data.get('username')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('idNumber')
    home_address = data.get('homeAddress')
    company = data.get('company')
    company_address = data.get('companyAddress')

    if not username:
        return jsonify({'status': 'error', 'message': '用户名不能为空'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET phone = ?, email = ?, id_number = ?, home_address = ?, company = ?, company_address = ?
        WHERE username = ?
    ''', (phone, email, id_number, home_address, company, company_address, username))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': '个人信息更新成功'})

@app.route('/connect-mqtt', methods=['POST'])
def connect_mqtt():
    global mqtt_client

    data = request.get_json()
    broker = data.get('brokerUrl')
    port = int(data.get('port'))
    client_id = data.get('clientId')

    if not all([broker, port, client_id]):
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400

    try:
        mqtt_client = mqtt.Client(client_id=client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.connect(broker, port, 60)
        mqtt_client.loop_start()

        return jsonify({'status': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/subscribe', methods=['POST'])
def subscribe():
    global mqtt_client
    data = request.get_json()
    topic = data.get('topic')
    if not topic:
        return jsonify({'status': 'error', 'message': '缺少topic'}), 400

    try:
        mqtt_client.subscribe(topic)
        return jsonify({'status': 'subscribed', 'topic': topic})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/messages/<device_id>', methods=['GET'])
def get_messages(device_id):
    topic = f"device/{device_id}"
    msgs = received_messages.get(topic, [])
    return jsonify({'topic': topic, 'messages': msgs})

def simulate_temperature():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            temp = round(random.uniform(20.0, 30.0), 2)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/temperature", json.dumps({"temperature": temp, "timestamp": timestamp}))
            save_to_db(temp, timestamp)
            time.sleep(5)
    threading.Thread(target=run, daemon=True).start()

def simulate_water_heater():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            temperature = round(random.uniform(30.0, 60.0), 2)
            status = random.choice(['running', 'stopped'])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/water_heater", json.dumps({"temperature": temperature, "status": status, "timestamp": timestamp}))
            save_water_heater_to_db(temperature, status, timestamp)
            time.sleep(5)
    threading.Thread(target=run, daemon=True).start()

def simulate_light_control():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            intensity = round(random.uniform(100.0, 800.0), 2)
            status = "on" if intensity < 200.0 or intensity > 600.0 else "off"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/light_control", json.dumps({"intensity": intensity, "status": status, "timestamp": timestamp}))
            save_light_control_to_db(intensity, status, timestamp)
            time.sleep(5)
    threading.Thread(target=run, daemon=True).start()

def simulate_fps():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            fps = round(random.uniform(20.0, 60.0), 2)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish("device/fps", json.dumps({"fps": fps, "timestamp": timestamp}))
            save_fps_to_db(fps, timestamp)
            time.sleep(5)
    threading.Thread(target=run, daemon=True).start()
    
def simulate_surveillance_camera():
    def run():
        pub_client = mqtt.Client()
        pub_client.connect("localhost", 1884, 60)
        pub_client.loop_start()
        while True:
            status = random.choice(['recording', 'idle'])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pub_client.publish(
                "device/surveillance_camera",
                json.dumps({"status": status, "timestamp": timestamp})
            )
            time.sleep(5)
    threading.Thread(target=run, daemon=True).start()

@app.route('/api/realtime/fps', methods=['GET'])
def get_latest_fps():
    topic = "device/fps"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'fps': None, 'timestamp': '', 'message': '暂无数据'})

@app.route('/api/history/fps', methods=['GET'])
def get_fps_history():
    conn = sqlite3.connect('fps.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, fps FROM fps_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'fps': row[1]} for row in rows]
    return jsonify({'history': history})

@app.route('/api/realtime/temperature', methods=['GET'])
def get_latest_temperature():
    topic = "device/temperature"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'value': None, 'timestamp': '', 'message': '暂无数据'})

@app.route('/api/realtime/water_heater', methods=['GET'])
def get_latest_water_heater():
    topic = "device/water_heater"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'temperature': None, 'status': None, 'timestamp': '', 'message': '暂无数据'})

@app.route('/api/realtime/light-control', methods=['GET'])
def get_latest_light_control():
    topic = "device/light_control"
    msgs = received_messages.get(topic, [])

    if msgs:
        return jsonify(msgs[-1])
    else:
        return jsonify({'intensity': None, 'status': None, 'timestamp': '', 'message': '暂无数据'})

@app.route('/api/history/temperature', methods=['GET'])
def get_temperature_history():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, value FROM temperature_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'value': row[1]} for row in rows]
    return jsonify({'history': history})

@app.route('/api/history/aircon', methods=['GET'])
def get_temperature_aircon_history():
    conn = sqlite3.connect('temperature.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, value FROM temperature_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'value': row[1]} for row in rows]
    return jsonify({'history': history})

@app.route('/api/history/water_heater', methods=['GET'])
def get_water_heater_history():
    conn = sqlite3.connect('water_heater.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, temperature, status FROM water_heater_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'temperature': row[1], 'status': row[2]} for row in rows]
    return jsonify({'history': history})

@app.route('/api/history/light_control', methods=['GET'])
def get_light_control_history():
    conn = sqlite3.connect('light_control.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, intensity, status FROM light_control_data ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [{'timestamp': row[0], 'intensity': row[1], 'status': row[2]} for row in rows]
    return jsonify({'history': history})

if __name__ == '__main__':
    init_db()
    init_user_db()
    init_water_heater_db()
    init_light_control_db()
    init_fps_db()
    init_surveillance_camera_db() 
    simulate_temperature()
    simulate_water_heater()
    simulate_light_control()
    simulate_fps()
    simulate_surveillance_camera()
    app.run(host='0.0.0.0', port=5050, debug=True)

