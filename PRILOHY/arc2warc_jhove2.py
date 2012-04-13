#!/usr/bin/env python
""" Martin Prokop:
    *Uprava nastroje arc2warc pro potrebu spusteni nastroje JHOVE2.
    *Nastroj JHOVE2 provede po svem spusteni analyzu souboru
    obsazenych v archivu. Na konce vypise informace do souboru
    XML.
   
    *Cesta k vystupnimu souboru z nastroje JHOVE se zadapomci prepinace "-j",
    pokud neni nastaven, ulozi vypis do souboru "./jhove2output.xml"
   
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
    *Pridani parametru "-j" pro output JHOVE2
"""
parser.add_option("-j", "--jhove", dest="jhove2output")
""" Martin Prokop: konec """

parser.set_defaults(output_directory=None, limit=None, log_level="info", gzip=False, jhove2output="./jhove2output.xml")

def main(argv):
    (options, input_files) = parser.parse_args(args=argv[1:])
    
    """ Martin Prokop:
        *Konfigurace a spusteni JVM
        *Nastaveni cesty k programu JHOVE2"""
    _jvmArgs = []
    _jvmArgs = ["-ea"] # enable assertions
    _jvmArgs.append("-Djava.ext.dirs=%s" % "/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/")
    _jvmArgs.append("-cp %s" % "-cp /home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/jhove2-2.0.0.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/aopalliance-1.0.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/je-4.0.103.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/jts-1.10.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/commons-beanutils-1.7.0.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/commons-logging-1.1.1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/commons-logging-api-1.1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/commons-pool-1.5.3.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/vecmath-1.3.2.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/jdom-1.0.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/junit-4.4.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/log4j-1.2.14.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/jsr-275-1.0-beta-2.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/jargs-1.0.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/gt-api-2.6.5.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/gt-main-2.6.5.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/gt-metadata-2.6.5.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/gt-referencing-2.6.5.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/gt-shapefile-2.6.5.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/mvel2-2.0.18.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/geoapi-2.3-M1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/geoapi-pending-2.3-M1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/spring-beans-2.5.6.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/spring-context-2.5.6.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/spring-core-2.5.6.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/spring-test-2.5.6.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/soap-2.3.1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/xercesImpl-2.9.1.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/xml-apis-1.3.04.jar:/home/kovar/NetBeansProjects/jhove2-2.0.0_unmodified/lib/xml-resolver-1.2.jar:/home/kovar/WEBARCHIV/TESTOVANI/jhove2-2.0.0/config:/home/kovar/WEBARCHIV/TESTOVANI/jhove2-2.0.0/config/droid")
    jpype.startJVM("/usr/lib/jvm/default-java/jre/lib/i386/client/libjvm.so", *_jvmArgs)
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
            *Promena i nese poradi souboru v archivu
        """ 
        filesource = []
        i = 0
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
                *Pridani souboru do seznamu pro JHOVE2
                
            """
            content2 = re.sub("^(\n?(.+\n)*(\n\n|\r\n)){1}", "", content[1])

            a = open("./temp/"+str(i), "w")
            a.write(content2)
            filesource.append(a.name)
            a.close()
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
        *Spusteni JHOVE2 (jako parametry pole cest k souborum a cestu k vystupu)
        *Vypnuti JVM
        *Nakonec mazu soubory z "./temp"
    """
        
    JHOVE2 = jpype.JClass("org.jhove2.app.RunFromARC2WARC")
    RUNJHOVE2 = JHOVE2()
    RUNJHOVE2.runJHOVE2(filesource, options.jhove2output)
    shutdownJVM()
    
    for x in range(0, len(filesource)):
        os.remove(str(filesource[x]))
    """ Martin Prokop: konec """
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
