from dataclasses import dataclass, field
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from typing import Any
import queue
import threading
import uuid
from ros_client import RosActionClient, RobotGoal

app = Flask(__name__, template_folder="../templates", static_folder="../static")

robot_client = RosActionClient()

@dataclass
class Order:
    id: str
    payload: dict[str, Any]
    status: str = "queued"
    progress: int = 0
    message: str = "주문이 대기열에 등록되었습니다."
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "payload": self.payload,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
        }


order_queue: queue.Queue[str] = queue.Queue()
orders: dict[str, Order] = {}
current_order_id: str | None = None
state_lock = threading.RLock()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def update_order(order_id: str, **changes: Any) -> None:
    with state_lock:
        order = orders[order_id]
        for key, value in changes.items():
            setattr(order, key, value)
        order.updated_at = now()


def visible_queue_ids() -> list[str]:
    with state_lock:
        return [
            order_id
            for order_id, order in orders.items()
            if order.status == "queued"
        ]


def validate_order_payload(order_data: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(order_data, dict):
        return None, "주문 데이터는 JSON 객체여야 합니다."

    base = order_data.get("base")
    if not base:
        return None, "베이스 음료를 선택해야 합니다."

    return {
        "base": base,
        "ice": order_data.get("ice"),
        "amount": order_data.get("amount"),
        "ingredients": order_data.get("ingredients", []),
    }, None

def build_robot_goal(order: Order) -> RobotGoal:
    payload = order.payload

    return RobotGoal(
        order_id=order.id,
        drink_type=payload["base"],
        target_object=f"{payload['base']}_cup",
        ingredients=payload.get("ingredients", []),
        serve_location="pickup_zone",
    )

def robot_bartender_worker() -> None:
    global current_order_id

    while True:
        order_id = order_queue.get()

        try:
            with state_lock:
                current_order_id = order_id

            print("\n" + "=" * 60)
            print(f"[로봇 작업 시작] order_id={order_id}")

            with state_lock:
                order = orders[order_id]

            goal = build_robot_goal(order)
            
            def handle_feedback(status: str, message: str, progress: int) -> None:
                update_order(
                    order_id,
                    status=status,
                    message=message,
                    progress=progress,
                )
                print(f"[{order_id}] {status} - {progress}%")

            robot_client.send_order(goal, handle_feedback)


            update_order(
                order_id,
                status="done",
                message="음료 제조 및 서빙이 완료되었습니다.",
                progress=100,
            )
            print(f"[로봇 작업 완료] order_id={order_id}")
            print("=" * 60 + "\n")

        except Exception as exc:
            update_order(
                order_id,
                status="failed",
                message="로봇 작업 중 오류가 발생했습니다.",
                error=str(exc),
            )
            print(f"[로봇 작업 실패] order_id={order_id}, error={exc}")

        finally:
            with state_lock:
                current_order_id = None
            order_queue.task_done()


robot_thread = threading.Thread(target=robot_bartender_worker, daemon=True)
robot_thread.start()


@app.route("/")
def home():
    return render_template("main.html")


@app.route("/intro")
def intro():
    return render_template("intro.html")


@app.route("/bar_list")
def bar_list():
    return render_template("bar_list.html")


@app.route("/gita")
def gita():
    return render_template("gita.html")


@app.route("/api/order", methods=["POST"])
def receive_order():
    order_data = request.get_json(silent=True)
    payload, error = validate_order_payload(order_data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    order_id = uuid.uuid4().hex[:12]
    order = Order(id=order_id, payload=payload)

    with state_lock:
        position = len(visible_queue_ids()) + (1 if current_order_id else 0) + 1
        orders[order_id] = order

    order_queue.put(order_id)

    if position == 1:
        message = "로봇이 비어있습니다. 즉시 제조를 시작합니다!"
    else:
        message = f"현재 로봇이 바쁩니다. 대기 순번 {position}번째로 예약되었습니다!"

    return jsonify({
        "status": "success",
        "message": message,
        "order": order.to_dict(),
    }), 202


@app.route("/api/orders", methods=["GET"])
def list_orders():
    with state_lock:
        order_list = [order.to_dict() for order in orders.values()]
        current_order = orders[current_order_id].to_dict() if current_order_id else None
        queue_list = [
            order.to_dict()
            for order in orders.values()
            if order.status == "queued"
        ]

    return jsonify({
        "current_order": current_order,
        "queue": queue_list,
        "orders": order_list,
    })


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id: str):
    with state_lock:
        order = orders.get(order_id)

    if not order:
        return jsonify({"status": "error", "message": "주문을 찾을 수 없습니다."}), 404

    return jsonify({"status": "success", "order": order.to_dict()})


@app.route("/api/status", methods=["GET"])
def get_status():
    with state_lock:
        current_order = orders[current_order_id].to_dict() if current_order_id else None
        queue_count = len(visible_queue_ids())

    return jsonify({
        "current_order": current_order,
        "queue_count": queue_count,
        "is_robot_working": current_order is not None,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
