import discord
import os
from discord.ext import commands
from poll import Poll
from utility import String

bot = commands.Bot(command_prefix='!')

client = discord.Client()

polls = {}

@client.event
async def on_ready():
  global roles
  roles_full = client.guilds[0].roles
  ignore = ["@everyone", "ButtlerBot", "Moderator", "Admin"]
  roles = {}
  for role in roles_full:
    if role.name not in ignore:
      roles[role.name] = role

@client.event
async def on_message(message):
  user       = message.author
  user_roles = [arg.name for arg in user.roles]
  if user == client.user:
    return
  
  # Neue Mitglieder zuordnen
  if message.channel.name == "neue_mitglieder":
    if not "Admin" in user_roles and message.content in list(roles):
      await giverole(client, message.author, roles[message.content])
    elif "Admin" not in user_roles:
      await message.channel.send(String.wrong_input_role)
    else:
      await message.channel.send(String.you_are_admin)
  # Botfunktionen
  else:
    if message.content.startswith("!"):
      cmd = message.content[1:]
      if cmd == "poll" and ("Admin" in user_roles or "Moderator" in user_roles):
        polls[message.channel.name] = Poll()
        await message.channel.send(String.move_help)
      elif cmd == "endpoll" and ("Admin" in user_roles or "Moderator" in user_roles):
        path = polls[message.channel.name].plot()
        await message.channel.send(file=discord.File(path))
        try:
          os.remove(path)
        except Exception as e:
          print(e)
        del polls[message.channel.name]
      elif cmd.startswith("move") and message.channel.name in polls.keys():
        move = cmd[len("move"):].strip()
        author = user.name
        author_id = user.id
        await message.delete()
        if len(move) == 0 or not polls[message.channel.name].add_vote(move, author):
          await message.channel.send(f"<@{author_id}> {String.illegal_vote}")
        else:
          await message.channel.send(f"<@{author_id}> {String.legal_vote}")

@bot.command(pass_context=True)
async def giverole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)

client.run(os.getenv('TOKEN'))
