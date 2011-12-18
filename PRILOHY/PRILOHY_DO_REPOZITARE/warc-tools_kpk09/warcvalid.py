#!/usr/bin/env python
"""warcvalid - check a warc is ok"""

import os
import sys

import sys
import os.path

from optparse import OptionParser

from warctools import ArchiveRecord

parser = OptionParser(usage="%prog [options] warc warc warc")

parser.add_option("-l", "--limit", dest="limit")
parser.add_option("-I", "--input", dest="input_format")
parser.add_option("-L", "--log-level", dest="log_level")

parser.set_defaults(output_directory=None, limit=None, log_level="info")

def main(argv):
    (options, input_files) = parser.parse_args(args=argv[1:])

    if len(input_files) < 1:
        parser.error("no imput warc file(s)")
        

    correct=True
    fh=None
    try:
        for name in input_files:
            fh = ArchiveRecord.open_archive(name, gzip="auto")

            for (offset, record, errors) in fh.read_records(limit=None):
                if errors:
                    if options.log_level:
                        print "warc errors at %s:%d"%(name, offset)
                    correct=False
                    break
                elif record is not None and record.validate() :
                    if options.log_level:
                        print record.validate()
                    correct=False
                    break

    except StandardError, e:
        correct=False
        if options.log_level: print "ERROR:", e
    finally:
        if fh: fh.close()
    
    if correct:
        return 0
    else:
        return -1 # failure code

if __name__ == '__main__':
    sys.exit(main(sys.argv))



