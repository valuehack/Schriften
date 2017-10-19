from db_connector import Connector


def updateSQL():
    '''
    Neuer Post alle 4 Tage. Nach Priorität sortieren.
    '''
    c = Connector()
    # Check, ob Beitrag in letzten Tagen
    last = c.query('SELECT * FROM blog WHERE publ_date <= CURDATE() AND DATEDIFF(CURDATE(),publ_date) < 6')
    if not last:
        # Suche nach neuem Beitrag mit Priorität.
        post = c.query('SELECT * FROM blog WHERE publ_date IS NULL AND priority = 1 ORDER BY n asc LIMIT 1')
        if not post:
            # Suche nach neuem Beistrag ohne Datum.
            post = c.query('SELECT * FROM blog WHERE publ_date IS NULL ORDER BY n asc LIMIT 1')

        if post:
            # Setze aktuelles Datum als Veröffentlichung.
            c.query('UPDATE blog SET publ_date = CURDATE() WHERE n = "%s"' % post[0][0])
            print('%s veröffentlicht.' % post[0][3])
        else:
            print('Kein neuer Beitrag vorhanden.')


def pubSM():
    '''
    Facebook, Twitter?
    '''
    pass

updateSQL()
