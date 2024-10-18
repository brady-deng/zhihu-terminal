"""
知乎api
"""

import re
import asyncio
from zhihu_client import ZhihuClient
from utils import SpiderBaseclass
import requests



class ArticleSpider(SpiderBaseclass):


    """文章相关"""

    async def get_recommend_article(self) -> dict:
        """
        获取推荐文章
        :return:
        """
        url = 'https://www.zhihu.com'
        for _ in range(2):
            async with self.client.get(url) as r:
                resp = await r.text()
                session_token = re.findall(r'session_token=([a-zA-Z0-9]+)', resp)
            if session_token:
                session_token = session_token[0]
                break
        else:
            raise AssertionError('获取session_token失败')
        url = 'https://www.zhihu.com/api/v3/feed/topstory/recommend?'
        data = {
            'session_token': session_token,
            'desktop': 'true',
            'page_number': '1',
            'end_offset': '2',
            'action': 'down',
            'after_id': '1',
        }
        async with self.client.get(url, params=data) as r:
            result = await r.json()
        self.logger.debug(result)
        return result

    async def endorse_answer(self, uid: str, typ: str = 'up') -> dict:
        """
        赞同回答
        :param uid:
        :param typ: up赞同, down踩, neutral中立
        :return:
        """
        # 724073802
        url = f'https://www.zhihu.com/api/v4/answers/{uid}/voters'
        data = {
            'type': typ
        }
        r = await self.client.post(url, json=data)
        result = await r.json()
        self.logger.debug(result)
        return result

    async def thank_answer(self, uid: str, delete: bool = False) -> dict:
        """
        感谢回答
        :param uid:
        :param delete:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/answers/{uid}/thankers'
        if delete:
            r = await self.client.delete(url)
        else:
            r = await self.client.post(url)
        result = await r.json()
        self.logger.debug(result)
        return result

    async def get_question_article_first(self, question_id: str, uid: str):
        """

        :param uid:
        :param question_id:
        :return:
        """
        url = f'https://www.zhihu.com/question/{question_id}/answer/{uid}'
        r = await self.client.get(url)
        resp = await r.text()
        self.logger.debug(resp)
        return resp

    async def get_article_by_question(self, question_id, offset: int = 0, limit: int = 3):
        """

        :param question_id:
        :param offset:
        :param limit:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/questions/{question_id}/feeds?'
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,attachment,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,reaction_instruction,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].author.follower_count,vip_info,badge[*].topics;data[*].settings.table_of_content.enabled',
            'offset': offset,
            'limit': limit,
            'order': 'default',
            'platform': 'desktop',
        }
        headers = {
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
            'Connection': 'Keep-Alive',
            'Referer': 'https://www.zhihu.com/',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cookie': '_zap=a792b47b-bd60-4853-a644-965a24a905f0; d_c0=ACASDAJjKBmPTnqcBys9KPIsZ6mZ8zY4Ez4=|1724987038; __snaker__id=Eq59DbXp3mTKxizh; q_c1=e1731e0b499144a4bc1c4423c23add23|1724987057000|1724987057000; _xsrf=NelCyn1XkKU9ImfoVvqH8xcsSFX5lo5M; z_c0=2|1:0|10:1728539414|4:z_c0|80:MS4xQzJ2SUFnQUFBQUFtQUFBQVlBSlZUWXNmNW1lQzFrWHJxNDZGOTVQVlBpZ2R3bFB2LXdtZWtRPT0=|13e7f9c1c9bb3360b986d2efc23f30e1fd23d404d283ba6195ae7f7797c55a8e; __zse_ck=003_bCekEKKPCP+B1hG9dBo5MuitZugrwAh9Y/zmZDvKqpKLJ5N2ihpmXwKa6CZUXtaT=Miec+Uj8MWzy5J/juyRrMIO73jxLGb1jl7nT1Omb9qH; tst=r; BEC=8b4a1b0a664dd5d88434ef53342ae417; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1729068122,1729128189,1729133602,1729136371; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1729136371; HMACCOUNT=1A05E2A0BC4697B4; SESSIONID=QG8aqBvkRA8nX5rkL3k7eme7KT1vW6Bb1fHx8L2xglO; JOID=Vl4QBk2Z3Gt_OqGREZgM9Zo6_1EIyphTHUnh5HrJn1ARYZbheW5ZeBk6oJISnWipq0TysPJ8GPmyiTnaNxhC8p4=; osd=W18VBkiU3W5_P6yQFJgJ-Js__1QFy51TGETg4XrMklEUYZPseGtZfRQ7pZIXkGmsq0H_sfd8HfSzjDnfOhlH8ps=',
            'x-zst-81': '3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZYTY0-4Lm-h3_tufIwJS8gcxTgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIeQuK7AFpS6O1vukyQ_R0rRnsyukMGvxBEqeCiRnxEL2ZZrxmDucmqhPXnXFMTAoTF6RhRuLPF4XmqU300huKTBSxnhHqvBV0LwSqgcSYoAS0NJNMcT3m6XXKWB3_mwxypJoTv03O67XmPvHBEbN1jqwYTUtB0qoVTD9M2cOmWUCfQuoq9U3B19VmgqpLQgCCwBe1qh3MeMxC-GXCr49KxwcxsvcM7cnf3uN99gpp_vCqvqYCDwH_OU2xVqfz-DCyXhX1zBCpXgOKbvg9o_xL2vwVwhomtGe1Hv3O-B2K69OBYMCB29XM1wc1AJS9B7Cqibo1wCg9Qg39K8LZoLHfJ_HXICHLYwNYeic92LC8CwHLKX2C',
            'x-zse-96': '2.0_n=XHLJzBzs3oGeJFVQIuRMlk1DgCQrAcpefLSGcSsTTJ/5SWexFnzOJHgjj2eGWq',
            'x-zse-93': '101_3_3.0',
            'x-requested-with': 'fetch'
        }
        r = requests.get(url, params=params, headers = headers)
        result = r.json()
        result['url'] = r.url
        return result

    async def get_article_by_question_url(self, url):
        """

        :param question_id:
        :param offset:
        :param limit:
        :return:
        """
        headers = {
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
            'Connection': 'Keep-Alive',
            'Referer': 'https://www.zhihu.com/',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cookie': '_zap=a792b47b-bd60-4853-a644-965a24a905f0; d_c0=ACASDAJjKBmPTnqcBys9KPIsZ6mZ8zY4Ez4=|1724987038; __snaker__id=Eq59DbXp3mTKxizh; q_c1=e1731e0b499144a4bc1c4423c23add23|1724987057000|1724987057000; _xsrf=NelCyn1XkKU9ImfoVvqH8xcsSFX5lo5M; z_c0=2|1:0|10:1728539414|4:z_c0|80:MS4xQzJ2SUFnQUFBQUFtQUFBQVlBSlZUWXNmNW1lQzFrWHJxNDZGOTVQVlBpZ2R3bFB2LXdtZWtRPT0=|13e7f9c1c9bb3360b986d2efc23f30e1fd23d404d283ba6195ae7f7797c55a8e; __zse_ck=003_bCekEKKPCP+B1hG9dBo5MuitZugrwAh9Y/zmZDvKqpKLJ5N2ihpmXwKa6CZUXtaT=Miec+Uj8MWzy5J/juyRrMIO73jxLGb1jl7nT1Omb9qH; tst=r; BEC=8b4a1b0a664dd5d88434ef53342ae417; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1729068122,1729128189,1729133602,1729136371; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1729136371; HMACCOUNT=1A05E2A0BC4697B4; SESSIONID=QG8aqBvkRA8nX5rkL3k7eme7KT1vW6Bb1fHx8L2xglO; JOID=Vl4QBk2Z3Gt_OqGREZgM9Zo6_1EIyphTHUnh5HrJn1ARYZbheW5ZeBk6oJISnWipq0TysPJ8GPmyiTnaNxhC8p4=; osd=W18VBkiU3W5_P6yQFJgJ-Js__1QFy51TGETg4XrMklEUYZPseGtZfRQ7pZIXkGmsq0H_sfd8HfSzjDnfOhlH8ps=',
            'x-zst-81': '3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZYTY0-4Lm-h3_tufIwJS8gcxTgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIeQuK7AFpS6O1vukyQ_R0rRnsyukMGvxBEqeCiRnxEL2ZZrxmDucmqhPXnXFMTAoTF6RhRuLPF4XmqU300huKTBSxnhHqvBV0LwSqgcSYoAS0NJNMcT3m6XXKWB3_mwxypJoTv03O67XmPvHBEbN1jqwYTUtB0qoVTD9M2cOmWUCfQuoq9U3B19VmgqpLQgCCwBe1qh3MeMxC-GXCr49KxwcxsvcM7cnf3uN99gpp_vCqvqYCDwH_OU2xVqfz-DCyXhX1zBCpXgOKbvg9o_xL2vwVwhomtGe1Hv3O-B2K69OBYMCB29XM1wc1AJS9B7Cqibo1wCg9Qg39K8LZoLHfJ_HXICHLYwNYeic92LC8CwHLKX2C',
            'x-zse-96': '2.0_n=XHLJzBzs3oGeJFVQIuRMlk1DgCQrAcpefLSGcSsTTJ/5SWexFnzOJHgjj2eGWq',
            'x-zse-93': '101_3_3.0',
            'x-requested-with': 'fetch'
        }
        r = requests.get(url, headers=headers)
        result = r.json()
        result['url'] = r.url
        return result


if __name__ == '__main__':
    from setting import USER, PASSWORD


    async def test():
        client = ZhihuClient(user=USER, password=PASSWORD)
        await client.login(load_cookies=True)
        spider = ArticleSpider(client)
        await spider.get_recommend_article()
        await client.close()


    asyncio.run(test())
