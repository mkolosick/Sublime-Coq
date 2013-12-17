from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
import re

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)


def get_lines(queue):
    lines = []
    line = False

    while line == False:
        try:
            line = q.get_nowait()
        except Empty:
            line = False
        else:
            lines.append(line)
            if not q.empty():
                line = False

    return lines

# returns (the next statement, rest) or
#         False if there are no more well-formed statements
def next_statement(program):
    if program == '':
        return False
    elif re.match('\\s+', program) is not None:
        return next_statement(re.sub('\\s+', '', program, 1))
    elif program[0:2] == '(*':
        try:
            index = program.index('*)')
        except ValueError:
            return False
        else:
            return ((program[0:index+2], program[index+2:]) if index+2 < len(program) else (program[0:index+2], ''))
    else:
        try:
            index = program.index('.')
        except ValueError:
            return False
        else:
            return ((program[0:index+1], program[index+1:]) if index+1 < len(program) else (program[0:index+1], ''))

if __name__ == '__main__':
    f = open('Basics.v', 'r')
    program = f.read()

    while True:
        temp = next_statement(program)
        if temp == False:
            break
        else:
            print(temp[0])
            print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
            program = temp[1]


if __name__ == '__not_main__':
    p = Popen(['coqtop'], stdin=PIPE, stderr=DEVNULL, stdout=PIPE, universal_newlines=True)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True
    t.start()

    lines = get_lines(q)
    for line in lines:
        print(line)

    p.stdin.write('Definition add1 (n : nat) : nat :=\n\tS n.\n')
    p.stdin.flush()

    lines = get_lines(q)
    for line in lines:
        print(line)

    p.stdin.write('Theorem test : forall (x y : nat), x + y = x + y.\n')
    p.stdin.flush()

    line = False

    lines = get_lines(q)
    for line in lines:
        print(line)