# ROS2 Smart Garbage Classification and Sorting Robot

## 1. Project Overview

The project is a **ROS2-based Smart Garbage Classification and Sorting System** that uses a camera and AI-based object detection to identify different types of garbage and automatically sort them into appropriate bins.

The system will initially run on a **laptop** for development and testing. After successful implementation, the ROS2 and AI components can optionally be migrated to a **Raspberry Pi** to make the system more compact and standalone.

The main garbage categories are:

- Plastic
- Paper
- Metal
- Glass
- Organic Waste

ROS2 acts as the **core middleware** responsible for communication between the camera, AI detection system, classification logic, and sorting hardware.

---

# 2. System Architecture

```text
                    ┌─────────────────────┐
                    │      USB CAMERA     │
                    │   Image Acquisition │
                    └──────────┬──────────┘
                               │
                               │ /camera/image_raw
                               ▼
                    ┌─────────────────────┐
                    │   CAMERA NODE       │
                    │       ROS2          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  DETECTION NODE     │
                    │ OpenCV + YOLO       │
                    └──────────┬──────────┘
                               │
                               │ Detected Object
                               ▼
                    ┌─────────────────────┐
                    │ CLASSIFICATION NODE │
                    │                     │
                    │ Object → Category   │
                    └──────────┬──────────┘
                               │
                               │ /waste_category
                               ▼
                    ┌─────────────────────┐
                    │   SORTING NODE      │
                    │                     │
                    │ Category → Angle    │
                    └──────────┬──────────┘
                               │
                               │ /servo_command
                               ▼
                    ┌─────────────────────┐
                    │       ESP32         │
                    │ Hardware Controller │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    SERVO MOTOR      │
                    │  Sorting Mechanism  │
                    └──────────┬──────────┘
                               │
                               ▼
             ┌────────────────────────────────────┐
             │          SORTING BINS               │
             │                                    │
             │ Plastic | Paper | Metal | Glass |  │
             │              Organic                │
             └────────────────────────────────────┘
```

---

# 3. Main Components

## 3.1 Camera

The USB camera continuously captures images or video of the garbage placed in the input area.

**Input:**
- Real-world garbage objects

**Output:**
- RGB image frames

The camera can initially be connected to the laptop and later replaced by a Raspberry Pi-compatible camera.

---

## 3.2 ROS2 Camera Node

The Camera Node is responsible for acquiring images from the camera and publishing them to a ROS2 topic.

**Node:**

```text
/camera_node
```

**Publishes:**

```text
/camera/image_raw
```

**Message Type:**

```text
sensor_msgs/msg/Image
```

---

# 4. AI Detection Node

The Detection Node receives images from the camera and processes them using **OpenCV and YOLO**.

**Node:**

```text
/detection_node
```

### Responsibilities

1. Subscribe to camera images.
2. Convert ROS2 image messages using `cv_bridge`.
3. Run YOLO inference.
4. Detect waste objects.
5. Generate bounding boxes.
6. Generate confidence scores.
7. Send detection information to the classification system.

Example:

```text
Input:
Image containing a plastic bottle

YOLO Output:
Object = plastic bottle
Confidence = 0.96
Bounding Box = (x, y, width, height)
```

---

# 5. Classification Node

The Classification Node converts the detected object into one of the predefined garbage categories.

**Node:**

```text
/classification_node
```

### Example

```text
YOLO Detection
       ↓
Plastic Bottle
       ↓
Plastic Category
```

Another example:

```text
YOLO Detection
       ↓
Aluminum Can
       ↓
Metal Category
```

### Categories

```text
PLASTIC
PAPER
METAL
GLASS
ORGANIC
```

**Publishes:**

```text
/waste_category
```

**Message Type:**

```text
std_msgs/msg/String
```

Example:

```text
"PLASTIC"
```

---

# 6. Sorting Node

The Sorting Node receives the waste category and determines the appropriate position of the sorting mechanism.

**Node:**

```text
/sorting_node
```

Example mapping:

| Category | Servo Position |
|---|---:|
| Plastic | 0° |
| Paper | 45° |
| Metal | 90° |
| Glass | 135° |
| Organic | 180° |

The node publishes the required servo position.

**Topic:**

```text
/servo_command
```

Example:

```text
90
```

This means the servo should move to 90°.

---

# 7. ESP32 Hardware Controller

The ESP32 receives servo commands from the ROS2 system and controls the physical servo motor.

There are two possible communication methods:

### Development Version

```text
Laptop
  │
  │ USB Serial
  ▼
ESP32
```

### Advanced Version

The ESP32 can communicate over Wi-Fi using a suitable ROS2-compatible communication approach.

The ESP32 is responsible for:

- Receiving commands
- Controlling servo motors
- Reading optional sensors
- Providing feedback to the ROS2 system

---

# 8. Sorting Mechanism

The project uses a **servo-controlled flap/rotating platform**.

When garbage reaches the sorting point:

```text
Camera → Classification → Servo Position
```

The servo rotates the mechanism to align the garbage with the correct bin.

Example:

```text
Detected: Plastic
       ↓
Servo = 0°
       ↓
Plastic Bin
```

---

# 9. Optional Object Detection Sensor

An IR sensor or ultrasonic sensor can be added to detect when garbage has entered the sorting area.

Example:

```text
IR Sensor
    │
    ▼
Object Detected
    │
    ▼
Camera Capture
    │
    ▼
YOLO Classification
```

This prevents unnecessary image processing when no garbage is present.

---

# 10. ROS2 Communication Architecture

The project primarily uses **ROS2 Topics** for communication.

```text
/camera/image_raw
        │
        ▼
/detection_node
        │
        ▼
/waste_category
        │
        ▼
/sorting_node
        │
        ▼
/servo_command
        │
        ▼
ESP32
```

### Topic Table

| Topic | Publisher | Subscriber | Message |
|---|---|---|---|
| `/camera/image_raw` | Camera Node | Detection Node | `sensor_msgs/msg/Image` |
| `/waste_category` | Classification Node | Sorting Node | `std_msgs/msg/String` |
| `/servo_command` | Sorting Node | ESP32 Controller | Servo command |

---

# 11. ROS2 Node Architecture

```text
┌──────────────────────┐
│     Camera Node      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Detection Node     │
│   OpenCV + YOLO      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Classification Node  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Sorting Node      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  ESP32 Controller    │
└──────────┬───────────┘
           │
           ▼
      Servo Motor
```

---

# 12. Hardware Architecture

```text
                 USB Camera
                     │
                     ▼
              ┌─────────────┐
              │    Laptop   │
              │             │
              │ ROS2        │
              │ OpenCV      │
              │ YOLO        │
              └──────┬──────┘
                     │
                  USB/Serial
                     │
                     ▼
                 ┌───────┐
                 │ ESP32 │
                 └───┬───┘
                     │
                     ▼
               Servo Motor
                     │
                     ▼
              Sorting Flap
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Plastic       Paper        Metal
       Bin           Bin          Bin

        + Glass Bin + Organic Bin
```

---

# 13. Development Architecture

The project will initially be developed using a laptop.

### Laptop

Runs:

- Ubuntu
- ROS2 Humble
- Python
- OpenCV
- YOLO
- RViz2
- Development tools

### External Hardware

- USB Camera
- ESP32
- Servo Motor

This approach reduces development cost and provides more processing power for YOLO.

---

# 14. Raspberry Pi Migration

After completing and testing the system on the laptop, the ROS2 application can be moved to a Raspberry Pi.

### Current Development

```text
USB Camera
     ↓
Laptop
ROS2 + YOLO
     ↓
ESP32
     ↓
Servo
```

### Future Standalone System

```text
Camera
   ↓
Raspberry Pi
ROS2 + YOLO
   ↓
ESP32
   ↓
Servo
```

The ROS2 node structure and topics remain largely the same. Only the computing platform changes.

For Raspberry Pi deployment, a lightweight/optimized YOLO model may be required because AI inference is more computationally demanding than on a typical laptop.

---

# 15. Software Architecture

```text
Application Layer
        │
        ▼
┌─────────────────────────┐
│ Waste Classification    │
│ Sorting Logic           │
└────────────┬────────────┘
             │
             ▼
ROS2 Middleware Layer
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
  Topics   Services  Actions
     │
     ▼
Hardware Interface
     │
     ▼
Camera / ESP32 / Servo
```

---

# 16. Package Structure

Recommended ROS2 workspace:

```text
garbage_sorting_ws/
└── src/
    ├── garbage_camera/
    │   └── camera_node
    │
    ├── garbage_detection/
    │   └── detection_node
    │
    ├── garbage_classification/
    │   └── classification_node
    │
    ├── garbage_sorting/
    │   └── sorting_node
    │
    └── garbage_interfaces/
        └── custom messages/services
```

---

# 17. Processing Pipeline

```text
1. Garbage placed
        ↓
2. Object sensor detects garbage
        ↓
3. Camera captures image
        ↓
4. ROS2 publishes image
        ↓
5. YOLO detects object
        ↓
6. Classification determines waste type
        ↓
7. ROS2 publishes waste category
        ↓
8. Sorting node calculates servo position
        ↓
9. ESP32 receives command
        ↓
10. Servo moves sorting mechanism
        ↓
11. Garbage falls into correct bin
```

---

# 18. Error Handling

The system should handle cases where the AI cannot confidently identify the waste.

Example:

```text
YOLO Confidence < 60%
        ↓
Classification = UNKNOWN
        ↓
Do NOT activate sorting
        ↓
Send alert / place in general waste bin
```

This prevents incorrect sorting caused by uncertain predictions.

---

# 19. Monitoring and Visualization

**RViz2** can be used to visualize relevant ROS2 information during development.

Possible visualization:

- Camera feed
- Detection results
- Waste category
- System status
- Sensor information

ROS2 command-line tools can also be used for debugging:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /waste_category
ros2 topic echo /servo_command
```

---

# 20. Expected System Output

For an input such as a plastic bottle:

```text
Camera
   ↓
YOLO
   ↓
Plastic Bottle
Confidence: 96%
   ↓
ROS2
   ↓
Category: PLASTIC
   ↓
Servo Command: 0°
   ↓
Plastic Bin
```

The system should provide real-time classification and automatic physical sorting.

---

# 21. Future Enhancements

- Autonomous mobile garbage collection.
- Robotic arm-based sorting.
- More waste categories.
- Conveyor belt system.
- Bin fill-level detection.
- IoT monitoring dashboard.
- Waste statistics and analytics.
- Improved AI model using a custom dataset.
- Raspberry Pi/Jetson standalone deployment.
- Integration with smart-city waste management systems.

---

# 22. Core Technologies

| Technology | Role |
|---|---|
| **ROS2** | Core robotic middleware |
| **Python** | ROS2 node development |
| **YOLO** | Waste object detection |
| **OpenCV** | Image processing |
| **ESP32** | Hardware control |
| **Servo Motor** | Waste sorting |
| **USB Camera** | Image acquisition |
| **RViz2** | ROS visualization |
| **Ubuntu** | Development platform |

---

# 23. Final Architecture Summary

The system follows a modular architecture where **ROS2 connects perception, AI, decision-making, and hardware control**.

```text
              PERCEPTION
                  │
              USB Camera
                  │
                  ▼
              ROS2 Node
                  │
                  ▼
            YOLO + OpenCV
                  │
                  ▼
             CLASSIFICATION
                  │
                  ▼
              ROS2 Topic
                  │
                  ▼
               SORTING
                  │
                  ▼
                ESP32
                  │
                  ▼
             Servo Motor
                  │
                  ▼
           Physical Sorting
                  │
                  ▼
          Correct Waste Bin
```

**Key Design Principle:** The system is developed on a **laptop first**, while keeping the ROS2 nodes modular so that the same architecture can later be deployed on a **Raspberry Pi** with minimal changes.