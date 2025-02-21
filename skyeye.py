import json
import asyncio
import mavsdk
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
import cv2
import os
import datetime
from ultralytics import YOLO

# Load the trained YOLO model
# model = YOLO("YOLOv8n.pt")
model = YOLO("pothole.pt")


# --- Load mission from .plan file ---
def load_mission(file_path="mission.plan"):
    with open(file_path, "r") as file:
        plan_data = json.load(file)

    waypoints = []
    for item in plan_data["mission"]["items"]:
        command = item["command"]
        lat, lon, alt = item["params"][4], item["params"][5], item["params"][6]
        if command == 16:  # Waypoint
            waypoints.append((lat, lon, alt, command))
        elif command == 20:  # RETURN_TO_LAUNCH
            waypoints.append(("RETURN_TO_LAUNCH", command, lat, lon, alt))
        elif command == 21:  # Land
            waypoints.append(("LAND", command, lat, lon, alt))
        elif command == 22:  # Takeoff
            waypoints.append(("TAKEOFF", command, lat, lon, alt))

    return waypoints


# --- Create mission plan ---
async def setup_mission(drone, waypoints):
    mission_items = []

    for item in waypoints:
        print(item)
        if item[0] == "RETURN_TO_LAUNCH":
            _, _, lat, lon, alt = item
            # mission_items.append(MissionItem(
            #     lat, lon, alt, 5.0, True,
            #     float('nan'), float('nan'), MissionItem.CameraAction.NONE,
            #     float('nan'), float('nan'), float('nan'), float('nan'),
            #     float('nan'), MissionItem.VehicleAction.NONE
            # ))
        elif item[0] == "LAND":
            _, _, lat, lon, alt = item
            mission_items.append(MissionItem(
                lat, lon, alt, 5.0, True,
                float('nan'), float('nan'), MissionItem.CameraAction.NONE,
                float('nan'), float('nan'), float('nan'), float('nan'),
                float('nan'), MissionItem.VehicleAction.LAND
            ))
        elif item[0] == "TAKEOFF":
            _, _, lat, lon, alt = item
            mission_items.append(MissionItem(
                lat, lon, alt, 5.0, True,
                float('nan'), float('nan'), MissionItem.CameraAction.NONE,
                float('nan'), float('nan'), float('nan'), float('nan'),
                float('nan'), MissionItem.VehicleAction.TAKEOFF
            ))
        else:
            lat, lon, alt, _ = item
            mission_items.append(MissionItem(
                lat, lon, alt, 5.0, True,
                float('nan'), float('nan'), MissionItem.CameraAction.NONE,
                float('nan'), float('nan'), float('nan'), float('nan'),
                float('nan'), MissionItem.VehicleAction.NONE
            ))

    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    print("📡 Uploading mission to the drone...")
    await drone.mission.upload_mission(mission_plan)
    await asyncio.sleep(5)  # Increased sleep to ensure mission upload is complete

    print("🚀 Starting mission...")
    await drone.mission.start_mission()

    # Check mission status continuously
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("-- Mission completed!")
            break
        await asyncio.sleep(2)  # Sleep before checking again


# --- Process image using YOLOv8 ---
def analyze_image(image_path, lat, lon, save_path):
    results = model(image_path)
    detections = []

    # 👇 إنشاء مجلد للحفر المكتشفة داخل save_path
    detections_path = f"{save_path}/detected_potholes"
    os.makedirs(detections_path, exist_ok=True)

    # 👇 تحميل الصورة الأصلية لرسم التعديلات عليها
    img = cv2.imread(image_path)
    confidence_text = f""
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # تحويل القيم إلى أعداد صحيحة
            confidence = float(box.conf[0])
            label = model.names[int(box.cls[0])]
            print(f"🔍 {label} with confidence {confidence:.3f}")

            if confidence > 0.25:
                # 👇 إضافة المعلومات إلى القائمة
                detections.append({
                    "image": image_path,
                    "coordinates": {"latitude": lat, "longitude": lon},
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "label": label
                })

                # 🖼️ رسم البوكس على الصورة
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                text = f"{label}: {confidence:.2f}"
                cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                confidence_text = f"Confidence: {confidence:.2f}"

    # 👇 إضافة التاريخ، الإحداثيات والثقة أسفل الصورة

    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    coords_text = f"Lat: {lat:.6f}, Lon: {lon:.6f}"

    # إعداد النصوص في الأسفل
    bottom_text = f"Date: {date_time} | {coords_text} | {confidence_text}"

    # 👇 كتابة النص في أسفل الصورة
    cv2.putText(img, bottom_text, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Drone Live", img)
    # 👇 حفظ الصور التي تحتوي على حفر في مجلد منفصل
    if detections:
        json_path = f"{save_path}/detections.json"
        with open(json_path, "a") as json_file:
            json.dump(detections, json_file, indent=4)

        # 👇 حفظ الصورة المعدلة في مجلد detected_potholes
        new_img_path = f"{detections_path}/{os.path.basename(image_path)}"
        cv2.imwrite(new_img_path, img)  # ✅ حفظ الصورة بعد التعديل

        print(f"✅ Pothole detected! Image saved in {new_img_path}")


# --- Record video and capture images continuously ---
async def record_video(drone):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = f"data/{timestamp}"  # Path to store frames
    os.makedirs(save_path, exist_ok=True)

    cap = cv2.VideoCapture("vid1.webm")
    if not cap.isOpened():
        print("❌ Failed to open video file! Skipping video-related tasks.")
        return  # Skip video processing if the file cannot be opened

    frame_count = 0
    frame_skip = 5  # 👈 عدد الفريمات التي سنتخطاها قبل التحليل

    # Continuously record and analyze frames from the video

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # 👇 تحليل فريم واحد كل frame_skip فريمات
        if frame_count % frame_skip == 0:
            # if True:
            img_path = f"{save_path}/frame_{frame_count}.jpg"
            cv2.imwrite(img_path, frame)
            print(f"📸 Image saved: {img_path}")

            # Get current position of the drone
            async for position in drone.telemetry.position():
                lat, lon = position.latitude_deg, position.longitude_deg
                break  # نأخذ أول قيمة فقط ثم نخرج من الحلقة

                frame = analyze_image_live(frame, lat, lon)  # 🔥 تحديث الصورة مباشرة

            # 👇 عرض الفيديو في نافذة

            # 👇 خروج عند الضغط على Q
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                # Analyze the image and detect potholes or issues
            # cv2.imshow("Drone Live", frame)
            analyze_image(img_path, lat, lon, save_path)

        frame_count += 1
        # await asyncio.sleep(1)  # Simulate real-time capture

    cap.release()


def analyze_image_live(frame, lat, lon):
    results = model(frame)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            label = model.names[int(box.cls[0])]

            if confidence > 0.50:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                text = f"{label}: {confidence:.2f}"
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                bottom_text = f"Date: {date_time} | Lat: {lat:.6f}, Lon: {lon:.6f}"
                cv2.putText(frame, bottom_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)

    return frame


# --- Main function ---
async def main():
    waypoints = load_mission()
    drone = System()

    print("🔗 Connecting to drone...")
    await drone.connect(system_address="udp://:14540")

    print("✅ Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Drone connected!")
            break

    print("✅ Waiting for GPS readiness...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("✅ GPS is ready!")
            break

    print("🚀 Taking off...")
    # print(await drone.param.get_all_params())
    await drone.action.arm()
    # await drone.param.set_param_float("MIS_TAKEOFF_ALT", 2.5)
    await drone.action.takeoff()
    await asyncio.sleep(5)

    # Run the tasks asynchronously without waiting for camera
    await asyncio.gather(
        setup_mission(drone, waypoints),  # Continue mission setup and execution
        record_video(drone)  # Continue video recording and analysis (video from file)
    )


if __name__ == "__main__":
    asyncio.run(main())
