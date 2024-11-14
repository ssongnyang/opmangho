import pymysql, pymysql.cursors
import discord

from multipledispatch import dispatch
from database.database import Database
from database.user import get_id, register


def has_account(itc: discord.Interaction) -> bool:
    db = Database("select * from account left join user on account.id=user.id where userID=%s and guildID=%s")
    return bool(db.execute(params=(itc.user.id, itc.guild.id)))


def create_account(itc: discord.Interaction) -> None:
    register(itc)
    db = Database("insert into account (id, money) values (%s, 10000)")
    db.execute(params=(get_id(itc),))


@dispatch(discord.Interaction)
def get_money(itc: discord.Interaction) -> int:
    db = Database("select money from account left join user on account.id=user.id where user.id=%s")
    result = db.execute(params=(get_id(itc),))
    del db
    return result[0]["money"]


@dispatch(int, int)
def get_money(userID: int, guildID: int) -> int:
    db = Database("select money from account  left join user on account.id=user.id where user.id=%s")
    result = db.execute(params=(get_id(userID, guildID),))
    del db
    return result[0]["money"]


@dispatch(discord.Interaction, int)
def give_money(itc: discord.Interaction, money: int) -> int:
    db = Database()
    sql = "update account set money = money+%s where id=%s"
    db.execute(sql, params=(money, get_id(itc)))
    del db
    return get_money(itc)


@dispatch(int, int, int)
def give_money(userID: int, guildID: int, money: int) -> int:
    db = Database()
    sql = "update account set money = money+%s where id=%s"
    db.execute(sql, params=(money, get_id(userID, guildID)))
    del db
    return get_money(userID, guildID)


@dispatch(discord.Interaction, int)
def take_money(itc: discord.Interaction, money: int) -> int:
    db = Database()
    sql = "update account set money = money-%s where id=%s"
    db.execute(sql, params=(money, get_id(itc)))
    del db
    return get_money(itc)


@dispatch(int, int, int)
def take_money(userID: int, guildID: int, money: int) -> int:
    db = Database()
    sql = "update account set money = money-%s where id=%s"
    db.execute(sql, params=(money, get_id(userID, guildID)))
    del db
    return get_money(userID, guildID)
