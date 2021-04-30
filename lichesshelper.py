import lichess.api
import datetime
from dateutil.parser import parse
import matplotlib.pyplot as plt
import numpy as np
import tempfile

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

    def execution_time(self):
        """
        Gibt zurück wann das Turnier vom jetzigen Zeitpunkt in Sekunden beendet ist.
        """
        now = datetime.datetime.now()
        exec_time = (self.endtime - now).seconds if (self.endtime-now).total_seconds() > 0 else 0 
        return exec_time

    @property
    def results(self):
        return self.tournament["standing"]["players"]

    @property
    def name(self):
        return self.tournament["fullName"]

    @property
    def description(self):
        return self.tournament["description"]

    @property
    def duration(self):
        return f"Das Turnier wird für eine Dauer von **{datetime.datetime.utcfromtimestamp(self.runtime.seconds).strftime('%H:%M')}** Stunden laufen."

    @property
    def clock(self):
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
    def startsAt(self):
        return f"Das Turnier startet **{self.date.strftime('%d.%m.%Y um %H:%M')}**."

    def plot_result(self):
        results = lichess.api.tournament_standings(self.t_id)
        players = []
        score = []
        for item in results:
          players.insert(0,item["name"])
          score.insert(0, item["score"])
        
        if len(players) < 0:
            player_index = []
        else:
            player_index = np.arange(len(players))
        
        for item in results:
            players.insert(0, item["name"])
            score.insert(0, item["score"])
        height = len(players)
        plt.figure(figsize=(15, height))
        plt.rcParams.update({'font.size': 22})
        plt.barh(player_index, score, align='center', alpha=0.5)
        plt.yticks(player_index, players)
        plt.xlabel("Score")
        plt.title(self.name)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

        for index, value in enumerate(score):
            plt.text(value, index, str(value))

        plt.savefig(tmp_file, dpi=300, bbox_inches="tight")
        return tmp_file


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

if __name__ == "__main__":
    t = Tournament("https://lichess.org/tournament/N9fapapb")
    print(t.plot_result())