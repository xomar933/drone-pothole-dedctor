# سوي مشروع ثم
# شفل الامر لتثبيت الاشياء المطلوبه
# pip install ultralytics opencv-python tqdm


from ultralytics import YOLO

# تحميل نموذج YOLOv8n الأساسي
model = YOLO("pothole.pt")

# تدريب النموذج على مجموعة بيانات الحفر
model.train(
    data="data.yaml",   # مسار ملف البيانات المشروحة
    epochs=50,          # عدد مرات التدريب (epochs)
    imgsz=640,          # حجم الصور
    batch=16,           # حجم الدفعة التدريبية
    device="cuda"       # استخدم كرت الشاشة إذا كان متاحًا او ضعها على "cpu" إذا كان لا يوجد
)

# حفظ النموذج بعد التدريب
model.save("pothole.pt")  # حفظ النموذج النهائي بالاسم المطلوب
