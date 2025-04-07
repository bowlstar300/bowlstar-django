# create_bowler_excel.py
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import django

# Django環境設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bowling_site.settings')
django.setup()

# ベースURL
detail_base_url = "https://www.jpba1.jp/player1/detail.html?id="

# 写真フォルダ（直下）
photo_dir = r"C:\Users\bowls\bowling_site\photos"

def get_bowler_name(license_no):
    url = f"{detail_base_url}{license_no}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"取得失敗: {license_no}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    name_tag = soup.find('span', class_='name')
    return name_tag.text.strip() if name_tag else None

# 写真ファイルからデータ収集
data = []
for filename in os.listdir(photo_dir):
    if filename.endswith('.jpg'):
        license_no = filename.replace('.jpg', '')  # 'F00000002.jpg' -> 'F00000002'
        name = get_bowler_name(license_no)
        if name:
            data.append({
                'license_no': license_no,
                'name': name,
                'photo': filename  # 'F00000002.jpg'（photos/なし）
            })
            print(f"取得成功: {license_no} - {name}")
        else:
            print(f"名前取得失敗: {license_no}")

# エクセルに保存
df = pd.DataFrame(data)
output_path = r"C:\Users\bowls\bowling_site\bowlers.xlsx"
df.to_excel(output_path, index=False)
print(f"エクセル保存完了: {output_path}")