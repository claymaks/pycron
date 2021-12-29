from pathlib import Path
import subprocess

class Job(object):
    def __init__(self, job="", tag=None):
        self.set(job, tag)

    def get(self):
        return f"{self.minute} {self.hour} {self.day} {self.month} {self.week} {self.cmd}" + (f" {self.tag}" if self.tag is not None else '')

    def set(self, job="", tag=None):
        self.job = job
        self.tag = "" if tag is None else f"#{tag}"
        
        if job != "":
            self.minute, self.hour, self.day, self.month, self.week, *cmd = [j for j in job.split(' ') if j != '']
            self.cmd = ' '.join(cmd)
            if '#' in self.cmd:
                self.cmd = self.cmd.split(" #")
                if tag is None:
                    self.tag = f"#{self.cmd[1]}"
                self.cmd = self.cmd[0]
                    
        else:
            self.minute, self.hour, self.day, self.month, self.week, *cmd = f"0 0 0 0 0 ".split(' ')
            self.cmd = ' '.join(cmd)
        
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Job(Minute='{self.minute}', Hour='{self.hour}', Month='{self.month}', Week='{self.week}', cmd={self.cmd}, tag={self.tag}"

    def _parse(self, args):
        params = []
        for arg in args:
            if type(arg) is range:
                params.append(f"{arg.start}-{arg.stop}")
            elif hasattr(arg, '__iter__'):
                params += list(map(lambda x: str(x), arg))
            else:
                params.append(str(arg))
        return ','.join(params)

    def Minute(self, *args, **kwargs):
        if 'every' in kwargs:
            self.minute = f"*/{kwargs['every']}"
        else:
            self.minute = self._parse(args)
        return self

    def Hour(self, *args, **kwargs):
        if 'every' in kwargs:
            self.hour = f"*/{kwargs['every']}"
        else:
            self.hour = self._parse(args)
        return self

    def Day(self, *args, **kwargs):
        if 'every' in kwargs:
            self.day = f"*/{kwargs['every']}"
        else:
            self.day = self._parse(args)
        return self

    def Month(self, *args, **kwargs):
        if 'every' in kwargs:
            self.month = f"*/{kwargs['every']}"
        else:
            self.month = self._parse(args)
        return self

    def Week(self, *args, **kwargs):
        if 'every' in kwargs:
            self.week = f"*/{kwargs['every']}"
        else:
            self.week = self._parse(args)
        return self

    def Command(self, cmd):
        self.cmd = cmd
        return self

    def Tag(self, tag):
        self.tag = None if tag is None else f"#{tag}"
        return self


class Crontab:
    def __init__(self, tag=None):
        self.tmp = Path(__file__).parent / "tmp.tab"
        self.tmp.touch(exist_ok=True)
        
        process = subprocess.Popen(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        self.jobs = []

        with self.tmp.open(mode='w+') as tab:
            for job in out.decode('utf-8').split('\n'):
                if job and (tag is None or f"#{tag}" in job):
                    self.jobs.append(Job(job))
                elif job:
                    print(job, file=tab)

        self.tag = tag

    def clear_jobs(self):
        self.jobs = []

    def add_job(self):
        self.jobs.append(Job(tag=self.tag))
        return self.jobs[-1]

    def write_back(self):
        with self.tmp.open(mode='a') as tab:
            for job in self.jobs:
                print(job.get(), file=tab)
                
        process = subprocess.Popen(['crontab', self.tmp.resolve()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.write_back()

        
if __name__ == "__main__":
    with Crontab(tag="test") as crontab:
        crontab.clear_jobs()
        j = crontab.add_job()
        j.Command("echo hello").Day(every=1).Month(every=1).Week(every=1)
