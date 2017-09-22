#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Converts Trello Liste to PDF"""

import argparse
import datetime
import codecs
import re
import pypandoc
import subprocess
import os
from trello import TrelloClient

#Auf mac aktivieren, auf win nicht verfügbar
#import sys  
#reload(sys)  
#sys.setdefaultencoding('utf8')

#Vorgaben
base_dir = os.path.dirname(os.path.abspath(__file__))
template = os.path.join(base_dir,"template","Scholien.latex")
bib = os.path.join(base_dir,"scholarium.bib")
meta = os.path.join(base_dir,"Meta","meta_scholien.yaml")


# Argumente parsen
parser = argparse.ArgumentParser(
    description='This is a script which use pandoc to convert the cards of a Trello list to different a PDF-file')
parser.add_argument('-l', '--list', help='List name', required=True)
args = parser.parse_args()

#Trello Connection
with open(os.path.join(base_dir, 'trello.key'), 'r') as f:
    lines = f.readlines()
    client = TrelloClient(
        api_key=lines[0].strip(),
        api_secret=lines[1].strip(),
        token=lines[2].strip(),
        token_secret=lines[3].strip()
    )

#Trello-Board
played_board=client.get_board('55c4665a4afe2f058bd3cb0a')

# Namen splitten
file_path = os.path.join(base_dir, 'Scholien' , args.list )
file_name = args.list
file_path_name=os.path.join(file_path,file_name)

try:
    os.mkdir(file_path)
except:
    pass

for list in played_board.open_lists():
    if list.name==args.list:
        #print(list.id)
        fobj_out = codecs.open("{}.md".format(file_path_name),"w+","utf-8")

        meta = codecs.open("%s" %meta,"r","utf-8")
        fobj_out.write(meta.read())
    
        for card in list.list_cards():           
            #print(card.name) 
            text=card.desc
            
            #ids löschen
            paragraphs=u"\u00A7"+u"\u00A7"+".*"
            p=re.compile(paragraphs)
            text= p.sub("",text, count=1)         
            
            #Trennungszeichen löschen
            p=re.compile(r"<<<")
            text= p.sub("",text, count=1) 

            fobj_out.write("# {}\n\n {}\n\n".format(
            card.name, text))


#Slashes in bib Pfad ändern
p=re.compile("\\\\")
bib=p.sub("/",bib)

#to tex
output = pypandoc.convert_file('{}.md'.format(file_path_name), 'tex', format='markdown+raw_tex', outputfile='{}.tex'.format(file_path_name) , extra_args=['--template=%s' % template, '--biblatex', '--bibliography=%s' % bib])
 
#Überschriften ersetzen -> \multicols
tex = codecs.open("{}.tex".format(file_path_name), "r", "utf-8")
p = re.compile(r"(\\chapter{.*\n{0,1}.*\n{0,1}.*}\\label{.*\n{0,1}.*\n{0,1}.*})", re.VERBOSE)
string = str(p.sub(r"\\multiend\n\\multi{\1}", tex.read()))
tex.close

#Erste und letzte Multi-umgebung anpassen
p = re.compile(r"\\multiend\n\\multi")
string = p.sub("\n\\multi", string, count=1)
p = re.compile(r"\\printbibliography")
string = p.sub(r"\\multiend\n\\printbibliography", string)
tex = codecs.open("{}.tex".format(file_path_name), "w", "utf-8")
tex.write(string)
tex.close

#Verzeichnis wechseln
os.chdir(file_path)

# to PDF
commands = [
    ['lualatex', file_name + '.tex'],
    ['biber', file_name + '.bcf'],
    #['bibtex', file_name + '.aux'],
    ['lualatex', file_name + '.tex'],
    ['lualatex', file_name + '.tex'],
    ['lualatex', file_name + '.tex']
]

for c in commands:
    subprocess.call(c)

# überflüssige Dateien löschen
def remove_if_exist(datei):
    if os.path.isfile(datei):   # falls Datei existiert
        os.remove(datei)

remove_if_exist('%s.html' % file_name )
remove_if_exist('%s.log' % file_name )
remove_if_exist('%s.bbl' % file_name )
remove_if_exist('%s.blg' % file_name )
remove_if_exist('%s.aux' % file_name )
remove_if_exist('%s.aux.bbl' % file_name )
remove_if_exist('%s.aux.blg' % file_name )
remove_if_exist('%s.bcf' % file_name )
remove_if_exist('%s.out' % file_name )
remove_if_exist('%s.toc' % file_name )
remove_if_exist('%s.ilg' % file_name )
remove_if_exist('%s.ind' % file_name )
remove_if_exist('%s.synctex.gz' % file_name )
remove_if_exist('%s.run.xml' % file_name )
remove_if_exist('%s-blx.bib' % file_name ) 
