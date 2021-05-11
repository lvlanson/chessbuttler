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
        return self.tournament["description"]

    @property
    def duration(self) -> str:
        return f"Das Turnier wird für eine Dauer von **{datetime.datetime.utcfromtimestamp(self.runtime.seconds).strftime('%H:%M')}** Stunden laufen."

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
    
    @property
    def startsAt(self) -> str:
        return f"Das Turnier startet **{self.date.strftime('%d.%m.%Y um %H:%M')}**."

    @property
    def results(self) -> list:
        con = lichess.api.tournament_standings(self.t_id)
        output  = "```"
        maxnamelen  = 0
        maxscorelen = 0
        results = list()
        for item in con:
          results.append(item)
        for item in results:
          if len(item["name"]) > maxnamelen:
            maxnamelen = len(item["name"])
          if len(str(item["score"])) > maxscorelen:
            maxscorelen = len(str(item["score"]))
        for item in results:
          listed_scores = item["sheet"]["scores"]
          scores = ""
          for score in listed_scores:

            if type(score) == list:
              for s in score:
                scores += str(s) + " "
            else:
              scores += str(score) + " "
          scores  = scores[:-1]
          newline = f"{item['rank']:5} | {item['name']:^{maxnamelen}} | {item['score']:^{maxscorelen}} | {scores}\n" 

          if len(output) + len(newline) > 2000:
            output += "```"
            yield output
            output = "```" + newline
          else:
            output += f"{item['rank']:5} | {item['name']:^{maxnamelen}} | {item['score']:^{maxscorelen}} | {scores}\n"
        output += "```"
        yield output


class UrlNotValidException(BaseException):
    message = "Die URL funktioniert nicht. Bitte gib die vollständige URL zum Turnier an."


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