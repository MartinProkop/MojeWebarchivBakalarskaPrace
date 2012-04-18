#!/usr/bin/env python
"""Martin Prokop"""
""" Uprava programu. Do souboru ./arc2warc_debug.log
    Vypise informace o prevodu archivu
    Pomoci toho se da zjistit, nakterem souboru prevod archivu havaroval"""

import os
import sys
import hashlib
import uuid

import sys
import os.path

from optparse import OptionParser

from warctools import ArcRecord,WarcRecord

parser = OptionParser(usage="%prog [options] arc (arc ...)")

parser.add_option("-o", "--output", dest="output",
                       help="output warc file")
parser.add_option("-l", "--limit", dest="limit")
parser.add_option("-Z", "--gzip", dest="gzip", action="store_true", help="compress")
parser.add_option("-L", "--log-level", dest="log_level")

parser.set_defaults(output_directory=None, limit=None, log_level="info", gzip=False)

def main(argv):
    (options, input_files) = parser.parse_args(args=argv[1:])
    
    
    out = sys.stdout
    if options.output:
        out = open(options.output, 'ab')
    if len(input_files) < 1:
        parser.error("no imput warc file(s)")
    
    i = 0
    a = open("./arc2warc_debug.log", "w")
    a.write("Martin Prokop")
    a.write("Program se pokusi prevest archiv do formatu warc."+'\n')
    a.write("Po kazdem uspesne prevedenem zazanamu, o nem vypise informace."+'\n')
    a.write("Soubory jsou cislovani souboru zacina od cisla 0."+'\n')
    a.write("Pricemz jejich poradi ve vypisu odpovida poradi v archivu arc."+'\n')
    a.write("Vadny je ten soubor, ktery ma poradove cislo o jedna vyssi nez posledni uspesny."+'\n')
    a.write("Jehe identifikace je pak jiz snadna."+'\n')
    a.write("**********"+'\n')
    
    for name in input_files:
        fh = ArcRecord.open_archive(name, gzip="auto")

        for record in fh:
            a.write("**PREVOD souboru s cislem "+str(i)+": ")
        	
            content = record.content
            
            headers = [
                (WarcRecord.TYPE, "response"),
                (WarcRecord.ID, "<urn:uuid:%s>"%uuid.UUID(hashlib.sha1(record.url+record.date).hexdigest()[0:32])),
            ]
            version = "WARC/1.0"
            
            url = record.url
            if url:
                headers.append((WarcRecord.URL,url))
            date = record.date
            if date:
                headers.append((WarcRecord.DATE,date))
            warcrecord = WarcRecord(headers=headers, content=content, version=version)
            warcrecord.write_to(out, gzip=options.gzip)
            
            a.write("USPESNE!"+'\n')
            i = i+1
	 
        fh.close()

	a.write("**********"+'\n')
	a.write("Cely archiv byl preveden USPESNE!")
	a.close()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
