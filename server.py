import discord
import os
import asyncio
from lichess.api import ApiHttpError
from discord.ext import commands
from poll import Poll
from utility import String
from lichesshelper import Tournament, UrlNotValidException, LichessUser, VS, UserNotValidException

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
  author     = user.name
  author_id  = user.id
  nickname   = user.display_name
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
    # Befehl an den Bot
    if message.content.startswith("!"):
      cmd = message.content[1:]

      # Abstimmung starten
      if cmd == "poll" and ("Admin" in user_roles or "Moderator" in user_roles):
        polls[message.channel.name] = Poll()
        await message.channel.send(String.move_help)

      # Abstimmung beenden
      elif cmd == "endpoll" and ("Admin" in user_roles or "Moderator" in user_roles):
        try:
          path = polls[message.channel.name].plot()
          await message.channel.send(file=discord.File(path))
          try:
            os.remove(path)
          except Exception as e:
            print(e)
          del polls[message.channel.name]
        
        except KeyError:
          await message.channel.send(String.no_vote_active)

      # Zugangabe bei Abstimmung
      elif cmd.startswith("move") and message.channel.name in polls.keys():
        move = cmd[len("move"):].strip()
        await message.delete()
        if len(move) == 0 or not polls[message.channel.name].add_vote(move, author):
          await message.channel.send(f"<@{author_id}> {String.illegal_vote}")
        else:
          await message.channel.send(f"<@{author_id}> {String.legal_vote}")

      # Turnier starten
      elif cmd.startswith("tournament"):
        await message.delete()
        url = cmd[len("tournament"):].strip()
        if not url.startswith("http://") and not url.startswith("https://"):
          await message.channel.send(String.tournament_url_http_error)
        else:
          try:
            tourn = Tournament(url)

            embed=discord.Embed(title=tourn.name, url=url, description=tourn.description) # Vorschaufenster
            msg = f"{author} hat {tourn.name} erstellt. {tourn.duration} {tourn.clock} {tourn.startsAt} Das Turnier findet ihr unter folgendem Link {url}." # Nachricht bauen
            await message.channel.send(msg, embed=embed) # Nachricht schicken / Turnier ank??ndigen
            await asyncio.sleep(tourn.execution_time() +  5) # Warten bis das Turnier beendet ist
            await message.channel.send(String.tournament_end) # Turnier beendet Nachricht senden
            for result in tourn.results:
              await message.channel.send(result) # Turnier Ergebnisse ver??ffentlichen
          except UrlNotValidException as e:
            await message.channel.send(e.message)
          except ApiHttpError:
            await message.channel.send("Etwas scheint mit der URL nicht zu stimmen. Ich finde da kein Turnier.")
      
      # Spieler Daten abfragen
      elif cmd.startswith("user"):
        lc_user = cmd[len("user"):].strip()
        lc_user = LichessUser(lc_user)
        await message.channel.send(lc_user.get_data())


      """
      # Versus Daten abfragen
      elif cmd.startswith("vs"):
        lc_user = cmd[len("vs"):].strip()
        try:
          await message.channel.send(f"Ich suche nach allen Spielen gegen {lc_user}. Das kann ein paar Minuten dauern.")
          vc = VS(nickname, lc_user)
          await message.channel.send(vc.results)
        except UserNotValidException as e:
          await message.channel.send(e.message)
      """

      """
      KOMMENTAR
      """

@bot.command(pass_context=True)
async def giverole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)

client.run(os.getenv('TOKEN'))
