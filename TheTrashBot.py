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

    if message.content.startswith('!stats'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        count_sql = 'SELECT count(*) FROM dumpster'
        stats_sql = 'SELECT author,count(*) FROM dumpster GROUP BY author ORDER BY count(*) DESC'
        active_sql = 'SELECT count(*) FROM dumpster WHERE score != 0'
        cursor.execute(count_sql)
        count = cursor.fetchall()
        cursor.execute(stats_sql)
        stats = cursor.fetchall()
        cursor.execute(active_sql)

        stats_msg = ''
        for x in stats:
            stats_msg = stats_msg + str(x[0]) + '\t' + str(x[1]) + '\n'


        count_msg = "The dumpster currently has " + str(count) + " pieces of trash in the dumpster"
        await client.send_message(message.channel, 'Top Contributors to the dumpster:\n' + stats_msg)

    if message.content.startswith('git gud'):
        await client.send_message(message.channel, "```error: branch 'gud' not found```")

    if message.content.startswith('!count'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        cursor.execute('SELECT id FROM dumpster')
        result = cursor.fetchall()
        msg = "The dumpster currently has " + str(len(result)) + " pieces of trash."
        await client.send_message(message.channel, msg)

    if message.content.startswith('!burn'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        decrement_sql = 'UPDATE dumpster SET score = score - 1 WHERE id = ?'
        report_sql = 'SELECT score FROM dumpster WHERE id = ?'
        zero_sql = 'UPDATE dumpster SET score = 0 WHERE id = ?'
        input_list = shlex.split(message.content)
        input_list.pop(0)
        id = str(input_list[0])
        cursor.execute(decrement_sql, (id,))
        db.commit()
        cursor.execute(report_sql, (id,))
        results = cursor.fetchone()
        msg = 'Score or TrashID is ' + str(results[0])
        if results[0] < 1:
            msg = msg + ', setting that trash on fire... you will never see it again... probably...'
            cursor.execute(zero_sql, (id,))
            db.commit()
        await client.send_message(message.channel, msg)

    if message.content.startswith('!trash'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()

        date_sql = 'UPDATE dumpster SET last_posted=date("now") WHERE id=?'
        update_sql = 'UPDATE dumpster SET score = score - 1 WHERE id = ?'
        select_sql = "SELECT url, id FROM dumpster WHERE (last_posted IS NULL OR last_posted < (SELECT DATETIME('now', '-7 day'))) AND score !=0 ORDER BY RANDOM() LIMIT 1"
        log_sql = 'INSERT INTO log (TrashID, user, date) VALUES (?,?,?)'
        
        cursor.execute(select_sql)
        trash_tuple = cursor.fetchone()
        trash = str(trash_tuple[0])
        id = str(trash_tuple[1])

        cursor.execute(date_sql, (id,))
        cursor.execute(update_sql, (id,))
        cursor.execute(log_sql, (id, ('{0.author.mention}'.format(message)).replace('@!', '@'), datetime.now()))
        db.commit()

        msg = trash.format(message) + " [TrashID: " + id + "]"
        await client.send_message(message.channel, msg)

    if message.content.startswith('!blame'):
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        input_list = shlex.split(message.content)
        input_list.pop(0)
        strID = str(input_list[0])
        blame_sql = 'SELECT author, date FROM dumpster WHERE id =?'
        cursor.execute(blame_sql, (strID,))
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
        embed.add_field(name="!burn [TrashID]", value="Burn trash, if enough people burn it, it will go away forever")
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
    await client.change_presence(game=discord.Game(name="Digging through trash"))

client.run(config.api_key)