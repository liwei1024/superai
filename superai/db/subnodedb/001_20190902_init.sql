-- 事件表 - 某一时间点,单独的信息
create table if not exists event
(
    id        INTEGER primary key autoincrement, -- id号
    account   character(20),                     -- 账号
    region    character(20),                     -- 大区
    role      character(20),                     -- 角色
    timepoint int,                               -- 时间点
    content   text                               -- 事件内容,json
);
create index if not exists event_idx1 on event (timepoint);

-- 状态表 - 最终的最近的状态
create table if not exists state
(
    id        INTEGER primary key autoincrement, -- id号
    account   character(20),                     -- 账号
    region    character(20),                     -- 大区
    role      character(20),                     -- 角色
    curlevel  int,                               -- 等级
    zhiye     character(20),                     -- 职业
    curpilao  int,                               -- 当前疲劳
    money     int,                               -- 金币
    wuse      int,                               -- 无色
    kicktime  int,                               -- 封号时间点
    kicklong  int,                               -- 封号持续时间
    timepoint int                                -- 数据更新时间
);

-- 流水表 - 每天的最新的单项数据的累积
create table if not exists item
(
    id           INTEGER primary key autoincrement, -- id号
    account      character(20),                     -- 账号
    region       character(20),                     -- 大区
    role         character(20),                     -- 角色
    yyyymmdd     character(20),                     -- yyyymmdd
    todaymoney   int,                               -- 今日收益金币
    todaywuse    int,                               -- 今日收益无色
    todaysumtime int                                -- 今日累积花的时间
);
create index if not exists item_idx1 on item (yyyymmdd);


-- 创建角色表 - 记录创建角色历史
create table if not exists createrole
(
    id           INTEGER primary key autoincrement, -- id号
    account      character(20),                     -- 账号
    region       character(20),                     -- 大区
    juese        character(20),                     -- 创建角色
    yyyymmdd     character(20)                      -- yyyymmdd
);
