import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
import threading
import time
import requests
import urllib.request

bot = commands.Bot(command_prefix='$nft ')

@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))
  print("in start program")
    #starts all the floor trackers when the program has to restart
  path = "/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots"
  for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as readFile:
      jsonFile = json.load(readFile)
      for c in jsonFile["collections"]:
        print("starting thread")
        asyncio.get_event_loop().create_task(checkForFloor(jsonFile["guild"], c))
      readFile.close()
  


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

#Command - DONE
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
  try:
    addFloorTracker(message.guild.id, collection.content)
    embedVar2 = discord.Embed(title="Successfully Added Floor", color=0x0000FF)
    await message.channel.send(embed=embedVar2)
  except:
    embedVar3 = discord.Embed(title="Error: Retry or Contact #Dev", color=0x0000FF)
    await message.channel.send(embed=embedVar3)
    return 
  
#function - DONE
def floorSetup(guild, channel, role):
  dictionary = {
    "guild" : str(guild),
    "channel" : channel,
    "role" : role,
    "collections" : []
  }
  with open(os.path.join('/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots','{} floor setup.json'.format(guild)), 'w+') as file:
      json.dump(dictionary, file)
      file.close()

#function - DONE - gets the default image for the collection
def getImage(collection):
  url = "https://api.opensea.io/api/v1/collection/{}/?format=json".format(collection)
  response = requests.request("GET", url)
  responseString = response.text
  jsonData = json.loads(responseString)
  url = jsonData['collection']['primary_asset_contracts']['image_url']
  urllib.request.urlretrieve(url,"{}.png".format(collection))
  
#function - DONE - gets data from opensea api
def parseData(collection, stat):
  url = "https://api.opensea.io/api/v1/collection/{}/?format=json".format(collection)
  response = requests.request("GET", url)
  responseString = response.text
  jsonData = json.loads(responseString)
  return jsonData["collection"]["stats"][stat]
  
async def autoStat(guild, collection, stat):
  with open(os.path.join('/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots','{} floor setup.json'.format(guild)), 'r') as file:
    jsonFile = json.load(file)
    guild = bot.get_guild(int(jsonFile["guild"]))
    channel = guild.get_channel(int(jsonFile["channel"]))
    role = jsonFile["role"]
    for r in guild.roles:
      if r.name == role:
        pingedRole = r
    embedVar = discord.Embed(
        title="{} Is: {} ETH {}".format(collection, parseData(collection, stat), pingedRole.mention), color=0x0000FF)
    await channel.send(embed=embedVar)
    return


#function - CHECK threading
def addFloorTracker(guild, collection):
  with open(os.path.join('/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots','{} floor setup.json'.format(guild)), "r") as file:
    jsonFile = json.load(file)
    collections = jsonFile["collections"]
    collections.append(collection)
    jsonFile["collections"] = collections
    file.close()
  with open(os.path.join('/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots','{} floor setup.json'.format(guild)), "w") as file:
    json.dump(jsonFile, file)
  with open('{} floor price.txt'.format(collection), 'w+') as file:
    file.write(str(0))
    file.close()
  asyncio.get_event_loop().create_task(checkForFloor(guild, collection))

#function - TODO autostat and writing to the file 
@tasks.loop(seconds=10, count=1)
async def checkForFloor(guild, collection):
  #print("inside thread")
  while(True):
    #print("start of while loop")
    price = float(parseData(collection, "floor_price"))
    #print("price is " + str(price))
    oldPrice = None
    with open('{} floor price.txt'.format(collection), 'r') as file:
      oldPrice = float(file.readline())
      #print(str(oldPrice))
      file.close()
    if (price != oldPrice) and (oldPrice != None):
      #print("old string does not equal new string")
      with open('{} floor price.txt'.format(collection), 'w') as file:
        file.write(str(price))
        file.close()
      await autoStat(guild, collection, "floor_price")
    #print("about to sleep")
    await asyncio.sleep(120)
    #print("done sleeping")

#starts the program
bot.run(os.environ['botKey'])