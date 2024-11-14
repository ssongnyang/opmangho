import discord
from database.database import Database
from database.stock import stockinfo, get_stockID, get_price
from database import user, stock


def has_stock(itc: discord.Interaction, name: str = "*"):
    db = Database()
    if name == "*":
        db.sql = "select * from stockaccount where playerID=%s"
        result = db.execute(params=(user.get_id(itc),))
    else:
        db.sql = "select * from stockaccount where playerID=%s and stockID=%s"
        result = db.execute(
            params=(
                user.get_id(itc),
                stock.get_stockID(name),
            )
        )
    print(result)
    return bool(result)


def create_stockaccount(itc: discord.Interaction, name: str, num: int = 0):
    db = Database(
        "insert into stockaccount (playerID, stockID, count, purchase_price) values (%s, %s, %s, %s)"
    )
    db.execute(params=(user.get_id(itc), get_stockID(name), num, get_price(name)))


def sell_stock(itc: discord.Interaction, name: str):
    playerID = user.get_id(itc)
    stockID = stock.get_stockID(name)
    db = Database("delete from stockaccount where playerID=%s and stockID=%s")
    db.execute(params=(playerID, stockID))
    del db


def get_purchase_price_sum(itc: discord.Interaction, name: str):
    playerID = user.get_id(itc)
    stockID = stock.get_stockID(name)
    db = Database("select purchase_price, count from stockaccount where playerID=%s and stockID=%s")
    result = db.execute(params=(playerID, stockID))
    del db
    return sum([r["purchase_price"] * r["count"] for r in result])


def count(itc: discord.Interaction, name: str):
    playerID = user.get_id(itc)
    stockID = stock.get_stockID(name)
    db = Database("select count from stockaccount where playerID=%s and stockID=%s")
    result = db.execute(params=(playerID, stockID))
    count = sum([r["count"] for r in result])
    del db
    return count
