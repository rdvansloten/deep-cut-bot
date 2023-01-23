# bot.py
import requests
import os
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from dateutil import parser
import random
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

headers = {
    'User-Agent': 'Deep Cut Bot',
    'From': 'https://github.com/rdvansloten/deep-cut-bot',
    'Contact': 'rudy@rdvansloten.com',
    'Message': 'Thank you so much for your wonderful data sources.'
}

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
  json_response = requests.get(f"https://splatoon3.ink/data/gear.json", headers=headers).json()
  now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%dT%H:%M:%SZ")

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
  json_response = requests.get(f"https://splatoon3.ink/data/festivals.json", headers=headers).json()

  # if json_response["US"]["data"]["festRecords"]["nodes"][0]["state"] != "CLOSED" and period == "now":
  #   instance = 0
  # elif json_response["US"]["data"]["festRecords"]["nodes"][0]["state"] == "CLOSED" and period == "previous":
  #   instance = 0
  # else:
  #   instance = 1
    
  splatfest_result = json_response["US"]["data"]["festRecords"]["nodes"][0]

  message = f"**SPLATFEST: {splatfest_result['title'].upper()}**\n"
  message += f"{get_schedule_time(category='range', start_time=splatfest_result['startTime'], end_time=splatfest_result['endTime'])}\n\n"

  current_lead_score = 0
  current_lead_team = ""
  score = ""
  index = 0

  for k, v in enumerate(splatfest_result["teams"]):
    message += f"** TEAM {v['teamName'].upper()} **\n"
    message += "```"
    try:
      message += f"Sneak Peek     : {'{:.2%}'.format(v['result']['horagaiRatio'])}\n"
    except:
      message += f"Sneak Peek     : Pending\n"

    try:
      message += f"Popularity     : {'{:.2%}'.format(v['result']['voteRatio'])}\n"
    except: 
      message += f"Popularity     : Pending\n"

    try:
      message += f"Normal Clout   : {'{:.2%}'.format(v['result']['regularContributionRatio'])}\n"
    except: 
      message += f"Normal Clout   : Pending\n"

    try:
      message += f"Pro Clout      : {'{:.2%}'.format(v['result']['challengeContributionRatio'])}\n"
    except: 
      message += f"Pro Clout      : Pending\n"

    try:
      message += f"Tricolor Clout : {'{:.2%}'.format(v['result']['tricolorContributionRatio'])}\n"
      
    except:
      message += f"Tricolor Clout : Pending \n"

    message += "```"
    message += f"\n"
    
    try:
      score = v['result']['horagaiRatio'] + v['result']['voteRatio'] + v['result']['regularContributionRatio'] + v['result']['challengeContributionRatio'] + v['result']['tricolorContributionRatio']
    except:
      score = 0

    if score > current_lead_score:
      current_lead_score = score
      current_lead_team = v['teamName'].upper()
      index = k
  
  if index == 0:
    current_lead_idol = "Shiver"
  elif index == 1:
    current_lead_idol = "Frye"
  elif index == 2:
    current_lead_idol = "Big Man"
  else:
    current_lead_idol = "N/A"

  if current_lead_team and current_lead_score > 0 and splatfest_result['state'] == "CLOSED":
    message += f"Winner: **TEAM {current_lead_team}** ({current_lead_idol})"
  elif current_lead_team and current_lead_score > 0 and splatfest_result['state'] != "CLOSED":
    message += f"Currently in the lead: **TEAM {current_lead_team}** ({current_lead_idol})"
  else:
    message += f"Results are pending. No team is in the lead yet."

  return message

def get_schedule(category, period=""):
  json_response = requests.get(f"https://splatoon3.ink/data/schedules.json", headers=headers).json()
  
  instance = 1 if period == "next" else 0
  when = "NEXT" if period == "next" else ""
    
  if category == "salmon-run":
    salmon_dict = {}
    salmon_dict['weapons'] = []

    salmon_run_schedule = json_response["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][instance]
    salmon_dict["description"] = f"**SALMON RUN**   {'_'+get_schedule_time(category='ends', end_time=salmon_run_schedule['endTime'])+'_' if period == 'now' else when}"
    
    salmon_dict["stage"] = f"{salmon_run_schedule['setting']['coopStage']['name']}"
    for i in salmon_run_schedule["setting"]["weapons"]:
      if i['name'] == "Random":
        salmon_dict['weapons'].append(f"[{i['name']}](https://splatoonwiki.org/wiki/Salmon_Run#Wildcard_rotation)")
      else:
        salmon_dict['weapons'].append(f"[{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')})")

    message = f"{salmon_dict['description']} \n"
    if period == "next":
      message += f"{get_schedule_time(category='range', start_time=salmon_run_schedule['startTime'], end_time=salmon_run_schedule['endTime'])}\n\n"
    else:
      message += "\n"
    message += f"**{salmon_dict['stage']}:**\n"
    for i in salmon_dict["weapons"]:
      message += f"- {i}\n"

  elif category == "anarchy-battle":
    anarchy_battle_schedule = json_response["data"]["bankaraSchedules"]["nodes"][instance]
    message = f"**ANARCHY BATTLE**   {'_'+get_schedule_time(category='ends', end_time=anarchy_battle_schedule['endTime'])+'_' if period == 'now' else when}\n"
    message += f"{get_schedule_time(category='range', start_time=anarchy_battle_schedule['startTime'], end_time=anarchy_battle_schedule['endTime'])}\n"

    for i in anarchy_battle_schedule['bankaraMatchSettings']:
      message += "\n"
      message += f"** {i['vsRule']['name']} ({'Series' if i['mode'] == 'CHALLENGE' else 'Open'}): **\n"

      for i in i['vsStages']:
        message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  elif category == "x-battle":
    x_battle_schedule = json_response["data"]["xSchedules"]["nodes"][instance]
    message = f"**X BATTLE**   {'_'+get_schedule_time(category='ends', end_time=x_battle_schedule['endTime'])+'_' if period == 'now' else when}\n"
    message += f"{get_schedule_time(category='range', start_time=x_battle_schedule['startTime'], end_time=x_battle_schedule['endTime'])}\n\n"

    message += f"** {x_battle_schedule['xMatchSetting']['vsRule']['name']}: **\n"
    for i in x_battle_schedule['xMatchSetting']['vsStages']:
      message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  elif category == "league-battle":
    league_battle_schedule = json_response["data"]["leagueSchedules"]["nodes"][instance]
    message = f"**LEAGUE BATTLE**   {'_'+get_schedule_time(category='ends', end_time=league_battle_schedule['endTime'])+'_' if period == 'now' else when}\n"
    message += f"{get_schedule_time(category='range', start_time=league_battle_schedule['startTime'], end_time=league_battle_schedule['endTime'])}\n\n"
    message += f"** {league_battle_schedule['leagueMatchSetting']['vsRule']['name']}: **\n"

    for i in league_battle_schedule['leagueMatchSetting']['vsStages']:
      message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  elif category == "regular-battle":
    regular_battle_schedule = json_response["data"]["regularSchedules"]["nodes"][instance]
    message = f"**REGULAR BATTLE**   {'_'+get_schedule_time(category='ends', end_time=regular_battle_schedule['endTime'])+'_' if period == 'now' else when}\n"
    message += f"{get_schedule_time(category='range', start_time=regular_battle_schedule['startTime'], end_time=regular_battle_schedule['endTime'])}\n\n"
    message += f"** {regular_battle_schedule['regularMatchSetting']['vsRule']['name']}: **\n"

    for i in regular_battle_schedule['regularMatchSetting']['vsStages']:
      message += f"- [{i['name']}](https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}) \n"

  else:
    message = "No valid game mode selected"

  return message

def subscribe_channel(guild_id, channel_id):
  return f"Server ID = {guild_id}, Channel ID = {channel_id}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Songs
class music(app_commands.Group):
  @app_commands.command(name="random", description="Get a random Deep Cut song.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_song(category="random"), suppress_embeds=False)

  @app_commands.command(name="all", description="Get a list of all Deep Cut songs.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_song(category="all"), suppress_embeds=True)

tree.add_command(music(name="music", description = "Get Deep Cut songs."))

# Regular Battle
class regular_battle(app_commands.Group):
  @app_commands.command(name="next", description="Get the next Regular Battle rotation.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("regular-battle", period = "next"), suppress_embeds=True)

  @app_commands.command(name="now", description="Get the current Regular Battle rotation.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("regular-battle", period = "now"), suppress_embeds=True)
  
  # @app_commands.command(name="now", description="Get the current Regular Battle rotation.")
  # async def now(self, interaction: discord.Interaction) -> None:
  #     schedule = get_schedule("regular-battle", period = "now")
  #     embed1 = discord.Embed(title='Test1', description="Hi")
  #     embed2 = discord.Embed(title='Wahoo World', url="https://splatoonwiki.org/wiki/Wahoo_World")
  #     await interaction.response.send_message(get_schedule("regular-battle", period = "next"), embeds=[embed1, embed2])

tree.add_command(regular_battle(name="regular-battle", description = "Get X Battle schedules."))

# X Battle
class x_battle(app_commands.Group):
  @app_commands.command(name="next", description="Get the current X Battle rotation.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("x-battle", period = "next"), suppress_embeds=True)

  @app_commands.command(name="now", description="Get the next X Battle rotation.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("x-battle", period = "now"), suppress_embeds=True)

tree.add_command(x_battle(name="x-battle", description = "Get X Battle schedules."))

# Anarchy Battle
class anarchy_battle(app_commands.Group):
  @app_commands.command(name="next", description="Get the current Anarchy Battle rotation.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("anarchy-battle", period = "next"), suppress_embeds=True)

  @app_commands.command(name="now", description="Get the next Anarchy Battle rotation.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("anarchy-battle", period = "now"), suppress_embeds=True)

tree.add_command(anarchy_battle(name="anarchy-battle", description = "Get Anarchy Battle schedules."))

# League Battle
class league_battle(app_commands.Group):
  @app_commands.command(name="next", description="Get the current League Battle rotation.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("League-battle", period = "next"), suppress_embeds=True)

  @app_commands.command(name="now", description="Get the next League Battle rotation.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("league-battle", period = "now"), suppress_embeds=True)

tree.add_command(x_battle(name="league-battle", description = "Get League Battle schedules."))

# Salmon Run
class salmon_run(app_commands.Group):
  @app_commands.command(name="next", description="Get the next Salmon Run rotation.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("salmon-run", period = "next"), suppress_embeds=True)

  @app_commands.command(name="now", description="Get the current Salmon Run rotation.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_schedule("salmon-run", period = "now"), suppress_embeds=True)

  # @app_commands.command(name="subscribe", description="Subscribe this channel to the Salmon Run schedule.")
  # async def subscribe(self, interaction: discord.Interaction):
  #   guild_id = interaction.message.guild.id
  #   channel_id = interaction.message.channel.id
  #   await interaction.response.send_message(subscribe_channel(guild_id=guild_id, channel_id=channel_id), suppress_embeds=True)

  @app_commands.command(name="subscribe", description="Subscribe this channel to the Salmon Run schedule.")
  async def subscribe(ctx):
      message = ctx.message
      channel_id = message.channel.id
      guild_id = message.guild.id
      await ctx.send(f"Channel ID: {channel_id}, Guild ID: {guild_id}")

tree.add_command(salmon_run(name="salmon-run", description = "Get Salmon Run schedules."))

# Splatnet Shop
class splatnet_shop(app_commands.Group):
  @app_commands.command(name="sale", description="Get the current On Sale gear.")
  async def next(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_gear(category="on-sale"), suppress_embeds=True)
  
  @app_commands.command(name="daily", description="Get the current Daily Drop gear.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_gear(category="daily-drop"), suppress_embeds=True)

tree.add_command(splatnet_shop(name="splatnet-shop", description = "Get Splatnet Shop gear."))

# Splatfest
class splatfest(app_commands.Group):
  @app_commands.command(name="results", description="Get the latest Splatfest results.")
  async def now(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(get_splatfest(), suppress_embeds=True)

tree.add_command(splatfest(name="splatfest", description = "Get Splatfest data."))

# Big Run
# class big_run(app_commands.Group):
#   @app_commands.command(name="next", description="Get the next Big Run rotation.")
#   async def next(self, interaction: discord.Interaction) -> None:
#     await interaction.response.send_message("The next Big Run is not known yet.", suppress_embeds=True)

#   @app_commands.command(name="now", description="Get the current Big Run rotation.")
#   async def now(self, interaction: discord.Interaction) -> None:
#     await interaction.response.send_message("There is no Big Run going on.", suppress_embeds=True)

# tree.add_command(big_run(name="big-run", description = "Get Big Run schedules."))

# Splatfest
# class splatfest(app_commands.Group):
#   @app_commands.command(name="last", description="Get the last Splatfest results.")
#   async def next(self, interaction: discord.Interaction) -> None:
#     await interaction.response.send_message(get_splatfest(), suppress_embeds=True)
  
#   @app_commands.command(name="previous", description="Get the previous Splatfest results.")
#   async def now(self, interaction: discord.Interaction) -> None:
#     await interaction.response.send_message(get_splatfest(), suppress_embeds=True)

# tree.add_command(splatfest(name="splatfest", description = "Get Splatfest results."))

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(TOKEN)