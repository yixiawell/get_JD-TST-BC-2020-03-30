'''
爬取内容：               详情页的标题价格以及前十页的评论
starturl：               https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=1&s=1&click=0
导入依赖：               requests, json, time,re,os,concurrent.futures,bs4,urllib
'''
import requests, json, time,re,os,concurrent.futures
from bs4 import BeautifulSoup
from urllib import parse
headers = {
"user-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
}
sess = requests.session()
# sess.headers = headers
#获取html
def get_html(url,headers=headers):
    req = sess.get(url,headers=headers)
    soup = BeautifulSoup(req.text, "lxml")
    return soup

#获取json
def get_json(url,headers=headers):
    req = requests.get(url, headers=headers)
    return req

'''
https://c0.3.cn/stock?skuId=100009082500&area=15_1290_22050_0&venderId=1000004123&buyNum=1&choseSuitSkuIds=&cat=9987,653,655&extraParam={%22originid%22:%221%22}&fqsp=0&pdpin=&pduid=881287141&ch=1
https://c0.3.cn/stock?skuId=100004559325&area=15_1290_22050_0&venderId=1000000904&buyNum=1&choseSuitSkuIds=&cat=9987,653,655&extraParam={%22originid%22:%221%22}&fqsp=0&pdpin=&pduid=881287141&ch=1
https://c0.3.cn/stock?skuId=100005207369&area=15_1290_22050_0&venderId=1000000904&buyNum=1&choseSuitSkuIds=&cat=9987,653,655&extraParam={%22originid%22:%221%22}&fqsp=0&pdpin=&pduid=881287141&ch=1

https://c0.3.cn/stock?skuId=100004791679&area=15_1290_22050_0&venderId=1000085868&buyNum=1&choseSuitSkuIds=&cat=9987,653,655&extraParam={%22originid%22:%221%22}&fqsp=0&pdpin=&pduid=881287141&ch=1
'''

#获取动态的30个商品
def get_dynamic(id_list,url):
    '''
    :param id_list: 前30个商品的pid
    :return: 后30个商品的详情页url
    '''
    headers = {
        "referer": "{}".format(url),
        "user-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
    }
    show_items = ",".join(id_list)
    comp_page = re.compile(r"&page=(\d+)&")
    page = int(comp_page.findall(url)[0]) + 1
    comp_s = re.compile(r"&s=(\d+)&")
    s = int(comp_s.findall(url)[0]) + 30
    log_id = time.time()
    url = "https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page={}&s={}&scrolling=y&log_id={}&tpl=3_M&show_items={}".format(page,s,log_id,show_items)
    html = get_html(url, headers)
    urls = [parse.urljoin("https://", i["href"]) for i in html.select(".gl-i-wrap .p-img a")]
    venids = html.select(".gl-i-wrap .p-img div")
    venid2 = []
    for v in venids:
        com = re.compile(r'data-venid="(\d+)"')
        data = com.findall(str(v))
        if data:
            venid2.append(data[0])
    return urls, venid2


'''
https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=2&s=31&scrolling=y&log_id=1583138369.47036&tpl=3_M&show_items=100009082500
https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=4&s=91&scrolling=y&log_id=1583139361.79767&tpl=3_M&show_items=100009165102
https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=6&s=151&scrolling=y&log_id=1583139571.11122&tpl=3_M&show_items=100005205683
https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=2&s=31&scrolling=y&log_id=1583140635.0713565&tpl=3_M&show_items=100010617232,100009082500,100004559325,100005207373,100008348542,100006947212,100005205683,100004036237,100000287117,100010260254,100009177368,100009165080,100011516656,100004918013,100000986052,100007958784,100010260230,100009177424,65787063961,100002749549,100004575499,100002071798,100008031678,100008348548,63645706693,100010547822,100000177760,100003717479,7635559,100008031676

'''

#获取商品详情页的url
def get_detailurl(url):
    '''
    :param url: 单个页面的url
    :return: 详情页url列表
    '''
    html = get_html(url)
    lis = html.select(".gl-item")
    ids = [i["data-sku"] for i in lis]
    venidlist = [i.select(".p-img div") for i in lis]
    venid1 = []
    for v in venidlist:
        com = re.compile(r'data-venid="(\d+)"')
        data = com.findall(str(v))[0]
        venid1.append(data)
    url1 = [parse.urljoin("https://", i["href"]) for i in html.select(".gl-i-wrap .p-img a")]
    url2, venid2 = get_dynamic(ids, url)
    detailurls = url1 + url2
    detailvenids = venid1 + venid2
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as threa:
        fun1 = [threa.submit(get_detailtitle, detailurls[i], detailvenids[i]) for i in range(len(detailurls))]
    # for d in range(len(detailurls)):
    #     get_detailtitle(detailurls[d], detailvenids[d])


#获取详情页标题及价格，商品介绍，评论
def get_detailtitle(url, venid):
    '''
    存入csv
    :param url: 单个详情页url
    :return: none
    '''
    geshu = os.listdir(".\商品详情")
    book = open(".\商品详情\{}.txt".format(str(len(geshu) + 1)),"w")
    html = get_html(url)
    title = html.select(".sku-name")[0].text.strip()
    book.write("以下为标题：\n")
    book.write(r"{}\n".format(title))
    print(title)

    shangpingjieshao = [i.text for i in html.select(".parameter2.p-parameter-list li")]
    book.write("以下为商品介绍：\n")
    book.write("{}\n".format(shangpingjieshao))

    comp_skuid = re.compile(r"/(\d+).html")
    skuid = comp_skuid.findall(url)[0]
    jiage_url = "https://c0.3.cn/stock?skuId={}&area=15_1290_22050_0&venderId={}&buyNum=1&choseSuitSkuIds=&cat=9987,653,655&extraParam={}&fqsp=0&pdpin=&pduid=881287141&ch=1".format(skuid, venid, "{%22originid%22:%221%22}")
    json_headers = {
        "Referer": "{}".format(url),
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
    }
    jiage_json = get_json(jiage_url, json_headers)
    jiage = json.loads(jiage_json.text)["stock"]["jdPrice"]["p"]
    book.write("以下为价格：\n")
    book.write("{}\n".format(jiage))

    book.write("以下为评论：\n")
    pinglun_url = ["https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1".format(skuid,i) for i in range(11)]
    for p in pinglun_url:
        pinglun_json = get_json(p, json_headers)
        jss = pinglun_json.text[len("fetchJSON_comment98("):len(pinglun_json.text) - 2]
        js = json.loads(jss)
        pinglun_list = js["comments"]
        name = []
        pinglun_one = []
        for p in pinglun_list:
            name.append(p["nickname"])
            pinglun_one.append(p["content"])
        pingluns = dict(zip(name,pinglun_one))
        for p in pingluns:
            book.write("{}:\n{}\n".format(p,pingluns[p]))



'''
https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=100004559325&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=100009082500&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=100005207369&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
'''



if __name__ == '__main__':
    i = [i for i in range(1, 12, 2)]
    j = [j for j in range(1, 302, 60)]
    p = dict(zip(i, j))
    urls = ["https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page={}&s={}&click=0".format(i,p[i]) for i in p]
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as proce:
        fun2 = [proce.submit(get_detailurl, i) for i in urls]
    # for u in urls:
    #     get_detailurl(u)
'''
https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=1&s=1&click=0
https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=3&s=61&click=0
https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&page=5&s=121&click=0
'''