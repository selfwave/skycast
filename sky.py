import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Literal, Optional
import os, requests, random, asyncio, aiohttp, wikipedia, yaml
import datetime as dt

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["command_prefix"]), intents=discord.Intents.all())
bot.remove_command('help')
tree = bot.tree

api_key = config["api_key"]

@tree.command(name='weather', description='Get the weather for a city')
async def weather(interaction: discord.Interaction, city: str):
    city_name = city
    complete_url = base_url + "key=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    weather_data = response.json()

    if "error" not in weather_data:
        await interaction.response.defer(thinking=True)
        current_temperature = weather_data.get("current", {}).get("temp_c")
        current_pressure = weather_data.get("current", {}).get("pressure_mb")
        current_humidity = weather_data.get("current", {}).get("humidity")
        weather_description = weather_data.get("current", {}).get("condition", {}).get("text", "No description available.")

        if current_temperature is not None:
            embed = discord.Embed(title=f"Weather in {city_name}",
                                color=interaction.guild.me.top_role.color,
                                timestamp=discord.utils.utcnow())
            embed.add_field(name="Description", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Temperature(C)", value=f"**{current_temperature}°C**", inline=False)
            if current_humidity is not None:
                embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            if current_pressure is not None:
                embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1212020481264193609/1217213785270652928/fiwtRwB1m6fjDIy.gif?ex=660335ad&is=65f0c0ad&hm=eab3183399466436d24e6c023860ede8141e85740cec358e30ed6612e3442284&=&width=610&height=610")
            embed.set_footer(text=f"Requested by {interaction.user.name}")

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Weather data for the requested city is incomplete.")
    else:
        await interaction.followup.send(f"Error: {weather_data.get('error', {}).get('message', 'City not found.')}")

@bot.command(name='weather', help='Get the weather for a city')
async def weather(ctx, *, city: str):
    city_name = city
    complete_url = base_url + "key=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    weather_data = response.json()

    if "error" not in weather_data:
        current_temperature = weather_data.get("current", {}).get("temp_c")
        current_pressure = weather_data.get("current", {}).get("pressure_mb")
        current_humidity = weather_data.get("current", {}).get("humidity")
        weather_description = weather_data.get("current", {}).get("condition", {}).get("text", "No description available.")

        if current_temperature is not None:
            embed = discord.Embed(title=f"Weather in {city_name}",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=discord.utils.utcnow())
            embed.add_field(name="Description", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Temperature(C)", value=f"**{current_temperature}°C**", inline=False)
            if current_humidity is not None:
                embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            if current_pressure is not None:
                embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1212020481264193609/1217213785270652928/fiwtRwB1m6fjDIy.gif?ex=660335ad&is=65f0c0ad&hm=eab3183399466436d24e6c023860ede8141e85740cec358e30ed6612e3442284&=&width=610&height=610")
            embed.set_footer(text=f"Requested by {ctx.author.name}")

            await ctx.send(embed=embed)
        else:
            await ctx.send("Weather data for the requested city is incomplete.")
    else:
        await ctx.send(f"Error: {weather_data.get('error', {}).get('message', 'City not found.')}")

@tree.command(name='wikipedia', description="Get information about something from Wikipedia")
async def cityinfo(interaction: discord.Interaction, text: str):
    await interaction.response.defer()

    try:
        page = wikipedia.page(text)
        summary = page.summary[0:150]
        page_url = page.url

        embed = discord.Embed(title=page.title, url=page_url, description=summary + "...", color=interaction.guild.me.top_role.color)
        embed.set_thumbnail(url=page.images[0])
        embed.set_footer(text="Information provided by Wikipedia")

        await interaction.followup.send(embed=embed)
    except wikipedia.exceptions.DisambiguationError as e:
        await interaction.followup.send(f"There are several pages that match the term '{text}'. Please be more specific.")
    except wikipedia.exceptions.PageError:
        await interaction.followup.send(f"Sorry, I couldn't find any information on '{text}'.")

@bot.command()
async def wikipedia(ctx, *, text: str):
    try:
        page = wikipedia.page(text)
        summary = page.summary[0:150]
        page_url = page.url

        embed = discord.Embed(title=page.title, url=page_url, description=summary + "...", color=ctx.guild.me.top_role.color)
        embed.set_thumbnail(url=page.images[0])
        embed.set_footer(text="Information provided by Wikipedia")

        await ctx.send(embed=embed)
    except wikipedia.exceptions.DisambiguationError as e:
        await ctx.send(f"There are several pages that match the term '{text}'. Please be more specific.")
    except wikipedia.exceptions.PageError:
        await ctx.send(f"Sorry, I couldn't find any information on '{text}'.")

from pytz import timezone
import pytz
from datetime import datetime

@tree.command(name='time', description='Get the time in a city')
async def time(interaction: discord.Interaction, timezone_name: str):
    try:
        city_timezone = timezone(timezone_name)
        city_time = datetime.now(city_timezone)
        await interaction.response.defer(thinking=True)
        await interaction.response.send_message(city_time.strftime('%H:%M:%S'))
    except pytz.exceptions.UnknownTimeZoneError:
        await interaction.response.send_message(f"Could not find the time zone for {timezone_name}. Please check the timezone name and try again.")

@bot.command()
async def time(ctx, *, timezone_name: str):
    try:
        city_timezone = timezone(timezone_name)
        city_time = datetime.now(city_timezone)
        await ctx.send(city_time.strftime('%H:%M:%S'))
    except pytz.exceptions.UnknownTimeZoneError:
        await ctx.send(f"Could not find the time zone for {timezone_name}. Please check the timezone name and try again.")

@bot.event
async def on_ready():
    current = dt.datetime.now()

    wow = current.strftime('%H:%M:%S')
    
    print(f'{wow} | Logged in as {bot.user.name}')

    await bot.tree.sync()

    await change_status_loop()

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def change_status_loop():
    while True:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=""))
        await asyncio.sleep(5)
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=""))
        await asyncio.sleep(5)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=""))
        await asyncio.sleep(5)

@tree.command(name="help", description="Get help on using SkyCast")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="SkyCast Help", color=interaction.guild.me.top_role.color)

    embed.add_field(name="time", value="Get the time in a city", inline=False)
    embed.add_field(name="weather", value="Get the weather for a city", inline=False)
    embed.add_field(name="wikipedia", value="Get information about something from Wikipedia", inline=False)

    embed.set_footer(text="TIP: U can use prefix to call commands (>time, >weather, >wikipedia)")

    await interaction.response.send_message(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="SkyCast Help", color=ctx.guild.me.top_role.color)

    embed.add_field(name="time", value="Get the time in a city", inline=False)
    embed.add_field(name="weather", value="Get the weather for a city", inline=False)
    embed.add_field(name="wikipedia", value="Get information about something from Wikipedia", inline=False)

    await ctx.send(embed=embed)

bot.run(config["token"])
