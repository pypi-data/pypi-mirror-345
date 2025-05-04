OBZ
===


**NAME**


``obz`` - OBZ


**SYNOPSIS**


|
| ``obz <cmd> [key=val] [key==val]``
| ``obz -cvaw``
| ``obz -d`` 
| ``obz -s``
|

**DESCRIPTION**


``OBZ`` is a demo bot, it can connect to IRC, fetch and display RSS
feeds, take todo notes, keep a shopping list and log text. You can
also copy/paste the service file and run it under systemd for 24/7
presence in a IRC channel. OBZ demo's the OBX and OBR packages.

``OBX`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``OBR`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``OBZ/OBR/OBX`` are Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install obz``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ obz srv > obz.service``
| ``$ sudo mv obz.service /etc/systemd/system/``
| ``$ sudo systemctl enable obz --now``
|
| joins ``#obz`` on localhost
|


**USAGE**


use ``obz`` to control the program, default it does nothing

|
| ``$ obz``
| ``$``
|

see list of commands

|
| ``$ obz cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``now,pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start console

|
| ``obz -c``
| ``>``
|

start daemon

|
| ``$ obz -d``
| ``$``
|

start service

|
| ``$ obz -s``
| ``<runs until ctrl-c>``
|


**COMMANDS**


here is a list of available commands

|
| ``cfg`` - irc configuration
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``now`` - show genocide stats
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**


irc

|
| ``$ obz cfg server=<server>``
| ``$ obz cfg channel=<channel>``
| ``$ obz cfg nick=<nick>``
|

sasl

|
| ``$ obz pwd <nsvnick> <nspass>``
| ``$ obz cfg password=<frompwd>``
|

rss

|
| ``$ obz rss <url>``
| ``$ obz dpl <url> <item1,item2>``
| ``$ obz rem <url>``
| ``$ obz nme <url> <name>``
|

opml

|
| ``$ obz exp``
| ``$ obz imp <filename>``
|


**FILES**

|
| ``~/.obz``
| ``~/.local/bin/obz``
| ``~/.local/pipx/venvs/obz/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``OBZ`` is Public Domain.
|