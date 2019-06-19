# -*- coding:utf-8 -*-

import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker


def draw_weekly_data(data, filename):
    if data is None:
        return ""
    data = list(data)
    if len(data) == 0:
        return ""

    # get stats
    df = pd.DataFrame(data)
    stats = df.set_index('updated').groupby(pd.Grouper(freq='D')).count()["_id"]

    # plot data
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    pic = stats.plot(kind="bar")
    pic.set_title("weekly newbies")
    pic.set_ylabel("# of newbies")
    pic.set_xlabel("day")
    pic.set_xticklabels(stats.index.strftime('%a'))

    # save to image
    fig.autofmt_xdate()
    plt.savefig(filename)
    plt.clf()

    return ""


def draw_quarterly_data(data, filename):
    if data is None:
        return ""
    data = list(data)
    if len(data) == 0:
        return ""

    # get stats
    df = pd.DataFrame(data)
    stats = df.set_index('updated').groupby(pd.Grouper(freq='W-MON')).count()["_id"]

    # plot data
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    pic = stats.plot(kind="bar", color="green")
    pic.set_ylabel("# of newbies")
    pic.set_xlabel("week")
    pic.set_xticklabels(stats.index.strftime('%b %d'))

    # save to image
    fig.autofmt_xdate()
    plt.savefig(filename)
    plt.clf()

    return ""

def draw_all_data(data, filename):
    if data is None:
        return ""
    data = list(data)
    if len(data) == 0:
        return ""

    # get stats
    df = pd.DataFrame(data)
    stats = df.set_index('updated').groupby(pd.Grouper(freq='M')).count()["_id"]

    # draw graph
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    pic = stats.plot(kind="bar", color="orange")
    pic.set_ylabel("# of newbies")
    pic.set_xlabel("month")
    pic.set_xticklabels(stats.index.strftime('%Y/%m'))

    # save to image
    fig.autofmt_xdate()
    plt.savefig(filename)
    plt.clf()

    return ""
