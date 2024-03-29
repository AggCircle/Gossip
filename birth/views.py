import datetime
import json
import logging
import requests

import concurrent.futures as my_futures
from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse

from .models import UserWx, UserDetailInfo, UserComments, LeaveMessage

logger = logging.getLogger("server_logger")
executor = my_futures.ThreadPoolExecutor(max_workers=5)

ten_heavenly = {0: '癸', 1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己', 7: '庚', 8: '辛', 9: '壬', 10: '癸'}
terrestrial_branch = {1: '子', 2: '丑', 3: '寅', 4: '卯', 5: '辰', 6: '巳', 7: '午', 8: '未', 9: '申', 10: '酉',
                      11: '戌', 12: '亥'}
branch_num = {'子': 1, '丑': 2, '寅': 3, '卯': 4, '辰': 5, '巳': 6, '午': 7, '未': 8, '申': 9, '酉': 10, '戌': 11,
              '亥': 12}
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
wx = ['金', '木', '水', '火', '土']


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
    wu_x = [wx_gz[all_suici[0]], wx_gz[all_suici[1]], wx_gz[all_suici[5]], wx_gz[all_suici[6]], wx_gz[all_suici[9]],
            wx_gz[all_suici[10]], wx_gz[all_suici[13]], wx_gz[all_suici[14]]]
    wu_x = list(set(wu_x))
    if len(wu_x) == 5:
        analyse = '您八字中五行诸全，五行不缺'
    else:
        str_wx = ''
        for i in wx:
            if i in wu_x:
                continue
            else:
                if str_wx:
                    str_wx = str_wx + '和' + i
                else:
                    str_wx = i
        analyse = f'您八字中的五行缺{str_wx}'
    return sz, analyse


def insert_birth(user_info):
    logger.info('insert is in')
    user_wx_obj = UserWx.objects.filter(open_id=(user_info.get('open_id') or ''))
    if user_wx_obj:
        UserDetailInfo.objects.create(user_wx=user_wx_obj[0], birth_datetime=user_info['birth'])


def get_eight_characters(request):
    birth = request.GET.get('birth')  # 生日datetime类型 ‘1991-10-21 21:14:04’
    cache_key = birth.replace(' ', '_')
    user_info = request.GET.get('user_info') or '{}'
    user_info = json.loads(user_info)
    open_id = request.GET.get('open_id')
    
    user_info['birth'] = birth
    user_info['open_id'] = open_id
    
    birth_datetime = datetime.datetime.strptime(birth, "%Y-%m-%d %H:%M:%S")
    hour = birth_datetime.hour
    date = birth.split(' ')[0].replace('-', '')
    try:
        eight_characters = cache.get(cache_key)
        if eight_characters:
            return JsonResponse({'code': 0, 'msg': 'success', 'data': json.loads(eight_characters)})
        res = requests.get(f'http://tools.2345.com/frame/api/GetLunarInfo?date={date}')
        res_dic = json.loads(res.text)
        suici = res_dic['html']['suici']
        hour_gz = get_hour_branch(suici, hour)
        suici_all = f'{suici} {hour_gz}时'
        sz, analyse = get_wx_sz(suici_all)
        
        data = {'gongli': res_dic['html']['gongli'],
                'nongli': res_dic['html']['nongli'],
                'suici': suici_all, 'sz': sz,
                'rg': sz[6],
                'ny': ny_wx[suici[:2]],
                'analyse': analyse}
        cache.set(cache_key, json.dumps(data))
        executor.submit(insert_birth, user_info)
        return JsonResponse({'code': 0, 'msg': 'success', 'data': data})
    except Exception as e:
        logger.error(f'Get calendar error: {e}')
    
    return JsonResponse({'code': 1, 'msg': '服务器出错啦，请稍后再试'})


def create_wx_user(request):
    json_template = {}
    res = request.body
    try:
        # 空格判断
        wx_info = json.loads(res)
        wx_user_info = wx_info['user_info']
        open_id = wx_info['open_id']
        wx_user = {
            'nick_name': wx_user_info['nickName'],
            'gender': wx_user_info['gender'],
            'avatar_url': wx_user_info['avatarUrl'],
            'city': wx_user_info['city'],
            'province': wx_user_info['province'],
            'country': wx_user_info['country']
        }
        UserWx.objects.update_or_create(wx_user, open_id=open_id)
        json_template['code'] = 0
        json_template['errMessage'] = '添加成功'
        return JsonResponse(json_template)
    except Exception as e:
        logger.error(str(e))
        json_template['errMessage'] = str(e)
        return JsonResponse(json_template)


def on_login(request):
    json_template = {}
    code = request.GET.get('code')
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid=wx2d8e4398af2b8906&' \
          f'secret=60b344d201b019aaab7b4e6c137115f1&js_code={code}&grant_type=authorization_code'
    try:
        res = requests.get(url)
        res_data = json.loads(res.text)
        UserWx.objects.update_or_create({'open_id': res_data['openid']}, open_id=res_data['openid'])
        json_template['code'] = 0
        json_template['openid'] = res_data['openid']
    except Exception as e:
        logger.error(f'create user error: {e}')
        json_template['code'] = 401
    return JsonResponse(json_template)


def get_user_comments(request):
    json_template = {'code': 0}
    open_id = request.GET.get('open_id')
    comments_data = []
    user_wx = UserWx.objects.filter(open_id=open_id)
    if user_wx:
        if open_id == 'oI35j5R8IyQdGh8s7R2lEBcUCqcg':
            comments_all = UserComments.objects.all().order_by('-id')
        else:
            comments_all = UserComments.objects.filter(Q(user_wx=user_wx[0]) | Q(top_comment=True)).order_by('-id')
        for comment in comments_all:
            data = {'data': {'comment_id': comment.id,
                             'username': comment.user_wx.nick_name,
                             'avatar': comment.user_wx.avatar_url,
                             'txt': comment.txt,
                             'top_comment': comment.top_comment}}
            leave_messages = LeaveMessage.objects.filter(user_comments=comment)
            message_list = []
            if leave_messages:
                for leave_message in leave_messages:
                    message_list.append({'username': leave_message.user_wx.nick_name,
                                         'comment': leave_message.message})
            data['leaveMessage'] = message_list
            if comment.top_comment:
                comments_data.insert(0, data)
            else:
                comments_data.append(data)
        
        json_template['comments'] = comments_data
    
    return JsonResponse(json_template)


def insert_user_comment(request):
    json_template = {'code': 0}
    res = request.body
    comment_info = json.loads(res)
    txt = comment_info['txt']
    open_id = comment_info['open_id']
    if open_id:
        user_wx_obj = UserWx.objects.filter(open_id=open_id)
        UserComments.objects.create(user_wx=user_wx_obj[0], txt=txt)
        json_template['success'] = 'success'
    else:
        json_template['code'] = 1
    return JsonResponse(json_template)


def create_leave_message(request):
    json_template = {'code': 0}
    res = request.body
    message_info = json.loads(res)
    message = message_info['message']
    user_comment = UserComments.objects.filter(id=message_info['comment_id'])
    user_wx_obj = UserWx.objects.filter(open_id=message_info['open_id'])
    if user_comment and user_wx_obj:
        LeaveMessage.objects.create(user_wx=user_wx_obj[0], message=message, user_comments=user_comment[0])
    else:
        json_template['code'] = 1
    return JsonResponse(json_template)


# 获取躲星信息
def avoid_star(request):
    birth = request.GET.get('birth')  # 生日datetime类型 ‘1991-10-21 21:14:04’
    sex = request.GET.get('sex') or 1  # 生日datetime类型 ‘1991-10-21 21:14:04’  0:女  1：男
    if int(sex) == 0:
        start_info = {0: {'star': '计都星', 'time': '正月十八未时（下午1:00-3:00)，面朝西南方躲星', 'destiny': '计都临头不自由，口舌相缠斗不休，坐立不稳要破财，体弱多病有烦忧', 'property': '凶星'},
                      1: {'star': '火德星', 'time': '正月二十九已时（上午9:00-11:00)，面朝东北方躲星', 'destiny': '火星照命心发焦，坐力不安好唠叨，且防小人放暗箭，恶言恶语梦中吵', 'property': '凶星'},
                      2: {'star': '木德星', 'time': '正月二十五卯时（上午5:00一7:00)，木星半凶半吉，宜面朝西南方躲星', 'destiny': '木星照命犯红鸾，有财有喜在当年，不落春天三月里，必定落在秋冬天', 'property': '吉星'},
                      3: {'star': '太阴星', 'time': '正月二十六辰时（上午7:00-9:00)，男要躲星、女要顺星，顺星躲星方向是面朝正西方', 'destiny': '女命太阴不随心，无精打采心发闷，体格软弱常失眠，悠悠荡荡象没魂', 'property': '吉星'},
                      4: {'star': '土德星', 'time': '正月十九申时（下午3:00-5:00)，面朝西北方躲星', 'destiny': '行年执土星，官司来相逢，出入多不顺，提防小人惊', 'property': '中性星'},
                      5: {'star': '罗候星', 'time': '正月初八戌时（晚上7:00-9:00)，面朝南方躲星', 'destiny': '女逢罗侯真不高，步步脚踩独木桥，招惹是非恼不尽，夜里多梦睡不着', 'property': '凶星'},
                      6: {'star': '太阳星', 'time': '正月二十七午时（中午11:00-1:00)，女要躲星、男要顺星，顺星躲星方向是面朝正南方', 'destiny': '女命太阳有灾殃，必有烦恼心发慌，要想免灾须躲星，先生自然有主张', 'property': '吉星'},
                      7: {'star': '金德星', 'time': '正月十五西时（下午5:00-7:00)，面朝东南方躲星', 'destiny': '女命金星最相当，喜中笑中得安康，是非口舌无大患，身体软弱也无妨', 'property': '吉凶参半'},
                      8: {'star': '水德星', 'time': '正月二十一亥时（晚上9:00一11:00)，面朝东方顺星', 'destiny': '水星照命乐自然，夫唱妇随福绵绵。求财望喜不费力，一年可坐顺风船', 'property': '吉星'}}
    else:
        start_info = {6: {'star': '计都星', 'time': '正月十八未时（下午1:00-3:00)，面朝西南方躲星',
                          'destiny': '男命不喜计都来，定有灾祸入你怀，六畜不旺多病患，远行无法去登台', 'property': '凶星'},
                      5: {'star': '火德星', 'time': '正月二十九已时（上午9:00-11:00)，面朝东北方躲星',
                          'destiny': '男遇火星真倒霉，总有烦恼把你随，心焦体弱坐不住，六畜不安须防贼', 'property': '凶星'},
                      8: {'star': '木德星', 'time': '正月二十五卯时（上午5:00一7:00)，木星半凶半吉，宜面朝西南方躲星',
                          'destiny': '木星照命犯红鸾，有财有喜在当年，不落春天三月里，必定落在秋冬天', 'property': '吉星'},
                      7: {'star': '太阴星',
                          'time': '正月二十六辰时（上午7:00-9:00)，男要躲星、女要顺星，顺星躲星方向是面朝正西方',
                          'destiny': '男命逢太阴，名利得随心，办事大吉利，处处听佳音', 'property': '吉星'},
                      1: {'star': '土德星', 'time': '正月十九申时（下午3:00-5:00)，面朝西北方躲星',
                          'destiny': '土星照命小人多，六畜不利有病魔，夜梦妖鬼常失眠，远行谋事定受挫', 'property': '中性星'},
                      0: {'star': '罗候星', 'time': '正月初八戌时（晚上7:00-9:00)，面朝南方躲星',
                          'destiny': '男命遇罗侯，言非口舌有，财宝有人争，颠倒百事忧', 'property': '凶星'},
                      4: {'star': '太阳星',
                          'time': '正月二十七午时（中午11:00-1:00)，女要躲星、男要顺星，顺星躲星方向是面朝正南方',
                          'destiny': '男遇太阳真有理，远行有财人有喜，君子行年遇此星，哭声难以找到你', 'property': '吉星'},
                      3: {'star': '金德星', 'time': '正月十五西时（下午5:00-7:00)，面朝东南方躲星',
                          'destiny': '金星照命不一般，男子能把好运添，添人进口多吉庆，里外喜事乐天然',
                          'property': '吉凶参半'},
                      2: {'star': '水德星', 'time': '正月二十一亥时（晚上9:00一11:00)，面朝东方顺星',
                          'destiny': '男命最喜见水星，财喜双全笑盈盈，添人进口贵人来，富神禄神到门庭', 'property': '吉星'}}
    birth_year = int(birth.split('-')[0])
    index = (datetime.datetime.now().year - birth_year + 1 - 10) % 9
    return JsonResponse({'code': 0, 'msg': 'success', 'data': start_info[index]})
