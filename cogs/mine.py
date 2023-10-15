import logging
import random

from discord.ext import commands
import discord.ui

import eggletbot.eggletBot
from log import setupLogging


class MineView(discord.ui.View):
    def __init__(self, bot: eggletbot.eggletBot.Bot, u: eggletbot.eggletBot.User, e: discord.Embed, logger: logging.Logger, timeout=120.0):
        self.bot = bot
        self.embed = e
        self.uses = random.randint(2, 4)
        self.u = u
        self.logger = logger
        self.message = discord.Message
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Mine', custom_id="mine", disabled=False, style=discord.ButtonStyle.green, emoji="⛏")
    async def MineButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        u = self.bot.getUser(interaction.user.id)
        if u != self.u:
            return await interaction.response.send_message("This isnt for you!", ephemeral=True)
        response = ""
        if random.randint(0, 99) in range(0, 30): # 10% chance
            multi = 2
            response = "Lucky! Got a 2x multiplier!\n"
        else:
            multi = 1

        money = random.randint(1, 3) * multi
        u.money += money
        response += f"<@{interaction.user.id}>, You now have ${u.money}!"
        await interaction.response.send_message(response)
        u.save()
        self.uses -= 1
        if self.uses <= 0:
            e = discord.Embed(title="Mine dried up!")
            e.set_footer(text="A bot developed by duve3 and aw3s0m3p0k3m0n.")
            e.description = "Uh oh! The cave dried up, there is nothing left to mine... :sob:"
            button.disabled = True
            await self.message.edit(embed=e, view=self)
            self.bot.currentOpenMines.remove(interaction.user.id)


class MineCog(commands.Cog):
    def __init__(self, bot: eggletbot.eggletBot.Bot):
        self.bot = bot
        self.logger = setupLogging(f"{self.__class__.__name__}")

    @commands.command(name="mine")
    async def mineV2(self, ctx: commands.Context):
        u = self.bot.getUser(ctx.author.id)
        if ctx.author.id not in self.bot.currentOpenMines:
            e = discord.Embed(title="Mine!")
            v = MineView(self.bot, u, e, setupLogging(f"{self.__class__.__name__}.MineView"))
            e.set_footer(text="A bot developed by duve3 and aw3s0m3p0k3m0n.")
            e.description = "You entered a cave and started mining! Start getting some MONEY by pressing the mine button!"
            v.message = await ctx.reply(embeds=[e], view=v)
            self.bot.currentOpenMines.append(ctx.author.id)
        else:
            await ctx.reply("Uh oh! You already are in a mine! How would you enter another one?")

    # doing something when the cog gets loaded
    async def cog_load(self):
        self.logger.debug(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        self.logger.debug(f"{self.__class__.__name__} unloaded!")


# usually you’d use cogs in extensions
# you would then define a global async function named 'setup', and it would take 'bot' as its only parameter
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(MineCog(bot=bot))
