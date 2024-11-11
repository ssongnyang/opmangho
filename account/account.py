from discord import ui, app_commands
from discord.ext import commands
import discord
import time
from datetime import datetime

from database import account, date
from template.embed import *


class Account(commands.Cog):
    @app_commands.command(name="계좌생성", description="새로운 계좌를 생성합니다.")
    async def newAccount(self, itc: discord.Interaction):
        if account.has_account(itc):
            return await itc.response.send_message("이미 계좌가 있습니다", ephemeral=True)
        else:
            account.create_account(itc)
            return await itc.response.send_message("계좌를 생성했습니다.")

    @app_commands.command(name="잔액", description="자신의 잔액을 확인합니다.")
    async def checkMoney(self, itc: discord.Interaction):
        if account.has_account(itc):
            money = account.get_money(itc)
            embed = discord.Embed(
                title="잔액 확인",
                description=f"{itc.user.display_name}님의 잔액은 **{money:,}₩**입니다.",
                color=Color.normal,
            )
            return await itc.response.send_message(embed=embed)
        else:
            return await itc.response.send_message(embed=no_account_embed(), ephemeral=True)

    @app_commands.command(name="돈줘", description="하루에 한 번 돈을 받을 수 있습니다.")
    async def giveMoney(self, itc: discord.Interaction):
        if account.has_account(itc):
            if date.get_lastDonjo(itc) < int(datetime.strftime(datetime.now(), "%y%m%d")):
                money = account.give_money(itc, 10000)
                embed = discord.Embed(
                    title="돈 지급(1일 1회 제한)", description="**10,000₩**이 입금되었습니다.", color=Color.normal
                )
                date.set_lastDonjo(itc)
                embed.set_footer(icon_url=itc.user.display_avatar.url, text=f"잔액: {money:,}₩")
                return await itc.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="이미 오늘 돈을 받았습니다.",
                    description="`/돈줘`는 매일 0시에 초기화됩니다.",
                    color=Color.fail,
                )
                return await itc.response.send_message(embed=embed, ephemeral=True)

        else:
            return await itc.response.send_message(embed=no_account_embed(), ephemeral=True)

    @app_commands.command(name="송금", description="다른 사람에게 돈을 보낼 수 있습니다.")
    @app_commands.describe(대상="송금할 대상을 입력해 주세요.")
    @app_commands.describe(금액="송금할 금액을 입력해 주세요.")
    async def sendMoney(self, itc: discord.Interaction, 대상: discord.Member, 금액: int):
        if account.get_money(itc) < 금액:
            return await itc.response.send_message(embed=money_tribe_embed(itc), ephemeral=True)

        account.take_money(itc, 금액)
        account.give_money(대상.id, itc.guild.id, 금액)

        return await itc.response.send_message(
            f"{itc.user.display_name}님이 {대상.display_name}님에게 {금액}원을 송금했습니다."
        )
