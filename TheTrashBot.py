import discord
import config
import random
import shlex
import sqlite3
from datetime import datetime, time, timedelta

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!count'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        cursor.execute('SELECT id FROM dumpster')
        result = cursor.fetchall()
        msg = "The dumpster currently has " + str(len(result)) + " pieces of trash."
        await client.send_message(message.channel, msg)


    if message.content.startswith('!trash'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        date_sql = 'UPDATE dumpster SET last_posted=date("now") WHERE id=?'
        select_sql = "SELECT url, id FROM dumpster WHERE last_posted IS NULL OR last_posted < (SELECT DATETIME('now', '-7 day')) ORDER BY RANDOM() LIMIT 1"
        cursor.execute(select_sql)
        trash_tuple = cursor.fetchone()
        trash = str(trash_tuple[0])
        id = str(trash_tuple[1])
        cursor.execute(date_sql, (id,))
        db.commit()
        msg = trash.format(message) + " [TrashID: " + id + "]"
        await client.send_message(message.channel, msg)

    if message.content.startswith('!blame'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        input_list = shlex.split(message.content)
        input_list.pop(0)
        strID = str(input_list[0])
        cursor.execute('SELECT author, date FROM dumpster WHERE id = ' + str(input_list[0]))
        blame_tuple = cursor.fetchone()
        author = blame_tuple[0]
        date = blame_tuple[1]
        msg = "You can blame " + author + " for adding that trash on " + date
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
        embed.add_field(name="!blame [TrashID]", value="Blame whoever added [TrashID] to the dumpster")
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