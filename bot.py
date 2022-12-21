# bot.py
import requests
import os
import json
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from dateutil import parser
import random
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def get_schedule_time(category, end_time, start_time=""):
  start_time = "" if not start_time else parser.parse(start_time).astimezone(timezone(timedelta(hours=0), name="UTC"))
  end_time = "" if not end_time else parser.parse(end_time).astimezone(timezone(timedelta(hours=0), name="UTC"))
  
  if category == "ends" and end_time:
    difference = end_time - datetime.now().astimezone(timezone(timedelta(hours=0), name="UTC"))

    if round(int(difference.total_seconds() / 3600)) == 0:
      time_remaining = f"{round(int(difference.total_seconds() / 60))} minutes remaining"

    elif round(int(difference.total_seconds() / 3600)) == 1:
      time_remaining = f"{round(int(difference.total_seconds() / 3600))} hour and {round(int(difference.total_seconds() / 60)) - (round(int(difference.total_seconds() / 3600)) * 60)} minutes remaining"

    else:
      time_remaining = f"{round(int(difference.total_seconds() / 3600))} hours and {round(int(difference.total_seconds() / 60)) - (round(int(difference.total_seconds() / 3600)) * 60)} minutes remaining"

  elif category == "range" and start_time and end_time:
    time_remaining = f"From [{datetime.strftime(start_time, '%d %b %H:%M')}](https://www.utctime.net) to [{datetime.strftime(end_time, '%d %b %H:%M')}](https://www.utctime.net) UTC"

  else:
    time_remaining = f"No valid category assigned, or start/end time are not set properly."

  return time_remaining
  
def get_song(category):
  songs = {
    'Til Depth Do Us Part':'https://www.youtube.com/watch?v=lw1XwyW39uk', 
    'Now or Never': 'https://www.youtube.com/watch?v=ua4s7tV8WGM', 
    'Calamari Inkantation 3MIX': 'https://www.youtube.com/watch?v=_TE22RCxCi4', 
    'Fins in the Air': 'https://www.youtube.com/watch?v=LOw5-bNoutg', 
    'Anarchy Rainbow':'https://www.youtube.com/watch?v=sZ4vY_UmMIY',
    'Hide and Sleek': 'https://www.youtube.com/watch?v=nsMWO_5aWE8',
    'The Spirit Lifter: Steerage & First Class': 'https://www.youtube.com/watch?v=mxOJ6OeF42E'
  }

  if category == "random":
    title, url = random.choice(list(songs.items()))
    message = f"[Deep Cut - {title}]({url})"
  elif category == "all":
    message = ""
    for k, v in songs.items():
      message += f"- [Deep Cut - {k}]({v})\n"

  print(message)
  return message

def get_gear(category):
  json_response = requests.get(f"https://splatoon3.ink/data/gear.json").json()
  now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%dT%H:%M:%SZ")
  utc_time = timezone(timedelta(hours=0), name="UTC")

  if category == "daily-drop":
    data = json_response["data"]["gesotown"]["pickupBrand"]

    if now <= data["saleEndTime"]:
      message = f"**THE DAILY DROP: {data['brand']['name']}**   _{get_schedule_time(category='ends', end_time=data['saleEndTime'])}_\n"

      for i in data['brandGears']:
        message += " \n"
        message += f"**[{i['gear']['name']}](https://splatoonwiki.org/wiki/{i['gear']['name'].replace(' ', '_')})** \n"
        message += "```"
        message += f"Ability : {i['gear']['primaryGearPower']['name']}\n"
        message += f"Price   : {i['price']}\n"
        message += f"```"

  elif category == "on-sale":
    message = f"**GEAR ON SALE NOW**\n"
    
    for i in json_response["data"]["gesotown"]["limitedGears"]:
      if now <= i["saleEndTime"]:
        message += " \n"
        message += f"**[{i['gear']['name']}](https://splatoonwiki.org/wiki/{i['gear']['name'].replace(' ', '_')})**   _{get_schedule_time(category='ends', end_time=i['saleEndTime'])}_\n"
        message += "```"
        message += f"Ability : {i['gear']['primaryGearPower']['name']}\n"
        message += f"Brand   : {i['gear']['brand']['name']}\n"
        message += f"Price   : {i['price']}\n"
        message += f"```"
  else:
    message = "Invalid category selected."
  
  return message

def get_splatfest():
  json_response = requests.get(f"https://splatoon3.ink/data/festivals.json").json()
  now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%dT%H:%M:%SZ")
  
  for i in json_response["US"]["data"]["festRecords"]["nodes"]:
    if now <= i["endTime"] and now >= i["startTime"]:      
      message = f"**{i['title'].upper()}** ({get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n\n"

      for i in i["teams"]:
        message += f"\n"
        message += f"** TEAM {i['teamName'].upper()} **\n"

        message += f"- Sneak Peek: {'{:.0%}'.format(i['result']['horagaiRatio'])}\n"
        message += f"- Popularity: {'{:.0%}'.format(i['result']['voteRatio'])}\n"
        message += f"- Regular Mode Clout: {'{:.0%}'.format(i['result']['regularContributionRatio'])}\n"
        message += f"- Pro Mode Clout {'{:.0%}'.format(i['result']['challengeContributionRatio'])}\n"

    else:
      message = f"There is currently no Splatfest going on. Please check back later."
   
  return message

def get_schedule(category):
  json_response = requests.get(f"https://splatoon3.ink/data/schedules.json").json()
  now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%dT%H:%M:%SZ")
  utc_time = timezone(timedelta(hours=0), name="UTC")
  
  if category == "salmon-run":
  #   if args == "upcoming" or args == "":
  #     message = f"**SALMON RUN (UPCOMING)**\n"
  #     message += f"{get_schedule_time(category='range', start_time=salmon_run_schedule['startTime'], end_time=salmon_run_schedule['endTime'])}\n\n"
  #     message += f"** {salmon_run_schedule['setting']['coopStage']['name']}: **\n"
  #     for i in salmon_run_schedule["setting"]["weapons"]:
  #       message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

    # elif args == "current":
    salmon_run_schedule = json_response["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][0]

    message = f"**SALMON RUN**   _{get_schedule_time(category='ends', end_time=salmon_run_schedule['endTime'])}_\n"
    message += f"{get_schedule_time(category='range', start_time=salmon_run_schedule['startTime'], end_time=salmon_run_schedule['endTime'])}\n\n"
    message += f"** {salmon_run_schedule['setting']['coopStage']['name']}: **\n"
    for i in salmon_run_schedule["setting"]["weapons"]:
      message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

    # for i in json_response["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"]:
    #   if now <= i["endTime"] and now >= i["startTime"]:
    #     message = f"**SALMON RUN**   _{get_schedule_time(category='ends', end_time=i['endTime'])}_\n"
    #     message += f"{get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n\n"
    #     message += f"** {i['setting']['coopStage']['name']}: **\n"
    #     for i in i["setting"]["weapons"]:
    #       message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  elif category == "anarchy-battle":
    for i in json_response["data"]["bankaraSchedules"]["nodes"]:
       if now <= i["endTime"] and now >= i["startTime"]:
        message = f"**ANARCHY BATTLE**   _{get_schedule_time(category='ends', end_time=i['endTime'])}_\n"
        message += f"{get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n"

        for i in i['bankaraMatchSettings']:
          if i['mode'] == "CHALLENGE":
            mode = "Series"
          elif i['mode'] == "OPEN":
            mode = "Open"
          else:
            mode = "Special"

          message += "\n"
          message += f"** {i['vsRule']['name']} ({mode}): **\n"

          for i in i['vsStages']:
            message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  elif category == "x-battle":
    for i in json_response["data"]["xSchedules"]["nodes"]:
       if now <= i["endTime"] and now >= i["startTime"]:
        message = f"**X BATTLE**   _{get_schedule_time(category='ends', end_time=i['endTime'])}_\n"
        message += f"{get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n\n"

        message += f"** {i['xMatchSetting']['vsRule']['name']}: **\n"
        for i in i['xMatchSetting']['vsStages']:
          message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"
  
  elif category == "league-battle":
    for i in json_response["data"]["leagueSchedules"]["nodes"]:
       if now <= i["endTime"] and now >= i["startTime"]:
        message = f"**LEAGUE BATTLE**   _{get_schedule_time(category='ends', end_time=i['endTime'])}_\n"
        message += f"{get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n\n"
        message += f"** {i['leagueMatchSetting']['vsRule']['name']}: **\n"
        for i in i['leagueMatchSetting']['vsStages']:
          message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"
  
  elif category == "regular-battle":
    for i in json_response["data"]["regularSchedules"]["nodes"]:
       if now <= i["endTime"] and now >= i["startTime"]:
        message = f"**REGULAR BATTLE**   _{get_schedule_time(category='ends', end_time=i['endTime'])}_\n"
        message += f"{get_schedule_time(category='range', start_time=i['startTime'], end_time=i['endTime'])}\n\n"
        message += f"** {i['regularMatchSetting']['vsRule']['name']}: **\n"
        for i in i['regularMatchSetting']['vsStages']:
          message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  else:
    message = "No valid game mode selected"

  return message

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "random-song", description = "Listen to a random Deep Cut song.")
async def songs(interaction):
    await interaction.response.send_message(get_song("random"), suppress_embeds=False)

@tree.command(name = "all-songs", description = "Get all Deep Cut songs.")
async def songs(interaction):
    await interaction.response.send_message(get_song("all"), suppress_embeds=True)

@tree.command(name = "regular-battle", description = "Get the current Regular Battle rotation.")
async def regular_battle(interaction):
    await interaction.response.send_message(get_schedule("regular-battle"), suppress_embeds=True)

@tree.command(name = "salmon-run", description = "Get the current Salmon Run rotation.")
async def salmon_run(interaction):
    await interaction.response.send_message(get_schedule("salmon-run"), suppress_embeds=True)

@tree.command(name = "anarchy-battle", description = "Get the current Anarchy Battle rotation.")
async def anarchy_battle(interaction):
    await interaction.response.send_message(get_schedule("anarchy-battle"), suppress_embeds=True)

@tree.command(name = "x-battle", description = "Get the current X Battle rotation.")
async def x_battle(interaction):
    await interaction.response.send_message(get_schedule("x-battle"), suppress_embeds=True)

@tree.command(name = "league-battle", description = "Get the current League Battle rotation.")
async def league_battle(interaction):
    await interaction.response.send_message(get_schedule("league-battle"), suppress_embeds=True)

@tree.command(name = "daily-drop", description = "Get the current Daily Drop Gear.")
async def daily_drop(interaction):
    await interaction.response.send_message(get_gear("daily-drop"), suppress_embeds=True)

@tree.command(name = "on-sale", description = "Get the current On Sale Gear.")
async def on_sale(interaction):
    await interaction.response.send_message(get_gear("on-sale"), suppress_embeds=True)

@tree.command(name = "splatfest", description = "Get the current Splatfest results.")
async def splatfest(interaction):
    await interaction.response.send_message(get_splatfest(), suppress_embeds=True)

@tree.command(name='salmon-run-beta')
async def salmon_run_beta(interaction, subcommand: str):
  if subcommand == 'upcoming':
    # code to display upcoming Salmon Run events
    pass
  elif subcommand == 'current':
    # code to display current Salmon Run event
    pass
  else:
    await interaction.response.send_message('Invalid subcommand. Please use "upcoming" or "current".')

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(TOKEN)