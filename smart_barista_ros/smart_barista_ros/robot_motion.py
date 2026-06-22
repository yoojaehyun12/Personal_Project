class Indy7Motion:
    def __init__(self, node):
        self.node = node
        self.robot = Indy7Motion(self)

        if stage == "picking":
            self.robot.pick(goal.target_object)
        elif stage == "making":
            self.robot.make_drink(goal.drink_type, list(goal.ingredients))
        elif stage == "serving":
            self.robot.serve(goal.serve_location)

    def pick(self, target_object: str):
        self.node.get_logger().info(f"[Indy7 Mock] Pick target: {target_object}")

    def make_drink(self, drink_type: str, ingredients: list[str]):
        self.node.get_logger().info(
            f"[Indy7 Mock] Make drink: {drink_type}, ingredients={ingredients}"
        )

    def serve(self, serve_location: str):
        self.node.get_logger().info(f"[Indy7 Mock] Serve to: {serve_location}")