class String:
  move_help = "Schreib mir deinen Zug:\n"\
        "Zuerst kommt einen Ausrufezeichen mit move `!move`. Danach kommt dein Zug. Wenn ein Bauer zieht schreibst du nur von Feld zu Feld mit Bindestrich. Wenn eine andere Figur setzt schreibst du den großen Anfangsbuchstaben der Figur und danach direkt von Feld zu Feld mit Bindestrich. Hier sind ein paar Beispiele. \n```Bauernzug: !move e2-e4\nSpringerzug: !move Se2-d4```"
  wrong_input_role = "Entschuldigung, ich habe dich nicht verstanden. Gehörst du zu **Freiberg**, **Dresden** oder **Mittweida**?\nBitte wiederhole deine Eingabe und verwende dabei genau eine der Vorgaben."
  you_are_admin = "Sehr witzig! Du bist ein Admin, du wirst gesondert behandelt!"
  illegal_vote = "Ich habe deinen Zug nicht verstanden. So sollte ein Zugvorschlag beispielhaft aussehen:\n"\
                  "\n```Bauernzug: !move e2-e4\nSpringerzug: !move Se2-d4```"
  legal_vote = "Danke, ich habe mir deinen Zug notiert."
  no_vote_active = "Entschuldigung, aber es ist gerade keine Abstimmung aktiv."
  tournament_end = "Das Turnier ist beendet. Ich schreibe noch schnell die Ergebnisse ab und stelle sie gleich rein."
  tournament_url_http_error = "Die Turnier URL muss mit `http://` oder `https://` beginnen"
