import discord
import config
import random

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!trash'):
        Trashbin = open('Dumpster.txt')
        input_list = Trashbin.read().splitlines()
        msg = random.choice(input_list).format(message)
        await client.send_message(message.channel, msg)
        Trashbin.close()

    if message.content.startswith('!add'):
        Trashbin = open('Dumpster.txt', 'a')
        input_list = message.content.split()
        input_list.pop(0)
        for line in input_list:
            Trashbin.write(line + "\n")
        Trashbin.close()
        msg = "Added to Dumpster"
        await client.send_message(message.channel, msg)

    if message.content.startswith('!help'):
        embed = discord.Embed(title="The Trash Bot", description="The shitposting bot we all deserve", color=0x00ff00)
        embed.add_field(name="!trash", value="Picks a post from the dumpster", inline=False)
        embed.add_field(name="!trashhelp", value="lists all current commands", inline=False)

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