from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
import re

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

'''
returns (the next statement, rest) or
        None if there are no more well-formed statements
'''
def next_statement(program):
    if program == '':
        return None
    elif re.match('\\s+', program) is not None:
        return next_statement(re.sub('\\s+', '', program, 1))
    elif program[0:2] == '(*':
        try:
            index = program.index('*)')
        except ValueError:
            return None
        else:
            return ((program[0:index+2], program[index+2:]) if index+2 < len(program) else (program[0:index+2], ''))
    else:
        try:
            index = program.index('.')
        except ValueError:
            return None
        else:
            return ((program[0:index+1], program[index+1:]) if index+1 < len(program) else (program[0:index+1], ''))

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

    def get_lines(self):
        lines = []
        line = False

        while line == False:
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
    Returns coqtop's output
    '''
    def send(self, statement):
        self.proc.stdin.write(statement+'\n')
        self.proc.stdin.flush()
        return self.get_lines()

if __name__ == '__main__':
    f = open('Basics.v', 'r')
    program = f.read()

    coqtop = Coqtop()

    temp = next_statement(program)
    if temp is None:
        print('No more valid statements')
    elif temp[0:2] != '(*':
        print('A comment')
    else:
        program = temp[1]
        print(coqtop.send(temp[0]))