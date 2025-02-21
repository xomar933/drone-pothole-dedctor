# مشروع الدرون لكشف جودة الطرق باستخدام الذكاء الاصطناعي

## وصف المشروع

يهدف هذا المشروع إلى استخدام طائرة درون مزودة بكاميرا ونموذج ذكاء اصطناعي لتحليل جودة الطرق واكتشاف الحفر تلقائيًا. يعتمد المشروع على مكتبة **MAVSDK** للتحكم في الطائرة ونموذج **YOLOv8** لاكتشاف الحفر في الصور الملتقطة أثناء الرحلة.

## مميزات المشروع
- **أتمتة الفحص البصري للطرق** باستخدام الدرون.
- **تحليل الصور مباشرة أثناء الطيران** باستخدام YOLOv8.
- **تحديد إحداثيات الحفر تلقائيًا** وربطها ببيانات الصور.
- **تحميل مسار الطيران من QGroundControl** وتنفيذ المهمة تلقائيًا.
- **تخزين نتائج الفحص في ملف JSON** يحتوي على معلومات عن الحفر المكتشفة.

## آلية عمل المشروع
1. تحميل مسار الطيران من ملف `.plan` الذي يتم إنشاؤه عبر **QGroundControl**.
2. تشغيل الدرون باستخدام **MAVSDK** وتنفيذ المسار المحدد.
3. تسجيل فيديو أثناء الرحلة وحفظ الإطارات المهمة.
4. تحليل الإطارات باستخدام **YOLOv8** لاكتشاف الحفر.
5. عند اكتشاف حفرة:
   - يتم حفظ صورة الحفرة مع تحديدها بإطار.
   - يتم حفظ إحداثيات الحفرة ومعلوماتها في ملف JSON.
   - يتم عرض الفيديو مع الإطارات المحددة للحفر.
6. عند انتهاء المهمة، يتم حفظ جميع البيانات وتحليلها لرفع التقارير.

## التدريب واستخدام النموذج
تم تدريب نموذج YOLOv8 باستخدام مجموعة بيانات تحتوي على صور لحفر الطرق. إذا كنت ترغب في إعادة تدريب النموذج، يمكنك استخدام الأدوات التالية:
1. جمع بيانات جديدة وإضافتها إلى **مجموعة البيانات**.
2. استخدام **Ultralytics YOLOv8** في تدريب النموذج (شاهد ملف train.py المرفق) .
3. ضبط المعلمات وتحسين دقة النموذج.

### رابط مجموعة البيانات:
يمكنك تحميل مجموعة البيانات من الرابط التالي: [https://public.roboflow.com/object-detection/pothole]

---

# Road Quality Inspection Drone Using AI

## Project Description

This project leverages a drone equipped with a camera and an AI model to automatically inspect road quality and detect potholes. The project utilizes **MAVSDK** for drone control and **YOLOv8** for pothole detection in captured images.

## Features
- **Automated road inspection** using a drone.
- **Real-time image analysis during flight** using YOLOv8.
- **Automatic pothole location detection** with geotagging.
- **Loading flight missions from QGroundControl** for automated execution.
- **Storing inspection results in a JSON file** with pothole details.

## How It Works
1. Load the flight path from a `.plan` file created via **QGroundControl**.
2. Execute the mission using **MAVSDK**, controlling the drone autonomously.
3. Record video during the flight and save relevant frames.
4. Analyze frames using **YOLOv8** to detect potholes.
5. When a pothole is detected:
   - Save the image with bounding boxes.
   - Store the pothole coordinates and details in a JSON file.
   - Display the video with detections marked.
6. Upon mission completion, all data is stored and analyzed for reporting.

## Training and Model Usage
The YOLOv8 model was trained using a dataset containing road pothole images. If you wish to retrain the model, follow these steps:
1. Collect new data and add it to the **dataset**.
2. Train the model using **Ultralytics YOLOv8** (attached on train.py ).
3. Adjust parameters to improve detection accuracy.

### Dataset Link:
Download the dataset from the following link: [https://public.roboflow.com/object-detection/pothole]

