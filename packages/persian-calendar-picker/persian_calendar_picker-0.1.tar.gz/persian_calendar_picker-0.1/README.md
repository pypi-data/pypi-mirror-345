مطمئناً! این نمونه فایل `README.md` را می‌توانید مستقیماً کپی کنید:

```
# Persian Calendar Picker 📅

## معرفی
**Persian Calendar Picker** یک ویجت انتخاب تاریخ شمسی برای **Tkinter** است که به شما امکان انتخاب تاریخ شمسی با طراحی زیبا و کاربرپسند را می‌دهد.

## ویژگی‌ها ✅
- نمایش تقویم شمسی با طراحی زیبا
- امکان تغییر ماه‌ها و انتخاب روزها
- هایلایت تاریخ روز جاری
- مناسب برای برنامه‌های پایتونی با رابط گرافیکی Tkinter

## نصب 📥
برای نصب این پکیج از دستور زیر استفاده کنید:
```
pip install persian_calendar_picker
```

## نحوه استفاده 🛠
```python
import tkinter as tk
from persian_calendar_picker.calendar import PersianCalendar

def on_date_selected(date):
    print(f"تاریخ انتخاب شده: {date}")

root = tk.Tk()
calendar = PersianCalendar(root, callback=on_date_selected)
root.mainloop()
```

## مشارکت 🤝
اگر قصد دارید در بهبود این پروژه کمک کنید، می‌توانید **Pull Request** ارسال کنید یا در بخش **Issues** مشکلات را گزارش دهید.

## مجوز 📜
این پروژه تحت مجوز **MIT** منتشر شده است. استفاده، تغییر و انتشار آن برای عموم آزاد است.

---