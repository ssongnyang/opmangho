from discord import ui, app_commands
from discord.ext import commands
import discord
import random
import time

from database import account
from template.embed import *
from template.color import Color


def cardToEmoji(card: int):
    shape, num = None, None
    match card // 13:
        case 0:
            shape = ":spades:"
        case 1:
            shape = ":diamonds:"
        case 2:
            shape = ":hearts:"
        case 3:
            shape = ":clubs:"
    match card % 13:
        case 0:
            num = ":regional_indicator_a:"
        case 1:
            num = ":two:"
        case 2:
            num = ":three:"
        case 3:
            num = ":four:"
        case 4:
            num = ":five:"
        case 5:
            num = ":six:"
        case 6:
            num = ":seven:"
        case 7:
            num = ":eight:"
        case 8:
            num = ":nine:"
        case 9:
            num = ":keycap_ten:"
        case 10:
            num = ":regional_indicator_j:"
        case 11:
            num = ":regional_indicator_q:"
        case 12:
            num = ":regional_indicator_k:"
    return shape + num


def cardToNum(card: int):
    if card % 13 >= 9:
        return 10
    else:
        return card % 13 + 1


def sum_card(cards: list[int], moreThan22: bool = True) -> list[int]:
    sum = [0]
    for c in cards:
        if cardToNum(c) == 1:
            sum = [s + cardToNum(c) for s in sum]
            sum.append(sum[-1] + 10)
        else:
            sum = [s + cardToNum(c) for s in sum]
    if not moreThan22:
        sum = [s for s in sum if s <= 21]
    return sum


class BlackJackGame:
    def __init__(self, itc: discord.Interaction, money: int):
        self.playerID: int = itc.user.id
        self.guildID: int = itc.guild.id
        self.player_icon: str = itc.user.display_avatar.url
        self.player_name: str = itc.user.display_name
        self.itc: discord.Interaction = itc
        self.money: int = money
        self.cards: list[int] = list(range(52))
        self.player: list[int] = [self.cards.pop(random.randint(0, 51)), self.cards.pop(random.randint(0, 50))]
        # self.player = [4, 4]
        self.player_splited: list[int] = []
        self.splited: bool = False
        self.dealer: list[int] = [self.cards.pop(random.randint(0, 49)), self.cards.pop(random.randint(0, 48))]
        self.player_result: str = ""  # 버스트, 스테이, 블랙잭
        self.player_result_splited: str = ""
        self.embed = discord.Embed(title=":black_joker:블랙잭 게임:black_joker:", color=Color.gametable)
        self.view = ui.View()
        self.btn_hit = ui.Button(style=discord.ButtonStyle.blurple, label="히트")
        self.btn_stay = ui.Button(style=discord.ButtonStyle.blurple, label="스테이")
        self.btn_hit_split = ui.Button(style=discord.ButtonStyle.blurple, label="히트(2)")
        self.btn_stay_split = ui.Button(style=discord.ButtonStyle.blurple, label="스테이(2)")
        self.btn_split = ui.Button(style=discord.ButtonStyle.green, label="스플릿", row=1)
        self.btn_doubledown = ui.Button(style=discord.ButtonStyle.danger, label="더블다운", row=1)
        if account.get_money(itc) < money * 2:
            self.btn_split.disabled = True
            self.btn_doubledown.disabled = True
        if self.player[0] % 13 != self.player[1] % 13:
            self.btn_split.disabled = True
        self.btn_hit.callback = self.hit
        self.btn_hit_split.callback = self.hit_split
        self.btn_stay.callback = self.stay
        self.btn_stay_split.callback = self.stay_split
        self.btn_split.callback = self.split
        self.btn_doubledown.callback = self.doubledown
        self.view.add_item(self.btn_hit)
        self.view.add_item(self.btn_stay)
        self.view.add_item(self.btn_split)
        self.view.add_item(self.btn_doubledown)

        self.embed.add_field(
            name=f"딜러의 카드: ", value="? + " + ",".join([cardToEmoji(c) for c in self.dealer[1:]]), inline=False
        )
        self.embed.add_field(
            name=f"{itc.user.display_name}님의 카드 : ",
            value=", ".join([cardToEmoji(c) for c in self.player]),
            inline=False,
        )

        self.embed.set_footer(icon_url=self.player_icon, text=f"베팅 금액: {self.money:,}₩")
        self.msg = None

    async def update_embed(self, __itc: discord.Interaction | None = None, open: bool = False):
        if open:
            self.embed.set_field_at(
                0, name=f"딜러의 카드: ", value=",".join([cardToEmoji(c) for c in self.dealer]), inline=False
            )
        else:
            self.embed.set_field_at(
                0,
                name=f"딜러의 카드: ",
                value="? + " + ",".join([cardToEmoji(c) for c in self.dealer[1:]]),
                inline=False,
            )
        if self.splited:
            self.embed.set_field_at(
                1,
                name=f"{self.player_name}님의 카드 : ",
                value="**[1] **" + ", ".join([cardToEmoji(c) for c in self.player]),
                inline=False,
            )
        else:
            self.embed.set_field_at(
                1,
                name=f"{self.player_name}님의 카드 : ",
                value=", ".join([cardToEmoji(c) for c in self.player]),
                inline=False,
            )
        if self.splited:
            self.embed.set_field_at(
                2,
                name="ㅤ ",
                value="**[2]** " + " , ".join([cardToEmoji(c) for c in self.player_splited]) + "\nㅤ ",
                inline=False,
            )
        if __itc:
            await __itc.followup.edit_message(message_id=self.msg.id, embed=self.embed, view=self.view)
        else:
            await self.itc.followup.edit_message(message_id=self.msg.id, embed=self.embed, view=self.view)

    async def dealer_turn(self, __itc: discord.Interaction | None = None):
        self.btn_hit.disabled = True
        self.btn_split.disabled = True
        self.btn_stay.disabled = True
        self.btn_doubledown.disabled = True
        time.sleep(1)
        if sorted(sum_card(self.dealer)) == [11, 21] and len(self.dealer) == 2:
            return "블랙잭"
        elif min(sum_card(self.dealer)) > 21:
            return "버스트"
        elif 18 <= max(sum_card(self.dealer, False)) <= 21:
            return "스테이"
        # 아래 줄을 주석 처리하면 soft 17 미허용
        elif (
            17 in sum_card(self.dealer)
            and not bool([c for c in self.dealer if c % 13 == 0])
            and not min(sum_card(self.dealer)) < 17
        ):
            return "스테이"
        else:
            self.dealer.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
            await self.update_embed(__itc, open=True)
            return await self.dealer_turn()

    async def finish(self, __itc: discord.Interaction | None = None):
        embed = discord.Embed(title="블랙잭 게임에서 ")
        dealer_result = ""
        game_result: int = 0  # 1: win | 0: draw | -1: lose
        game_result_main: int = 0
        game_result_split: int = 0
        if self.player_result == "버스트" or self.player_result == "버스트(더블다운)":
            game_result_main = -1
        else:
            dealer_result = await self.dealer_turn()
            if dealer_result == "블랙잭" and self.player_result == "블랙잭":
                pass  # draw
            elif dealer_result == "블랙잭":
                game_result_main = -1
            elif self.player_result == "블랙잭":
                game_result_main = 1
            elif dealer_result == "버스트":
                game_result_main = 1
            elif max(sum_card(self.dealer, False)) == max(sum_card(self.player, False)):
                pass  # draw
            elif max(sum_card(self.dealer, False)) > max(sum_card(self.player, False)):
                game_result_main = -1
            else:
                game_result_main = 1

        if self.splited:
            if self.player_result_splited == "버스트":
                game_result_split = -1
            else:
                if dealer_result == "블랙잭" and self.player_result_splited == "블랙잭":
                    pass  # draw
                elif dealer_result == "블랙잭":
                    game_result_split = -1
                elif self.player_result_splited == "블랙잭":
                    game_result_split = 1
                elif dealer_result == "버스트":
                    game_result_split = 1
                elif max(sum_card(self.dealer, False)) == max(sum_card(self.player_splited, False)):
                    pass  # draw
                elif max(sum_card(self.dealer, False)) > max(sum_card(self.player_splited, False)):
                    game_result_split = -1
                else:
                    game_result_split = 1
        game_result = game_result_main + game_result_split
        match (game_result):
            case 2:
                embed.title += "대승했습니다!"
                embed.color = Color.success
            case 1:
                embed.title += "승리했습니다!"
                embed.color = Color.success
            case 0:
                embed.title += "비겼습니다."
                embed.color = Color.normal
            case -1:
                embed.title += "패배했습니다."
                embed.color = Color.fail
            case -2:
                embed.title += "대패했습니다."
                embed.color = Color.fail

        match (game_result_main):
            case 1:
                game_result_main = "승리"
            case 0:
                game_result_main = "무승부"
            case -1:
                game_result_main = "패배"

        match (game_result_split):
            case 1:
                game_result_split = "승리"
            case 0:
                game_result_split = "무승부"
            case -1:
                game_result_split = "패배"

        await self.update_embed(open="버스트" not in [self.player_result])

        embed.add_field(
            name="딜러의 카드 : ",
            value=(
                " , ".join([cardToEmoji(c) for c in self.dealer])
                + (f" **({dealer_result})**" if dealer_result != "" else "")
                + "\nㅤ"
            ),
            inline=False,
        )

        embed.add_field(
            name=f"{self.player_name}님의 카드 : ",
            value=" , ".join([cardToEmoji(c) for c in self.player])
            + f" **({self.player_result} - {game_result_main})**"
            + "\nㅤ ",
            inline=False,
        )
        if self.splited:
            embed.add_field(
                name=" , ".join([cardToEmoji(c) for c in self.player_splited])
                + f" ({self.player_result_splited} - {game_result_split})"
                + "\nㅤ ",
                value="",
                inline=False,
            )
        multiplier = 1
        if self.player_result in ("더블다운", "버스트(더블다운)"):
            multiplier *= 2
        if self.player_result == "블랙잭":
            multiplier *= 1.5
        embed.add_field(name=f"결과 : {self.money * game_result * multiplier:+,}₩", value="", inline=False)
        if game_result >= 0:
            account.give_money(self.itc, int(self.money * game_result * multiplier))
        else:
            account.take_money(self.itc, int(self.money * -game_result * multiplier))
        embed.set_footer(icon_url=self.itc.user.display_avatar.url, text=f"잔액 : {account.get_money(self.itc):,}₩")

        del BlackJack.games[(self.playerID, self.guildID)]

        if __itc:
            return await __itc.followup.edit_message(message_id=self.msg.id, embed=embed, view=None)
        else:
            return await self.itc.followup.edit_message(message_id=self.msg.id, embed=embed, view=None)

    async def hit(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        self.player.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
        await self.update_embed()
        await _itc.response.defer()
        if min(sum_card(self.player)) >= 22:
            self.player_result = "버스트"
            self.btn_hit.disabled = True
            self.btn_stay.disabled = True
            await self.update_embed()
            if self.player_result_splited == "" and self.player_splited != []:
                return
            return await self.finish(_itc)
        return await _itc.followup.edit_message(message_id=self.msg.id, embed=self.embed, view=self.view)

    async def hit_split(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        self.player_splited.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
        await self.update_embed()
        await _itc.response.defer()
        if min(sum_card(self.player_splited)) >= 22:
            self.player_result_splited = "버스트"
            self.btn_hit_split.disabled = True
            self.btn_stay_split.disabled = True
            await self.update_embed()
            if self.player_result == "" and self.player != []:
                return
            return await self.finish(_itc)

        return await _itc.followup.edit_message(message_id=self.msg.id, embed=self.embed, view=self.view)

    async def stay(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        self.btn_hit.disabled = True
        self.btn_stay.disabled = True
        await self.update_embed()
        await _itc.response.defer()
        if sorted(sum_card(self.player)) == [11, 21] and not self.splited:
            self.player_result = "블랙잭"
        else:
            self.player_result = "스테이"
        if self.player_result_splited == "" and self.player_splited != []:
            return
        await self.dealer_turn()
        return await self.finish(_itc)

    async def stay_split(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        self.btn_hit_split.disabled = True
        self.btn_stay_split.disabled = True
        await self.update_embed()
        await _itc.response.defer()
        if sorted(sum_card(self.player_splited)) == [11, 21] and not self.splited:
            self.player_result_splited = "블랙잭"
        else:
            self.player_result_splited = "스테이"
        if self.player_result == "" and self.player != []:
            return
        await self.dealer_turn()
        return await self.finish(_itc)

    async def split(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        # split은 처음 2장이 같을 때만 1번 가능
        self.btn_doubledown.disabled = True
        self.btn_split.disabled = True
        self.btn_split.label = "🔥스플릿🔥"
        self.btn_hit.label = "히트(1)"
        self.btn_stay.label = "스테이(1)"
        self.view.add_item(self.btn_hit_split)
        self.view.add_item(self.btn_stay_split)
        self.splited = True

        self.player_splited.append(self.player.pop())
        self.player.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
        self.player_splited.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))

        if self.splited:
            self.embed.add_field(
                name="ㅤ ",
                value=" , ".join([cardToEmoji(c) for c in self.player_splited]) + "\nㅤ ",
                inline=False,
            )
        await _itc.response.defer()
        if cardToNum(self.player[0]) == 1:  # 에이스는 스플릿 후 한 장만 받기
            self.player_result = "스테이"
            self.player_result_splited = "스테이"
            await self.update_embed()
            return await self.finish(_itc)
        return await self.update_embed(_itc)

    async def doubledown(self, _itc: discord.Interaction):
        if _itc.user.id != self.playerID:
            return await _itc.response.send_message("게임 중인 사람만 조작할 수 있습니다.", ephemeral=True)
        self.btn_doubledown.disabled = True
        self.btn_doubledown.label = "🔥더블다운!🔥"
        self.player.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
        await self.update_embed()
        await _itc.response.defer()
        if min(sum_card(self.player)) >= 22:
            self.player_result = "버스트(더블다운)"
            return await self.finish(_itc)
        else:
            self.player_result = "더블다운"
            return await self.finish(_itc)


class BlackJack(commands.Cog):
    games: dict[tuple[int, int], BlackJackGame] = {}

    @app_commands.command(name="블랙잭", description="돈을 걸고 블랙잭 게임을 합니다.")
    @app_commands.describe(금액="베팅할 금액을 입력해 주세요.")
    async def blackjack(self, itc: discord.Interaction, 금액: app_commands.Range[int, 500]):
        if not account.has_account(itc):
            return await itc.response.send_message(embed=no_account_embed(), ephemeral=True)
        user_money = account.get_money(itc)
        if 금액 > user_money:
            return await itc.response.send_message(
                embed=money_tribe_embed(itc),
                ephemeral=True,
            )
        key = (itc.user.id, itc.guild.id)
        if key in self.games:
            return await itc.response.send_message("먼저 진행 중인 게임을 완료해야 합니다.", ephemeral=True)

        self.games[key] = BlackJackGame(itc, 금액)
        game = self.games[key]

        await itc.response.defer()
        game.msg = await itc.followup.send(embed=game.embed, view=game.view)
