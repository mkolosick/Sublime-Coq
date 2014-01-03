from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import time

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

class Coqtop:
    def __init__(self):
        self.proc = Popen(['coqtop'], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        self.out_queue = Queue()
        self.out_thread = Thread(target=self.enqueue_output)
        self.out_thread.daemon = True
        self.out_thread.start()
        self.get_output()

    def kill(self):
        self.proc.kill()

    def enqueue_output(self):
        while True:
            data = self.proc.stdout.read(1)
            if not data:
                break
            self.out_queue.put(data)

    # strips preceding prompts and returns (output, prompt)
    def get_output(self):
        raw = self.get_raw_output()
        while raw[0:6] == ['C', 'o', 'q', ' ', '<', ' ']:
            raw[:] = raw[6:]

        return ''.join(raw)

    def get_raw_output(self):
        lines = []
        start = time.time()

        while time.time() - start < 1:
            while not self.out_queue.empty():
                lines.append(self.out_queue.get_nowait())
            if lines[-2:] == ['<', ' ']:
                break

        return lines

    '''
    Sends statement to coqtop
    Only give it statements, not comments
    Returns coqtop's output
    '''
    def send(self, statement):
        self.proc.stdin.write(statement+'\n')
        self.proc.stdin.flush()