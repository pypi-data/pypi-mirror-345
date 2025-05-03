# -*- coding: utf-8 -*-
# DiscordMessageCleaner
# Project by https://github.com/rix1337

import argparse
import asyncio
import datetime
import sys
import time

import discord
from discord.ext import commands

from discord_message_cleaner.providers import version


def run():
    print("[DiscordMessageCleaner] Version " + version.get_version() + " by rix1337")

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="Discord Bot Token")
    parser.add_argument("--channel_id", help="Discord Channel ID with the bot already in it")
    parser.add_argument("--days", type=int, default=7, help="Number of days to keep messages (default: 7)")
    arguments = parser.parse_args()

    if not arguments.token:
        print("[DiscordMessageCleaner] Please provide a token using --token")
        sys.exit(1)
    if not arguments.channel_id:
        print("[DiscordMessageCleaner] Please provide a channel ID using --channel_id")
        sys.exit(1)

    token = arguments.token
    channel_id = int(arguments.channel_id)
    days = int(arguments.days)

    print(f"[DiscordMessageCleaner] Token: {token}")
    print(f"[DiscordMessageCleaner] Channel ID: {channel_id}")
    print(f"[DiscordMessageCleaner] Days: {days}")

    try:
        while True:
            intents = discord.Intents.default()
            intents.messages = True
            bot = commands.Bot(command_prefix='!', intents=intents)

            @bot.event
            async def on_ready():
                print(f'Logged in as {bot.user}')
                channel = bot.get_channel(channel_id)

                if channel:
                    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
                    async for msg in channel.history(limit=None, before=cutoff):
                        try:
                            await msg.delete()
                            print(f"Deleted: {msg.id}")
                            await asyncio.sleep(1.1)  # Small delay to avoid hitting rate limits
                        except discord.Forbidden:
                            print(f"Missing permissions to delete message {msg.id}")
                        except discord.HTTPException as e:
                            print(f"Rate limited or failed to delete {msg.id}: {e}")
                            await asyncio.sleep(5)  # Wait longer if rate-limited

                await bot.close()

            bot.run(token)
            time.sleep(60 * 60)

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        print(f"[DiscordMessageCleaner] An error occurred: {e}")
        pass
