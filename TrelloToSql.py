#!/usr/bin/env python
# coding: utf8

'''
Liest Trello-Karten aus Liste "Texte lektoriert" des "Play-Boards" aus
und wandelt Sie mit Pandoc in html um. Inklusive Literaturverzeichnis.
Zusätzlich werden ein paar weitere Formatierungen vorgenommen.
Das Ergebnis wird dann in die Datenbank geschrieben.
Die Trello-Karten werden hinterher verschoben.
'''

import mysql.connector
import codecs
import re
import pypandoc
import os
import subprocess
from trello import TrelloClient
from slugify import slugify
import datetime
#import sys

#Possible Fix for encoding problems.
#reload(sys)
#sys.setdefaultencoding('utf-8')


base_dir = os.path.dirname(os.path.abspath(__file__))
bib = os.path.join(base_dir,"scholarium.bib")
md_path = os.path.join(base_dir,"Markdown")
html_path = os.path.join(base_dir,"HTML")

#Trello Connection
with open(os.path.join(base_dir, 'trello.key'), 'r') as f:
    lines = f.readlines()
    client = TrelloClient(
        api_key=lines[0].strip(),
#        api_secret=lines[1].strip(),
        token=lines[1].strip(),
#        token_secret=lines[3].strip()
    )

#Database connection
with open(os.path.join(base_dir, 'database.key'), 'r') as f:
    lines = f.readlines()
    config = {
        'user': lines[0].strip(),
        'password': lines[1].strip(),
        'host': lines[2].strip(),
        'database': lines[3].strip(),
        # 'raise_on_warnings': lines[4].strip(),
        # 'use_unicode': lines[5].strip(),
        # 'collation': lines[6].strip()
    }

play_board=client.get_board('55d5dfee98d40fcb68fc0e0b')
played_board=client.get_board('55c4665a4afe2f058bd3cb0a')
target_list=played_board.get_list('5774e15c515d20dd2aa0b534')

for list in play_board.open_lists():
    if list.name=="Texte lektoriert":
        print('%d lektorierte(n) Text(e) gefunden.' % len(list.list_cards()))
        # Karten werden von unten nach oben abgearbeitet.
        for card in list.list_cards()[::-1]:
            title=card.name
            text=card.desc
            fobj_out = codecs.open(os.path.join(md_path, "%s.md" % title),"w","utf-8")
            #meta = codecs.open("%s" %meta,"r","utf-8")
            #fobj_out.write(meta.read())

            #ids
            p = re.compile(r"§§.*")
            id = p.findall(text)
            id = id[0][2:] if id else title
            priority = 1 if id[0] == '!' else 0
            id = slugify(id)
            text = p.sub("",text, count=1)

            fobj_out.write("---\nbibliography: {}\n---\n\n{}\n\n## Literatur".format(bib, text))
            fobj_out.close

            #to html
            fobj_out = codecs.open(os.path.join(md_path, "%s.md" % title),"r","utf-8")
            md=fobj_out.read()
            extra_args=[]
            filters=['pandoc-citeproc']
            html=pypandoc.convert(md, 'html', format='md',  extra_args=extra_args, filters=filters)

            #blockquotes mit class versehen
            p=re.compile("<blockquote>")
            html=p.sub("<blockquote class=\"blockquote\">",html)

            #Gedankenstriche ("--" nach "–")
            p=re.compile("--")
            html=p.sub("&ndash;",html)

            #Trennungszeichen
            p=re.compile(r"<p>&lt;&lt;&lt;</p>")
            split=re.split(p,html)
            public=split[0]
            # lstrip entfernt mögliche Absätze am Anfang.
            privat=split[1].lstrip() if len(split) > 1 else ""
            if not privat:
                print('Keinen privaten Teil gefunden.')
                # print(html)
            #sql
            try:
                cnx = mysql.connector.connect(**config)
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
            else:
                cursor = cnx.cursor()
                public=cnx.converter.escape(public)
                privat=cnx.converter.escape(privat)
                query = """INSERT INTO blog (id, title, public_text, private_text, priority, edited)
                        VALUES ("{}","{}","{}","{}",{},1);""".format(id,title,public,privat,priority)

                cursor.execute(query)
                cnx.commit()
                cursor.close()
                cnx.close()
                print('%s erfolgreich in DB übertragen.' % title)

                card.change_board(played_board.id, target_list.id)
                card.set_pos('top')
