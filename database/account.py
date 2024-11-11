import os
from dotenv import load_dotenv
import pymysql, pymysql.cursors
import discord

from multipledispatch import dispatch
from database.database import Database


def has_account(itc: discord.Interaction) -> bool:
    db = Database("select * from account where userID=%s and guildID=%s")
    return bool(db.execute(params=(itc.user.id, itc.guild.id)))


def create_account(itc: discord.Interaction) -> None:
    db = Database("insert into account  (userID, guildID, money) values (%s, %s, 10000)")
    db.execute(params=(itc.user.id, itc.guild.id))


@dispatch(discord.Interaction)
def get_money(itc: discord.Interaction) -> int:
    db = Database("select money from account where (userID=%s) and (guildID=%s)")
    result = db.execute(params=(itc.user.id, itc.guild.id))
    del db
    return result[0]["money"]


@dispatch(int, int)
def get_money(userID: int, guildID: int) -> int:
    db = Database("select money from account where (userID=%s) and (guildID=%s)")
    result = db.execute(params=(userID, guildID))
    del db
    return result[0]["money"]


@dispatch(discord.Interaction, int)
def give_money(itc: discord.Interaction, money: int) -> int:
    db = Database()
    sql = "update account set money = money+%s where (userID=%s) and (guildID=%s)"
    db.execute(sql, params=(money, itc.user.id, itc.guild.id))
    del db
    return get_money(itc)


@dispatch(int, int, int)
def give_money(userID: int, guildID: int, money: int) -> int:
    db = Database()
    sql = "update account set money = money+%s where (userID=%s) and (guildID=%s)"
    db.execute(sql, params=(money, userID, guildID))
    del db
    return get_money(userID, guildID)


@dispatch(discord.Interaction, int)
def take_money(itc: discord.Interaction, money: int) -> int:
    db = Database()
    sql = "update account set money = money-%s where (userID=%s) and (guildID=%s)"
    db.execute(sql, params=(money, itc.user.id, itc.guild.id))
    del db
    return get_money(itc)


@dispatch(int, int, int)
def take_money(userID: int, guildID: int, money: int) -> int:
    db = Database()
    sql = "update account set money = money-%s where (userID=%s) and (guildID=%s)"
    db.execute(sql, params=(money, userID, guildID))
    del db
    return get_money(userID, guildID)


def already_donjo(itc: discord.Interaction) -> bool:
    db = Database("select donjo from account where (userID=%s) and (guildID=%s)")
    result = db.execute(params=(itc.user.id, itc.guild.id))
    del db
    return result[0]["donjo"] == 1


def donjo(itc: discord.Interaction) -> int:
    db = Database(sql="update account set donjo = 1 where (userID=%s) and (guildID=%s)")
    db.execute(params=(itc.user.id, itc.guild.id))
    del db
    return give_money(itc, 10000)


def clear_donjo() -> None:
    db = Database(sql="update account set donjo = 0")
    db.execute()
    del db
