import pytesseract
import cv2
import re

# 1. Rasmni o'qish
image = cv2.imread('check3.jpg')

# 2. Rasmni kulrang (grayscale) formatga o'tkazish
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. Thresholding (agar kerak bo'lsa)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# 4. OCR orqali matnni olish
text = pytesseract.image_to_string(gray)

print("Chekdan o'qilgan matn:")
print(text)

# 5. Summani ajratib olish
summa_match = re.search(r'(\d{1,5}[.,]\d{2})\s*so\'?m', text.lower())
if summa_match:
    summa = summa_match.group(1)
    print(f"Topilgan summa: {summa}")
else:
    print("Summani topib bo'lmadi.")

# 6. Karta raqamini ajratish (masalan, oxirgi 4 raqam)
card_match = re.search(r'\d{4}\s\d{4}\s\d{4}\s\d{4}', text)
if card_match:
    card_number = card_match.group()
    print(f"Topilgan karta raqami: {card_number}")
else:
    print("Karta raqami topilmadi.")
