# tankstellenPreisvergleich
Ein Projekt zum Thema Preisentwicklung und Tankempfehlung an Tankstellen in der Region Iserlohn.
Das Projekt entstand im Rahmen einer Ausarbeitung an der Fachhochschule Südwestfalen im Modul Skriptsprachen.

## Backend API
URL: ./preise
    Optional URL-Parameters:
        begin = [yyyy-mm-dd hh:mm:ss]
            Startdartum der Datenauswahl
        end = [yyyy-mm-dd hh:mm:ss]
            Enddatum der Datenauswahl
        id = [TankstellenID]
        filter=[all/durchschnitt/id]
            all: Zeigt alle Tankstellen
                interval = [days/hours/weekdays]
            durchschnitt: Zeigt den Durchschnitt der Preise
                interval = [days/hours/weekdays]
            id: Zeigt eine Tankstelle, ID Parameter muss angegeben werden!

URL: ./tankstellen
    URL-Parameter:
        id = [TankstellenID]
            Zeigt generelle Informationen wie Adresse von einer Tankstelle an.
    
    
