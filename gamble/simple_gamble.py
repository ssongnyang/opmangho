from discord import app_commands
from discord.ext import commands
import discord
import random
import time

from database import account
from template.embed import *
from template.color import Color


class SimpleGamble(commands.Cog):
    @app_commands.command(name="도박", description="돈을 걸고 도박을 합니다")
    @app_commands.describe(금액="베팅할 금액을 입력해 주세요.")
    async def simple_gamble(self, itc: discord.Interaction, 금액: app_commands.Range[int, 500]):
        if not account.has_account(itc):
            return await itc.response.send_message(embed=no_account_embed(), ephemeral=True)
        user_money = account.get_money(itc)
        if 금액 > user_money:
            return await itc.response.send_message(
                embed=money_tribe_embed(itc),
                ephemeral=True,
            )

        p, c = random.randint(25, 75), random.randint(1, 100)
        embed = discord.Embed(title="게임 진행 중", description=f"성공 확률 : {p}%")
        embed.set_footer(text="결과 : ...")
        await itc.response.defer(thinking=True)
        msg = await itc.followup.send(embed=embed)
        time.sleep(1.5)
        if p < c:
            embed.title = "도박에 성공했습니다!"
            embed.color = Color.success  # lime
            embed.add_field(name=f"**결과 : + {금액:,}₩**", value="")
            account.give_money(itc, 금액)
            embed.set_footer(icon_url=itc.user.display_avatar.url, text=f"잔액 : ₩{user_money+금액:,}")
        else:
            embed.title = "도박에 실패했습니다."
            embed.color = Color.fail  # red
            embed.add_field(name=f"**결과 : - {금액:,}₩**", value="")
            account.take_money(itc, 금액)
            embed.set_footer(icon_url=itc.user.display_avatar.url, text=f" 잔액: ₩{user_money-금액:,}")
        return await itc.followup.edit_message(message_id=msg.id, embed=embed)

    @app_commands.command(name="test")
    async def test(self, itc: discord.Interaction):
        print(itc.user.id)
