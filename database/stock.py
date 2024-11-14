import discord
from database.database import Database


def register(name: str, price: int):
    pass


def get_stockID(name: str) -> int:
    db = Database("select id from stockinfo where name=%s")
    result = db.execute(params=(name,))
    return result[0]["id"]


def get_price(name: str) -> int:
    db = Database("select price from stockinfo where name=%s")
    result = db.execute(params=(name,))
    return result[0]["price"]


def get_keyword(name: str) -> str:
    db = Database("select keyword from stockinfo where name=%s")
    result = db.execute(params=(name,))
    del db
    return result[0]["keyword"]


def change_price(name: str, value: int):
    db = Database("update stockinfo set price=price+%s where name=%s")
    db.execute(params=(value, name))
    del db
    set_recent_change(name, value)


def set_recent_change(name: str, value: int):
    db = Database("update stockinfo set recent_change = %s where name=%s")
    db.execute(params=(value, name))
    del db


def stockinfo(*, column: str = "*", order: str = "") -> dict[str, tuple[str] | tuple[int]]:
    order_by = ""
    match (order):
        case "가격 순":
            order_by = " order by price desc"
        case "최근 변동량 순":
            order_by = " order by abs(recent_change) desc"

    db = Database(f"select * from stockinfo" + order_by)
    result = db.execute()
    # print(result)
    id: tuple[int] = tuple([r["id"] for r in result])
    name: tuple[str] = tuple([r["name"] for r in result])
    price: tuple[int] = tuple([r["price"] for r in result])
    recent_change: tuple[int] = tuple([r["recent_change"] for r in result])
    # print(result)
    del db
    match column:
        case "*":
            return result
        case "id":
            return id
        case "name":
            return name
        case "price":
            return price
        case "recent_change":
            return recent_change
        case _:
            raise KeyError(f"Invalid parameter: column {column}")
