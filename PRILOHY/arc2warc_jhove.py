#!/usr/bin/env python
""" Martin Prokop:
    *Uprava nastroje arc2warc pro potrebu spusteni nastroje JHOVE2.
    *Nastroj JHOVE2 provede po svem spusteni analyzu souboru
    obsazenych v archivu. Na konce vypise informace do souboru
    XML.
    
    *Nástroj musí být umístěn v kořenovém adresáři warctools
    
    *Je nutné v kořenovém adresáři vytvořit i složku "./temp"
    kam nástroj ukládá dočasné soubory
    
    *Cesta k adresari JHOVE2 (adresar ./lib v korenove slozce JHOVE2
    (musi v ni byt umisteny i slozky ./config a ./config/droid) se
    zadava prepinacem "-c". Zadava se ve forme: "x/".
    
    *Cesta k JVM se zadava prepinacem "-m".
    
    
   
    *Cesta k vystupnimu souboru z nastroje JHOVE se zada pomoci prepinace "-j",
    pokud neni nastaven, ulozi vypis do souboru "./jhove2output.xml"
    
    *Do souboru arc2warc.py_errorlog jsou vypsany vyjimky z jhove2.
   
    *V kodu jsem okomentoval svoje zasahy.
"""
import os
import sys
import hashlib
import uuid

import sys
import os.path
import datetime


""" Martin Prokop:
    *Import knihoven:
    RE - regularni vyrazy
    Jpype - slouzi k spusteni JVM a nasledni nastroje JHOVE2
"""
import time
import re
from jpype import * 
import jpype
""" Martin Prokop: konec """

from optparse import OptionParser

from hanzo.warctools import ArcRecord,WarcRecord
from hanzo.warctools.warc import warc_datetime_str

parser = OptionParser(usage="%prog [options] arc (arc ...)")

parser.add_option("-o", "--output", dest="output",
                       help="output warc file")
parser.add_option("-l", "--limit", dest="limit")
parser.add_option("-Z", "--gzip", dest="gzip", action="store_true", help="compress")
parser.add_option("-L", "--log-level", dest="log_level")


""" Martin Prokop:
    *Pridani parametru "-j" pro output JHOVE2
    *Pridani parametru "-c" pro cestu k JHOVE2
    *Pridani parametru "-m" pro cestu k JVM
"""
parser.add_option("-c", "--config jhove", dest="jhove2config")
parser.add_option("-m", "--JVM", dest="jvm")
""" Martin Prokop: konec """


parser.set_defaults(output_directory=None, limit=None, log_level="info", gzip=False, jvm="/usr/lib/jvm/default-java/jre/lib/i386/client/libjvm.so")
def make_warc_uuid(text):
    return "<urn:uuid:%s>"%uuid.UUID(hashlib.sha1(text).hexdigest()[0:32])

def main(argv):
    (options, input_files) = parser.parse_args(args=argv[1:])
    
    """ Martin Prokop:
        *Konfigurace a spusteni JVM
        *Nastaveni cesty k programu JHOVE2"""
    _jvmArgs = []
    _jvmArgs = ["-ea"] # enable assertions
    _jvmArgs.append("-Djava.ext.dirs=%s" % options.jhove2config)
    _jvmArgs.append("-cp %s" % "-cp options.jhove2config+jhove2-2.0.0.jar:options.jhove2config+aopalliance-1.0.jar:options.jhove2config+je-4.0.103.jar:options.jhove2config+jts-1.10.jar:options.jhove2config+commons-beanutils-1.7.0.jar:options.jhove2config+commons-logging-1.1.1.jar:options.jhove2config+commons-logging-api-1.1.jar:options.jhove2config+commons-pool-1.5.3.jar:options.jhove2config+vecmath-1.3.2.jar:options.jhove2config+jdom-1.0.jar:options.jhove2config+junit-4.4.jar:options.jhove2config+log4j-1.2.14.jar:options.jhove2config+jsr-275-1.0-beta-2.jar:options.jhove2config+jargs-1.0.jar:options.jhove2config+gt-api-2.6.5.jar:options.jhove2config+gt-main-2.6.5.jar:options.jhove2config+gt-metadata-2.6.5.jar:options.jhove2config+gt-referencing-2.6.5.jar:options.jhove2config+gt-shapefile-2.6.5.jar:options.jhove2config+mvel2-2.0.18.jar:options.jhove2config+geoapi-2.3-M1.jar:options.jhove2config+geoapi-pending-2.3-M1.jar:options.jhove2config+spring-beans-2.5.6.jar:options.jhove2config+spring-context-2.5.6.jar:options.jhove2config+spring-core-2.5.6.jar:options.jhove2config+spring-test-2.5.6.jar:options.jhove2config+soap-2.3.1.jar:options.jhove2config+xercesImpl-2.9.1.jar:options.jhove2config+xml-apis-1.3.04.jar:options.jhove2config+xml-resolver-1.2.jar:options.jhove2config+config:options.jhove2config+config/droid")
    jpype.startJVM(options.jvm, *_jvmArgs)
    """ Martin Prokop: konec """

    out = sys.stdout
    if options.output:
        out = open(options.output, 'ab')
        if options.output.endswith('.gz'):
            options.gzip = True
    if len(input_files) < 1:
        parser.error("no imput warc file(s)")
        
    """ Martin Prokop:
        *Pole do ktereho se ukladaji soubory k otestovani programem JHOVE2
        *Promena i nese poradi souboru v archivu
        *Spusteni JHOVE2 a nastaveni vystupu ve forme XML
        *Vytvoren soubor na vypis chyb arc2warc.py_errorlog
    """ 
    filesource = []
    i = 0
    #errorlog = open("./arc2warc.py_errorlog", "w")
              
    JHOVE2 = jpype.JClass("org.jhove2.app.RunFromARC2WARCLoop")
    RUNJHOVE2 = JHOVE2()
    """ Martin Prokop: konec """        
   
    for name in input_files:
        fh = ArcRecord.open_archive(name, gzip="auto")
        
        filedesc = None

        warcinfo_id = None
        for record in fh:
            version = "WARC/1.0"

            """ Martin Prokop:
                *Pomoci regularniho vyrazu vyfiltruju z obsahu archivu
                jednotlive soubory k testovani
                *Ukladani vyfiltrovanych souboru
                *Spusteni JHOVE2 pro kazdy soubor a nasteveni vystupu z JHOVE
                *Take zachyceni vyjimek z jhove2
            """
            content2 = re.sub("^(\n?(.+\n)*(\n\n|\r\n)){1}", "", record.content[1])

            a = open("./temp/"+str(i), "w")
            a.write(content2)
            filesource.append(a.name)
            
            try: 
                RUNJHOVE2.runJHOVE2Loop("./temp/"+str(i),"./temp/"+str(i)+"_out.xml")
            except JavaException, ex :
                filesource.remove(a.name)
                #printf "Zachycena chyba: "+str(JavaException.message())
                continue
            a.close()
                
            i = i+1      
            """ Martin Prokop: konec """
            
            warc_id = make_warc_uuid(record.url+record.date)
            headers = [
                (WarcRecord.ID, warc_id),
            ]
            
            
            if record.date:
                date = datetime.datetime.strptime(record.date,'%Y%m%d%H%M%S')
                headers.append((WarcRecord.DATE, warc_datetime_str(date)))


            if record.type == 'filedesc':
                warcinfo_id = warc_id

                warcinfo_headers = list(headers)
                warcinfo_headers.append((WarcRecord.FILENAME, record.url[11:]))
                warcinfo_headers.append((WarcRecord.TYPE, WarcRecord.WARCINFO))

                warcinfo_content = ('application/warc-fields', 'software: hanzo.arc2warc\r\n')

                warcrecord = WarcRecord(headers=warcinfo_headers, content=warcinfo_content, version=version)
                warcrecord.write_to(out, gzip=options.gzip)

                warc_id = make_warc_uuid(record.url+record.date+"-meta")
                warcmeta_headers = [
                    (WarcRecord.TYPE, WarcRecord.METADATA),
                    (WarcRecord.CONCURRENT_TO, warcinfo_id),
                    (WarcRecord.ID, warc_id),
                    (WarcRecord.URL, record.url),
                    (WarcRecord.DATE, warcrecord.date),
                    (WarcRecord.WARCINFO_ID, warcinfo_id),
                ]
                warcmeta_content =('application/arc', record.raw())

                warcrecord = WarcRecord(headers=warcmeta_headers, content=warcmeta_content, version=version)
                warcrecord.write_to(out, gzip=options.gzip)
            else:
                content_type, content = record.content
                if record.url.startswith('http'):
                    # don't promote content-types for http urls,
                    # they contain headers in the body.
                    content_type="application/http;msgtype=response"

                headers.extend([
                    (WarcRecord.TYPE, WarcRecord.RESPONSE ),
                    (WarcRecord.URL,record.url),
                    (WarcRecord.WARCINFO_ID, warcinfo_id),
                ])
                      
            
                warcrecord = WarcRecord(headers=headers, content=(content_type, content), version=version)

                warcrecord.write_to(out, gzip=options.gzip)


        fh.close()
        
    """ Martin Prokop:
        *Spusteni JHOVE2 (jako parametry pole cest k souborum a cestu k vystupu)
        *Vypnuti JVM
        *Nakonec mazu soubory z "./temp"
        *Zaviram soubor pro logovani chyb
    """
        
    RUNJHOVE2.close()
    shutdownJVM()
    #errorlog.close()
    
    for x in range(0, len(filesource)):
        os.remove(str(filesource[x]))
    """ Martin Prokop: konec """
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))



