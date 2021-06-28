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
wx_gz = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火', '未': '土', '申': '金',
         '酉': '金', '戌': '土', '亥': '水', '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
         '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
ny_wx = {'甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火', '戊辰': '大林木', '己巳': '大林木',
         '庚午': '路旁土', '辛未': '路旁土', '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
         '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土', '庚辰': '白腊金', '辛巳': '白腊金',
         '壬午': '杨柳木', '癸未': '杨柳木', '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
         '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木', '壬辰': '长流水', '癸巳': '长流水',
         '甲午': '沙中金', '乙未': '沙中金', '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
         '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金', '甲辰': '佛灯火', '乙巳': '佛灯火',
         '丙午': '天河水', '丁未': '天河水', '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
         '壬子': '桑拓木', '癸丑': '桑拓木', '甲寅': '大溪水', '乙卯': '大溪水', '丙辰': '沙中土', '丁巳': '沙中土',
         '戊午': '天上火', '己未': '天上火', '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水'}


def get_hour_branch(suici, hour):
    rg_num = heavenly_num[suici.split(' ')[-1][0]]
    sz_num = (hour + 1) // 2 + 1
    sg_num = (rg_num * 2 + sz_num - 2) % 10
    if sz_num > 12:
        sz_num = sz_num % 12
    return ten_heavenly[sg_num] + terrestrial_branch[sz_num]


def get_wx_sz(all_suici):
    sz = f'{wx_gz[all_suici[0]]}{wx_gz[all_suici[1]]} {wx_gz[all_suici[5]]}{wx_gz[all_suici[6]]}' \
         f' {wx_gz[all_suici[9]]}{wx_gz[all_suici[10]]} {wx_gz[all_suici[13]]}{wx_gz[all_suici[14]]}'
    return sz


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
        sz = get_wx_sz(suici_all)

        data = {'gongli':res_dic['html']['gongli'],
                'nongli': res_dic['html']['nongli'],
                'suici': suici_all, 'sz': sz,
                'rg': sz[6],
                'ny': ny_wx[suici[:2]]}
        return JsonResponse({'code': 0, 'msg': 'success', 'data': data})
    except Exception as e:
        logger.error(f'Get calendar error: {e}')

    return JsonResponse({'code': 1, 'msg': 'error'})
