#!/usr/bin/env python
"""Converts Markdown-Input File to PDF and mobi"""

import argparse
from subprocess import call
import os
import pypandoc
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

base_dir = os.path.dirname(os.path.abspath(__file__))
kindlegen_pfad = base_dir
template = base_dir+'/template/Analyse.latex'
bib = base_dir+'/scholarium.bib'

# Argumente parsen
parser = argparse.ArgumentParser(
    description='This is a script wich use pandoc to convert the Mardown input file to different Output-files')
parser.add_argument('-i', '--input', help='Input file name', required=True)
args = parser.parse_args()

# Namen splitten
pfad = base_dir + "/" + os.path.split(args.input)[0]
file_name_with_path = os.path.splitext(args.input)[0]
file_name = os.path.splitext(os.path.split(args.input)[1])[0]
file_endung = os.path.splitext(args.input)[1]

# to TEX
output = pypandoc.convert_file('%s' % args.input, 'tex', format='md', outputfile='%s.tex' % file_name_with_path, extra_args=[
                               '--template=%s' % template, '--biblatex', '--bibliography=%s' % bib])

os.chdir(pfad)
# to PDF
commands = [
    ['lualatex', file_name + '.tex'],
    ['biber', file_name + '.aux'],
    #['bibtex', file_name + '.aux'],
    ['lualatex', file_name + '.tex'],
    ['lualatex', file_name + '.tex'],
    ['lualatex', file_name + '.tex']
]

for c in commands:
    call(c)

# to html and then to mobi
output = pypandoc.convert_file('%s' % args.input, 'html', format='md',
                               outputfile='%s.html' % file_name_with_path, extra_args=['-s'])
call([r'%s\kindlegen ' % kindlegen_pfad, '-c2', '-o', '%s.mobi' %
      file_name, '%s.html' % file_name_with_path])


# ueberfluessige Dateien loeschen
def remove_if_exist(datei):
    if os.path.isfile(datei):   # falls Datei existiert
        os.remove(datei)

remove_if_exist('%s.html' % file_name_with_path)
remove_if_exist('%s.log' % file_name_with_path)
remove_if_exist('%s.bbl' % file_name_with_path)
remove_if_exist('%s.blg' % file_name_with_path)
remove_if_exist('%s.aux' % file_name_with_path)
remove_if_exist('%s.out' % file_name_with_path)
remove_if_exist('%s.toc' % file_name_with_path)
remove_if_exist('%s.ilg' % file_name_with_path)
remove_if_exist('%s.ind' % file_name_with_path)
remove_if_exist('%s.synctex.gz' % file_name_with_path)
remove_if_exist('%s.run.xml' % file_name_with_path)
remove_if_exist('%s-blx.bib' % file_name_with_path)
