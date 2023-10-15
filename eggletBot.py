import discord
import os
from user_handling import User
from shop_handling import Shop
import json
import random
from discord.ext import commands
import hashlib
import asyncio
import discord.ext.tasks
from log import setupLogging
from logging import INFO, DEBUG

ITEMS = [
    {"name": "Stronger Fists", "weight": 0.2, "info": "Used to make Attack more", "price": 100},
    {"name": "Health up", "weight": 0.3, "info": "Used to make Health more", "price": 100},
    {"name": "Griddy gobbler", "weight": 0.4, "info": "Steals Coin from someone", "price": 100},
    {"name": "Cup", "weight": 0.1, "info": "Gives one extra health", "price": 100}
]


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


class Bot(commands.Bot):
    def __init__(self, prefix="."):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        self.cachedPlayers = {}
        self.OWNER_IDS = [
            743639972191535116,
            680116696819957810
        ]
        self.currentOpenMines = []
        super().__init__(
            command_prefix=prefix,
            intents=intents
        )

    # the method to override in order to run whatever you need before your bot starts
    async def setup_hook(self):
        save_users.start()

        for file in os.listdir(cogPath.replace(".", "/")):
            if file.endswith(".py") and not file.startswith("DISABLED_") and file != "log.py" and not file.startswith("_"):
                await self.load_extension(cogPath + file.split(".")[0])

    def getUser(self, aid):
        """
        Checks if user is cached to return, if not then create new user
        :param aid: authorid
        :return: User
        """
        if aid in self.cachedPlayers.keys():
            plr = self.cachedPlayers[aid]
            return plr

        return User(aid)


bot = Bot(prefix=".")


def randomname():
    with open('./db/names/first-names.json') as fp:
        data = json.load(fp)

        random_index = random.randint(0, len(data) - 1)
        return data[random_index]


def health(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    hash_value = int(hash_object.hexdigest(), 16)
    custom_probability = 1 - (hash_value / (2 ** 256))
    selected_number = int(custom_probability * 10) + 1
    return selected_number


def damage(input_string):
    hash_object = hashlib.md5(input_string.encode())
    hash_value = int(hash_object.hexdigest(), 16)
    custom_probability = hash_value / (2 ** 128)
    selected_number = int(custom_probability * 10) + 1
    return selected_number


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}#{bot.user.discriminator}')


@bot.command()
async def start(ctx: commands.Context):
    m = await ctx.reply("Creating user data...")
    user_file_path = f"./db/users/{ctx.author.id}.json"

    # Check if the user file already exists
    if not os.path.isfile(user_file_path):
        # If it doesn't exist, create it with initial data
        bot.cachedPlayers[ctx.author.id] = User(ctx.author.id, new=True)
    else:
        await m.edit(content="Error! This user already exists!")
        return

    await m.edit(content="Successfully created user!")


@bot.command()
async def buy(ctx: commands.Context):
    try:
        data = bot.getUser(ctx.author.id)
        person = randomname()
        if data.money >= 1000:

            data.people.append({"name": person, "health": health(person), "damage": damage(person)})

            data.money -= 1000
            await ctx.reply("You just bought " + person + " who has " + str(damage(person)) + " Damage and " + str(
                health(person)) + " Health For 1000 coins")
            await ctx.reply("You have " + str(data.money) + " coins")
            data.save()
        else:
            await ctx.reply("You're Broke")
            await ctx.reply("You have " + str(data.money) + " coins")
    except FileNotFoundError:
        await ctx.reply("Player not found. Try using .start")
    except Exception as e:
        await ctx.reply(f"An error occurred: {str(e)}")


@bot.command()
async def people(ctx: commands.Context):
    try:
        data = bot.getUser(ctx.author.id)
        string = "You have "
        for person in data["people"]:
            string += person + ","
        string = string[:-1]
        await ctx.reply(string)
    except FileNotFoundError:
        await ctx.reply("Player not found. Try using !start")
    except Exception as e:
        await ctx.reply(f"An error occurred: {str(e)}")


@bot.command(name="stats", aliases=["profile"])
async def stats(ctx: commands.Context):
    data = bot.getUser(ctx.author.id)
    embed = discord.Embed(
        title="Stats",
        description=f"xp:{data.xp}",
        color=0x00ff00
    )
    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
    embed.add_field(name="Money:", value=data.money, inline=False)
    for p in data.people:
        embed.add_field(name=p['name'], value=f"who has {p['health']} health and has {p['damage']} attack damage", inline=False)
    embed.set_footer(text=f"{data.permissions} Your rights xd")
    await ctx.reply(embed=embed)


@bot.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        await bot.process_commands(message)


@bot.command(name="shop")
async def shop_cmd(ctx: commands.Context):
    message = ctx.message

    shop = Shop(ITEMS)
    i1, i2, i3 = shop.randomItem(), shop.randomItem(), shop.randomItem()
    itemList = [i1, i2, i3]
    desc = f"Items (type number to purchase):"
    embed = discord.Embed(title="Shop Menu", description=desc)
    for n, i in enumerate(itemList):
        embed.add_field(name=f"{n + 1}: {i.name}:${i.price}", value=i.info)

    embed.set_author(name=message.author.name)

    await message.reply(content="A random shop appeared!", embeds=[embed])

    def check(msg: discord.Message):
        return msg.author.id == ctx.message.author.id and msg.channel.id == ctx.channel.id

    try:
        reply = await bot.wait_for('message', check=check, timeout=60)
        user_response = reply

        if user_response.content.split(' ')[0] == "1":
            data = bot.getUser(message.author.id)
            if i1.price < data.money:
                data.money -= i1.price
                data.inv.append(i1)
                await user_response.reply(f"Purchased {i1.name}! (Added to your inventory)")
                data.save()
                return
            else:
                await user_response.reply(
                    f"Seems like you do not have enough money to purchase {i1.name}! Please get richer.")

        elif user_response.content.split(' ')[0] == "2":
            data = bot.getUser(message.author.id)
            if i2.price < data.money:
                data.money -= i2.price
                data.inv.append(i2)
                await user_response.reply(f"Purchased {i2.name}! (Added to your inventory)")
                data.save()
                return
            else:
                await user_response.reply(
                    f"Seems like you do not have enough money to purchase {i2.name}! Please get richer.")

        elif user_response.content.split(' ')[0] == "3":
            data = bot.getUser(message.author.id)
            if i3.price < data.money:
                data.money -= i3.price
                data.inv.append(i3)
                await user_response.reply(f"Purchased {i3.name}! (Added to your inventory)")
                data.save()
                return
            else:
                await user_response.reply(
                    f"Seems like you do not have enough money to purchase {i3.name}! Please get richer.")

        else:
            await user_response.reply("Could not parse the number! Please try again!")
            return

    except asyncio.TimeoutError:
        await message.reply("You ran out of time to buy from the shop")
    except Exception as e:
        print("An error occurred: " + str(e))


@bot.command(name="wipe")
async def wipe(ctx: commands.Context):
    u = bot.getUser(ctx.author.id)

    await ctx.reply("**Are you sure you want to wipe your own data!**\nThis **cannot** be reversed. (yes/no)")

    def check(message):
        return message.author == ctx.message.author

    m = await bot.wait_for('message', check=check, timeout=30)

    if isATypeOfYes(m.content):
        await ctx.reply("Wiping your data...")
        u.resetUser()
        u.reload()
        await ctx.reply("Successfully wiped your data.\nWelcome newbie.")
    else:
        await ctx.reply("Cancelled operation.")


"""
@bot.command()
async def fight(ctx, *, message):
    try:
        with open(f"user/{ctx.message.author}.json", "r") as file:
            data = json.load(file)
            print(type(data))
        for person in data["people"]:
            if message.lower() == person["name"].lower():
                haveperson = True
        if haveperson:
            await ctx.send(
                "Ready to fight")  # Hope to make a gride that you can move on kinda like chess and every turn it send the board
        else:
            print("you do you Have the player, " + message)
    except FileNotFoundError:
        await ctx.send("Player not found. Try using !start")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
"""



@discord.ext.tasks.loop(minutes=1)
async def save_users():
    logger.debug("Auto saving data...")
    for u in bot.cachedPlayers:
        u.save()
        u.reload()
    logger.debug("Auto save complete!")


def main():
    try:
        with open("./token.secret", 'r') as tf:
            TOKEN = tf.read()

        if TOKEN == "":
            logger.fatal("token.secret is empty! Exiting...")
            return
    except FileNotFoundError:
        logger.fatal("Could not find token file (token.secret)! Exiting...")
        return
    try:
        bot.run(TOKEN, log_handler=None)
    finally:
        logger.info("Saving data...")
        for u in bot.cachedPlayers:
            u.save()
        logger.info("Successfully Saved Data!")


if __name__ == "__main__":
    logger = setupLogging("main", level=DEBUG)
    setupLogging("discord", level=INFO)
    setupLogging("discord.http", level=INFO)
    cogPath = "cogs."
    main()
