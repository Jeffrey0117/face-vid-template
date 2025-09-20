from PIL import Image, ImageDraw, ImageFont
import os

# 創建 assets 資料夾
if not os.path.exists('assets'):
    os.makedirs('assets')

# 創建一個簡單的圖標
img = Image.new('RGBA', (256, 256), color='#2563eb')
draw = ImageDraw.Draw(img)

# 繪製文字
try:
    # 嘗試使用系統字體
    font = ImageFont.truetype("arial.ttf", 60)
except:
    # 使用預設字體
    font = ImageFont.load_default()

# 在圖標中心繪製文字
text = "剪映"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
position = ((256 - text_width) // 2, (256 - text_height) // 2)
draw.text(position, text, fill='white', font=font)

# 保存為 ICO 檔案
img.save('assets/icon.ico', format='ICO', sizes=[(256, 256)])
print("圖標檔案已創建: assets/icon.ico")