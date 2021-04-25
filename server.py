import discord
import os
from discord.ext import commands
from discord.utils import find

bot = commands.Bot(command_prefix='!')

client = discord.Client()


@client.event
async def on_ready():
  global roles
  print(f"Hello {client.user}")
  roles_full = client.guilds[0].roles
  ignore = ["@everyone", "ButtlerBot", "Moderator", "Admin"]
  roles = {}
  for role in roles_full:
    if role.name not in ignore:
      roles[role.name] = role

@client.event
async def on_message(message):
  user = message.author
  if user == client.user:
    return
  
  if message.channel.name == "neue_mitglieder":
    user_roles = [arg.name for arg in user.roles]
    print("Admin" in user_roles)
    print(user_roles)
    if not "Admin" in user_roles and message.content in list(roles):
      await giverole(client, message.author, roles[message.content])
    elif "Admin" not in user_roles:
      await message.channel.send("Entschuldigung, ich habe dich nicht verstanden. Gehörst du zu **Dresden** oder **Mittweida**?\nBitte wiederhole deine Eingabe und verwende dabei genau eine der Vorgaben.")
    else:
      await message.channel.send("Sehr witzig! Du bist ein Admin, du wirst gesondert behandelt!")

@bot.command(pass_context=True)
async def giverole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)

client.run(os.getenv('TOKEN'))
