#!/usr/bin/env python
""" Martin Prokop:
    *Uprava nastroje arc2warc pro potrebu spusteni nastroje JHOVE2.
    *Nastroj provede prevod archivu a pro kazdy v nem obsazeny soubor
    vlozi do adresare "./temp" vystup z nastroje JHOVE2 ve formatu XML.
    Nazev vystupu bude ve forme: "poradovecislovarchivu_out.xml".

    *Cesta k adresari JHOVE2 (adresar ./lib v korenove slozce JHOVE2
    (musi v ni byt umisteny i slozky ./config a ./config/droid) se
    zadava prepinacem "-c". Zadava se ve forme: "x/".
    
    *Cesta k JVM se zadava prepinacem "-m".

    *V kodu jsem okomentoval svoje zasahy.
"""

import os
import sys
import hashlib
import uuid
import sys
import os.path

""" Martin Prokop:
    *Import knihoven:
    RE - regularni vyrazy
    Jpype - slouzi k spusteni JVM a nasledni nastroje JHOVE2
"""
import re
from jpype import * 
import jpype
""" Martin Prokop: konec """

from optparse import OptionParser
from warctools import ArcRecord,WarcRecord
parser = OptionParser(usage="%prog [options] arc (arc ...)")
parser.add_option("-o", "--output", dest="output", help="output warc file")
parser.add_option("-l", "--limit", dest="limit")
parser.add_option("-Z", "--gzip", dest="gzip", action="store_true", help="compress")
parser.add_option("-L", "--log-level", dest="log_level")

""" Martin Prokop:
    *Pridani parametru "-c" pro cestu k JHOVE2
    *Pridani parametru "-m" pro cestu k JVM
"""
parser.add_option("-c", "--config jhove", dest="jhove2config")
parser.add_option("-m", "--JVM", dest="jvm")
""" Martin Prokop: konec """
parser.set_defaults(output_directory=None, limit=None, log_level="info", gzip=False, jvm="/usr/lib/jvm/default-java/jre/lib/i386/client/libjvm.so")

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
    if len(input_files) < 1:
        parser.error("no imput warc file(s)")
        
    for name in input_files:
        fh = ArcRecord.open_archive(name, gzip="auto")

        """ Martin Prokop:
            *Pole do ktereho se ukladaji soubory k otestovani programem JHOVE2
            *Spusteni JHOVE2 a nastaveni vystupu ve forme XML
        """ 
        filesource = []
        i = 0
        JHOVE2 = jpype.JClass("org.jhove2.app.RunFromARC2WARCLoop")
        RUNJHOVE2 = JHOVE2()

        """ Martin Prokop: konec """
		
        for record in fh:
        	
            content = record.content
            
            headers = [
                (WarcRecord.TYPE, "response"),
                (WarcRecord.ID, "<urn:uuid:%s>"%uuid.UUID(hashlib.sha1(record.url+record.date).hexdigest()[0:32])),
            ]
            
            version = "WARC/1.0"
            
            
            """ Martin Prokop:
                *Pomoci regularniho vyrazu vyfiltruju z obsahu archivu
                jednotlive soubory k testovani
                *Ukladani vyfiltrovanych souboru
                *Spusteni JHOVE2 pro kazdy soubor a nasteveni vystupu z JHOVE
                
            """
            content2 = re.sub("^(\n?(.+\n)*(\n\n|\r\n)){1}", "", content[1])

            a = open("./temp/"+str(i), "w")
            a.write(content2)
            filesource.append(a.name)
            a.close()
            RUNJHOVE2.runJHOVE2Loop("./temp/"+str(i),"./temp/"+str(i)+"_out.xml")
            i = i+1
            """ Martin Prokop: konec """
            
            url = record.url
            if url:
                headers.append((WarcRecord.URL,url))
            date = record.date
            if date:
                headers.append((WarcRecord.DATE,date))
            warcrecord = WarcRecord(headers=headers, content=content, version=version)
            warcrecord.write_to(out, gzip=options.gzip)       
        fh.close()
        
    """ Martin Prokop:
        *Vypnuti JHOVE2
        *Vypnuti JVM
        *Nakonec mazu soubory z "./temp"
    """
        
    RUNJHOVE2.killEmAll()
    shutdownJVM()
    
    for x in range(0, len(filesource)):
        os.remove(str(filesource[x]))
    """ Martin Prokop: konec """
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
