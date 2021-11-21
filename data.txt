import threading
import time
import requests
import json
import urllib.request
import os

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
  thread = threading.Thread(target=checkForFloor, args=(guild, collection))
  thread.start()

#function - TODO autostat and writing to the file 
def checkForFloor(guild, collection):
  print("inside thread")
  while(True):
    print("start of while loop")
    price = parseData(collection, "floor_price")
    oldPrice = None
    with open('{} floor price.txt'.format(collection), 'r') as file:
      oldPrice = file.read()
      file.close()
    if (price != oldPrice) and (oldPrice != None):
      with open('{} floor price.txt'.format(collection), 'w') as file:
        file.write(str(price))
        file.close()
      autoStat(guild, collection, price)
    print("about to sleep")
    time.sleep(5)
    print("done sleeping")


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
  return jsonData['collection']['stats'][stat]
  
#starts all the floor trackers when the program has to restart
path = "/home/runner/NFT-OpenSea-Floor-Pinger/Floor Bots"

for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as readFile:
      jsonFile = json.load(readFile)
      for c in jsonFile["collections"]:
        floorThread = threading.Thread(target=checkForFloor, args=(jsonFile["guild"], c))
        floorThread.start()
      readFile.close()
    
