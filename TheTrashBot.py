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

    if message.content.startswith('!zeros'):
        """ SQL command for identifying the worst three contributors
        It does this by calculating the ratio of how much trash they've
        contributed over consumed. Loops through the tuple from fetchall
        to build string """
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        stats_sql = """ select author, log_count, dump_count,
                    round((dump_count * 1.0) / (log_count * 1.0),1) AS Ratio, dump_count - log_count
                    AS difference
                    FROM (SELECT user,count(1) log_count FROM log GROUP BY user) l
                    JOIN (SELECT author,count(1) dump_count
                    FROM dumpster GROUP BY author ) d
                    on d.author = l.user ORDER BY ratio ASC LIMIT 3;"""
        cursor.execute(stats_sql)
        stats = cursor.fetchall()
        stats_msg = ''
        for row in stats:
            stats_msg = stats_msg  + str(row[0]) + '\tRatio: ' + str(row[3]) + '\tDifference: ' + str(row[4]) + '\n'
        await client.send_message(message.channel, 'The Bottom 3 Contributors to the dumpster:\n' + stats_msg)

    if message.content.startswith('!heros'):
        """ SQL command for identifying the best three contributors
        It does this by calculating the ratio of how much trash they've
        contributed over consumed. Loops through the tuple from fetchall
        to build string """
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        stats_sql = """ select author, log_count, dump_count, round((dump_count * 1.0) / (log_count * 1.0),1) 
                    AS Ratio, dump_count - log_count AS difference
                    FROM (SELECT user,count(1) log_count FROM log GROUP BY user) l
                    JOIN (SELECT author,count(1) dump_count
                    FROM dumpster GROUP BY author ) d
                    on d.author = l.user ORDER BY ratio DESC LIMIT 3;"""
        cursor.execute(stats_sql)
        stats = cursor.fetchall()
        stats_msg = ''
        for row in stats:
            stats_msg = stats_msg  + str(row[0]) + '\tRatio: ' + str(row[3]) + '\tDifference: ' + str(row[4]) + '\n'
        await client.send_message(message.channel, 'Top 3 Contributors to the dumpster:\n' + stats_msg)

    if message.content.startswith('git gud'):
        await client.send_message(message.channel, "```error: branch 'gud' not found```")

    if message.content.startswith('!count'):
        """ Using SQL statement to identify how
        many total pieces of trash there is in the
        dumpster """
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        cursor.execute('SELECT id FROM dumpster')
        result = cursor.fetchall()
        msg = "The dumpster currently has " + str(len(result)) + " pieces of trash."
        await client.send_message(message.channel, msg)

    if message.content.startswith('!burn'):
        """ Reduces the Score of a piece of
        trash in the dumpster with decrement_sql to prevent reposts.
        Uses shlex library to split the string and assigns the TrashID
        to id . Uses report_sql to check the current score and message the chat
        If its 0, it gives a forboding warning. If it gets
        below 0, zero_sql brings it back to 0 beccause I'm a
        bad programmer"""
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
        """ Posts trash into the discord channel using select_sql. It will select a
        random row that has not been posted in the past 7 days. date_sql
        sets last_posted column to today, and update_sql decremets the trash 
        score. Finally the event is logged into the log table with log_sql for
        statistic purposes. If a user has a custom name in the channel,
        their User ID sometimes has a ! inserted into it, deleted before
        being inserted into the table"""
        db = sqlite3.connect('Dumpster.db')
        cursor = db.cursor()
        date_sql = 'UPDATE dumpster SET last_posted=date("now") WHERE id=?'
        update_sql = 'UPDATE dumpster SET score = score - 1 WHERE id = ?'
        select_sql = """SELECT url, id FROM dumpster WHERE (last_posted IS
                    NULL OR last_posted < (SELECT DATETIME('now', '-7 day')))
                    AND score !=0 ORDER BY RANDOM() LIMIT 1"""
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
        """ Uses blame_sql to lookup the author
        of a piece of trash and when it was inserted
        into the dumpster. Message.content is message in Discord"""
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
        """ Used insert_sql to insert URL
        into database as a new piece of trash.
        Message.content is message in Discord"""
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
        embed.add_field(name="!heros", value="Lists Top 3 Contributors based on ratio how much trash they ontribute over how much they consume")
        embed.add_field(name="!zeros", value="Lists Bottom 3 Contributors based on ratio how much trash they ontribute over how much they consume")
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
    await client.change_presence(game=discord.Game(name="Garbage Truck Simulator"))

client.run(config.api_key)