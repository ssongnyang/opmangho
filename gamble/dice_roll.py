from discord import app_commands
from discord.ext import commands
import discord
import random
import time

from database import account
from template.embed import *
from template.color import Color


def numToEmoji(num: int):
    match num:
        case 1:
            return ":one:"
        case 2:
            return ":two:"
        case 3:
            return ":three:"
        case 4:
            return ":four:"
        case 5:
            return ":five:"
        case 6:
            return ":six:"


class DiceRoll(commands.Cog):
    @app_commands.command(name="주사위", description="돈을 걸고 주사위를 굴립니다.")
    @app_commands.describe(금액="베팅할 금액을 입력해 주세요.")
    async def dice_roll(self, itc: discord.Interaction, 금액: app_commands.Range[int, 500]):
        if not account.has_account(itc):
            return await itc.response.send_message(embed=no_account_embed(), ephemeral=True)
        user_money = account.get_money(itc)
        if 금액 > user_money:
            return await itc.response.send_message(
                embed=money_tribe_embed(itc),
                ephemeral=True,
            )

        player = (random.randint(1, 6), random.randint(1, 6))
        computer = (random.randint(1, 6), random.randint(1, 6))
        await itc.response.defer()
        embed = discord.Embed(title="주사위 굴리는 중...", color=Color.normal)
        embed.add_field(name=f"{itc.user.display_name} : ", value="", inline=False)
        embed.add_field(name=f"봇 : ", value="", inline=False)
        msg = await itc.followup.send(embed=embed)
        time.sleep(1)
        embed.set_field_at(0, name=f"{itc.user.display_name} : {numToEmoji(player[0])}", value="", inline=False)
        embed.set_field_at(1, name=f"봇 : {numToEmoji(computer[0])}", value="", inline=False)
        await itc.followup.edit_message(message_id=msg.id, embed=embed)
        time.sleep(1)
        embed.set_field_at(
            0,
            name=f"{itc.user.display_name} : {numToEmoji(player[0])} + {numToEmoji(player[1])} ( = {sum(player)})",
            value="",
            inline=False,
        )
        embed.set_field_at(
            1,
            name=f"봇 : {numToEmoji(computer[0])} + {numToEmoji(computer[1])} ( = {sum(computer)})",
            value="",
            inline=False,
        )
        await itc.followup.edit_message(message_id=msg.id, embed=embed)
        if sum(player) > sum(computer):
            embed.title = "게임에서 승리했습니다!"
            embed.color = Color.success
            embed.add_field(name=f"결과 : + **{금액:,}₩**", value="", inline=False)
            account.give_money(itc, 금액)
        elif sum(player) == sum(computer):
            embed.title = "게임이 무승부로 끝났습니다."
            embed.color = Color.normal
        else:
            embed.title = "게임에서 패배했습니다."
            embed.color = Color.fail
            embed.add_field(name=f"결과 : - **{금액:,}₩**", value="", inline=False)
            account.take_money(itc, 금액)
        embed.set_footer(icon_url=itc.user.display_avatar.url, text=f"잔액 : {get_money(itc):,}₩")
        return await itc.followup.edit_message(message_id=msg.id, embed=embed)
