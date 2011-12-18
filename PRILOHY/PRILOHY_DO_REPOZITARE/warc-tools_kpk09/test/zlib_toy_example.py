#!/usr/bin/env python

import zlib

CHUNK_SIZE = 1024 # the size to read in, make this bigger things go faster.
verbose = 0

def read(fh,z):
    """
        Takes an open file-handle and a zlib.decompressobj().
        Returns one member of a concatenated gzip file.
    """
    global CHUNK_SIZE
    out = ''
    done = False
    while True:
        if done: return out
        if verbose: print 'read chunk at', fh.tell(), done
        chunk = fh.read(CHUNK_SIZE)
        out += z.decompress(chunk)
        
        if z.unused_data:
            if verbose: print 'unused', len(z.unused_data)
            fh.seek(-len(z.unused_data),1)
            done=True
            continue
        if not chunk:
            done = True
            continue
        
if __name__ == '__main__':
    f = "IAH-20110605172416-00000-kevin-laptop-9090.arc.gz"
    fh = open(f,'rb+')
    while True:
        pos = fh.tell()
        z = zlib.decompressobj(16+zlib.MAX_WBITS)
        print '#'*20
        print read(fh,z)
        if fh.tell() == pos: break
    
    
