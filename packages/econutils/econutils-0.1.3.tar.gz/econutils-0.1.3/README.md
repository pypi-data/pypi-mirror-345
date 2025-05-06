# econutils

`econutils` เป็น Python utility package ที่ให้ฟังก์ชัน `get_token()`  
สำหรับดึง Token จากระบบเฉพาะของผู้พัฒนา

---

## การติดตั้ง

```bash
pip install econutils
```

## การใช้งาน
```bash
import econutils as eu

token = eu.get_token()
print("Token:", token)
```