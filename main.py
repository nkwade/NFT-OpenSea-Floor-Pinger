import discord
from discord.ext import commands
from data import floorSetup, parseData, addFloorTracker
import asyncio
import os
import json

bot = commands.Bot(command_prefix='$nft ')

@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))


@bot.command() 
async def floor(message, collection):
  def check(m):
    return m.author == message.author and m.channel == message.channel

  embedVar = discord.Embed(
      title="{} Floor Price Is: {} ETH".format(collection, parseData(collection, "floor_price"),
      color=0x0000FF))
  await message.channel.send(embed=embedVar)
  return

#Command - DONE
@bot.command()
async def setup(message):
  #g = message.guild.name

  def check(m):
    return m.author == message.author and m.channel == message.channel

  embedVar = discord.Embed(
      title="Please Enter The Name Of The @ You Would Like To Mention ",
      description="Example: If:@everyone Then Type: everyone",
      color=0x0000FF)
  await message.channel.send(embed=embedVar)

  try:
    roleName = await bot.wait_for('message', check=check, timeout=30.0)
  except asyncio.TimeoutError:
    embedVar6 = discord.Embed(title="Command Timed Out Please Restart",
                              color=0x0000FF)
    await message.channel.send(embed=embedVar6)
    return

  #go through all the roles and find the right role id for the specified roel
  for r in message.guild.roles:
    if (r.name == roleName.content):
      role = r

  embedVar2 = discord.Embed(
      title="Please Enter The Channel ID Of The Channel You Would Like To Post To",
      description="Example: 828656735991627778",
      color=0x0000FF)
  await message.channel.send(embed=embedVar2)

  try:
    channel = await bot.wait_for('message', check=check, timeout=30.0)
  except asyncio.TimeoutError:
    embedVar6 = discord.Embed(title="Command Timed Out Please Restart",
                              color=0x0000FF)
    await message.channel.send(embed=embedVar6)
    return
  
  try:
    floorSetup(message.guild.id, channel.content, role.name)
    embedVar2 = discord.Embed(title="Successfully Setup Bot", color=0x0000FF)
    await message.channel.send(embed=embedVar2)
  except:
    embedVar3 = discord.Embed(title="Error: Retry or Contact Dev", color=0x0000FF)
    await message.channel.send(embed=embedVar3)
  return

@bot.command()
async def addFloor(message):
  def check(m):
    return m.author == message.author and m.channel == message.channel

  embedVar = discord.Embed(
      title="What is the name of the collection you would like to add?",
      color=0x0000FF)
  await message.channel.send(embed=embedVar)

  try:
    collection = await bot.wait_for('message', check=check, timeout=30.0)
  except asyncio.TimeoutError:
    embedVar6 = discord.Embed(title="Command Timed Out Please Restart",
                              color=0x0000FF)
    await message.channel.send(embed=embedVar6)
    return
  #try:
  addFloorTracker(message.guild.id, collection.content)
  embedVar2 = discord.Embed(title="Successfully Added Floor", color=0x0000FF)
  await message.channel.send(embed=embedVar2)
  #except:
  #  embedVar3 = discord.Embed(title="Error: Retry or Contact #Dev", color=0x0000FF)
  #  await message.channel.send(embed=embedVar3)
  #  return 
  

def autoStat(guild, collection, stat):
  with open(os.path.join('/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots','{} floor setup.json'.format(guild)), 'r') as file:
    jsonFile = json.load(file)
    guild = bot.get_guild(int(jsonFile["guild"]))
    channel = guild.get_channel(jsonFile["channel"])
    role = jsonFile["role"]
    for r in guild.roles:
      if r.name == role:
        pingedRole = r
    embedVar = discord.Embed(
        title="{} {} Is: {} ETH {}".format(collection, parseData(collection, stat), pingedRole.mention), color=0x0000FF)
    channel.send(embed=embedVar)
    return

#starts the program
bot.run(os.environ['botKey'])