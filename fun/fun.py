import discord
from discord.ext import commands
from random import randint, choice
import string
from dadjokes import Dadjoke

Cog = getattr(commands, "Cog", object)

def escape(text: str, *, mass_mentions: bool = False, formatting: bool = False) -> str:
    """Escape text for Discord to prevent mass mentions and markdown formatting.

    Parameters
    ----------
    text : str
        The text to be escaped.
    mass_mentions : bool, optional
        Set to True to escape mass mentions in the text.
    formatting : bool, optional
        Set to True to escape markdown formatting in the text.

    Returns
    -------
    str
        The escaped text.
    """
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = text.replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
    return text

class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"

class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            self.choice = None

class Fun(Cog):
    """Fun commands for interaction and entertainment."""

    ball = [
        "As I see it, yes",
        "It is certain",
        "It is decidedly so",
        "Most likely",
        "Outlook good",
        "Signs point to yes",
        "Without a doubt",
        "Yes",
        "Yes – definitely",
        "You may rely on it",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ]

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *choices):
        """Choose between multiple options."""
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send("Not enough options to pick from.")
        else:
            await ctx.send(choice(choices))

    @commands.command()
    async def roll(self, ctx, number: int = 6):
        """Roll a random number between 1 and `<number>`. Defaults to 6."""
        if number > 1:
            n = randint(1, number)
            await ctx.send(f"{ctx.author.mention} :game_die: {n} :game_die:")
        else:
            await ctx.send(f"{ctx.author.mention} Maybe a number higher than 1? ;P")

    @commands.command()
    async def flip(self, ctx):
        """Flip a coin."""
        answer = choice(["HEADS!", "TAILS!"])
        await ctx.send(f"*Flips a coin and... {answer}")

    @commands.command()
    async def rps(self, ctx, your_choice: RPSParser):
        """Play Rock, Paper, Scissors."""
        player_choice = your_choice.choice
        if not player_choice:
            return await ctx.send("This isn't a valid option. Try rock, paper, or scissors.")

        bot_choice = choice(list(RPS))
        cond = {
            (RPS.rock, RPS.paper): False,
            (RPS.rock, RPS.scissors): True,
            (RPS.paper, RPS.rock): True,
            (RPS.paper, RPS.scissors): False,
            (RPS.scissors, RPS.rock): False,
            (RPS.scissors, RPS.paper): True,
        }

        outcome = cond.get((player_choice, bot_choice), None)
        if outcome is True:
            await ctx.send(f"{bot_choice.value} You win {ctx.author.mention}!")
        elif outcome is False:
            await ctx.send(f"{bot_choice.value} You lose {ctx.author.mention}!")
        else:
            await ctx.send(f"{bot_choice.value} It's a tie {ctx.author.mention}!")

    @commands.command(name="8ball", aliases=["8"])
    async def _8ball(self, ctx, *, question: str):
        """Ask the 8-ball a question."""
        if not question.endswith("?") or question == "?":
            return await ctx.send("That doesn't look like a question.")

        embed = discord.Embed(title='Question: | :8ball:', description=question, color=0x2332e4)
        embed.add_field(name='Answer:', value=choice(self.ball), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["badjoke"])
    async def dadjoke(self, ctx):
        """Get a random Dad joke."""
        joke = Dadjoke().joke
        await ctx.send(joke)

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Create a lmgtfy link."""
        search_terms = escape(search_terms.replace("+", "%2B").replace(" ", "+"), mass_mentions=True)
        await ctx.send(f"<https://lmgtfy.com/?q={search_terms}>")

    @commands.command()
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""
        msg = escape(message, mass_mentions=True)
        await ctx.send(msg)

    @commands.command()
    async def sayd(self, ctx, *, message: str):
        """Same as say command, but deletes your message."""
        msg = escape(message, mass_mentions=True)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("Not enough permissions to delete messages.", delete_after=2)
        await ctx.send(msg)

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """Reverse the text."""
        reversed_text = escape("".join(reversed(text)), mass_mentions=True)
        await ctx.send(reversed_text)

    @commands.command()
    async def meme(self, ctx):
        """Get a random meme from r/dankmemes."""
        async with self.bot.session.get("https://www.reddit.com/r/dankmemes/top.json?sort=top&t=day&limit=500") as r:
            data = await r.json()
        data = choice(data["data"]["children"])["data"]
        img = data["url"]
        title = data["title"]
        upvotes = data["ups"]
        downvotes = data["downs"]

        embed = discord.Embed(color=ctx.author.color, title=title)
        embed.set_image(url=img)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"👍{upvotes} | 👎 {downvotes}")
        await ctx.send(embed=embed)

    @commands.command()
    async def emojify(self, ctx, *, text: str):
        """Convert text into emojis."""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        to_send = ""
        numbers = {
            "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
            "6": "six", "7": "seven", "8": "eight", "9": "nine", "0": "zero"
        }
        for char in text:
            if char == " ":
                to_send += " "
            elif char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                to_send += f":regional_indicator_{char.lower()}: "
            elif char in numbers:
                to_send += f":{numbers[char]}: "
            else:
                return await ctx.send("Unsupported characters. Only letters and numbers are allowed.")

        if len(to_send) > 2000:
            return await ctx.send("Emoji message is too long to fit in a single message!")

        await ctx.send(to_send)

    @commands.command()
    @commands.guild_only()
    async def roast(self, ctx, *, user: discord.Member = None):
        """Roast someone or yourself."""
        roasts = [
            "I'd give you a nasty look but you've already got one.",
            "If you're going to be two-faced, at least make one of them pretty.",
            "The only way you'll ever get laid is if you crawl up a chicken's ass and wait.",
            "It looks like your face caught fire and someone tried to put it out with a hammer.",
            "I'd like to see things from your point of view, but I can't seem to get my head that far up your ass.",
            "Scientists say the universe is made up of neutrons, protons, and electrons. They forgot to mention morons.",
            "Why is it acceptable for you to be an idiot but not for me to point it out?",
            "Just because you have one doesn't mean you need to act like one.",
            "Someday you'll go far... and I hope you stay there.",
            "Which sexual position produces the ugliest children? Ask your mother.",
            "No, those pants don't make you look fatter - how could they?",
            "Save your breath - you'll need it to blow up your date.",
            "If you really want to know about mistakes, you should ask your parents.",
            "Whatever kind of look you were going for, you missed.",
            "Hey, you have something on your chin... no, the 3rd one down.",
            "I don't know what makes you so stupid, but it really works.",
            "You are proof that evolution can go in reverse.",
            "Brains aren't everything. In your case, they're nothing.",
            "I thought of you today. It reminded me to take out the garbage.",
            "You're so ugly when you look in the mirror, your reflection looks away.",
            "Quick - check your face! I just found your nose in my business.",
            "It's better to let someone think you're stupid than open your mouth and prove it.",
            "You're such a beautiful, intelligent, wonderful person. Oh, I'm sorry, I thought we were having a lying competition.",
            "I'd slap you but I don't want to make your face look any better.",
            "You have the right to remain silent because whatever you say will probably be stupid anyway."
        ]
        if user is None:
            if ctx.bot.user.id == ctx.author.id:
                return await ctx.send(f"Nice try! I am not going to roast myself. Instead, I am going to roast you now.\n\n {ctx.author.mention} {choice(roasts)}")
            else:
                return await ctx.send(f"{ctx.author.mention} {choice(roasts)}")
        if user.id == ctx.bot.user.id:
            return await ctx.send(f"Nice try! I am not going to roast myself. Instead, I am going to roast you now.\n\n {ctx.author.mention} {choice(roasts)}")
        await ctx.send(f"{user.mention} {choice(roasts)}")

    @commands.command(aliases=['sc'])
    @commands.guild_only()
    async def smallcaps(self, ctx, *, message: str):
        """Convert text to small caps."""
        alpha = list(string.ascii_lowercase)
        converter = ['ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 'ɴ', 'ᴏ', 'ᴘ', 'ǫ', 'ʀ', 'ꜱ', 'ᴛ', 'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ']
        new_message = "".join(converter[alpha.index(char)] if char in alpha else char for char in message.lower())
        await ctx.send(new_message)

    @commands.command()
    async def cringe(self, ctx, *, message: str):
        """Make the text cringy by alternating case."""
        cringy_text = "".join(
            char.lower() if idx % 2 == 0 else char.upper()
            for idx, char in enumerate(message)
        )
        await ctx.send(cringy_text)
        await ctx.message.delete()

async def setup(bot):
    bot.add_cog(Fun(bot))
