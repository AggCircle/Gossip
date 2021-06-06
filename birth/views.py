import datetime
from django.http import JsonResponse


ten_heavenly = {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6:'己', 7: '庚', 8: '辛', 9: '壬', 10: '癸'}
terrestrial_branch = {1: '子', 2: '丑', 3: '寅', 4: '卯', 5: '辰', 6: '巳', 7: '午', 8: '未', 9: '申', 10: '酉', 11: '戌', 12: '亥'}


def get_eight_characters(request):
    birth = request.GET.get('birth')  # 生日datetime类型 ‘1991-10-21 21:14:04’
    birth_datetime = datetime.datetime.strptime(birth, "%Y-%m-%d %H:%M:%S")
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day
    hour = birth_datetime.hour

    return JsonResponse({'code': 0, 'msg': 'success', 'data': {}})
