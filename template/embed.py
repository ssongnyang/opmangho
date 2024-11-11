import discord
from database.account import get_money
from template.color import Color


def no_account_embed() -> discord.Embed:
    embed = discord.Embed(title="아직 계좌가 없습니다", color=Color.fail)
    embed.add_field(name="먼저 계좌를 만들어주세요", value="계좌 만들기: /계좌생성")
    return embed


def money_tribe_embed(itc: discord.Interaction) -> discord.Embed:
    embed = discord.Embed(title="계좌에 잔액이 부족합니다.", color=Color.fail)
    embed.add_field(name="참고 : 하루에 한 번 돈을 받을 수 있습니다.", value="명령어 : `/돈줘`")
    embed.set_footer(icon_url=itc.user.display_avatar.url, text=f"현재 잔액: {get_money(itc):,}₩")
    return embed
