import discord
from discord.ext import commands
from discord import ui, app_commands
import typing
import time
import asyncio
import functools
import math
import emoji
import random

from database import account, stock
from database import stockaccount as s_account

from stock.similarity import similarity

from template.embed import money_tribe_embed
from template.color import Color
from template import colortext


# ₩


def static(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


@static(last_change=time.localtime().tm_min)
async def change_price():
    # while time.localtime().tm_hour > 9 or time.localtime().tm_hour >= 18:
    #     await asyncio.sleep(1)
    for s in stock.stockinfo(column="name"):
        sim = await similarity(stock.get_keyword(s))
        change = math.floor(stock.get_price(s) * ((sim - 5) / 100))
        stock.change_price(s, change)
    change_price.last_change = time.localtime().tm_min
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    while time.localtime().tm_min % 5 != 0 or time.localtime().tm_min == change_price.last_change:
        await asyncio.sleep(1)

    return await change_price()


class Stock(commands.Cog):
    stockGroup = app_commands.Group(
        name="주식", description="주식 투자를 통해 세계 최고의 부자가 되세요!"
    )
    stocks: tuple[str] = stock.stockinfo(column="name")

    def update_stock(self):
        self.stocks = stock.stockinfo(column="name")

    async def stockname_autocomplete(
        self, itc: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=s + f" ({stock.get_price(s):,}₩)", value=s)
            for s in self.stocks
            if current in s
        ]

    async def mystockname_autocomplete(
        self, itc: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(
                name=s + f" ({stock.get_price(s):,}₩, {s_account.count(itc, s)}주 보유)", value=s
            )
            for s in self.stocks
            if (current in s) and s_account.has_stock(itc, s)
        ]

    @stockGroup.command(name="확인", description="주식 리스트를 확인합니다.")
    # @app_commands.describe(기업이름="특정 기업을 선택할 경우, 과거 통계를 보여 줍니다.")
    @app_commands.describe(정렬기준="정렬 기준을 선택합니다.")
    # @app_commands.autocomplete(기업이름=stockname_autocomplete)
    async def check(
        self,
        itc: discord.Interaction,
        # 기업이름: str = "*",
        정렬기준: typing.Literal["번호 순 (기본)", "가격 순", "최근 변동량 순"] = "번호 순 (기본)",
    ):
        stockinfolist = stock.stockinfo(order=정렬기준)
        embed = discord.Embed(
            title=":chart_with_upwards_trend:주식 리스트:chart_with_upwards_trend:",
            description=f"정렬 기준 : {정렬기준}",
            color=Color.stock,
        )
        for index, info in enumerate(stockinfolist, start=1):
            recent_change = info["recent_change"]
            if recent_change > 0:
                embed.add_field(
                    name=f"{index}. {info["name"]}",
                    value=f"**```ansi\n{info["price"]:,}₩ {colortext.red(f'(⬆️ {recent_change:+,}₩)')}\n```**",
                    inline=False,
                )
            elif recent_change < 0:
                embed.add_field(
                    name=f"{index}. {info["name"]}",
                    value=f"**```ansi\n{info["price"]:,}₩ {colortext.blue(f'(⬇️ {recent_change:+,}₩)')}\n```**",
                    inline=False,
                )
            else:  # recent_change = 0
                embed.add_field(
                    name=f"{index}. {info["name"]}",
                    value=f"**```ansi\n{info["price"]:,}₩ {colortext.green(f'(➡️ {recent_change:+,}₩)')}\n```**",
                    inline=False,
                )
            embed.add_field(name="ㅤ", value="")
        return await itc.response.send_message(embed=embed)

    @stockGroup.command(name="매수", description="시장의 주식을 매수합니다.")
    @app_commands.describe(주식이름="매수할 주식 이름을 입력하세요.")
    @app_commands.describe(개수="몇 주를 매수할지 입력하세요.")
    @app_commands.autocomplete(주식이름=stockname_autocomplete)
    async def buy(self, itc: discord.Interaction, 주식이름: str, 개수: app_commands.Range[int, 1]):
        if 주식이름 not in self.stocks:
            embed = discord.Embed(
                title=f'"{주식이름}" 주식이 존재하지 않습니다.',
                description="`/주식 확인`으로 주식 리스트를 확인할 수 있습니다.",
                color=Color.fail,
            )
            return await itc.response.send_message(embed=embed)
        price = stock.get_price(주식이름)
        if account.get_money(itc) < price * 개수:
            return await itc.response.send_message(embed=money_tribe_embed(itc))
        s_account.create_stockaccount(itc, 주식이름, 개수)
        account.take_money(itc, price * 개수)
        embed = discord.Embed(title="주식 매수 성공", color=Color.stock)
        embed.add_field(name=f"{주식이름} 주식 {개수}주를 매수했습니다.", value="")
        embed.set_footer(icon_url=itc.user.display_avatar.url, text=f"구매 가격 : {price:,}₩ / 1주")
        return await itc.response.send_message(embed=embed)

    @stockGroup.command(name="매도", description="가지고 있는 주식을 매도합니다.")
    @app_commands.describe(주식이름="매도할 주식 이름을 입력하세요.")
    @app_commands.autocomplete(주식이름=mystockname_autocomplete)
    async def sell(self, itc: discord.Interaction, 주식이름: str):
        if 주식이름 not in self.stocks:
            embed = discord.Embed(
                title=f'"{주식이름}" 주식이 존재하지 않습니다.',
                description="`/주식 확인`으로 주식 리스트를 확인할 수 있습니다.",
                color=Color.fail,
            )
            return await itc.response.send_message(embed=embed)
        if not s_account.has_stock(itc, 주식이름):
            embed = discord.Embed(
                title=f"{주식이름} 주식을 보유하고 있지 않습니다.",
                description="`/주식 내주식`으로 보유 주식을 확인할 수 있습니다.",
                color=Color.fail,
            )
            return await itc.response.send_message(embed=embed)
        stock_num = s_account.count(itc, 주식이름)
        sell_money = stock.get_price(주식이름) * stock_num

        account.give_money(itc, sell_money)
        embed = discord.Embed(title="주식 매도 성공", color=Color.stock)
        embed.add_field(
            name=f"{주식이름} 주식 {stock_num}주를 매도했습니다.", value="", inline=False
        )
        embed.add_field(
            name=f"손익 : {sell_money-s_account.get_purchase_price_sum(itc, 주식이름):+,}₩",
            value="",
            inline=False,
        )
        embed.set_footer(
            icon_url=itc.user.display_avatar.url, text=f"잔액 : {account.get_money(itc):,}₩"
        )
        s_account.sell_stock(itc, 주식이름)
        return await itc.response.send_message(embed=embed)

    @stockGroup.command(name="내주식", description="내가 보유하고 있는 주식을 확인합니다.")
    async def mystock(self, itc: discord.Interaction):
        if not s_account.has_stock(itc):
            embed = discord.Embed(
                title="보유한 주식이 없습니다.",
                description="`/주식 매수`로 주식을 매수할 수 있습니다.",
                color=Color.fail,
            )
            return await itc.response.send_message(embed=embed)
        embed = discord.Embed(title="내 보유 주식", color=Color.stock)
        for s in self.stocks:
            if s_account.has_stock(itc, s):
                embed.add_field(
                    name=f"{s} ({s_account.count(itc, s)}주) - {stock.get_price(s):,}₩",
                    value=f"매수 가격 (평균) : {int(s_account.get_purchase_price_sum(itc, s) / s_account.count(itc, s)):,}₩ / 1주",
                    inline=False,
                )
        embed.set_footer(
            icon_url=itc.user.display_avatar.url, text=f"잔액 : {account.get_money(itc):,}₩"
        )
        return await itc.response.send_message(embed=embed)
