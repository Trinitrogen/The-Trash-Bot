import discord
import config
import random

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!Trash'):
        Trashbin = open('Dumpster.txt')
        input_list = Trashbin.read().splitlines()
        msg = random.choice(input_list).format(message)
        await client.send_message(message.channel, msg)
        Trashbin.close()

    if message.content.startswith('!Add'):
        Trashbin = open('Dumpster.txt', 'a')
        input_list = message.content.split()
        input_list.pop(0)
        for line in input_list:
            Trashbin.write(line + "\n")
        Trashbin.close()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(config.api_key)