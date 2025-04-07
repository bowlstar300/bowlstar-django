import requests
from bs4 import BeautifulSoup
import os
import time
import django
from django.conf import settings

# Django環境設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bowling_site.settings')
django.setup()

from scores.models import Score

# ベースURL
detail_base_url = "https://www.jpba1.jp/player1/detail.html?id="

# 保存先ディレクトリ（MEDIA_ROOT/photos/）
photo_dir = settings.MEDIA_ROOT
if not os.path.exists(photo_dir):
    os.makedirs(photo_dir)

# ライセンス番号範囲
female_range = range(1, 626)  # F00000001〜F00000625
male_range = range(1, 1477)  # M00000001〜M00001476

def scrape_and_save_bowler(license_no):
    url = f"{detail_base_url}{license_no}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"取得失敗: {license_no}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 名前
    name_tag = soup.find('span', class_='name')
    name = name_tag.text.strip() if name_tag else None
    if not name:
        print(f"名前なし: {license_no}")
        return None
    
    # 写真URL
    photo_div = soup.find('div', class_='detail-header__photo-pic')
    photo_url = None
    if photo_div:
        img_tag = photo_div.find('img')
        photo_url = img_tag['src'] if img_tag else None
        if photo_url and not photo_url.startswith('http'):
            photo_url = "https://www.jpba1.jp" + photo_url
    
    if not photo_url:
        print(f"写真なし: {license_no}")
        return None
    
    # 写真をローカルに保存
    photo_filename = f"{license_no}.jpg"  # ファイル名だけ
    photo_path = os.path.join(photo_dir, photo_filename)
    if not os.path.exists(photo_path):
        img_response = requests.get(photo_url)
        if img_response.status_code == 200:
            with open(photo_path, 'wb') as f:
                f.write(img_response.content)
            print(f"写真保存: {photo_filename}")
        else:
            print(f"写真ダウンロード失敗: {license_no}")
            return None
    
    # データベースに保存（photos/なし）
    bowler, created = Score.objects.get_or_create(
        license_no=license_no,
        defaults={
            'name': name,
            'photo': photo_filename  # ここでphotos/を入れない
        }
    )
    if created:
        print(f"登録完了: {license_no} - {name}")
    else:
        print(f"既に存在: {license_no}")
    
    return bowler

# 既存データクリア（必要ならコメントアウト）
# Score.objects.all().delete()

# 女子選手
for i in female_range:
    license_no = f"F{str(i).zfill(8)}"  # F00000001形式
    scrape_and_save_bowler(license_no)
    time.sleep(1)  # サーバー負荷軽減

# 男子選手
for i in male_range:
    license_no = f"M{str(i).zfill(8)}"  # M00000001形式
    scrape_and_save_bowler(license_no)
    time.sleep(1)

print("全ての選手の登録が完了しました！")