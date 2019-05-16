# -*- coding:utf-8 -*-

import traceback

from bs4 import BeautifulSoup
from markdown import markdown

from utils.logging.logger import logger


def get_message(id):
    return build_message(id)

def build_message(id):
    return MESSAGES[id] + MESSAGE_ID.format(message_id=id)

def verify_message(id, body):
    try:
        html = markdown(body)
        soup = BeautifulSoup(html, "html.parser")
        msg_div = soup.find("div", {"message_id": id})
        if msg_div:
            return True
    except:
        logger.info("Failed when verifying message, with error: {}".format(traceback.format_exc()))

    return False

TABLE_TEMPLATE = """
<table>
<thead>
<tr>
{head}
</tr>
</thead>
<tbody>
{body}
</tbody>
</table>
"""

def build_table(head, data):
    if head and data and len(head) > 0 and len(data) > 0:
        head = "\n".join(["  <th>{}</th>".format(c) for c in head])
        rows = []
        for row in data:
            row_md = "\n".join(["<tr>", "\n".join(["  <td>{}</td>".format(c) for c in row]), "</tr>"])
            rows.append(row_md)
        body = "\n".join(rows)
        table = TABLE_TEMPLATE.format(head=head, body=body)
        return table
    return ""


MESSAGE_ID = """
<div message_id=\"{message_id}\"></div>
"""

MESSAGES = {}

MESSAGES["welcome"] = """
@{name} 你好，欢迎来到精彩的Steem世界~~~ 🙂

Steem和其他社区有很多不同，新人在早期经常会面临**各种困难**，例如：

1. 在Steem上活动是需要**能量**的，而新人能量很少，发了一段时间帖子没能量了就无法继续发帖。[点击此处](https://steemd.com/@{name})查看Resource Credits（活动能量）：你目前总共还能发表 **{comments_num}** 篇文章或者回帖，每天恢复的20%能量可支持发表 **{daily_comments_num}** 篇文章或者回帖，请控制好发帖节奏；
1. Steem非常注重**版权和原创**。很多新人刚加入时从其他网站转载别人的文章发表，马上就会被**警告、惩罚甚至加入黑名单**；
1. Steem的规则和玩法很丰富、但也比较复杂，新人经常有很多**疑问**希望解答、有很多**知识**需要学习；
1. Steem是个**社交**平台，初期没有朋友和团队支持，举目无亲、无人搭理，很难生存；
1. Steem是个**应用**平台，不仅仅是写作，**内涵多姿多彩**，如绘画、摄影、游戏、编程等等，但找到自己的定位和方向需要一些时间探索。

为了**解决这些问题**，我们建议：

1. 加入**新手村** @team-cn 参与各种活动与交流，和众多的多才多艺的小伙伴们一起玩耍，加入微信群便于提问和互动。想要加入新手村，可以在 @team-cn 的帖子下留言，或者联系村长 @ericet（微信账号：ericet）；
1. 阅读[简明的新手攻略](https://busy.org/@ericet/db528bhdn3)，了解新手的基本玩法；如有时间，可以进一步阅读Steem中文社区联合创作的[《Steem指南》](https://steem-guides.github.io/steemh) ([PDF版](https://steem-guides.github.io/steemh/steemh.pdf) / [EPUB版](https://steem-guides.github.io/steemh/steemh.epub)) ，关注 @steem-guides 《Steem指南》，详细了解Steem中的规则、攻略、社交和人物。

最后，再次欢迎你来到Steem中文社区大家庭🎉 ，祝你在Steem的旅程愉快！！！

有任何问题，可以咨询 @team-cn 或 @cn-hello
"""


MESSAGES["daily_summary"] = """
<img src="https://cdn.pixabay.com/photo/2018/08/31/08/35/doodle-3644073_960_720.png" alt="" /><br/> (Image Source  <a href="https://cdn.pixabay.com/photo/2018/08/31/08/35/doodle-3644073_960_720.png">Pixabay</a>)

在下 @cn-hello 是新手村 @team-cn 的接引小门童，为各位初来乍到的朋友指路。

本文推荐每日的新人文章，欢迎CN区的朋友们支持新手们。😄


### 新人文章推荐

今日，本门童推荐来自新人的 {daily_total} 篇文章。

{articles_table}


### 7日内新人统计

过去7日，本门童接待了 {weekly_total} 位新手；下面是他们目前的状态，欢迎给他们提供建议。

{stats_table}


### 给新人的建议

1. 加入**新手村** @team-cn 参与各种活动与交流，和CN区的伙伴们一起学习和玩耍，加入微信群参与提问和互动；想要加入新手村，可以在 @team-cn 的帖子下留言，或者联系村长 @ericet；
1. 阅读[简明的新手攻略](https://busy.org/@ericet/db528bhdn3)，了解新手的基本玩法；如有时间，可以进一步阅读Steem中文社区联合创作的[《Steem指南》](https://steem-guides.github.io/steemh) ([PDF版](https://steem-guides.github.io/steemh/steemh.pdf) / [EPUB版](https://steem-guides.github.io/steemh/steemh.epub)) ，关注 @steem-guides 《Steem指南》，详细了解Steem中的规则、攻略、社交和人物。

祝你在Steem玩得开心、有所收获！有更多问题，请联系 @team-cn 或者 @cn-hello
"""
