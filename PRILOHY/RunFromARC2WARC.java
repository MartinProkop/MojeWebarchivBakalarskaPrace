/*
 * Copyright 2012 Martin Prokop.
 */
package org.jhove2.app;

import java.io.Closeable;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.lang.reflect.Array;
import org.jhove2.core.JHOVE2Exception;

/**
 * Vlastní třída přidaná k progragramu JHOVE2. Slouží ke spouštění
 * JHOVE2 z nástroje pro migraci arc souborů (warctools: arc2warc_jhove2.py).
 * Nástroj warctools je implementován v Pythonu. Pomocí nástroje Jpype
 * (slouží ke spuštění JVM nad programem v Pythonu) mohu spouštět tuto třídu.
 * 
 * Třída dostane na vstup set souborů ke zpracování a do zadeného souboru
 * vypíše jejich analýzu.
 * 
 * @author Martin Prokop
 */
public class RunFromARC2WARC implements Closeable{

    /**
     * Metoda dostane na vstup seznam souborů, které předá ke zpracování
     * aplikaci JHOVE2 a nakonec na vypíše do zadaného souboru výstup z JHOVE2.
     * 
     * Výpis chyb je přesměrován do souboru "./arc2warc.py_jhove2_errorlog"
     * 
     * @param contents Pole cest k souborům
     * @param path Cesta k souboru, do kterého se mají vypsat informace
     * @throws IOException
     * @throws JHOVE2Exception 
     */
    public void runJHOVE2(String contents[], String path) throws IOException, JHOVE2Exception {
        // Presmerovani vystupu z JHOVE2 do souboru "./arc2warc.py_jhove2_errorlog"
        OutputStream output = new FileOutputStream("./arc2warc.py_jhove2_errorlog");
        PrintStream nullOut = new PrintStream(output);
        System.setErr(nullOut);
        System.setOut(nullOut);

        String[] data = {"-o", path, "-d", "XML"};

        String[] seznam = arrayMerge(data, contents);

        JHOVE2CommandLine.main(seznam);
    }
    
    @Override
    public void close()
    {
    }

    public static void main(String[] args) throws IOException, JHOVE2Exception {
    }

    /**
     * Pomocná metoda, dostane dvě pole Stringů a spojí je.
     * @param <T> Seznam polí Stringů
     * @param arrays Pole
     * @return Spojená pole Stringů
     */
    public static <T> T[] arrayMerge(T[]... arrays) {
        int count = 0;
        for (T[] array : arrays) {
            count += array.length;
        }
        T[] mergedArray = (T[]) Array.newInstance(arrays[0][0].getClass(), count);

        int start = 0;
        for (T[] array : arrays) {
            System.arraycopy(array, 0,
                    mergedArray, start, array.length);
            start += array.length;
        }
        return (T[]) mergedArray;
    }
}

