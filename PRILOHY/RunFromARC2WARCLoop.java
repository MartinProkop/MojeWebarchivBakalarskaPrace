/*
 * Copyright 2012 Martin Prokop.
 */
package org.jhove2.app;

import java.io.Closeable;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.util.Date;
import org.jhove2.config.spring.SpringConfigInfo;
import org.jhove2.core.Invocation;
import org.jhove2.core.JHOVE2;
import org.jhove2.core.JHOVE2Exception;
import org.jhove2.core.io.Input;
import org.jhove2.core.source.FileSource;
import org.jhove2.core.source.Source;
import org.jhove2.module.display.Displayer;
import org.jhove2.persist.PersistenceManager;
import org.jhove2.persist.PersistenceManagerUtil;

/**
 * Vlastní třída přidaná k progragramu JHOVE2. Slouží ke spouštění
 * JHOVE2 z nástroje pro migraci arc souborů (warctools: arc2warc_loop_jhove2.py).
 * Nástroj warctools je implementován v Pythonu. Pomocí nástroje Jpype
 * (slouží ke spuštění JVM nad programem v Pythonu) mohu spouštět tuto třídu.
 * 
 * Výpis chyb je přesměrován do souboru "./arc2warc.py_loop_jhove2_errorlog"
 * 
 * třída obstará spuštění nastroje JHOVE2. Pomocí metody run pak zpracuje
 * analýzu pro zadaný soubor. Tato akce se dá opakovat.
 * 
 * @author Martin Prokop
 */
public class RunFromARC2WARCLoop implements Closeable {
    //privátní atributy

    private int EEXCEPTION;
    //jednotlivé třídy z JHOVE2
    private Displayer displayer;
    private JHOVE2 jhove2;
    private PersistenceManager persistenceManager;

    /**
     * Konstruktor. Vytvoří funkční JHOVE2.
     */
    public RunFromARC2WARCLoop() throws FileNotFoundException {
        // Presmerovani vystupu z JHOVE2 do souboru "./arc2warc.py_loop_jhove2_errorlog"
        OutputStream output = new FileOutputStream("./arc2warc.py_loop_jhove2_errorlog");
        PrintStream nullOut = new PrintStream(output);
        System.setErr(nullOut);
        System.setOut(nullOut);
        
        persistenceManager = null;
        try {
            SpringConfigInfo factory = new SpringConfigInfo();
            PersistenceManagerUtil.createPersistenceManagerFactory(factory);
            persistenceManager = PersistenceManagerUtil.getPersistenceManagerFactory().getInstance();
            persistenceManager.initialize();
            JHOVE2CommandLine app =
                    SpringConfigInfo.getReportable(JHOVE2CommandLine.class,
                    "JHOVE2CommandLine");

            displayer = app.getDisplayer();
            if (displayer == null) {
                Class defaultDisplayerClass =
                        (Class) Class.forName(Displayer.DEFAULT_DISPLAYER_CLASS);
                displayer =
                        (Displayer) SpringConfigInfo.getReportable(defaultDisplayerClass,
                        "XML");
                displayer = app.setDisplayer(displayer);
            }
            app.getDisplayer().setConfigInfo(factory);
            app.setDateTime(new Date());
            app = (JHOVE2CommandLine) app.getModuleAccessor().persistModule(app);
            jhove2 = SpringConfigInfo.getReportable(JHOVE2.class,
                    "JHOVE2");
            Invocation inv = app.getInvocation();
            jhove2.setInvocation(inv);
            jhove2.setInstallation(app.getInstallation());
            displayer = app.getDisplayer();
            displayer.setConfigInfo(factory);
            displayer = app.setDisplayer(displayer);
        } catch (Exception e) {
            System.err.println(e.getMessage());
            e.printStackTrace(System.err);
            System.exit(EEXCEPTION);
        }
    }

    /**
     * Metoda dá JHOVE2 na vstup cestu k souboru a cestu kam má uložit výstup
     * z analýzy.
     * @param sourcePath Cesta k vstupnímu souboru
     * @param outputPath Cesta kam se má uližt analýza
     * @throws JHOVE2Exception
     * @throws IOException 
     */
    public void runJHOVE2Loop(String sourcePath, String outputPath) throws JHOVE2Exception, IOException {
        // vytvoreni source z vstupního souboru
        Source source = (FileSource) jhove2.getSourceFactory().getSource(jhove2, sourcePath);
        //charakterizace
        jhove2 = (JHOVE2) jhove2.getModuleAccessor().startTimerInfo(jhove2);
        Input input = source.getInput(jhove2);
        try {
            source = jhove2.characterize(source, input);
        } finally {
            if (input != null) {
                input.close();
            }
        }
        jhove2 = (JHOVE2) jhove2.getModuleAccessor().endTimerInfo(jhove2);
        //výstup
        displayer.display(source, outputPath);
    }

    /**
     * Metoda, která vypne JHOVE2 a databázy
     */
    @Override
    public void close() {
        if (persistenceManager != null) {
            try {
                persistenceManager.close();
            } catch (JHOVE2Exception je) {
                System.err.println(je.getMessage());
                je.printStackTrace(System.err);
                System.exit(EEXCEPTION);
            }
        }
    }
}

