package JepDr;

import jep.Jep;
import jep.JepConfig;
import jep.Interpreter;
import jep.SubInterpreter;


public class JepTestGetValue {

    public void run(String argv[]) 
    {
        try 
        {
            String spt = argv [0];

            JepConfig config = new JepConfig();
            config.addIncludePaths("subprocess");
            
            Interpreter interp = new SubInterpreter(config);
            interp.runScript(spt);

            interp.set("test",argv [1]);
            interp.getValue("test");

        }
        catch (Exception e) 
        {
            return;
        }

    }

    public static void main(String argv[]) throws Throwable 
    {
        JepTestGetValue jep_drive = new JepTestGetValue();
        jep_drive.run(argv);
    }


}
