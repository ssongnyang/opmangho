import discord
from database.database import Database
from multipledispatch import dispatch


def register(itc: discord.Interaction):
    db = Database("insert into user (userID, guildID, name) values (%s, %s, %s)")
    db.execute(params=(itc.user.id, itc.guild.id, itc.user.global_name))
    del db


@dispatch(discord.Interaction)
def get_id(itc: discord.Interaction):
    db = Database("select id from user where (userID=%s) and (guildID=%s)")
    result = db.execute(params=(itc.user.id, itc.guild.id))[0]["id"]
    del db
    return result


@dispatch(int, int)
def get_id(userID: int, guildID: int):
    db = Database("select id from user where (userID=%s) and (guildID=%s)")
    result = db.execute(params=(userID, guildID))[0]["id"]
    del db
    return result
