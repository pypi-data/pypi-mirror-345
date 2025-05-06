from enum import Enum


class Prefecture(Enum):
    HOKKAIDO = 1
    AOMORI = 2
    IWATE = 3
    MIYAGI = 4
    AKITA = 5
    YAMAGATA = 6
    FUKUSHIMA = 7
    IBARAKI = 8
    TOCHIGI = 9
    GUNMA = 10
    SAITAMA = 11
    CHIBA = 12
    TOKYO = 13
    KANAGAWA = 14
    NIIGATA = 15
    TOYAMA = 16
    ISHIKAWA = 17
    FUKUI = 18
    YAMANASHI = 19
    NAGANO = 20
    GIFU = 21
    SHIZUOKA = 22
    AICHI = 23
    MIE = 24
    SHIGA = 25
    KYOTO = 26
    OSAKA = 27
    HYOGO = 28
    NARA = 29
    WAKAYAMA = 30
    TOTTORI = 31
    SHIMANE = 32
    OKAYAMA = 33
    HIROSHIMA = 34
    YAMAGUCHI = 35
    TOKUSHIMA = 36
    KAGAWA = 37
    EHIME = 38
    KOCHI = 39
    FUKUOKA = 40
    SAGA = 41
    NAGASAKI = 42
    KUMAMOTO = 43
    OITA = 44
    MIYAZAKI = 45
    KAGOSHIMA = 46
    OKINAWA = 47


class Branch(Enum):
    GUNMA = 10
    SAITAMA = 11
    TOKYO = 13
    FUKUI = 18
    SHIZUOKA = 22
    AICHI = 23
    MIE = 24
    SHIGA = 25
    OSAKA = 27
    HYOGO = 28
    OKAYAMA = 33
    HIROSHIMA = 34
    YAMAGUCHI = 35
    TOKUSHIMA = 36
    KAGAWA = 37
    FUKUOKA = 40
    SAGA = 41
    NAGASAKI = 42


class PrefectureFactory:
    @staticmethod
    def create(name: str) -> Prefecture:
        if "北海道" in name:
            return Prefecture.HOKKAIDO
        elif "青森" in name:
            return Prefecture.AOMORI
        elif "岩手" in name:
            return Prefecture.IWATE
        elif "宮城" in name:
            return Prefecture.MIYAGI
        elif "秋田" in name:
            return Prefecture.AKITA
        elif "山形" in name:
            return Prefecture.YAMAGATA
        elif "福島" in name:
            return Prefecture.FUKUSHIMA
        elif "茨城" in name:
            return Prefecture.IBARAKI
        elif "栃木" in name:
            return Prefecture.TOCHIGI
        elif "群馬" in name:
            return Prefecture.GUNMA
        elif "埼玉" in name:
            return Prefecture.SAITAMA
        elif "千葉" in name:
            return Prefecture.CHIBA
        elif "東京" in name:
            return Prefecture.TOKYO
        elif "神奈川" in name:
            return Prefecture.KANAGAWA
        elif "新潟" in name:
            return Prefecture.NIIGATA
        elif "富山" in name:
            return Prefecture.TOYAMA
        elif "石川" in name:
            return Prefecture.ISHIKAWA
        elif "福井" in name:
            return Prefecture.FUKUI
        elif "山梨" in name:
            return Prefecture.YAMANASHI
        elif "長野" in name:
            return Prefecture.NAGANO
        elif "岐阜" in name:
            return Prefecture.GIFU
        elif "静岡" in name:
            return Prefecture.SHIZUOKA
        elif "愛知" in name:
            return Prefecture.AICHI
        elif "三重" in name:
            return Prefecture.MIE
        elif "滋賀" in name:
            return Prefecture.SHIGA
        elif "京都" in name:
            return Prefecture.KYOTO
        elif "大阪" in name:
            return Prefecture.OSAKA
        elif "兵庫" in name:
            return Prefecture.HYOGO
        elif "奈良" in name:
            return Prefecture.NARA
        elif "和歌山" in name:
            return Prefecture.WAKAYAMA
        elif "鳥取" in name:
            return Prefecture.TOTTORI
        elif "島根" in name:
            return Prefecture.SHIMANE
        elif "岡山" in name:
            return Prefecture.OKAYAMA
        elif "広島" in name:
            return Prefecture.HIROSHIMA
        elif "山口" in name:
            return Prefecture.YAMAGUCHI
        elif "徳島" in name:
            return Prefecture.TOKUSHIMA
        elif "香川" in name:
            return Prefecture.KAGAWA
        elif "愛媛" in name:
            return Prefecture.EHIME
        elif "高知" in name:
            return Prefecture.KOCHI
        elif "福岡" in name:
            return Prefecture.FUKUOKA
        elif "佐賀" in name:
            return Prefecture.SAGA
        elif "長崎" in name:
            return Prefecture.NAGASAKI
        elif "熊本" in name:
            return Prefecture.KUMAMOTO
        elif "大分" in name:
            return Prefecture.OITA
        elif "宮崎" in name:
            return Prefecture.MIYAGI
        elif "鹿児島" in name:
            return Prefecture.KAGOSHIMA
        elif "沖縄" in name:
            return Prefecture.OKINAWA
        else:
            raise ValueError


class BranchFactory:
    @staticmethod
    def create(name: str) -> Branch:
        if "群馬" in name:
            return Branch.GUNMA
        elif "埼玉" in name:
            return Branch.SAITAMA
        elif "東京" in name:
            return Branch.TOKYO
        elif "福井" in name:
            return Branch.FUKUI
        elif "静岡" in name:
            return Branch.SHIZUOKA
        elif "愛知" in name:
            return Branch.AICHI
        elif "三重" in name:
            return Branch.MIE
        elif "滋賀" in name:
            return Branch.SHIGA
        elif "大阪" in name:
            return Branch.OSAKA
        elif "兵庫" in name:
            return Branch.HYOGO
        elif "岡山" in name:
            return Branch.OKAYAMA
        elif "広島" in name:
            return Branch.HIROSHIMA
        elif "山口" in name:
            return Branch.YAMAGUCHI
        elif "徳島" in name:
            return Branch.TOKUSHIMA
        elif "香川" in name:
            return Branch.KAGAWA
        elif "福岡" in name:
            return Branch.FUKUOKA
        elif "佐賀" in name:
            return Branch.SAGA
        elif "長崎" in name:
            return Branch.NAGASAKI
        else:
            raise ValueError
