import contextlib
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.common import InitLog

import logging

logger = logging.getLogger(__name__)

import sqlite3 as sqlite

if os.path.exists("c:/win/superdb/"):
    dbdir = "c:/win/superdb/"
elif os.path.exists("d:/win/superdb/"):
    dbdir = "d:/win/superdb/"
else:
    dbdir = "d:/win/studio/dxf/superdb/"

versionIter = ["001_20190902_init.sql"]

gdb = None


def InitDb():
    if not os.path.exists(dbdir):
        os.mkdir(dbdir)

    if not os.path.exists(dbdir + "version"):
        dbfile = os.path.join(dbdir, "superdb.db")
        with contextlib.closing(sqlite.connect(dbfile)) as con:
            sqlfile = os.path.join(os.path.dirname(__file__), "db", versionIter[0])
            logger.info("刷%s 脚本", sqlfile)
            with open(sqlfile, encoding='utf-8') as f:
                sqltxt = f.read()
                cur = con.cursor()
                cur.executescript(sqltxt)

        with open(os.path.join(dbdir, "version"), "w+") as f:
            f.write("0")

    with open(dbdir + "version") as f:
        version = int(f.read())

        if version < len(versionIter) - 1:
            logger.warning("版本更新, %d -> %d", version, len(versionIter) - 1)

            for i in range(version, len(versionIter)):
                dbfile = os.path.join(dbdir, "superdb.db")
                with contextlib.closing(sqlite.connect(dbfile)) as con:
                    sqlfile = os.path.join(os.path.dirname(__file__), "db", versionIter[i])
                    logger.info("刷%s 脚本", sqlfile)
                    with open(sqlfile, encoding='utf-8') as f:
                        sqltxt = f.read()
                        cur = con.cursor()
                        cur.executescript(sqltxt)

    global gdb
    dbfile = os.path.join(dbdir, "superdb.db")
    gdb = sqlite.connect(dbfile)


def CloseDb():
    gdb.close()


# 追加事件
def DbEventAppend(account, region, role, content):
    c = gdb.cursor()
    c.execute("begin")
    try:
        c.execute("insert into event (account, region, role, timepoint, content) values(?, ?, ?, ?, ?)", (
            account, region, role, int(time.time()), content))
        c.execute("commit")
    except gdb.Error as e:
        logger.warning("sql error! %s" % e)
        c.execute("rollback")


def DbStateInsert(account, region, role):
    c = gdb.cursor()
    c.execute("begin")
    try:
        c.execute("select count(*) from state where account=? and region=? and role=?", (account, region, role))
        rows = c.fetchall()
        if rows[0][0] == 0:
            c.execute("insert into state (account, region, role) values (?, ?, ?)", (account, region, role))

        c.execute("commit")
    except gdb.Error as e:
        logger.warning("sql error! %s" % e)
        c.execute("rollback")


# 更新状态
def DbStateUpdate(account, region, role, curlevel=None, zhiye=None, curpilao=None, money=None, wuse=None, kicktime=None,
                  kicklong=None):
    DbStateInsert(account, region, role)

    c = gdb.cursor()
    c.execute("begin")
    try:
        conditionstr = " where account = ? and region = ? and role = ?"
        conditiontup = (account, region, role)

        if curlevel is not None:
            c.execute("update state set curlevel = ? %s" % conditionstr, (curlevel,) + conditiontup)
        if zhiye is not None:
            c.execute("update state set zhiye = ? %s" % conditionstr, (zhiye,) + conditiontup)
        if curpilao is not None:
            c.execute("update state set curpilao = ? %s" % conditionstr, (curpilao,) + conditiontup)
        if money is not None:
            c.execute("update state set money = ? %s" % conditionstr, (money,) + conditiontup)
        if wuse is not None:
            c.execute("update state set wuse = ? %s" % conditionstr, (wuse,) + conditiontup)
        if kicktime is not None:
            c.execute("update state set kicktime = ? %s" % conditionstr, (kicktime,) + conditiontup)
        if kicklong is not None:
            c.execute("update state set kicklong = ? %s" % conditionstr, (kicklong,) + conditiontup)
        t = time.time()
        c.execute("update state set timepoint = ? %s" % conditionstr, (int(t),) + conditiontup)
        c.execute("commit")
    except gdb.Error as e:
        logger.warning("sql error! %s" % e)
        c.execute("rollback")


def DbItemInsert(account, region, role):
    c = gdb.cursor()
    c.execute("begin")
    try:
        yyyymmdd = datetime.today().strftime('%Y%m%d')

        c.execute("select count(*) from item where account=? and region=? and role=? and yyyymmdd=?",
                  (account, region, role, yyyymmdd))
        rows = c.fetchall()
        if rows[0][0] == 0:
            c.execute(
                "insert into item (account, region, role, yyyymmdd, todaymoney, todaywuse, todaysumtime) values (?, ?, ?, ?, ?, ?, ?)",
                (account, region, role, yyyymmdd, 0, 0, 0))

        c.execute("commit")
    except gdb.Error as e:
        logger.warning("sql error! %s" % e)
        c.execute("rollback")


# 追加流水
def DbItemAppend(account, region, role, moneyadd=None, wuseadd=None, timeadd=None):
    DbItemInsert(account, region, role)

    c = gdb.cursor()
    c.execute("begin")
    try:
        yyyymmdd = datetime.today().strftime('%Y%m%d')
        conditionstr = " where account = ? and region = ? and role = ? and yyyymmdd = ?"
        conditiontup = (account, region, role, yyyymmdd)

        c.execute("select todaymoney, todaywuse, todaysumtime from item %s" % conditionstr, conditiontup)
        rows = c.fetchall()

        for row in rows:
            todaymoney, todaywuse, todaysumtime = row[0], row[1], row[2]

            if moneyadd is not None:
                c.execute("update item set todaymoney = ? %s" % conditionstr, (todaymoney + moneyadd,) + conditiontup)
            if wuseadd is not None:
                c.execute("update item set todaywuse = ? %s" % conditionstr, (todaywuse + wuseadd,) + conditiontup)
            if timeadd is not None:
                c.execute("update item set todaysumtime = ? %s" % conditionstr,
                          (todaysumtime + timeadd,) + conditiontup)

        c.execute("commit")
    except gdb.Error as e:
        logger.warning("sql error! %s" % e)
        c.execute("rollback")


def main():
    InitLog()

    InitDb()
    # DbEventAppend("13023252617","上海一区", "小春春", "登陆上线")
    DbStateUpdate("13023252617", "上海一区", "小春春", curlevel=10, zhiye="格斗家", curpilao=100, money=10000)
    DbItemAppend("13023252617", "上海一区", "小春春", moneyadd=100, wuseadd=10, timeadd=100)
    CloseDb()


if __name__ == '__main__':
    main()