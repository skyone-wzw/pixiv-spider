import re
import os
import sys
import requests
import pymysql

args = sys.argv
headers_logged = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/90.0.4430.93 Safari/537.36',
    'Referer': "https://www.pixiv.net/",
    'Cookie': "PHPSESSID=37666475_lrU8rY9ZskNdHzoSvVWFjPEniua6XZed" + os.environ["COOKIE"]
}
headers_normal = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/90.0.4430.93 Safari/537.36',
    'Referer': "https://www.pixiv.net/",
}
sql_del = """
DROP TABLE IF EXISTS `%s`;
""" % args[1]
sql_create = """
CREATE TABLE IF NOT EXISTS `%s`  (
  `_` int NOT NULL AUTO_INCREMENT,
  `id` varchar(25) NOT NULL,
  `count` int NOT NULL,
  `r18` int NOT NULL,
  `r18g` int NOT NULL,
  PRIMARY KEY (`_`)
) CHARACTER SET = utf8;
""" % args[1]
reg = re.compile(r'likeCount":(.*?),')
connection = pymysql.connect(host=os.environ['SQLHOST'], user=os.environ['SQLUSER'], password=os.environ['SQLPSD'], database=os.environ['SQLDB'])
cursor = connection.cursor()
cursor.execute(sql_del)
connection.commit()
cursor.execute(sql_create)
connection.commit()

for p in range(1, 9999999):
    try:
        url = ('https://www.pixiv.net/ajax/search/illustrations/%s?lang=zh&p=' % args[1]) + str(p)
        info = requests.get(url, headers=headers_logged).json()

        if len(info["body"]["illust"]["data"]) > 0:
            for item in info["body"]["illust"]["data"]:
                try:
                    p_id = item["id"]
                    url = 'https://www.pixiv.net/artworks/' + p_id
                    page = requests.get(url, headers=headers_normal)
                    page.encoding = page.apparent_encoding
                    like_count = eval(reg.findall(page.text)[0])
                    r18 = 1 if "R-18" in item["tags"] else 0
                    r18g = 1 if "R-18G" in item["tags"] else 0
                    cursor.execute('INSERT INTO `%s`(`id`, `count`, `r18`, `r18g`) values ("%s", %d, %d, %d)'
                                   % (args[1], p_id, like_count, r18, r18g))
                    connection.commit()
                    print(p_id, like_count)
                except Exception as e_2:
                    print(e_2)
        else:
            break
    except Exception as e_1:
        print(e_1)
