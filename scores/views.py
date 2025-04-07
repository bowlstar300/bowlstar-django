from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from .models import Score

def index(request):
    return HttpResponse("スコア管理ページへようこそ！")

def score_list(request):
    # フィルタを削除して全選手を取得
    all_scores = Score.objects.all()
    
    # 全員のデータがない場合
    if not all_scores:
        return render(request, 'scores/score_list.html', {
            'male_a_scores': [], 'male_b_scores': [], 'male_all_scores': [],
            'female_a_scores': [], 'female_b_scores': [], 'female_all_scores': [],
            'current_game': 0
        })

    # 現在のゲーム数を計算（0でも表示するので影響なし）
    current_game = max(score.games_played() for score in all_scores) if all_scores else 0

    # 男女シフト別スコア（フィルタ済みのall_scoresを使う）
    male_a_scores = [s for s in all_scores if s.gender == 'M' and s.shift == 'A']
    male_b_scores = [s for s in all_scores if s.gender == 'M' and s.shift == 'B']
    male_all_scores = [s for s in all_scores if s.gender == 'M']
    female_a_scores = [s for s in all_scores if s.gender == 'F' and s.shift == 'A']
    female_b_scores = [s for s in all_scores if s.gender == 'F' and s.shift == 'B']
    female_all_scores = [s for s in all_scores if s.gender == 'F']

    def process_scores(scores, final_border_idx, semi_border_idx):
        # total降順、ハイローの差分昇順でソート
        sorted_scores = sorted(scores, key=lambda x: (-x.total, x.game_high_low_diff() or float('inf')))
        top_total = sorted_scores[0].total if sorted_scores else 0
        final_border_total = sorted_scores[7].total if len(sorted_scores) > 7 else 0
        semi_border_total = sorted_scores[semi_border_idx].total if len(sorted_scores) > semi_border_idx else 0

        scores_with_games = []
        for i, score in enumerate(sorted_scores, 1):
            data = {
                'obj': score,
                'games_played': score.games_played(),
                'diff': score.total - (score.games_played() * 200),
            }
            if i == 1:
                data['top_diff'] = 0
            elif 2 <= i <= 8:
                data['top_diff'] = top_total - score.total
            elif 9 <= i <= semi_border_idx + 1:
                data['final_border_diff'] = final_border_total - score.total
            else:
                data['semi_border_diff'] = semi_border_total - score.total
            scores_with_games.append(data)
        return scores_with_games

    # 男子45位、女子30位に準決勝枠を更新
    male_a_processed = process_scores(male_a_scores, 7, 44)  # 8位決勝、45位準決
    male_b_processed = process_scores(male_b_scores, 7, 44)
    male_all_processed = process_scores(male_all_scores, 7, 44)
    female_a_processed = process_scores(female_a_scores, 7, 29)  # 8位決勝、30位準決
    female_b_processed = process_scores(female_b_scores, 7, 29)
    female_all_processed = process_scores(female_all_scores, 7, 29)

    return render(request, 'scores/score_list.html', {
        'male_a_scores': male_a_processed,
        'male_b_scores': male_b_processed,
        'male_all_scores': male_all_processed,
        'female_a_scores': female_a_processed,
        'female_b_scores': female_b_processed,
        'female_all_scores': female_all_processed,
        'current_game': current_game
    })

def upload_scores(request):
    if request.method == 'POST':
        file = request.FILES['file']
        df = pd.read_excel(file).fillna(0)
        
        for _, row in df.iterrows():
            license_no = str(row.get('license_no', '')).strip()  # ライセンスナンバー
            name = row.get('name', '').strip()
            gender = row.get('gender', 'M').upper()
            shift = row.get('shift', 'A').upper()
            total = row.get('TOTAL', 0)
            score_data = {
                'name': name,
                'total': total,
                'gender': gender if gender in ['M', 'F'] else 'M',
                'shift': shift if shift in ['A', 'B'] else 'A',
            }
            # 12ゲームまで対応
            for i in range(1, 13):
                column_name = f'G{i}'
                if column_name in df.columns:
                    score_data[f'game{i}'] = int(row[column_name])
                else:
                    score_data[f'game{i}'] = 0

            # license_noがある場合
            if license_no and Score.objects.filter(license_no=license_no).exists():
                Score.objects.update_or_create(
                    license_no=license_no,
                    defaults=score_data
                )
            # license_noがない場合
            else:
                try:
                    # 名前で既存選手を検索
                    score = Score.objects.get(name=name)
                    # スコア更新
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
                    score.game12 = score_data['game12']
                    score.save()
                except Score.DoesNotExist:
                    # 名前が一致しない場合、新規アマチュア登録
                    score_data['license_no'] = generate_amateur_license()
                    Score.objects.create(**score_data)

        return HttpResponse("アップロード完了！")
    return render(request, 'upload.html')

def generate_amateur_license():
    """アマチュア用のライセンスナンバーを生成"""
    from random import randint
    while True:
        license_no = f"A{randint(10000000, 99999999)}"  # "A" + 8桁
        if not Score.objects.filter(license_no=license_no).exists():
            return license_no

def mens_final(request):
    return render(request, 'scores/mensfinal.html')

def womens_final(request):
    return render(request, 'scores/womensfinal.html')