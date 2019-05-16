### Introduction

@cn-hello is a bot that is built to serve the Steem Chinese Community Newbies, to faciliate the efforts of @team-cn and @steem-guides.

![Pixabay](https://cdn.pixabay.com/photo/2018/08/31/08/35/doodle-3644073_960_720.png)
<br/>
Image Source: [Pixabay](https://cdn.pixabay.com/photo/2018/08/31/08/35/doodle-3644073_960_720.png)


### Features

1. Search the newbies who has posts recently under the #cn tag, and reply their posts with the welcome message and suggestions;
2. Summarize the daily statistics of interaction with newbies, and publish summary of the efforts in recent days.


### Installation

The python packages in this project is managed with `pipenv` so you need to run below commands to install the packages before run the relevant commands.

``` bash
pip install pipenv
pipenv install
```


### Commands

The commands / tasks in this project is manged with `invoke` package.

By running `pipenv run invoke -l`, you're able to see the available tasks in the bot.

``` bash
Available tasks:

  cn-hello.reply       reply to a post by cn-hello
  cn-hello.search      search the latest posts by newbies
  cn-hello.summarize   publish summary post for daily and weekly update
  cn-hello.vote        vote a post by cn-hello
  cn-hello.welcome     send welcome messages to newbies
  steem.list-posts     list the post by account, tag, keyword, etc.
```

To see the introduction of a command, run `pipenv run invoke -h <command>`.


### Execution

The below two commands will be triggered daily automatically to search the Chinese newbies (reputation: [25, 35], language: Chinese) who has posted in last day, and welcome them with useful messages, and introduce them the @team-cn and @steem-guides to accelerate their activity and interaction in the community.

``` bash
pipenv run invoke cn-hello.welcome -d 3
pipenv run invoke cn-hello.summarize -d 3

```

Here `-d 3` means we'll look at the posts publised in last 3 days actually.


### Reuse the Project

The project is built with the objective that you could reuse it easily to build another bot.

The `cn_hello` module contains the `messages`, `commands`,`logic` of the bot with extensible structure.

```
├── cn_hello
│   ├── __init__.py
│   ├── bot.py      # the behaviors of the bot
│   ├── command.py    # the commands that trigger the bot to act
│   ├── message.py    # the messages for the bot to speak
│   └── newbies.py    # the data operations of newbies
```


### Reference

The interaction with Steem blockchain is built with [beem](https://github.com/holgern/beem) project.


### License

The project is open sourced under MIT license.
