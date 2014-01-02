from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
import time

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

class Coqtop:
    def __init__(self):
        self.proc = Popen(['coqtop'], stdin=PIPE, stderr=DEVNULL, stdout=PIPE, universal_newlines=True)
        self.queue = Queue()
        self.thread = Thread(target=self.enqueue_output)
        self.thread.daemon = True
        self.thread.start()
        print(self.get_lines())

    def enqueue_output(self):
        for line in iter(self.proc.stdout.readline, ''):
            self.queue.put(line)

    '''
    2 second timeout
    '''
    def get_lines(self):
        lines = []
        line = False
        start = time.time()

        while line == False and time.time()-start < 2:
            try:
                line = self.queue.get_nowait()
            except Empty:
                line = False
            else:
                lines.append(line)
                if not self.queue.empty():
                    line = False

        return lines

    '''
    Sends statement to coqtop
    Only give it statements, not comments
    Returns coqtop's output
    '''
    def send(self, statement):
        self.proc.stdin.write(statement+'\n')
        self.proc.stdin.flush()
        return self.get_lines()