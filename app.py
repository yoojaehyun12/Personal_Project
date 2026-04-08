from flask import Flask, request, jsonify, render_template
import queue
import threading
import time

app = Flask(__name__)

# 🌟 핵심 1: 주문 대기열(Queue)과 로봇 상태 변수 생성 🌟
order_queue = queue.Queue()
is_robot_working = False

# 🌟 핵심 2: 백그라운드에서 계속 돌아가는 로봇 바텐더 작업자(Thread) 🌟
def robot_bartender_worker():
    global is_robot_working
    
    while True:
        # 대기열에 주문이 들어올 때까지 기다렸다가 하나씩 꺼냅니다.
        current_order = order_queue.get()
        is_robot_working = True
        
        print("\n" + "🤖"*20)
        print(f"▶️ [로봇 작동 시작] 대기열에서 주문을 꺼냈습니다!")
        print(f"▶️ 레시피: {current_order}")
        
        # =========================================================
        # ⚠️ 실제 하드웨어 제어 코드가 들어갈 자리입니다 ⚠️
        # 1. 컵 픽업: rtde_c.moveJ(cup_position)
        # 2. 베이스 추출: serial.write(b'WATER_ON') -> time.sleep(3)
        # 3. 시럽 펌프 작동: 엣지 보드(아두이노/라즈베리파이)로 신호 전송
        # 4. 서빙 위치로 이동: rtde_c.moveL(serve_position)
        # =========================================================
        
        # 하드웨어가 없으니 지금은 7초 동안 로봇이 움직인다고 가정(가상 딜레이)
        time.sleep(7) 
        
        print(f"✅ [로봇 작동 완료] 음료 서빙이 끝났습니다!")
        print("🤖"*20 + "\n")
        
        is_robot_working = False
        order_queue.task_done() # 이 주문은 끝났다고 알려줌

# 서버가 켜질 때 로봇 작업자(Thread)도 백그라운드에서 같이 실행시킵니다.
robot_thread = threading.Thread(target=robot_bartender_worker, daemon=True)
robot_thread.start()


# --- 아래는 기존과 동일한 웹 화면 서빙 라우터 ---
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/bar_list')
def bar_list():
    return render_template('bar_list.html')

@app.route('/gita')
def gita():
    return render_template('gita.html')

# 🌟 핵심 3: 웹에서 주문이 들어오면 대기열에 넣고 즉시 응답 🌟
@app.route('/api/order', methods=['POST'])
def receive_order():
    global is_robot_working
    order_data = request.get_json()
    
    # 주문을 Queue(대기열)에 밀어 넣습니다.
    order_queue.put(order_data)
    
    # 현재 내 앞에 몇 잔이 밀려있는지 계산 (현재 만들고 있는 것 + 대기열)
    wait_count = order_queue.qsize()
    if is_robot_working:
        wait_count += 1
        message = f"현재 로봇이 바쁩니다. 대기 순번 {wait_count}번째로 예약되었습니다!"
    else:
        message = "로봇이 비어있습니다. 즉시 제조를 시작합니다!"
    
    # 사용자 화면에는 로봇을 기다리게 하지 않고 바로 예약 완료 팝업을 띄워줍니다.
    return jsonify({
        "status": "success", 
        "message": message
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)