import re
import coqtop

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