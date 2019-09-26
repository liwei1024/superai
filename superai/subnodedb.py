import contextlib
import json
import os
import sys
import time
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.accountsetup import GetAccount, GetRegion
from superai.gameapi import IsDestSupport, GetMenInfo, BagWuseNum, GetRemaindPilao

from superai.pathsetting import getDbFile, GetDbDir
from superai.common import InitLog

import logging

logger = logging.getLogger(__name__)

import sqlite3 as sqlite

versionIter = ["001_20190902_init.sql"]


def InitDb():
    if not os.path.exists(GetDbDir()):
        os.mkdir(GetDbDir())

    if not os.path.exists(GetDbDir() + "version"):
        with contextlib.closing(sqlite.connect(getDbFile())) as con:
            sqlfile = os.path.join(GetDbDir(), "db/subnodedb", versionIter[0])
            logger.info("刷%s 脚本", sqlfile)
            with open(sqlfile, encoding='utf-8') as f:
                sqltxt = f.read()
                cur = con.cursor()
                cur.executescript(sqltxt)

        with open(os.path.join(GetDbDir(), "version"), "w+") as f:
            f.write("0")

    with open(GetDbDir() + "version") as f:
        version = int(f.read())

        if version < len(versionIter) - 1:
            logger.warning("版本更新, %d -> %d", version, len(versionIter) - 1)

            for i in range(version, len(versionIter)):
                dbfile = os.path.join(GetDbDir(), "superdb.db")
                with contextlib.closing(sqlite.connect(dbfile)) as con:
                    sqlfile = os.path.join(GetDbDir(), "db/subnodedb", versionIter[i])
                    logger.info("刷%s 脚本", sqlfile)
                    with open(sqlfile, encoding='utf-8') as f:
                        sqltxt = f.read()
                        cur = con.cursor()
                        cur.executescript(sqltxt)


def query_db(query, args=(), one=False):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        cur = con.cursor()
        cur.execute(query, args)
        r = [dict((cur.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur.fetchall()]
        return (r[0] if r else None) if one else r


# 追加事件
def DbEventAppend(account, region, role, content):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute("insert into event (account, region, role, timepoint, content) values(?, ?, ?, ?, ?)", (
                account, region, role, int(time.time()), content))
            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 查询事件 (最近20条?)
def DbEventSelect():
    result = query_db("select account, region, role, timepoint, content from event order by timepoint desc limit 20")
    return result


# 状态没有就插入
def DbStateInsert(account, region, role):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute("select count(*) from state where account=? and region=? and role=?", (account, region, role))
            rows = c.fetchall()
            if rows[0][0] == 0:
                c.execute("insert into state (account, region, role) values (?, ?, ?)", (account, region, role))

            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 更新状态
def DbStateUpdate(account, region, role, curlevel=None, zhiye=None, curpilao=None, money=None, wuse=None, kicktime=None,
                  kicklong=None, timeup=False):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        DbStateInsert(account, region, role)

        c = con.cursor()
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

            if timeup:
                t = time.time()
                c.execute("update state set timepoint = ? %s" % conditionstr, (int(t),) + conditiontup)
            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 查询状态
def DbStateSelect():
    result = query_db(
        "select account, region, role, curlevel, zhiye, curpilao, money, wuse, kicktime, kicklong, timepoint from state  where timepoint != 0 order by timepoint desc")
    return result


# 查询最近的状态的时间戳
def DbStateGetNearestTimepoint():
    result = query_db("select timepoint,account,region  from state order by timepoint desc limit 1")
    return result


# 账号&大区  下的角色有多少
def AccountRoles(account, region):
    count = 0
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute("select count(*) from state where account=? and region=?", (account, region))
            rows = c.fetchall()
            count = rows[0][0]
            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")
    return count


# 账号&大区 的角色有超过25级别的(肯定可以租聘幸运星了把)
def AccountXingyunxingRule(account, region):
    count = 0
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute("select count(*) from state where account=? and region=? and curlevel >= 25", (account, region))
            rows = c.fetchall()
            count = rows[0][0]
            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")
    return count > 0


# 今日早上六点时间戳
def TodaySixTimestamp():
    t = datetime.datetime.today()
    sixt = datetime.datetime(t.year, t.month, t.day, hour=6)
    return sixt.timestamp()


# 是否今日的疲劳刷完了
def IsTodayHavePilao(account, region):
    objs = query_db(
        "select account, region, role, curlevel, zhiye, curpilao, money, wuse, kicktime, kicklong, timepoint from state where account=? and region=?",
        (account, region))

    pilaoShuawan = 0

    for obj in objs:
        if obj["zhiye"] is None:
            # 没有初始化过
            logger.info("职业没有初始化过,进去看看")
            return True
        else:
            if IsDestSupport(obj["zhiye"]):
                # 上次更新时间点在今日六点之前
                if obj["timepoint"] < TodaySixTimestamp() < time.time():
                    logger.info("上次时间戳在今天6点之前")
                    return True

                if obj["curpilao"] is not None and obj["curpilao"] == 0:
                    pilaoShuawan += 1

                # 最多刷3个!!!
                if pilaoShuawan >= 3:
                    logger.warning("最多刷3个角色!")
                    return False

                # 还有疲劳呢!!
                if obj["curpilao"] > 0:
                    logger.warning("还有疲劳")
                    return True

    if len(objs) == 0:
        logger.info("没有角色,上去看看!")
        return True

    return False


# 获取应该选择角色下标
def GetToSelectIdx(account, region):
    objs = query_db(
        "select account, region, role, curlevel, zhiye, curpilao, money, wuse, kicktime, kicklong, timepoint from state where account=? and region=?",
        (account, region))

    for i, obj in enumerate(objs):
        if obj["zhiye"] is None:
            logger.info("职业没有初始化过,进去看看[GetToSelectIdx]")
            return i
        else:
            if not IsDestSupport(obj["zhiye"]):
                continue

        # 上次更新时间点在今日六点之前
        if obj["timepoint"] < TodaySixTimestamp() < time.time():
            logger.info("上次时间戳在今天6点之前[GetToSelectIdx]")
            return i

        # 还有疲劳呢!!
        if obj["curpilao"] > 0:
            logger.warning("还有疲劳[GetToSelectIdx]")
            return i

    raise Exception("没有可以选择的角色?")


# 更新人物信息
def UpdateMenState():
    meninfo = GetMenInfo()
    DbStateUpdate(account=GetAccount(), region=GetRegion(), role=meninfo.name, curlevel=meninfo.level,
                  zhiye=meninfo.zhuanzhihou, curpilao=GetRemaindPilao(), money=meninfo.money,
                  wuse=BagWuseNum(), timeup=True)


# 流水没有就插入
def DbItemInsert(account, region, role):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            yyyymmdd = datetime.datetime.today().strftime('%Y%m%d')

            c.execute("select count(*) from item where account=? and region=? and role=? and yyyymmdd=?",
                      (account, region, role, yyyymmdd))
            rows = c.fetchall()
            if rows[0][0] == 0:
                c.execute(
                    "insert into item (account, region, role, yyyymmdd, todaymoney, todaywuse, todaysumtime) values (?, ?, ?, ?, ?, ?, ?)",
                    (account, region, role, yyyymmdd, 0, 0, 0))

            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 追加流水
def DbItemAppend(account, region, role, moneyadd=None, wuseadd=None, timeadd=None):
    with contextlib.closing(sqlite.connect(getDbFile())) as con:

        DbItemInsert(account, region, role)

        c = con.cursor()
        c.execute("begin")
        try:
            yyyymmdd = datetime.datetime.today().strftime('%Y%m%d')
            conditionstr = " where account = ? and region = ? and role = ? and yyyymmdd = ?"
            conditiontup = (account, region, role, yyyymmdd)

            c.execute("select todaymoney, todaywuse, todaysumtime from item %s" % conditionstr, conditiontup)
            rows = c.fetchall()

            for row in rows:
                todaymoney, todaywuse, todaysumtime = row[0], row[1], row[2]

                if moneyadd is not None:
                    c.execute("update item set todaymoney = ? %s" % conditionstr,
                              (todaymoney + moneyadd,) + conditiontup)
                if wuseadd is not None:
                    c.execute("update item set todaywuse = ? %s" % conditionstr, (todaywuse + wuseadd,) + conditiontup)
                if timeadd is not None:
                    c.execute("update item set todaysumtime = ? %s" % conditionstr,
                              (todaysumtime + timeadd,) + conditiontup)

            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 查询流水
def DbItemSelect():
    result = query_db(
        "select account, region, role, yyyymmdd, todaymoney, todaywuse, todaysumtime from item order by yyyymmdd desc")
    return result


# 创建角色插入
def CreateJueseAppend(account, region, juese):
    yyyymmdd = datetime.datetime.today().strftime('%Y-%m-%d')
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute(
                "insert into createrole (account, region, juese, yyyymmdd) values (?, ?, ?, ?)",
                (account, region, juese, yyyymmdd))

            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")


# 查询某天创建了多少角色
def DayCreateJueseNum(account, region):
    yyyymmdd = datetime.datetime.today().strftime('%Y-%m-%d')
    count = 0
    with contextlib.closing(sqlite.connect(getDbFile())) as con:
        c = con.cursor()
        c.execute("begin")
        try:
            c.execute("select count(*) from createrole where account=? and region=? and yyyymmdd=?",
                      (account, region, yyyymmdd))
            rows = c.fetchall()
            count = rows[0][0]
            c.execute("commit")
        except con.Error as e:
            logger.warning("sql error! %s" % e)
            c.execute("rollback")
    return count


# 查询创建角色列表(根据此判断下一个创建什么角色)
def CreateJueses(account, region):
    result = query_db(
        "select juese from createrole where account=? and region=?", (account, region))
    return result


def main():
    InitLog()
    InitDb()

    # DbEventAppend("13023252617", "上海一区", "小春春", "登陆上线")
    # DbEventAppend("13023252617", "上海一区", "小春春", "下线")
    # DbStateUpdate("13023252617", "上海一区", "小春春", curlevel=10, )
    # DbItemAppend("13023252617", "上海一区", "小春春", moneyadd=100, wuseadd=10, timeadd=100)

    # rows = DbStateSelect()
    # jsonstr = json.dumps(rows, ensure_ascii=False)
    # print(jsonstr)

    print(IsTodayHavePilao(account='3115907573', region='北京3区'))


if __name__ == '__main__':
    main()
