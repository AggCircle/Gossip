import datetime
import json
import logging
import requests

from django.http import JsonResponse


logger = logging.getLogger("server_logger")


ten_heavenly = {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己', 7: '庚', 8: '辛', 9: '壬', 10: '癸'}
terrestrial_branch = {1: '子', 2: '丑', 3: '寅', 4: '卯', 5: '辰', 6: '巳', 7: '午', 8: '未', 9: '申', 10: '酉', 11: '戌', 12: '亥'}
branch_num = {'子': 1, '丑': 2, '寅': 3, '卯': 4, '辰': 5, '巳': 6, '午': 7, '未': 8, '申': 9, '酉': 10, '戌': 11, '亥': 12}
heavenly_num = {'甲': 1, '乙': 2, '丙': 3, '丁': 4, '戊': 5, '己': 6, '庚': 7, '辛': 8, '壬': 9, '癸': 10}

def get_hour_branch(suici, hour):
    rg_num = heavenly_num[suici.split(' ')[-1][0]]
    sz_num = (hour + 1) // 2 + 1
    sg_num = (rg_num * 2 + sz_num - 2) % 10
    return ten_heavenly[sg_num] + terrestrial_branch[sz_num % 12]


def get_eight_characters(request):
    birth = request.GET.get('birth')  # 生日datetime类型 ‘1991-10-21 21:14:04’
    birth_datetime = datetime.datetime.strptime(birth, "%Y-%m-%d %H:%M:%S")
    hour = birth_datetime.hour
    date = birth.split(' ')[0].replace('-', '')
    try:
        res = requests.get(f'http://tools.2345.com/frame/api/GetLunarInfo?date={date}')
        res_dic = json.loads(res.text)
        suici = res_dic['html']['suici']
        hour_gz = get_hour_branch(suici, hour)
        suici_all = f'{suici} {hour_gz}时'

        data = {'gongli':res_dic['html']['gongli'],
                'nongli': res_dic['html']['nongli'],
                'wuxing': res_dic['html']['wuxing'],
                'suici': suici_all}
    except Exception as e:
        logger.error(f'Get calendar error: {e}')


    return JsonResponse({'code': 0, 'msg': 'success', 'data': data})
