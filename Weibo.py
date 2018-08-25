import requests
import os
import json
import time


# todo 修改header
def headers():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Cookie': 'SINAGLOBAL=7218550127685.028.1506059490109; UM_distinctid=1645b1fc666bd1-0d4ab1cac23a3f-47e1039-1fa400-1645b1fc667b5f; login_sid_t=b4fb855a0229710a74e90d806d08be58; cross_origin_proto=SSL; YF-Ugrow-G0=9642b0b34b4c0d569ed7a372f8823a8e; YF-V5-G0=4955da6a9f369238c2a1bc4f70789871; _s_tentry=-; Apache=7073321147433.957.1534920437111; ULV=1534920437118:48:2:1:7073321147433.957.1534920437111:1533107785523; SSOLoginState=1534920455; un=13160672756; wvr=6; YF-Page-G0=70942dbd611eb265972add7bc1c85888; wb_timefeed_1935822083=1; _T_WM=0e9bfa595309176ecb6c05c8573e2fbe; UOR=,,login.sina.com.cn; wb_view_log_1935822083=1920*10801; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhToMOzi.uGPG0expOaU0iE5JpX5KMhUgL.Fo24e0-Reoz71he2dJLoIpjLxKBLBonLBK-LxKqL1heLBK5LxK.L1hML1K2t; ALF=1566656175; SCF=ArFtg-iniCx8enu9rVhXx_FgKz29LuoXdgHpyIae34mJgSNETha5oXnS8tPdJ6FUN1-nPdE0EbgN_xT0irKeysc.; SUB=_2A252hGNhDeRhGedH6FcZ8izMwz-IHXVV8NOprDV8PUNbmtBeLUfzkW9NUKtohmdYD9r6Vv6O2x6PI9c5TFaLeG0N; SUHB=04WvUprA07D7pY',
    }
    return header


def strftime(ttint):
    """转time.time()格式为人类可读"""
    format = '%Y%m%d-%H:%M:%S'
    value = time.localtime(int(ttint))
    dt = time.strftime(format, value)
    return dt


def log(*args, **kwargs):
    """
    写入log.txt文件，带有输出时间
    """
    format = '%Y%m%d-%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, file=f, **kwargs)


class Model(object):
    """打印显示类属性的信息"""

    def __repr__(self):
        name = self.__class__.__name__
        properties = (f'{k}=({v})' for k, v in self.__dict__.items())
        string = '\n '.join(properties)
        s = f'\n<{name} \n {string}>'
        return s


class Weibo(Model):
    def __init__(self):
        self.ct = ''
        self.device = ''
        self.text = ''
        # 被转发数
        self.forward = ''
        # 评论数
        self.comment_c = ''
        if self.comment_c is not 0:
            self.comment_ct = ''
            self.comment = ''
            self.ans_ct = ''
            self.ans_comment = ''

        self.like = ''
        self.photo = ''
        # Todo 转发的内容
        self.expand = ''
        # 新浪的id
        self.id = ''
        self.mid = ''

    def dict_attr(self):
        """
        将属性及值转化为字典
        清除value为空的键值对
        """
        return {name: value
                for name, value in vars(self).items()
                if value is not ''
                if value is not None
                if value is not 0
                }


def write_cached(strs, path):
    """写入数据"""
    with open(path, 'w', encoding='utf-8') as f:
        r = f.write(strs)
        log(f"{path}\n已写入cached")
    return r


def read_cached(path):
    """从缓存中读出json数据"""
    with open(path, 'rb') as f:
        r = json.load(f)
        log(f"{path}\n从cached中读出")
    return r


def weibo_path(url):
    """微博缓存的下载路径"""
    folder = 'cached'
    filename = url.split('=')[-1] + '.txt'
    path = os.path.join(folder, filename)
    return folder, path


def comment_path(url):
    """
    评论缓存的下载路径
    folder: cached\comment
    path: cached\comment\w_id.txt
    """
    folder_f = 'cached'
    folder_c = 'comment'
    folder = os.path.join(folder_f, folder_c)
    # print(folder)
    filename = url.split('id=')[-2].split('&')[0] + '.txt'
    # print(filename)
    path = os.path.join(folder, filename)
    # print(path)
    return folder, path


def cached_page(url, folder, path):
    """
    下载微博ajax的json数据
    :url:weibo ajax api
    :return:json.loads()的字典格式
    """
    # 如果没有'cached'目录则创建
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 已下载则直接读出，数据有时效性
    if os.path.exists(path):
        r = read_cached(path)
        return r

    # 连接上网站，获取数据
    else:
        r = requests.get(url, headers=headers())
        # print('r', type(r), r.content)
        time.sleep(3)
        log('every connecting', r)
        log(f"向url请求数据,暂停3秒,\n{url}")

    # 判断Json中包含 s 则不保存,微博数据如果没有了 会包含s，
    # 评论数据如果没有了则只有一个key，json长度为8
    s = bytes('这里还没有内容', encoding='unicode_escape')
    if s not in r.content and r.status_code != 400 and len(r.content) >= 10:
        # 转成json,再转成字典，再转回json
        # 实现json的缩进，方便阅读，后期取出数据，可删后一行
        # print(type(r.content))

        # Debug: 'utf-8' codec can't decode byte 0xd0
        # Debug: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        # 一是： 评论的数据没有，返回的不是json，是document  #<Response [400]>
        # 二是： cookie过时了
        log('before wring cached', r.status_code)
        # print(url)
        # print(res)
        js = json.loads(r.content)
        j = json.dumps(dict(js), indent=4, ensure_ascii=False)

        # 写入数据
        write_cached(j, path)
        return js
    else:
        print('内容下载完成,或无法解析')


def who_say(data):
    """如果评论者有备注，显示备注名，否则显示用户名"""
    whoSay = data['user']['screen_name']
    # print(data['user'].keys())
    if 'remark' in data['user']:
        whoSay = data['user']['remark']
    return whoSay


def answer_comment_clean(ans_comment):
    """
    传入完始的comment数据，html格式
    筛选出干净的comment
    """
    ans_comment1 = ans_comment.split('<a')[0]
    ans_comment2 = ans_comment.split('>')[1].split('<')[0]
    ans_comment3 = ans_comment.split('/a>')[-1]
    ans_comment32 = ans_comment3.split('<')[0]

    # 取出链接
    ans_comment4 = ''
    if ' src="' in ans_comment3:
        ans_comment4 = ans_comment3.split(' src="')[1].split('"')[0]
    ans_comment = ans_comment1 + ans_comment2 + ans_comment32 + ans_comment4

    return ans_comment


def answer_comments(data):
    """
    对评论回覆，相互回覆的内容
    返回[{time: say}]的列表
    """
    if data['comments']:
        n = len(data['comments'])
        ans_cts = []
        ans_comments = []
        for i in range(n):
            ans_ct = data['comments'][i]['created_at']
            ans_comment_dirty = data['comments'][i]['text']

            # 筛选出干净的ans_comments
            ans_comment = answer_comment_clean(ans_comment_dirty)
            # print(ans_comment, '\n\n')
            ans_cts.append(ans_ct)
            ans_comments.append({ans_ct: ans_comment})
    else:
        ans_comments = None
        ans_cts = None
    # 返回ans_ct 作为属性,用于索引comments
    return ans_cts, ans_comments


def get_comment(w_id, w_mid):
    """
    获取评论
    转发的内容，评论的内容(id作为url的一部分，在另一json中)
    """
    url = f'https://m.weibo.cn/comments/hotflow?id={w_id}&mid={w_mid}&max_id_type=0'
    print('have comment_count\'s url', url)
    # r = requests.get(url, headers()).content
    # jsons = json.loads(r)

    # down_comment()
    # TODO 排除是否被封了，无法获取评论
    # 下载评论的数据进cache\comment
    folder, path = comment_path(url)
    jsons = cached_page(url, folder, path)

    # 有评论数而无评论时
    # print(len(jsons), jsons)

    # 返回格式
    if jsons is None or len(jsons) <= 1:
        log(f'评论被删除了,\n{url}')
        return '评论被删除了'

    data = jsons['data']['data'][0]

    ct = data['created_at']
    whoSay = who_say(data)
    comment = data['text']
    # 互评互答的时间与内容
    ans_cts, ans_comments = answer_comments(data)
    return [(ct, whoSay, comment), ans_cts, ans_comments]


def split_to_link(str, weibo_dict):
    """
    分割出链接的字符串，如href=".*?",src=".*?"
    """
    texts = weibo_dict['text'].split('<', 1)
    text2 = texts[1].split(str, 1)[1].split('"')[0]
    link = text2
    return link


def weibo_text_clean(w, weibo_dict):
    """
    :param w: Weibo的对象
    :param weibo_dict: 从json内刨出来的,关于微博内容的字典
    :return: 清除html的内容的净化w.text
    """
    # 清除text后面的四个空格
    if ' ​​​' in weibo_dict['text']:
        text = weibo_dict['text'].split(' ​​​', 1)[0] + weibo_dict['text'].split(' ​​​')[1]
    else:
        text = weibo_dict['text']

    # 存在链接，则取出来
    if ' src="' in weibo_dict['text'] and ' href="' in weibo_dict['text']:
        log('src and href in weibotext', weibo_dict['text'])
        texts = weibo_dict['text'].split('<a', 1)
        text1 = texts[0]
        link1 = split_to_link(' src="', weibo_dict)
        link2 = split_to_link(' href="', weibo_dict)
        text = text1 + link1 + link2

    elif ' src="' in weibo_dict['text']:
        texts = weibo_dict['text'].split('<a', 1)
        text1 = texts[0]
        link = split_to_link(' src="', weibo_dict)
        text = text1 + link

    elif ' href="' in weibo_dict['text']:
        texts = weibo_dict['text'].split('<a', 1)
        text1 = texts[0]
        # text2 = texts[1].split(' href="', 1)[1].split('"')[0]
        # text2 = text1 + text2
        link = split_to_link(' href="', weibo_dict)
        text = text1 + link

    w.text = text
    return w.text


def set_weibo_attr(weibo_dict):
    """每条微博的属性"""
    w = Weibo()
    w.ct = weibo_dict['created_at']
    # todo text 超过 140字的内容
    w.text = weibo_text_clean(w, weibo_dict)

    if 'original_pic' in weibo_dict:
        w.photo = weibo_dict['original_pic']

    # w.id w.mid为str，w.comment_c为int
    w.id = weibo_dict['id']
    w.mid = weibo_dict['mid']

    w.comment_c = weibo_dict['comments_count']
    # 如果评论数不为0,（评论有可能被删了）
    if w.comment_c is not 0:
        # 获取评论的列表
        comments = get_comment(w.id, w.mid)
        # print('debug', comments)
        if '评论被删除了' not in comments:
            w.comment_ct = comments[0][0]
            # user + ':' + 说的东西
            w.comment = comments[0][1] + ':' + comments[0][2]
            w.ans_comment = comments[2]
            # print(w.comment)
            # print(w.ans_comment, '\n\n')
        else:
            w.comment = '评论被删除了'

    w.like = weibo_dict['attitudes_count']
    w.forward = weibo_dict['reposts_count']
    w.device = weibo_dict['source']

    return w


def weibo_list(url):
    """
    读取一个url的数据,遍历出每个mblog，生成对象，返回list列表
    """
    folder, path = weibo_path(url)
    j = cached_page(url, folder, path)

    # 一般十个mblog 为一张 cards
    # 即十条微博一个json文件
    # 判断没有内容停止(cached_page is None)
    if j is None:
        return

    mblogs = j['data']['cards']
    lens = len(mblogs)
    # print(lens)

    # lists 十条微博对象的列表
    # lists = [set_weibo_attr(j['data']['cards'][i]['mblog']) for i in range(lens)]

    lists = []
    # 遍历出每个mblog，生成对象，返回list列表
    for i in range(lens):
        mblog = j['data']['cards'][i]['mblog']
        m = set_weibo_attr(mblog)
        lists.append(m)
        # print(m.text)
    # print(lists)
    return lists


def weibo_list_dick(url):
    """
    每个url对应的字典
    {
        id: {'ct': 2017, 'text': ".*?"},
    }
    """
    lists = weibo_list(url)
    if lists is None:
        return

    # 将遍历每个对象，生成字典
    dicts = {}
    for w in lists:
        d = w.dict_attr()

        # id 和 mid是一样的吗？
        if d['id'] == d['mid']:
            del d['mid']
        else:
            log(f"发现了一枚神奇的mid,\n{url}")

        # 新增进字典
        dicts[d['id']] = d
    print(dicts)
    return dicts


def write_weibo_json(url):
    """
    以追加的形式写入webo.txt
    """
    d = weibo_list_dick(url)
    if d is None:
        return
    with open('weibo.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(d, indent=4, ensure_ascii=False))
        log(f"已写入weibo.txt,\n{url}")
    return d


def auto(func, url_root):
    """
    自动运行直至没有数据
    """
    b, n = 1, 1
    while b is not None:
        # todo url 自增 加 导致 1 12 123 1234 跳页
        url = url_root
        url = url + str(n)
        b = func(url)
        # print(url)
        # print("debug b", b)
        n += 1
        log('auto function url', n)
    # print('b is None?')


def main():
    # 启动前删除weibo.txt(因为追加写入)
    if os.path.exists('weibo.txt'):
        os.remove('weibo.txt')
        os.remove('log.txt')

    # m.weibo.cn 的ajax API
    # 将页数删掉。 url以 'page=' 结尾
    # todo 这里修改url
    url = f'https://m.weibo.cn/api/container/getIndex?containerid=1076031935822083&page='
    auto(write_weibo_json, url)

    # write_weibo_json(url)
    # weibo_list(url)
    # weibo_list_dick(url)


if __name__ == '__main__':
    main()
