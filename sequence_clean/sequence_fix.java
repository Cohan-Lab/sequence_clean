import java.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.IOException;
import java.util.Date;

public class sequence_fix {

    public static void main(String[] args) {

        String newick_file;
        String fasta_file;
        Float cutoff;
        String fasta_out;
        String log_name;

        List<String> settings = import_settings();
        System.out.println(settings);
        // try, except taken out for now
        if (settings != null) {
            newick_file = settings.get(0);
            fasta_file = settings.get(1);
            cutoff = Float.parseFloat(settings.get(2));
            fasta_out = settings.get(3);
            log_name = settings.get(4);
        }
        else {
            ArrayList<String> logs = new ArrayList<String>();
            String workingDir = System.getProperty("user.dir");
            logs.add("Error: Could not find all required settings in 'seq_clean_settings.txt' in " + workingDir);
            logs.add("--NEED: newick file, fasta file, cutoff, new fasta file name, new log name." +
                    "Each should be entered on a new line in the specified order.");
            logging(logs, "SEQ_CLEAN_ERROR_LOG.txt");
        }
    }

    private String import_fasta(String filename) {

    }

    private static void logging(ArrayList<String> logs, String log_name) {
        // logs is a dictionary of all items to be logged
        Date date = new Date();
        String string = "Date: " +  date.toString() + "\n" + "\n";
        // for each thing in the dictionary
        for (Integer i = 0; i < logs.size(); i ++) {
            string = string + logs.get(i) + "\n" + "\n";
        }
        try {

            File file = new File(log_name);

            // if file doesn't exist, create it
            if (!file.exists()) {
                file.createNewFile();
            }

            FileWriter fw = new FileWriter(file.getAbsoluteFile());
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write(string);
            bw.close();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Imports settings from file. Expects a newick file, a fasta file, a name for
    // the new fasta file, and a name for the log file.
    // THE SETTINGS MUST BE CALLED 'seq_clean_settings.txt' and must be in
    // the current directory! If not found, will write to log file that it can't find settings
    // in CWD.
    private static List<String> import_settings() {

        BufferedReader br = null;
        List<String> settings = new ArrayList<String>();

        try {
                String sCurrentLine;

                br = new BufferedReader(new FileReader("seq_clean_settings.txt"));

                while ((sCurrentLine = br.readLine()) != null) {
                    settings.add(sCurrentLine);
                    }
                return settings;
            } catch (IOException x) {
                    return null;
                }
    }
}

