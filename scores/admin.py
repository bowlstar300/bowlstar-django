from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Score
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# 名前の変換ルール（辞書形式で管理）
NAME_CONVERSIONS = {
    "ブライアングリーンウッド": "BrianGreenwood",
    "徳久恵大": "德久恵大",
}

def normalize_name(raw_name):
    """名前を正規化する関数。特殊な変換ルールを適用"""
    raw_name = raw_name.strip() if raw_name else ""
    return NAME_CONVERSIONS.get(raw_name, raw_name)

def generate_amateur_license():
    """アマチュア用のライセンスナンバーを生成"""
    from random import randint
    while True:
        license_no = f"A{randint(10000000, 99999999)}"
        if not Score.objects.filter(license_no=license_no).exists():
            return license_no

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('license_no', 'name', 'gender', 'shift', 'total', 'photo')
    actions = ['upload_master_data', 'upload_score_data']

    def upload_master_data(self, request, queryset=None):
        if request.method == 'POST' and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            df = df.replace({pd.NA: None, float('nan'): None})
            logger.debug(f"マスターデータ最初の5行: {df.head().to_dict()}")

            Score.objects.all().delete()  # 初回全削除

            processed_count = 0
            for index, row in df.iterrows():
                try:
                    license_no = str(row['license_no']).strip()
                    raw_name = row.get('name', '')
                    gender = row.get('gender', 'M').upper()
                    shift = row.get('shift', 'A').upper()
                    if not raw_name or not license_no:
                        logger.warning(f"名前またはlicense_noなし、スキップ: 行={index}")
                        continue
                    photo_path = f"photos/{row.get('photo', f'{license_no}.jpg')}"

                    logger.debug(f"マスター処理中: license_no={license_no}, name={raw_name}, gender={gender}, shift={shift}")

                    score_data = {
                        'name': raw_name,
                        'gender': gender,
                        'shift': shift,
                        'total': 0,
                        'game1': 0,
                        'game2': 0,
                        'game3': 0,
                        'game4': 0,
                        'game5': 0,
                        'game6': 0,
                        'game7': 0,
                        'game8': 0,
                        'game9': 0,
                        'game10': 0,
                        'game11': 0,
                        'game12': 0,  # game13, game14を削除
                        'photo': photo_path,
                    }

                    Score.objects.update_or_create(
                        license_no=license_no,
                        defaults=score_data
                    )
                    processed_count += 1
                except Exception as e:
                    logger.error(f"マスターエラー: license_no={license_no}, name={raw_name}, 詳細={str(e)}")
                    continue

            self.message_user(request, f"マスターデータが正常にアップロードされました。{processed_count}人処理済み。")
            return HttpResponseRedirect('/admin/scores/score/')

        return render(request, 'admin/upload_excel.html', {'opts': self.model._meta})

    def upload_score_data(self, request, queryset=None):
        if request.method == 'POST' and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            df = df.replace({pd.NA: None, float('nan'): None})
            logger.debug(f"スコアデータ最初の5行: {df.head().to_dict()}")

            processed_count = 0
            for index, row in df.iterrows():
                try:
                    raw_name = row.get('name', '')
                    if not raw_name:
                        logger.warning(f"名前なし、スキップ: 行={index}")
                        continue
                    normalized_name = normalize_name(raw_name)
                    gender = row.get('gender', 'M').upper()
                    shift = row.get('shift', 'A').upper()

                    logger.debug(f"スコア処理中: raw_name={raw_name}, normalized_name={normalized_name}, gender={gender}, shift={shift}")

                    score_data = {
                        'total': int(row.get('TOTAL', 0) or 0),
                        'game1': int(row.get('G1', 0) or 0),
                        'game2': int(row.get('G2', 0) or 0),
                        'game3': int(row.get('G3', 0) or 0),
                        'game4': int(row.get('G4', 0) or 0),
                        'game5': int(row.get('G5', 0) or 0),
                        'game6': int(row.get('G6', 0) or 0),
                        'game7': int(row.get('G7', 0) or 0),
                        'game8': int(row.get('G8', 0) or 0),
                        'game9': int(row.get('G9', 0) or 0),
                        'game10': int(row.get('G10', 0) or 0),
                        'game11': int(row.get('G11', 0) or 0),
                        'game12': int(row.get('G12', 0) or 0),  # game13, game14を削除
                        'gender': gender if gender in ['M', 'F'] else 'M',
                        'shift': shift if shift in ['A', 'B'] else 'A',
                    }

                    try:
                        score = Score.objects.get(name=normalized_name)
                        # 既存選手のスコア更新
                        score.total = score_data['total']
                        score.game1 = score_data['game1']
                        score.game2 = score_data['game2']
                        score.game3 = score_data['game3']
                        score.game4 = score_data['game4']
                        score.game5 = score_data['game5']
                        score.game6 = score_data['game6']
                        score.game7 = score_data['game7']
                        score.game8 = score_data['game8']
                        score.game9 = score_data['game9']
                        score.game10 = score_data['game10']
                        score.game11 = score_data['game11']
                        score.game12 = score_data['game12']  # game13, game14を削除
                        score.gender = score_data['gender']
                        score.shift = score_data['shift']
                        score.save()
                        logger.debug(f"名前でスコア更新: {score.license_no} - {normalized_name}")
                    except Score.DoesNotExist:
                        # 新規アマチュア登録
                        score_data['license_no'] = generate_amateur_license()
                        score_data['name'] = normalized_name
                        score_data['photo'] = None
                        Score.objects.create(**score_data)
                        logger.debug(f"新規アマチュア登録: {score_data['license_no']} - {normalized_name}")
                    except Score.MultipleObjectsReturned:
                        logger.error(f"複数一致: name={normalized_name}, スキップ")
                        continue

                    processed_count += 1

                except Exception as e:
                    logger.error(f"スコアエラー: name={raw_name}, 詳細={str(e)}")
                    continue

            self.message_user(request, f"スコアが正常にアップロードされました。{processed_count}人処理済み。")
            return HttpResponseRedirect('/admin/scores/score/')

        return render(request, 'admin/upload_excel.html', {'opts': self.model._meta})

    upload_master_data.short_description = "マスターデータをアップロード"
    upload_score_data.short_description = "スコアデータをアップロード"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload_master/', self.upload_master_data, name='upload_master_data'),
            path('upload_scores/', self.upload_score_data, name='upload_score_data'),
        ]
        return custom_urls + urls