# Web-ROS2 Smart Barista with Indy7

태블릿 웹 주문 화면에서 음료 제조 명령을 보내면, Flask 백엔드가 주문을 Queue로 관리하고 ROS2 Action Server로 전달하는 스마트 바리스타 프로토타입입니다.

현재 단계에서는 Neuromeka Indy7 실제 하드웨어 제어 전 단계로, `Indy7Motion` Mock 계층을 통해 웹 주문, ROS2 Action, 진행률 feedback, 로봇 모션 호출 흐름을 end-to-end로 검증했습니다.

## 주요 기능

- Flask 기반 웹 주문 화면
- 주문 Queue 관리
- 현재 주문 상태 및 대기열 실시간 표시
- ROS2 Action 기반 로봇 작업 요청
- Action feedback을 통한 진행률 업데이트
- `Indy7Motion` 모션 계층 분리
- 향후 Neuromeka Indy7 제어 코드 연동 가능 구조

## 시스템 흐름

```text
Web UI
  -> Flask /api/order
  -> Order Queue
  -> RosActionClient
  -> ROS2 /make_drink Action Server
  -> Indy7Motion Mock
  -> Action Feedback
  -> Web Status Panel
  ```

## 프로젝트 구조
```
Personal_Project/
├─ code/
│  ├─ app.py
│  └─ ros_client.py
├─ templates/
│  ├─ main.html
│  ├─ intro.html
│  ├─ bar_list.html
│  └─ gita.html
├─ static/
└─ smart_barista_ros/
   ├─ package.xml
   ├─ CMakeLists.txt
   ├─ setup.py
   ├─ action/
   │  └─ MakeDrink.action
   ├─ resource/
   │  └─ smart_barista_ros
   └─ smart_barista_ros/
      ├─ __init__.py
      ├─ barista_action_server.py
      ├─ robot_motion.py
      ├─ vision_node.py
      └─ pick_place_node.py
```

## ROS2 Action 인터페이스

`smart_barista_ros/action/MakeDrink.action`
```
string order_id
string drink_type
string target_object
string[] ingredients
string serve_location
---
bool success
string message
---
string stage
int32 progress
string message
```

## 실행 방법

1. ROS2 패키지 빌드
WSL2 Ubuntu 24.04 + ROS2 Jazzy 환경에서 실행합니다.
```
source /opt/ros/jazzy/setup.bash

mkdir -p ~/ros2_ws/src
cp -r /mnt/e/Solo_proj/github/Personal_Project/smart_barista_ros ~/ros2_ws/src/

cd ~/ros2_ws
colcon build --packages-select smart_barista_ros
source install/setup.bash
```

2. ROS2 Action Server 실행
```
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 run smart_barista_ros barista_action_server.py
```

3. Flask 웹 서버 실행
다른 Ubuntu 터미널에서 실행합니다.
```
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

cd /mnt/e/Solo_proj/github/Personal_Project/code
python3 app.py
```

브라우저에서 접속:
```
http://localhost:5000/bar_list
```

## Action 직접 테스트
웹 없이 ROS2 Action Server만 테스트할 수도 있습니다.
```
ros2 action send_goal /make_drink smart_barista_ros/action/MakeDrink "{order_id: test001, drink_type: latte, target_object: blue_capsule, ingredients: [milk, syrup], serve_location: pickup_zone}" --feedback
```

예상 흐름:
```
detecting 20%
picking 45%
making 75%
serving 95%
result success
```

## 현재 구현 상태
완료:
- 웹 주문 화면 구현
- Flask 주문 API 구현
- Queue 기반 주문 처리
- 웹 상태 패널 구현
- ROS2 Action 인터페이스 정의
- ROS2 Action Server 구현
- Flask에서 ROS2 Action Goal 전송
- Action feedback 기반 상태 갱신
- Indy7Motion Mock 모션 계층 구현

진행 예정:
- Neuromeka Indy7 실제 제어 API 연동
- Intel RealSense 기반 3D 좌표 추정
- YOLO/OpenCV 기반 물체 인식 노드 구현
- Pick-and-Place 경로 생성
- web_video_server 기반 실시간 영상 스트리밍
- MoveIt 또는 Indy ROS Driver 기반 모션 플래닝

기술 스택:
- Python
- Flask
- HTML/CSS/JavaScript
- ROS2 Jazzy
- ROS2 Action
- WSL2 Ubuntu 24.04
- Neuromeka Indy7 예정
- OpenCV/YOLOv8 예정
- Intel RealSense 예정

## 이 프로젝트 핵심 포인트!!!

이 프로젝트는 단순 웹앱이 아니라, 웹 주문 시스템과 ROS2 Action 기반 로봇 작업 시스템을 연결하는 구조를 목표로 합니다.

현재는 실제 하드웨어 없이 Mock 모션 계층으로 검증했으며, 향후 robot_motion.py 내부를 Neuromeka Indy7 제어 코드로 교체하면 실제 로봇 작업 흐름으로 확장할 수 있습니다.