from discord.ext import commands
import discord.ui
from log import setupLogging


def isATypeOfYes(msg: str):
    typeOfYeses = [
        "yes",
        "y",
        "ye",
        "ya",
        "yah",
        "yea",
        "yeh",
        "yeah",
        "yessir"
    ]
    if msg.lower() in typeOfYeses:
        return True
    return False


class SuperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = setupLogging(f"{self.__class__.__name__}")

    @commands.command()
    async def super_give(self, ctx: commands.Context, *args):
        user = self.bot.getUser(ctx.author.id)
        if ctx.author.id in self.bot.OWNER_IDS or user.permissions[0] is True:
            for arg in args:
                cmd, value = arg.split("=")
                if cmd == "coins" or cmd == "money" or cmd == "coin":
                    user.money = float(value)
                    await ctx.reply(f"Gave ${value}!")
                else:
                    await ctx.reply(f"Couldn't parse what to add (cmd: {cmd}, val: {value})")

            user.save()

    @commands.command()
    async def super_user(self, ctx: commands.Context, *args):
        userid = args[0]
        userid = str(userid).replace("<", '').replace("@", '').replace(">", '')
        userid = int(userid)
        user = self.bot.getUser(ctx.author.id)

        if user.permissions[2] is True or ctx.author.id in self.bot.OWNER_IDS:
            nsu = self.bot.getUser(userid)

            nsu.permissions = [True, True, True]

            await ctx.reply(f"Made <@{userid}> to SUPERUSER status")

            nsu.save()

    @commands.command()
    async def super_remove(self, ctx: commands.Context, *args):
        userid = args[0]
        userid = str(userid).replace("<", '').replace("@", '').replace(">", '')
        userid = int(userid)

        u = self.bot.getUser(ctx.author.id)

        if ctx.author.id in self.bot.OWNER_IDS:
            nsu = self.bot.getUser(userid)

            nsu.permissions = [False, False, False]

            await ctx.reply(f"Made <@{userid}> to NORMALUSER status")

            nsu.save()

        elif u.permissions == [True, True, True]:
            await ctx.reply(
                "Sorry, while you have SUPERUSER permissions, this command is only possible by OWNER level permissions.")

    @commands.command()
    async def super_wipe(self, ctx: commands.Context, *args):
        userid = int(str(args[0].replace("<", '').replace("@", '').replace(">", '')))

        u = self.bot.getUser(ctx.author.id)
        if ctx.author.id in self.bot.OWNER_IDS:
            nsu = self.bot.getUser(userid)

            await ctx.reply(f"Are you sure you want to wipe <@{userid}>?")

            def check(message):
                return message.author == ctx.message.author

            res = await self.bot.wait_for('message', check=check, timeout=30)

            if isATypeOfYes(res.content):
                nsu.resetUser()
                nsu.reload()
                await ctx.reply(f"Successfully wiped <@{userid}>!")
            else:
                await ctx.reply("Cancelled operation.")
        elif u.permissions == [True, True, True]:
            await ctx.reply("Sorry, while you have SUPERUSER permissions, this command is only possible by OWNER level permissions.")

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
    await bot.add_cog(SuperCog(bot=bot))
