import lichess.api
import datetime
from dateutil.parser import parse

class Tournament:

    def __init__(self, url: str):
        pos = url.rfind("/")
        if pos == -1:
            raise UrlNotValidException
        self.t_id = url[url.rfind("/")+1:]    

        # Turnierobjekt
        self.tournament         = lichess.api.tournament(self.t_id)
        
        # Zeitdatenm zum Turnier
        self.runtime: datetime  = datetime.timedelta(minutes=self.tournament["minutes"])
        self.date: datetime     = parse(self.tournament["startsAt"])
        self.endtime: datetime  = (self.date + self.runtime).replace(tzinfo=None)

    def execution_time(self) -> int:
        """
        Gibt zurück wann das Turnier vom jetzigen Zeitpunkt in Sekunden beendet ist.
        """
        now = datetime.datetime.now()
        exec_time = (self.endtime - now).seconds if (self.endtime-now).total_seconds() > 0 else 0 
        return exec_time

    @property
    def name(self) -> str:
        return self.tournament["fullName"]

    @property
    def description(self) -> str:
      description = ""
      try:
        description = self.tournament["description"]
      except KeyError:
        bedenkzeit, inkrement = self.__clock()
        description = f"Start: {self.date.strftime('%d.%m.%Y um %H:%M')}\n"\
                      f"Dauer: {self.__duration}\n"\
                      f"Zeitmodus: {bedenkzeit}\n"\
                      f"Inkrement: {inkrement}"
      finally:
        return description

    @property
    def duration(self) -> str:
        return f"Das Turnier wird für eine Dauer von **{datetime.datetime.utcfromtimestamp(self.runtime.seconds).strftime('%H:%M')}** Stunden laufen."
    
    @property
    def __duration(self) -> str:
        return datetime.datetime.utcfromtimestamp(self.runtime.seconds).strftime('%H:%M')

    @property
    def clock(self) -> str:
        t_format = self.tournament["clock"]
        if t_format["limit"] > 3600 and t_format["limit"] % 60 != 0:
            bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Hh:%Mm:%Ss')
        elif t_format["limit"] > 3600 and t_format["limit"] % 60 == 0:
            bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Hh:%Mm')
        elif t_format["limit"] % 60 == 0:
            bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%M Minuten')
        else:
            bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Mm:%Ss')
        return f"Das Zeitformat für ein Spiel ist **{bedenkzeit}** mit einem Inkrement von **{t_format['increment']}** Sekunden je Zug."
    
    def __clock(self) -> str:
      t_format = self.tournament["clock"]
      if t_format["limit"] > 3600 and t_format["limit"] % 60 != 0:
          bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Hh:%Mm:%Ss')
      elif t_format["limit"] > 3600 and t_format["limit"] % 60 == 0:
          bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Hh:%Mm')
      elif t_format["limit"] % 60 == 0:
          bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%M Minuten')
      else:
          bedenkzeit = datetime.datetime.utcfromtimestamp(t_format['limit']).strftime('%Mm:%Ss')
      
      return (bedenkzeit, str(t_format['increment']) + " Sekunden")
  
    @property
    def startsAt(self) -> str:
        return f"Das Turnier startet **{self.date.strftime('%d.%m.%Y um %H:%M')}**."

    @property
    def results(self) -> list:
        con = lichess.api.tournament_standings(self.t_id)
        output  = "```"
        maxnamelen  = 0
        maxscorelen = len("Punkte")
        maxratinglen = len("Rating")
        results = list()
        for item in con:
          results.append(item)
        for item in results:
          print(item)
          if len(item["name"]) > maxnamelen:
            maxnamelen = len(item["name"])
          if len(str(item["score"])) > maxscorelen:
            maxscorelen = len(str(item["sheet"]["total"]))
        
        output += f"{'Platz':6} | {'Name':^{maxnamelen}} | {'Rating':^{maxratinglen}} | {'Punkte':^{maxscorelen}} | Spielpunkte\n"
        for _ in range(len(output)):
          output += "-"
        output += "\n"
        for item in results:
          listed_scores = item["sheet"]["scores"]
          scores = ""
          for score in listed_scores:

            if type(score) == list:
              scores += str(score[0]) + " "
            else:
              scores += str(score) + " "
          scores  = scores[:-1]
          newline = f"{item['rank']:6} | {item['name']:^{maxnamelen}} | {item['sheet']['total']:^{maxscorelen}} | {scores}\n" 

          if len(output) + len(newline) > 1997:
            output += "```"
            yield output
            output = "```" + newline
          else:
            output += f"{item['rank']:6} | {item['name']:^{maxnamelen}} | {item['rating']:^{maxratinglen}} | {item['score']:^{maxscorelen}} | {scores}\n"
        output += "```"
        yield output


class UrlNotValidException(BaseException):
    message = "Die URL funktioniert nicht. Bitte gib die vollständige URL zum Turnier an."

class UserNotValidException(BaseException):
  message = "Ich kann den User nicht finden. Bitte schau nach, ob er auch richtig geschrieben ist."

class AuthorNameNotValidException(BaseException):
  message = "Hast du deinen Namen an die Namenskonventionen des Servers angepasst? Mir gelingt es nicht deinen Namen herauszulesen"

class LichessUser:

  def __init__(self, user: str):
    self.user = lichess.api.user(user)

  def get_data(self):
    data = f"__Name: {self.user['username']}__\n\n"
    for category, perf in self.user["perfs"].items():
      try:
        data += f"**{category}**: {perf['rating']} (Rating)\n"
      except KeyError:
        try:
          data += f"**{category}**: {perf['score']} (Score)\n"
        except:
          pass
    data.strip()
    return data

class VS:

  def __init__(self, caller: str, enemy:str):
    self.enemy = enemy
    self.caller = "" 
    print("VS is called, searching Data")
    try:
      self.caller = caller.split("-")[1].strip()
      if "[" in self.caller:
        self.caller = self.caller[:self.caller.find("[")]
    except IndexError:
      print(f"Nickname {caller} not valid.")
      raise AuthorNameNotValidException

    self.user = lichess.api.user_games(self.caller)

    self.wins = dict()
    self.losses = dict()

    for item in self.user:
      try:
        if item["players"]["white"]["user"]["name"].lower() == enemy.lower():
          if item["winner"] == "white":
            if item["speed"] in self.losses:
              self.losses[item["speed"]] += 1
            else:
              self.losses[item["speed"]] = 1
          else:
            if item["speed"] in self.wins:
              self.wins[item["speed"]] += 1
            else:
              self.wins[item["speed"]] = 1

        elif item["players"]["black"]["user"]["name"].lower() == enemy.lower():
          if item["winner"] == "white":
            if item["speed"] in self.wins:
              self.wins[item["speed"]] += 1
            else:
              self.wins[item["speed"]] = 1
          else:
            if item["speed"] in self.losses:
              self.losses[item["speed"]] += 1
            else:
              self.losses[item["speed"]] = 1
      except:
        # Spiele mit unvollständigen Daten ignorieren
        pass
    
  @property
  def results(self) -> str:
    keys = self.wins.keys()

    len_keys = max([len(x) for x in keys])
    len_keys = len("Disziplin") if len("Disziplin")>len_keys else len_keys
    len_call = len(self.caller)
    len_enem = len(self.enemy)

    output = f"``` {'Disziplin':^{len_keys}} | {self.caller:^{len_call}} | {self.enemy:^{len_enem}}\n"

    for key in keys:
      output += f" {key:^{len_keys}} | {self.wins[key]:^{len_call}} | {self.losses[key]:^{len_enem}}\n"

    output += "```"
    return output