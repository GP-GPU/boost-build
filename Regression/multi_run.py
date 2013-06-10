import shutil
import os
import subprocess
import sys
import json

class Runner(object):
    def __init__(self, machine_vars, cleanup=False):
        self.mvs = machine_vars
        self.runs = self.mvs['runs']
        self.cleanup = False
        self.start_dir = os.getcwd()

    def run_one(self, run_str):
        f = open("CurrentRun.json",'w')
        s = json.dump(run_str, f)
        f.close()
        
        run = self.runs[run_str]
    
        os.chdir(run["dir"])
        
        command = ['python', 'run.py', '--runner=' + self.mvs['machine'] + 
            run['dir'] + '-' + self.mvs['os'] + '-' + run['arch'] + "on" + 
            self.mvs['os_arch'], '--force-update', '--toolsets=' + 
            run['compilers'], '--bjam-options="-j' + str(self.mvs['procs']) + 
            ' address-model=' + run['arch'] + '"', '--comment=..\info.html']

        # Output the command to the screen before running it            
        cmd_str = ""
        for s in command:
            cmd_str += " " + s
        print "Runing command:"            
        print cmd_str[1:]            
            
        # Run
        proc = subprocess.Popen(command)#, 
                                #stdout=subprocess.PIPE, 
                                #stderr=subprocess.PIPE)
        
        # Tee the output to output.log as well as the screen
        with open("output.log", "w") as log_file:
            while proc.poll() is None:
                if proc.stderr:
                    line = proc.stderr.readline()
                    if line:
                        sys.stderr.write(line)
                        log_file.write(line)
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line:
                        sys.stdout.write(line)
                        log_file.write(line)      

        if self.cleanup:
            shutil.rmtree('results')
            #rmtree on temp???
            
        os.chdir(self.start_dir)
        
    def loop(self, start_at=None):
        sorted_runs = sorted(self.runs.keys())
        
        num = 0
        if start_at:
            # Jump to that run
            num = sorted_runs.index(start_at)
            start_at = None

        while True:
            r = sorted_runs[num % len(sorted_runs)]
            self.run_one(r)
            num += 1
        
    def restart(self):
        start_at = "a"
        try:
            f = open("CurrentRun.json",'r')
            at = json.load(f)
            f.close
            if isinstance(at, basestring):
                start_at = at
        except IOError:
            pass #No file?

        self.loop(start_at)
           

if __name__ == '__main__':
    f = open("machine_vars.json", 'r')
    machine_vars = json.load(f)
    f.close()
    
    r = Runner(machine_vars)
    if len(sys.argv) > 1:
        r.run_one(sys.argv[1])
    else:
        r.restart()