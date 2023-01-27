import csv
import requests
import os
import discord
from discord import app_commands
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from dateutil import parser
from discord.ext import tasks, commands

def check_csv(channel_id, guild_id, csv_file):
  try:
    with open(csv_file, 'r') as f:
      for i, row in enumerate(csv.reader(f)):
        if i == 0:
          if row[1] == str(channel_id) and row[0] == str(guild_id):
            return True
    return False
  except FileNotFoundError:
    open(csv_file, 'w').close()
    return False

def subscribe_channel(guild_id, channel_id, guild_name, channel_name, administrator, csv_file):
  if not administrator:
    return "Only Administrators can subscribe a channel to the Salmon Run schedule."

  # Add entry to csv file
  if not check_csv(channel_id=channel_id, guild_id=guild_id, csv_file=csv_file):
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
      csv.writer(f).writerow([
        guild_id, 
        channel_id, 
        guild_name, 
        channel_name
      ])
      return f"Successfully subscribed <#{channel_id}> to the Salmon Run schedule!"
  else:
    return f"Channel <#{channel_id}> is already subscribed to the Salmon Run schedule."

def unsubscribe_channel(guild_id, channel_id, administrator, csv_file):
  if not administrator:
    return "Only Administrators can unsubscribe a channel from the Salmon Run schedule."

  # Remove entry from csv file
  if check_csv(channel_id=channel_id, guild_id=guild_id, csv_file=csv_file):
    rows = []
    with open(csv_file, "r") as f:
      for row in csv.reader(f):
        if row[1] != str(channel_id) and row[0] != str(guild_id):
          rows.append(row)

      # Write the updated rows to a new CSV file
      with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    return f"Successfully unsubscribed <#{channel_id}> from the Salmon Run schedule!"
  else:
    return f"Failed to unsubscribe. Channel <#{channel_id}> was not subscribed to the Salmon Run schedule."

# Scheduled message
@tasks.loop(minutes=1)
async def salmon_run_schedule():
  json_response = requests.get(f"https://splatoon3.ink/data/schedules.json").json()
  salmon_run_schedule = json_response["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][0]

  start_time = salmon_run_schedule["startTime"]
  end_time = salmon_run_schedule["endTime"]
  now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%dT%H:%M:%SZ")

  # if now <= end_time and now >= start_time:
  if True:
    if salmon_run_schedule['setting']['coopStage']['name']:
      utc_time = timezone(timedelta(hours=0), name="UTC")
      start_time = parser.parse(start_time).astimezone(utc_time)
      end_time = parser.parse(end_time).astimezone(utc_time)

      message = f"**{salmon_run_schedule['setting']['coopStage']['name']}** \n The current rotation runs from {datetime.strftime(start_time, '%Y-%m-%d %H:%M')} to {datetime.strftime(end_time, '%Y-%m-%d %H:%M')} [UTC Time](https://www.utctime.net). \n \n GET TO WORK. \n \n **Weapons:**"

      embeds = []
        
      for i in salmon_run_schedule["setting"]["weapons"]:        
        embed = discord.Embed()
        # Set the thumbnail
        embed.set_thumbnail(url=f"{i['image']['url']}")
        embed.description(message)
        # Set the title and URL
        embed.set_author(name=f"{i['name']}", url=f"https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}")

        # Set the URL of the embed
        embed.url = f"https://splatoonwiki.org/wiki/{i['name'].replace(' ', '_')}"
        
        embeds.append(embed)
      
      print(embeds)

  if os.path.isfile('channels.csv'):
    with open('channels.csv', newline='', encoding='utf-8') as csvfile:
      for row in csv.reader(csvfile):
        print(f"Sending schedule to Guild {row[0]}, {row[1]}")
        guild = client.get_guild(int(row[0]))
        channel = guild.get_channel(int(row[1]))
        await channel.send(f"Hello, this is a scheduled test message for the **#{row[3]}** channel!", embeds=embeds)