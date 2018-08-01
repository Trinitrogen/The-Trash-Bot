import discord
import config

#TOKEN = 'NDczOTkxNDg5NTA5MzkyMzk0.DkJ_WQ.j7ZNuJUWDlpexd6EuKmnyejNoeQ'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!Trash'):
        msg = '{0.author.mention} http://i.imgur.com/aZZTF0r.gifv'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(config.api_key)
#client.run(TOKEN)