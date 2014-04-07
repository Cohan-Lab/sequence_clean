import java.util.*;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class sequence_fix {

    public static void main(String[] args) {

        import_settings();
    }

    private void logging() {
        Map<String, String>
    }

    // Imports settings from file. Expects a newick file, a fasta file, a name for
    // the new fasta file, and a name for the log file.
    // THE SETTINGS MUST BE CALLED 'seq_clean_settings.txt' and must be in
    // the current directory! If not found, will write to log file that it can't find settings
    // in CWD.
    private static void import_settings() {

        BufferedReader br = null;
        List<String> settings = new ArrayList<String>();

        try {
                String sCurrentLine;

                br = new BufferedReader(new FileReader("seq_clean_settings.txt"));

                while ((sCurrentLine = br.readLine()) != null) {
                    System.out.println(sCurrentLine);
                }
            } catch (IOException x) {
                    // return false;
                }


    }
}

