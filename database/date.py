from database.database import Database
from database.user import get_id
import discord


def get_lastDonjo(itc: discord.Interaction):
    db = Database(
        f"select date_format(lastdonjo, '%y%m%d') as lastdonjo from account  left join user on account.id=user.id where (userID={itc.user.id}) and (guildID={itc.guild.id})"
    )
    result = db.execute()
    del db
    return int(result[0]["lastdonjo"])


def set_lastDonjo(itc: discord.Interaction):
    db = Database("update account set lastdonjo = NOW() where id=%s")
    db.execute(params=(get_id(itc),))
    del db
