cmake_minimum_required(VERSION 3.8)
project(smart_barista_ros)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MakeDrink.action"
  DEPENDENCIES action_msgs
)

install(PROGRAMS
  smart_barista_ros/barista_action_server.py
  smart_barista_ros/vision_node.py
  smart_barista_ros/pick_place_node.py
  smart_barista_ros/robot_motion.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()