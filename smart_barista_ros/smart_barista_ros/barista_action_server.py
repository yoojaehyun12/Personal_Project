#!/usr/bin/env python3
import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from smart_barista_ros.action import MakeDrink
from robot_motion import Indy7Motion


class BaristaActionServer(Node):
    def __init__(self):
        super().__init__("barista_action_server")

        self._action_server = ActionServer(
            self,
            MakeDrink,
            "make_drink",
            self.execute_callback,
        )

        self.robot = Indy7Motion(self)

        self.get_logger().info("Barista Action Server started.")

    def execute_callback(self, goal_handle):
        goal = goal_handle.request

        self.get_logger().info(
            f"Received order: {goal.order_id}, "
            f"drink_type={goal.drink_type}, "
            f"target_object={goal.target_object}"
        )

        feedback = MakeDrink.Feedback()

        steps = [
            ("detecting", f"AI 비전으로 {goal.target_object} 인식 중", 20),
            ("picking", f"Indy7이 {goal.target_object} 집는 중", 45),
            ("making", f"{goal.drink_type} 제조 중", 75),
            ("serving", f"{goal.serve_location} 위치로 서빙 중", 95),
        ]

        for stage, message, progress in steps:
            feedback.stage = stage
            feedback.message = message
            feedback.progress = progress
            goal_handle.publish_feedback(feedback)

            self.get_logger().info(f"{stage}: {progress}%")

            if stage == "picking":
                self.robot.pick(goal.target_object)
            elif stage == "making":
                self.robot.make_drink(goal.drink_type, list(goal.ingredients))
            elif stage == "serving":
                self.robot.serve(goal.serve_location)

            time.sleep(2)

        goal_handle.succeed()

        result = MakeDrink.Result()
        result.success = True
        result.message = "음료 제조 및 서빙 완료"
        return result


def main(args=None):
    rclpy.init(args=args)

    server = BaristaActionServer()

    try:
        rclpy.spin(server)
    finally:
        server.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()