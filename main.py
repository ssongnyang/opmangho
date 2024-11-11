import discord
from discord.ext import commands
from discord import app_commands

import os
from dotenv import load_dotenv

from gamble.simple_gamble import SimpleGamble
from gamble.dice_roll import DiceRoll
from gamble.blackjack import BlackJack

from account.account import Account
from database.account import clear_donjo

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} \nID: {bot.user.id}")
    print("================")
    await bot.add_cog(Account(bot))
    await bot.add_cog(SimpleGamble(bot))
    await bot.add_cog(DiceRoll(bot))
    await bot.add_cog(BlackJack(bot))
    synced = await bot.tree.sync()
    print("Loaded Slash Command: ", len(synced))


load_dotenv()
bot.run(os.environ.get("TOKEN"))
