from dataclasses import dataclass
from typing import Any, Callable
import time


FeedbackCallback = Callable[[str, str, int], None]


@dataclass
class RobotGoal:
    order_id: str
    drink_type: str
    target_object: str
    ingredients: list[str]
    serve_location: str


class RobotClient:
    def send_order(self, goal: RobotGoal, feedback_cb: FeedbackCallback) -> None:
        raise NotImplementedError


class MockRosClient(RobotClient):
    def send_order(self, goal: RobotGoal, feedback_cb: FeedbackCallback) -> None:
        
        steps = [
            (
                "detecting",
                f"AI 비전으로 '{goal.target_object}' 물체를 인식하는 중입니다.",
                20,
            ),
            (
                "picking",
                f"Indy7이 '{goal.target_object}' 물체를 집는 중입니다.",
                45,
            ),
            (
                "making",
                f"{goal.drink_type} 베이스와 {', '.join(goal.ingredients) or '기본 재료'}를 사용해 제조 중입니다.",
                75,
            ),
            (
                "serving",
                f"완성된 음료를 '{goal.serve_location}' 위치로 이동하는 중입니다.",
                95,
            ),
        ]

        for status, message, progress in steps:
            feedback_cb(status, message, progress)
            time.sleep(2)


class RosActionClient(RobotClient):
    def __init__(self) -> None:
        import rclpy
        from rclpy.action import ActionClient
        from smart_barista_ros.action import MakeDrink

        if not rclpy.ok():
            rclpy.init(args=None)

        self.rclpy = rclpy
        self.MakeDrink = MakeDrink
        self.node = rclpy.create_node("flask_barista_action_client")
        self.client = ActionClient(self.node, MakeDrink, "make_drink")

    def send_order(self, goal: RobotGoal, feedback_cb: FeedbackCallback) -> None:
        ros_goal = self.MakeDrink.Goal()
        ros_goal.order_id = goal.order_id
        ros_goal.drink_type = goal.drink_type
        ros_goal.target_object = goal.target_object
        ros_goal.ingredients = goal.ingredients
        ros_goal.serve_location = goal.serve_location

        if not self.client.wait_for_server(timeout_sec=5.0):
            raise RuntimeError("ROS Action Server '/make_drink'를 찾을 수 없습니다.")

        def handle_ros_feedback(feedback_msg):
            feedback = feedback_msg.feedback
            feedback_cb(
                feedback.stage,
                feedback.message,
                feedback.progress,
            )

        send_goal_future = self.client.send_goal_async(
            ros_goal,
            feedback_callback=handle_ros_feedback,
        )

        self.rclpy.spin_until_future_complete(self.node, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            raise RuntimeError("ROS Action goal이 거부되었습니다.")

        result_future = goal_handle.get_result_async()
        self.rclpy.spin_until_future_complete(self.node, result_future)

        result = result_future.result().result
        if not result.success:
            raise RuntimeError(result.message)