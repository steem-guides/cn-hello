# -*- coding:utf-8 -*-

import os, time, datetime, random
from invoke import task

from steem.settings import settings
from utils.logging.logger import logger

from cn_hello.bot import CnHelloBot


@task(help={
      'tag': 'the tag of the posts to watch',
      'days': 'the posts in recent days to fetch',
      'debug': 'enable the debug mode'
      })
def search(ctx, tag="cn", days=3.0, debug=False):
    """ search the latest posts by newbies"""

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    bot = CnHelloBot(tag=tag, days=days)
    posts = bot.get_latest_posts()
    if len(posts) > 0:
        filename = bot.write_posts()
        bot.list_newbies()
    bot.send_notification()


@task(help={
      'url': 'the url of the post to reply',
      'message_id': 'the message_id to reply',
      'debug': 'enable the debug mode'
      })
def reply(ctx, url, message_id="welcome", debug=False):
    """ reply to a post by cn-hello """

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    bot = CnHelloBot()
    bot.reply(url=url, message_id=message_id)

@task(help={
      'url': 'the url of the post to reply',
      'debug': 'enable the debug mode'
      })
def vote(ctx, url, debug=False):
    """ vote a post by cn-hello """

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    bot = CnHelloBot()
    bot.vote(url=url)


@task(help={
      'tag': 'the tag of the posts to watch',
      'days': 'the posts in recent days to fetch',
      'debug': 'enable the debug mode'
      })
def welcome(ctx, tag="cn", days=3.0, debug=False):
    """ send welcome messages to newbies """

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    bot = CnHelloBot(tag=tag, days=days)
    posts = bot.welcome_all()
    if len(posts) > 0:
        filename = bot.write_posts()
    bot.send_notification()


@task(help={
      'debug': 'enable the debug mode'
      })
def daily_stats(ctx, tag="cn", days=7.0, debug=False):
    """ publish summary post for daily and weekly update """

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    bot = CnHelloBot(tag=tag, days=days)
    bot.publish_daily_stats()


@task(help={
      'debug': 'enable the debug mode'
      })
def weekly_stats(ctx, tag="cn", days=7.0, debug=False):
    """ publish weekly stats of cn-hello """

    if debug:
        settings.set_debug_mode()

    settings.set_steem_node()

    day_of_the_week = datetime.datetime.today().weekday()

    # only Sunday
    if day_of_the_week == 6:
        logger.info("Create the weekly summary")
        bot = CnHelloBot(tag=tag, days=days)
        bot.publish_weekly_stats()
    else:
        logger.info("Skip the weekly summary until its Sunday")


