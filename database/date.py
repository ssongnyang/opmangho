from database.database import Database
import discord


def get_lastDonjo(itc: discord.Interaction):
    db = Database(
        f"select date_format(lastdonjo, '%y%m%d') as lastdonjo from account where (userID={itc.user.id}) and (guildID={itc.guild.id})"
    )
    result = db.execute()
    del db
    return int(result[0]["lastdonjo"])


def set_lastDonjo(itc: discord.Interaction):
    db = Database("update account set lastdonjo = NOW() where (userID=%s) and (guildID=%s)")
    db.execute(params=((itc.user.id, itc.guild.id)))
    del db
