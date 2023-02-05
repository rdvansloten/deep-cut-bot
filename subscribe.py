import requests
import os
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from dateutil import parser
import discord
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import tasks
import csv
import logging

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def check_stage():
  file_path = 'current_stage.txt'
  if not os.path.exists(file_path):
    try:
      with open(file_path, 'w') as f:
        f.write('content')
      return True
    except:
      return False
  else:
    return True

def register_stage(content):
  file_path = 'current_stage.txt'
  if check_stage():
    with open(file_path) as f:
      file_content = f.read()
    if file_content != content:
      with open(file_path, 'w') as f:
        f.write(content)
      return True
    else:
      return False

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
    message = f"Only Administrators can subscribe a channel to the Salmon Run schedule."
    logging.warning(f"Guild {guild_name}({guild_id}): {message}")
    return message

  # Add entry to csv file
  if not check_csv(channel_id=channel_id, guild_id=guild_id, csv_file=csv_file):
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
      csv.writer(f).writerow([
        guild_id, 
        channel_id, 
        guild_name, 
        channel_name
      ])
      message = f"Successfully subscribed <#{channel_id}> to the Salmon Run schedule!"
      logging.info(f"Guild {guild_name}({guild_id}): {message}")
      return message
  else:
    message = f"Channel <#{channel_id}> is already subscribed to the Salmon Run schedule."
    logging.warning(f"Guild {guild_name}({guild_id}): {message}")
    return message

def unsubscribe_channel(guild_id, channel_id, guild_name, channel_name, administrator, csv_file):
  if not administrator:
    message = "Only Administrators can unsubscribe a channel from the Salmon Run schedule."
    logging.warning(f"Guild {guild_name}({guild_id}): {message}")
    return message

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

    message = f"Successfully unsubscribed <#{channel_id}> from the Salmon Run schedule!"
    logging.info(f"Guild {guild_name}({guild_id}): {message}")
    return message
  else:
    message = f"Failed to unsubscribe. Channel <#{channel_id}> was not subscribed to the Salmon Run schedule."
    logging.warning(f"Guild {guild_name}({guild_id}): {message}")
    return message