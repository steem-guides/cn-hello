# -*- coding:utf-8 -*-

import time
from datetime import datetime
import pytz
import os

from steem.comment import SteemComment
from steem.account import SteemAccount
from steem.writer import Writer
from steem.voter import Voter
from steem.uploader import Uploader
from steem.collector import get_comments, get_posts
from steem.settings import settings, STEEM_HOST, STEEMD_HOST
from data.reader import SteemReader
from cn_hello.newbies import Newbies
from cn_hello.message import get_message, verify_message, build_table
from cn_hello.analysis import draw_weekly_data, draw_quarterly_data, draw_all_data
from utils.logging.logger import logger


CN_HELLO_REVIEW_DURACTION = 3 # days
CN_HELLO_ACCOUNT = settings.get_env_var("CN_HELLO_ACCOUNT") or "cn-hello"
VOTE_WEIGHT = settings.get_env_var("CN_HELLO_VOTE_WEIGHT") or 50

SUMMARY_POST_TAGS = ["cn", "cn-hello", "cn-stats", "newbie", "zzan"]
DAILY_SUMMARY_PREFIX = "CN区每日新人统计 Newbies Daily"
WEEKLY_SUMMARY_PREFIX = "CN区每周新人数据汇总 Newbies Weekly"

ACCESSIBLE_STEEM_HOST = "https://busy.org"



class CnHelloBot(SteemReader):

    def __init__(self, tag="cn", days=CN_HELLO_REVIEW_DURACTION):
        SteemReader.__init__(self, tag=tag, days=days)
        self.attributes = [u'title', u'pending_payout_value',
            u'author', u'net_votes', u'created', u'url'
            # u'permlink', u'authorperm', u'body', u'community', u'category',
        ]
        self.author = CN_HELLO_ACCOUNT
        self.writer = Writer(author=self.author)
        self.voter = Voter(author=self.author
                           )
        self.uploader = Uploader(author=self.author)
        self.newbies = Newbies()
        self.db = settings.get_db()
        self.comments = []

    def get_name(self):
        name = "cn-hello"
        return "{}-{}".format(name, self._get_time_str())

    def is_qualified(self, post):
        # c = SteemComment(comment=post)
        author = post.author
        return self.is_recent(post=post, days=CN_HELLO_REVIEW_DURACTION) and self.newbies.verify(author, post)

    def _get_newbie_list(self):
        return self.newbies.get(local=True)

    def list_newbies(self):
        # show newbies
        newbies = self._get_newbie_list()
        print ("{} newbies are found".format(len(newbies)), newbies)

    def _read_comments(self):
        if len(self.comments) == 0:
            self.comments = get_comments(self.author)
        return self.comments

    def _add_reply_record(self, receiver, message_id, post, timestamp=None):
        if receiver and message_id and post:
            if not self._has_reply_record(receiver, message_id):
                timestamp = timestamp or datetime.now(pytz.utc)
                reply = {
                    "receiver" : receiver,
                    "reputation" : SteemAccount(receiver).reputation(),
                    "message_id" : message_id,
                    "url": post.get_url(),
                    "title": post.get_comment().title,
                    "updated": timestamp
                }
                self.db.insert_reply(reply)
                logger.info("Add reply to author @{} with message [{}] into database".format(receiver, message_id))
                return True
        return False

    def _has_reply_record(self, receiver, message_id):
        return self.db.has_reply(receiver, message_id)

    def _has_reply_comment(self, receiver, message_id):
        comments = self._read_comments()
        for c in comments:
            # check the receiver and the message_id fingerprint
            if c.parent_author == receiver and verify_message(message_id, c.body):
                logger.info("I found I replied to @{} with message [{}] by searching comment history".format(receiver, message_id))
                return (True, c)
        return (False, None)

    def _has_replied(self, receiver, message_id):
        # has reply records in DB, or has replied by checking steem APIs
        if self._has_reply_record(receiver, message_id):
            return True
        (replied, comment) = self._has_reply_comment(receiver, message_id)
        if replied:
            c = SteemComment(comment=comment.get_parent())
            # cache the record into database since not found
            self._add_reply_record(receiver, message_id, c, comment["created"])
            return True
        return False

    def _get_reply_body(self, message_id, author):
        account = SteemAccount(author)
        comments_num = account.remaining_comments() or ''
        daily_comments_num = round(account.daily_recovery_comments(), 1) or ''
        return get_message(message_id).format(name=author, comments_num=comments_num, daily_comments_num=daily_comments_num)

    def reply(self, message_id, post=None, url=None):
        """ reply to the newbies' post """
        c = SteemComment(comment=post, url=url)
        receiver = c.get_comment().author
        if not self._has_replied(receiver, message_id):
            title = c.get_comment().title
            message = self._get_reply_body(message_id, receiver)
            self.writer.reply(c.get_comment(), message)
            self._add_reply_record(receiver, message_id, c)
            logger.info("Replied to @{}'s post [{}] with [{}] message".format(receiver, title, message_id))
            return True
        else:
            logger.info("Skip reply account @{} with [{}] message, because we already reliped before".format(receiver, message_id))
            return False

    def vote(self, post=None, url=None):
        c = SteemComment(comment=post, url=url)
        receiver = c.get_comment().author
        title = c.get_comment().title

        if not c.is_upvoted_by(self.author):
            self.voter.upvote(c.get_comment(), weight=float(VOTE_WEIGHT))
            logger.info("I have upvoted @{}'s post [{}] successfully".format(receiver, title))
            return True
        else:
            logger.info("Skip upvote @{} because I already upvoted his/her post [{}]".format(receiver, title))
            return False

    def _pause(self):
        # You may only comment once every 3 seconds due to HF20
        time.sleep(5)

    def welcome_all(self, message_id="welcome"):
        if len(self.posts) == 0:
            self.get_latest_posts()

        if len(self.posts) > 0:
            # welcome newbies by replying and voting
            replied_posts = []
            for post in self.posts:
                replied = self.reply(post=post, message_id=message_id)
                if replied:
                    self.vote(post=post)
                    replied_posts.append(post)
                    self._pause()
            self.posts = replied_posts
            return self.posts
        return []

    def _get_replies(self, message_id, days):
        return list(self.db.get_replies(message_id, days))

    def _has_published(self, title, keyword):
        posts = get_posts(account=self.author, keyword=keyword, limit=10)
        if len(posts) > 0:
            for post in posts:
                if post.title == title:
                    return True
        return False

    def _get_accessible_url(self, url):
        if url and len(url) > 0:
            return url.replace(STEEM_HOST, ACCESSIBLE_STEEM_HOST)
        return ""

    def _get_daily_blog_body(self, message_id):
        delta = 0.05
        daily_replies = self._get_replies("welcome", 1.0 - delta) # 1 days
        weekly_replies = self._get_replies("welcome", 7.0 - delta) # 7 days

        daily_total = len(daily_replies)
        weekly_total = len(weekly_replies)

        articles = [("@{}".format(r['receiver']),
                     "<a href=\"{}\">{}</a>".format(self._get_accessible_url(r['url']), r['title'])
                     ) for r in daily_replies]
        articles_table = build_table(["作者", "文章"], articles)

        stats = []
        for r in weekly_replies:
            author = r['receiver']
            account = SteemAccount(author)
            steemd_link = "{}/@{}".format(STEEMD_HOST, author)
            row = ("@{}".format(author),
                   round(account.age_in_days(), 1),
                   round(account.reputation(), 1),
                   "<a href=\"{}\">{}%</a>".format(steemd_link, round(account.rc_percentage(), 1)),
                   round(account.steem_power(), 1),
                   account.follower_count(),
                   account.post_count()
            )
            stats.append(row)
        stats = sorted(stats, key=(lambda row: row[1]), reverse=False)
        stats_table = build_table(["新人", "天数", "声望", "活动能量", "Steem Power", "粉丝数", "发帖数"], stats)

        return get_message(message_id).format(daily_total=daily_total,
                                              weekly_total=weekly_total,
                                              articles_table=articles_table,
                                              stats_table=stats_table)

    def publish_daily_stats(self):
        """ publish the daily statistics post about newbies """
        title = "{} {}".format(DAILY_SUMMARY_PREFIX, self._get_time_str())
        if not self._has_published(title, DAILY_SUMMARY_PREFIX):
            body = self._get_daily_blog_body("daily_summary")
            self.writer.post(title, body, SUMMARY_POST_TAGS)
            logger.info("I have published today's post [{}] successfully".format(title))
            return True
        else:
            logger.info("Skip this post [{}], because I already published the post with the same title".format(title))
            return False

    def _get_img_md(self, path):
        if path and len(path) > 0:
            url = self.uploader.upload(path)
            if url and len(url) > 0:
                name = os.path.split(path)[-1]
                return "![{}]({})".format(name, url)
        return ""

    def _get_weekly_blog_body(self, message_id):
        delta = 0.05
        weekly_replies = self._get_replies("welcome", 7.0 - delta) # 7 days
        quarterly_replies = self._get_replies("welcome", 90.0 - delta) # 90 days
        all_replies = self._get_replies("welcome", 365.0 - delta) # 365 days

        weekly_total = len(weekly_replies)
        quarterly_total = len(quarterly_replies)
        total = len(all_replies)

        print (weekly_total, quarterly_total, total)

        pic_weekly = draw_weekly_data(weekly_replies, os.path.join(self.folder, "weekly.png"))
        pic_quarterly = draw_quarterly_data(quarterly_replies, os.path.join(self.folder, "quarterly.png"))
        pic_all = draw_all_data(all_replies, os.path.join(self.folder, "all.png"))

        weekly_graph = self._get_img_md(pic_weekly)
        quarterly_graph = self._get_img_md(pic_quarterly)
        all_graph = self._get_img_md(pic_all)

        return get_message(message_id).format(total=total,
                                              weekly_total=weekly_total,
                                              quarterly_total=quarterly_total,
                                              weekly_graph=weekly_graph,
                                              quarterly_graph=quarterly_graph,
                                              all_graph=all_graph)

    def publish_weekly_stats(self):
        """ publish the weekly statistics post about newbies """
        title = "{} {}".format(WEEKLY_SUMMARY_PREFIX, self._get_time_str())
        if not self._has_published(title, WEEKLY_SUMMARY_PREFIX):
            body = self._get_weekly_blog_body("weekly_summary")
            self.writer.post(title, body, SUMMARY_POST_TAGS)
            logger.info("I have published this week's post [{}] successfully".format(title))
            return True
        else:
            logger.info("Skip this post [{}], because I already published the post with the same title".format(title))
            return False
