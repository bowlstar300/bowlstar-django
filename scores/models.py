from django.db import models

class Score(models.Model):
    license_no = models.CharField(max_length=9, unique=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')  # 性別
    shift = models.CharField(max_length=1, choices=[('A', 'Shift A'), ('B', 'Shift B')], default='A')  # シフト
    total = models.IntegerField(default=0)
    game1 = models.IntegerField(default=0)
    game2 = models.IntegerField(default=0)
    game3 = models.IntegerField(default=0)
    game4 = models.IntegerField(default=0)
    game5 = models.IntegerField(default=0)
    game6 = models.IntegerField(default=0)
    game7 = models.IntegerField(default=0)
    game8 = models.IntegerField(default=0)
    game9 = models.IntegerField(default=0)
    game10 = models.IntegerField(default=0)
    game11 = models.IntegerField(default=0)
    game12 = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def games_played(self):
        games = [self.game1, self.game2, self.game3, self.game4, self.game5,
                 self.game6, self.game7, self.game8, self.game9, self.game10,
                 self.game11, self.game12]
        return sum(1 for g in games if g > 0)

    def game_high_low_diff(self):
        """最高スコアと最低スコアの差を返す。プレイ済みゲームがない場合はNone"""
        games = [self.game1, self.game2, self.game3, self.game4, self.game5,
                 self.game6, self.game7, self.game8, self.game9, self.game10,
                 self.game11, self.game12]
        played = [g for g in games if g > 0]
        if not played:
            return None
        return max(played) - min(played)

    def __str__(self):
        return f"{self.license_no} - {self.name} - {self.total}点"