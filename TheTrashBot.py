import discord
import config
import random
import shlex
import sqlite3
from datetime import datetime, time

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!trash'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        cursor.execute('SELECT url FROM dumpster ORDER BY RANDOM() LIMIT 1')
        trash = str(cursor.fetchone()[0])
        msg = trash.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!add'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        insert_sql = 'INSERT INTO dumpster (url, author, date) VALUES (?, ?, ?)'
        input_list = shlex.split(message.content)
        input_list.pop(0)
        for trash in input_list:
            try:
                cursor.execute(insert_sql, (trash, '{0.author.mention}'.format(message), datetime.now()))
                db.commit()
                await client.send_message(message.channel, "Added to the dumpster")
            except sqlite3.IntegrityError as e:
                await client.send_message(message.channel, "Uh oh, this trash is already in the dumpster")
                break

    if message.content.startswith('!help'):
        embed = discord.Embed(title="The Trash Bot", description="The bot we all deserve. Contribute at https://github.com/Trinitrogen/The-Trash-Bot", color=0x00ff00)
        embed.add_field(name="!trash", value="Picks a post from the dumpster", inline=False)
        embed.add_field(name="!add", value="Follow by URL or sentance is quotes")
        embed.add_field(name="!help", value="lists all current commands", inline=False)


        msg = 'http://i.imgur.com/aZZTF0r.gifv'.format(message)

        await client.send_message(message.channel, msg)
        await client.send_message(message.channel, embed=embed)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(config.api_key)