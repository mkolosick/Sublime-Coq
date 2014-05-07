from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import time
import sys
import os
import select

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

class Coqtop:
    def __init__(self, manager):
        if sys.platform.startswith('darwin'):
            self.proc = Popen(['coqtop'], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            self.proc = Popen(['coqtop'], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        else:
            self.proc = Popen(['coqtop'], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        self.manager = manager
        self.out_thread = Thread(target=self.receive)
        self.out_thread.daemon = True
        self.out_thread.start()

    def kill(self):
        self.proc.kill()

    def receive(self):
        buf = ""

        while True:
            while not buf.endswith(' < '):
                select.select([self.proc.stdout], [], [self.proc.stdout])
                try:
                    data = os.read(self.proc.stdout.fileno(), 256)
                    print(data)
                    buf += data.decode(encoding='UTF-8')
                except OSError as e:
                    print(e)

            while buf.startswith('Coq < '):
                buf = buf[6:]

            if buf.find("\n") == -1:
                output = ""
                prompt = buf
            else:
                (output, prompt) = buf.rsplit("\n", 1)

            buf = ""

            self.manager.receive(output, prompt)

    def send(self, statement):
        self.proc.stdin.write(statement + '\n')
        self.proc.stdin.flush()
