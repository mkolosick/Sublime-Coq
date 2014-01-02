import re
import sublime, sublime_plugin
from SublimeCoq.coqtop import Coqtop

class CoqtopManager:
    def __init__(self):
        self.coqtop = None
        self.output_view = None

    def start(self):
        self.coqtop = Coqtop()

    def send(self, statement):
        result_list = self.coqtop.send(statement)
        output = ''.join(result_list)
        self.output_view.run_command('coqtop_output', {'output': output})


manager = CoqtopManager()

class CoqtopOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output):
        entire_region = sublime.Region(0, self.view.size())
        self.view.set_read_only(False)
        self.view.erase(edit, entire_region)
        self.view.insert(edit, 0, output)
        self.view.set_read_only(True)

class CoqNextStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.name() == '*COQTOP*':
            coqfile_id = self.view.settings().get('coqfile_id')
            coqfile_group = self.view.settings().get('coqfile_group')
            views = self.view.window().views_in_group(coqfile_group)
            for v in views:
                if v.id() == coqfile_id:
                    coqfile_view = v
                    break
        else:
            coqfile_view = self.view
        
        current_position = coqfile_view.settings().get('current_position')
        current_position = coqfile_view.find('\\s*', current_position).end()

        indicator = coqfile_view.substr(current_position) + coqfile_view.substr(current_position + 1)

        if indicator == '(*':
            r = coqfile_view.find('\\(\\*(.|\\n)*?\\*\\)', current_position)
            current_comment_number = coqfile_view.settings().get('current_comment_number')
            name = 'comment: ' + repr(current_comment_number)
            coqfile_view.settings().set('current_comment_number', current_comment_number + 1)
        else:
            r = coqfile_view.find('(.|\\n)*?\\.', current_position)
            text = coqfile_view.substr(r)

            if coqfile_view.scope_name(current_position) == 'source.coq keyword.source.coq ':
                if text == 'Proof.':
                    coqfile_view.settings().set('proof_mode', True)

            if coqfile_view.settings().get('proof_mode'):
                if text == 'Qed.' or text == 'Admitted.' or text == 'Save.' or text == 'Defined.':
                    coqfile_view.settings().set('proof_mode', False)
                current_proof_number = coqfile_view.settings().get('current_proof_number')
                name = 'proof: ' + repr(current_proof_number)
                coqfile_view.settings().set('current_proof_number', current_proof_number + 1)
            else:
                current_statement_number = coqfile_view.settings().get('current_statement_number')
                name = 'statement: ' + repr(current_statement_number)
                coqfile_view.settings().set('current_statement_number', current_statement_number + 1)
            manager.send(coqfile_view.substr(r))
            
        coqfile_view.show(r)
        coqfile_view.settings().set('current_position', r.end())
        coqfile_view.add_regions(name, [r], 'comment')

class CoqUndoStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.name() == '*COQTOP*':
            coqfile_id = self.view.settings().get('coqfile_id')
            coqfile_group = self.view.settings().get('coqfile_group')
            views = self.view.window().views_in_group(coqfile_group)
            for v in views:
                if v.id() == coqfile_id:
                    coqfile_view = v
                    break
        else:
            coqfile_view = self.view

        if coqfile_view.settings().get('proof_mode'):
            previous_proof_number = coqfile_view.settings().get('current_proof_number') - 1
            previous_region = coqfile_view.get_regions('proof: ' + repr(previous_proof_number))[0]
            if coqfile_view.substr(previous_region) == 'Proof.':
                print('Abort and resend.')
                coqfile_view.settings().set('proof_mode', False)
            else:
                print('Undo.')
            coqfile_view.settings().set('current_proof_number', previous_proof_number)
            coqfile_view.erase_regions('proof: ' + repr(previous_proof_number))
        else:
            no_comment = False
            no_statement = False
            try:
                previous_comment_number = coqfile_view.settings().get('current_comment_number') - 1
                previous_comment_region = coqfile_view.get_regions('comment: ' + repr(previous_comment_number))[0]
            except IndexError:
                no_comment = True
            try:
                previous_statement_number = coqfile_view.settings().get('current_statement_number') - 1
                previous_statement_region = coqfile_view.get_regions('statement: ' + repr(previous_statement_number))[0]
            except IndexError:
                no_statement = True
            if no_statement or (not no_comment and previous_comment_region.begin() > previous_statement_region.begin()):
                previous_region = previous_comment_region
                coqfile_view.erase_regions('comment: ' + repr(previous_comment_number))
                coqfile_view.settings().set('current_comment_number', previous_comment_number)
            else:
                previous_region = previous_statement_region
                name = coqfile_view.substr(coqfile_view.word(coqfile_view.word(previous_region.begin()).end() + 1))
                print('Reset ' + name)
                while True:
                    previous_proof_number = coqfile_view.settings().get('current_proof_number') - 1
                    if previous_proof_number == -1:
                        break
                    else:
                        previous_proof_region = coqfile_view.get_regions('proof: ' + repr(previous_proof_number))[0]
                        if previous_proof_region.begin() < previous_region.begin():
                            break
                        else:
                            coqfile_view.erase_regions('proof: ' + repr(previous_proof_number))
                            coqfile_view.settings().set('current_proof_number', previous_proof_number)
                coqfile_view.settings().set('current_statement_number', previous_statement_number)
                coqfile_view.erase_regions('statement: ' + repr(previous_statement_number))
        coqfile_view.settings().set('current_position', previous_region.begin())


class CoqStopCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.name() == '*COQTOP*':
            coqfile_id = self.view.settings().get('coqfile_id')
            coqfile_group = self.view.settings().get('coqfile_group')
            views = self.view.window().views_in_group(coqfile_group)
            for v in views:
                if v.id() == coqfile_id:
                    coqfile_view = v
                    break
            self.view.window().run_command('close')
        else:
            coqfile_view = self.view
            coqtop_group = self.view.settings().get('coqtop_group')
            views = self.view.window().views_in_group(coqtop_group)
            for v in views:
                if v.name() == '*COQTOP*':
                    self.view.window().focus_view(v)
                    v.window().run_command('close')
                    break
        coqfile_view.settings().set('coqtop_running', False)
        for number in range(0, coqfile_view.settings().get('current_comment_number')):
            coqfile_view.erase_regions('comment: ' + repr(number))
        for number in range(0, coqfile_view.settings().get('current_statement_number')):
            coqfile_view.erase_regions('statement: ' + repr(number))
        for number in range(0, coqfile_view.settings().get('current_proof_number')):
            coqfile_view.erase_regions('proof: ' + repr(number))
        coqfile_view.settings().set('current_position', 0)
        coqfile_view.settings().set('current_comment_number', 0)
        coqfile_view.settings().set('current_statement_number', 0)
        coqfile_view.settings().set('current_proof_number', 0)
        coqfile_view.settings().set('proof_mode', False)

class RunCoqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coq_syntax = self.view.settings().get('syntax')
        window = self.view.window()
        editor_group = window.active_group()
        self.view.settings().set('coqtop_running', True)
        self.view.settings().set('current_position', 0)
        self.view.settings().set('current_comment_number', 0)
        self.view.settings().set('current_statement_number', 0)
        self.view.settings().set('current_proof_number', 0)
        self.view.settings().set('proof_mode', False)

        window.run_command('new_pane', {"move": False})
        window.focus_group(editor_group)
        coq_group = window.num_groups() - 1
        coqtop_view = window.active_view_in_group(coq_group)
        coqtop_view.set_syntax_file(coq_syntax)
        coqtop_view.set_name('*COQTOP*')
        coqtop_view.set_read_only(True)
        coqtop_view.set_scratch(True)
        coqtop_view.settings().set('coqtop_running', True)
        coqtop_view.settings().set('coqfile_id', self.view.id())

        coqtop_view.settings().set('coqfile_group', editor_group)
        self.view.settings().set('coqtop_group', coq_group)

        manager.output_view = coqtop_view
        manager.start()

class CoqContext(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'running_coqtop':
            running = view.settings().get('coqtop_running')
            if running is None:
                return None
            if operator == sublime.OP_EQUAL:
                return running
            elif operator == sublime.OP_NOT_EQUAL:
                return not running
            else:
                return False
        return None