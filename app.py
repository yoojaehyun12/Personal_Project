from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 1. 메인 페이지
@app.route('/')
def home():
    return render_template('main.html')

# 2. 소개(추천/커스텀 선택) 페이지
@app.route('/intro')
def intro():
    return render_template('intro.html')

# 3. 칵테일(직접 제조) 페이지
@app.route('/bar_list')
def bar_list():
    return render_template('bar_list.html')

# 4. 문의 페이지
@app.route('/gita')
def gita():
    return render_template('gita.html')

# 5. 로봇에게 데이터 쏘는 API
@app.route('/api/order', methods=['POST'])
def receive_order():
    order_data = request.get_json()
    
    print("\n" + "="*40)
    print("🍸 [새로운 주문 접수] 🍸")
    print(f"베이스: {order_data.get('base')}")
    print(f"얼음 여부: {order_data.get('ice')}")
    print(f"베이스 양: {order_data.get('amount')}")
    print(f"첨가 재료: {order_data.get('ingredients')}")
    print("="*40 + "\n")
    
    return jsonify({"status": "success", "message": "로봇이 성공적으로 주문을 수신했습니다!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)