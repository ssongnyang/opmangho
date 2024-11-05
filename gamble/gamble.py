from discord import ui, app_commands
from discord.ext import commands
import discord
import random
import pymysql

database = {}


class Gamble(commands.Cog):
    @app_commands.command(name="계좌생성", description="new account")
    async def newAccount(self, itc: discord.Interaction):
        if itc.user.id in database:
            return await itc.response.send_message(
                "이미 계좌가 있습니다", ephemeral=True
            )
        else:
            database.update({itc.user.id: 10000})
            return await itc.response.send_message("계좌를 생성했습니다")

    @app_commands.command(name="도박", description="d")
    @app_commands.describe(money="금액")
    async def gamble(self, itc: discord.Interaction, money: int):
        p, c = random.randint(25, 75), random.randint(1, 100)
        embed = discord.Embed()
        embed.description = f"성공 확률: {p}%"
        if p > c:
            embed.title = "성공"
            embed.add_field(name=f"결과: +{money}원")
            if itc.user.id in database:
                database[itc.user.id] += money
                embed.set_footer(text=f"잔액: {database[itc.user.id]}원")
        else:
            embed.title = "실패"
            embed.add_field(name=f"결과: -{money}원")
            if itc.user.id in database:
                database[itc.user.id] -= money
                embed.set_footer(text=f"잔액: {database[itc.user.id]}원")
        return await itc.response.send_message(embed=embed)

    @app_commands.command(name="test")
    async def test(self, itc: discord.Interaction):
        print(itc.user.id)
