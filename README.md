# tankstellenPreisvergleich
Ein Projekt zum Thema Preisentwicklung und Tankempfehlung an Tankstellen in der Region Iserlohn.
Das Projekt entstand im Rahmen einer Ausarbeitung an der Fachhochschule Südwestfalen im Modul Skriptsprachen.

## Backend API
:URL: ./preise<br>
::Optionale URL-Parameter:<br>
        *begin = [yyyy-mm-dd hh:mm:ss] - Startdartum der Datenauswahl<br>*
        end = [yyyy-mm-dd hh:mm:ss] - Enddatum der Datenauswahl<br>
        id = [TankstellenID]<br>
        filter=[all/durchschnitt/id]<br>
            all: Zeigt alle Tankstellen -> 
                interval = [days/hours/weekdays/hourmin]<br>
            durchschnitt: Zeigt den Durchschnitt der Preise -> 
                interval = [days/hours/weekdays]<br>
            id: Zeigt eine Tankstelle, ID Parameter muss angegeben werden!<br>

URL: ./tankstellen<br>
    URL-Parameter:<br>
        id = [TankstellenID] - Zeigt generelle Informationen wie Adresse von einer Tankstelle an. Wenn kein Parameter angegeben wird, anzeige für alle Tankstellen.
