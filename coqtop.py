from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
import time

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

class Coqtop:
    def __init__(self):
        self.proc = Popen(['coqtop'], stdin=PIPE, stderr=PIPE, stdout=PIPE, universal_newlines=True)
        self.out_queue = Queue()
        self.out_thread = Thread(target=self.enqueue_output)
        self.out_thread.daemon = True
        self.out_thread.start()
        self.err_queue = Queue()
        self.err_thread = Thread(target=self.enqueue_err)
        self.err_thread.daemon = True
        self.err_thread.start()
        self.get_output()
        self.get_prompt()

    def kill(self):
        self.proc.kill()

    def enqueue_output(self):
        while True:
            data = self.proc.stdout.read(1)
            if not data:
                break
            self.out_queue.put(data)

    def enqueue_err(self):
        while True:
            data = self.proc.stderr.read(1)
            if not data:
                break
            self.err_queue.put(data)

    def get_output(self):
        lines = []
        start = time.time()

        while time.time() - start < 1:
            while not self.out_queue.empty():
                lines.append(self.out_queue.get_nowait())
            if lines:
                break

        return ''.join(lines)

    '''
    Sends statement to coqtop
    Only give it statements, not comments
    Returns coqtop's output
    '''
    def send(self, statement):
        self.proc.stdin.write(statement+'\n')
        self.proc.stdin.flush()

    def get_prompt(self):
        lines = []
        start = time.time()

        while time.time() - start < 1:
            while not self.err_queue.empty():
                lines.append(self.err_queue.get_nowait())
            if lines:
                break

        return ''.join(lines)
