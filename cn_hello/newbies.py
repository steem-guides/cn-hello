# -*- coding:utf-8 -*-

import os
import re

from steem.comment import SteemComment
from steem.account import SteemAccount

from data.page_language import PageLanguage
from data.authors import AuthorsCollection


NEWBIE_REPUTATION_RANGE = [25, 35]
NEWBIE_STEEM_POWER_THRESHOLD = 100

# NEWBIE_CREATED_DAYS_THRESHOLD = 90 # days
NEWBIE_POST_COUNT_THRESHOLD = 100
NEWBIE_FOLLOWER_COUNT_THRESHOLD = 50


def _in_range(value, range):
    return value >= range[0] and value <= range[1]


class Newbies(AuthorsCollection):

    list_name = "cn_newbies"
    author_list_file = "cn_newbies.csv"
    newbies_list = []

    def __init__(self):
        super(Newbies, self).__init__()

    def verify(self, author, post):
        account = SteemAccount(author)
        is_newbie =  self._by_reputation(account) # and self._by_experience(account)

        if is_newbie:
            is_cn = self._is_chinese(post)
            if is_cn:
                self._add(account)
                self._add_locally(author)
                return True
        return False

    def get(self, author=None, local=False):
        if author is None:
            if local:
                return self.newbies_list
        return None

    def _is_chinese(self, post):
        c = SteemComment(comment=post)
        body = c.get_text_body()
        languages = PageLanguage(body).detect(strict=False)
        if languages:
            for lang in languages:
                if lang and lang[:2].lower() == "zh":
                    return True
        return False

    def _add_locally(self, author):
        if author not in self.newbies_list:
            self.newbies_list.append(author)
            return True
        return False

    def _by_experience(self, account):
        # (1) created; (2) posts count; (3) followers count
        return account.post_count() < NEWBIE_POST_COUNT_THRESHOLD \
            or account.follower_count() < NEWBIE_FOLLOWER_COUNT_THRESHOLD
            # self._is_recent(account, NEWBIE_CREATED_DAYS_THRESHOLD) \

    def _by_reputation(self, account):
        # (1) reputation; (2) steem power owned by the account
        return _in_range(account.reputation(), NEWBIE_REPUTATION_RANGE) \
            and account.steem_power() < NEWBIE_STEEM_POWER_THRESHOLD
