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
        t_id = url[url.rfind("/")+1:]    

        # Turnierobjekt
        self.tournament         = lichess.api.tournament(t_id)
        
        # Zeitdatenm zum Turnier
        self.runtime: datetime  = datetime.timedelta(minutes=self.tournament["minutes"])
        self.date: datetime     = parse(self.tournament["startsAt"])
        self.endtime: datetime  = (self.date + self.runtime).replace(tzinfo=None)

    def execution_time(self):
        """
        Gibt zurück wann das Turnier vom jetzigen Zeitpunkt in Sekunden beendet ist.
        """
        now = datetime.datetime.now()
        exec_time = self.endtime - now if (self.endtime-now).total_seconds() > 0 else 0 
        return exec_time.seconds

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
    
    def plot_result(self):
        results = self.tournament["standing"]["players"]
        
        if len(results) < 0:
            player_index = []
        else:
            player_index = np.arange(len(results))
        
        players = []
        score = []
        for item in results:
            print(item)
            players.insert(0, item["name"])
            score.insert(0, item["score"])
        plt.figure(figsize=(15,8))
        plt.rcParams.update({'font.size': 22})
        plt.barh(player_index, score, align='center', alpha=0.5)
        plt.yticks(player_index, players)
        plt.xlabel("Score")
        if len(score) > 0:
          plt.xticks(np.arange(max(score)+1))
        plt.title(self.name)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

        for index, value in enumerate(score):
            plt.text(value, index, str(value))

        plt.savefig(tmp_file, dpi=300)
        return tmp_file

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
        results = self.tournament["standing"]["players"]
        
        if len(results) < 0:
            player_index = []
        else:
            player_index = np.arange(len(results))
        
        players = []
        score = []
        for item in results:
            print(item)
            players.insert(0, item["name"])
            score.insert(0, item["score"])
        plt.figure(figsize=(15,8))
        plt.rcParams.update({'font.size': 22})
        plt.barh(player_index, score, align='center', alpha=0.5)
        plt.yticks(player_index, players)
        plt.xlabel("Score")
        if len(score) > 0:
          plt.xticks(np.arange(max(score)+1))
        plt.title(self.name)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

        for index, value in enumerate(score):
            plt.text(value, index, str(value))

        plt.savefig(tmp_file, dpi=300)
        return tmp_file

class UrlNotValidException(BaseException):
    message = "Die URL funktioniert nicht. Bitte gib die vollständige URL zum Turnier an."

t = Tournament("https://lichess.org/tournament/5KfBYIOB")
