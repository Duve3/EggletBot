from discord.ext import commands
from discord.ext import tasks
import discord
from log import setupLogging


class PresenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = setupLogging(f"{self.__class__.__name__}")
        self.currentStatus = 0
        self.statuses = [discord.Activity(type=discord.ActivityType.watching, name="Duve3 Code"), discord.Game("My game!")]

    @tasks.loop(minutes=1)
    async def ChangeStatus(self):
        await self.bot.change_presence(activity=self.statuses[self.currentStatus])
        self.currentStatus += 1
        if not self.currentStatus <= len(self.statuses) - 1:
            self.currentStatus = 0

    @ChangeStatus.before_loop
    async def wait_login(self):
        await self.bot.wait_until_ready()

    # doing something when the cog gets loaded
    async def cog_load(self):
        self.ChangeStatus.start()
        self.logger.debug(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        self.logger.debug(f"{self.__class__.__name__} unloaded!")


# usually you’d use cogs in extensions
# you would then define a global async function named 'setup', and it would take 'bot' as its only parameter
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(PresenceCog(bot=bot))
