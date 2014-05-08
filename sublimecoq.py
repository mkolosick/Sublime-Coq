import re
import sublime, sublime_plugin
from .coqtop import Coqtop

class CoqtopManager:
    def __init__(self):
        self.coqtop = None
        self.output_view = None
        self.file_view = None
        self.focused_proof_mode = False
        self.current_position = 0
        self.current_comment_number = 0
        self.current_statement_number = 0
        self.current_proof_number = 0
        self.proof_mode = False

    def start(self):
        self.coqtop = Coqtop(self)

    def send(self, statement):
        self.output_view.run_command('coqtop_clear')
        self.coqtop.send(statement)

    def receive(self, output, prompt):
        self.output_view.run_command('coqtop_output', {'output': output})
        if prompt != 'Coq < ':
            self.focused_proof_mode = True
        else:
            self.focused_proof_mode = False

    def stop(self):
        if self.coqtop is not None:
            self.coqtop.kill()
        self.coqtop = None
        self.output_view = None
        self.file_view = None
        self.focused_proof_mode = False
        self.current_position = 0
        self.current_comment_number = 0
        self.current_statement_number = 0
        self.current_proof_number = 0
        self.proof_mode = False

manager = CoqtopManager()

class CoqtopClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        entire_region = sublime.Region(0, self.view.size())
        self.view.set_read_only(False)
        self.view.erase(edit, entire_region)
        self.view.set_read_only(True)

class CoqtopOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output):
        entire_region = sublime.Region(0, self.view.size())
        self.view.set_read_only(False)
        self.view.erase(edit, entire_region)
        self.view.insert(edit, 0, output)
        self.view.set_read_only(True)

class CoqNextStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view

        manager.current_position = coqfile_view.find('\\s*', manager.current_position).end()

        indicator = coqfile_view.substr(manager.current_position) + coqfile_view.substr(manager.current_position + 1)

        if indicator == '(*':
            r = coqfile_view.find('\\(\\*(.|\\n)*?\\*\\)', manager.current_position)
            name = 'comment: ' + repr(manager.current_comment_number)
            manager.current_comment_number = manager.current_comment_number + 1
        else:
            r = coqfile_view.find('(.|\\n)*?\\.', manager.current_position)
            text = coqfile_view.substr(r)

            if coqfile_view.scope_name(manager.current_position) == 'source.coq keyword.source.coq ':
                if text == 'Proof.':
                    manager.proof_mode = True

            if manager.proof_mode:
                if text == 'Qed.' or text == 'Admitted.' or text == 'Save.' or text == 'Defined.':
                    manager.proof_mode = False
                name = 'proof: ' + repr(manager.current_proof_number)
                manager.current_proof_number = manager.current_proof_number + 1
            else:
                name = 'statement: ' + repr(manager.current_statement_number)
                manager.current_statement_number = manager.current_statement_number + 1
            manager.send(coqfile_view.substr(r))

        coqfile_view.show(r)
        manager.current_position = r.end()
        coqfile_view.add_regions(name, [r], 'meta.coq.proven')

class CoqUndoStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view

        if manager.proof_mode:
            previous_proof_number = manager.current_proof_number - 1
            previous_region = coqfile_view.get_regions('proof: ' + repr(previous_proof_number))[0]
            if coqfile_view.substr(previous_region) == 'Proof.':
                manager.proof_mode = False
            else:
                manager.send('Undo.')
            manager.current_proof_number = previous_proof_number
            coqfile_view.erase_regions('proof: ' + repr(previous_proof_number))
        else:
            no_comment = False
            no_statement = False
            try:
                previous_comment_number = manager.current_comment_number - 1
                previous_comment_region = coqfile_view.get_regions('comment: ' + repr(previous_comment_number))[0]
            except IndexError:
                no_comment = True
            try:
                previous_statement_number = manager.current_statement_number - 1
                previous_statement_region = coqfile_view.get_regions('statement: ' + repr(previous_statement_number))[0]
            except IndexError:
                no_statement = True
            if no_statement or (not no_comment and previous_comment_region.begin() > previous_statement_region.begin()):
                previous_region = previous_comment_region
                coqfile_view.erase_regions('comment: ' + repr(previous_comment_number))
                manager.current_comment_number = previous_comment_number
            else:
                previous_region = previous_statement_region
                name = coqfile_view.substr(coqfile_view.word(coqfile_view.word(previous_region.begin()).end() + 1))
                if manager.focused_proof_mode:
                    manager.send('Abort.')
                else:
                    manager.send('Reset ' + name + '.')
                while True:
                    previous_proof_number = manager.current_proof_number - 1
                    if previous_proof_number == -1:
                        break
                    else:
                        previous_proof_region = coqfile_view.get_regions('proof: ' + repr(previous_proof_number))[0]
                        if previous_proof_region.begin() < previous_region.begin():
                            break
                        else:
                            coqfile_view.erase_regions('proof: ' + repr(previous_proof_number))
                            manager.current_proof_number = previous_proof_number
                manager.current_statement_number = previous_statement_number
                coqfile_view.erase_regions('statement: ' + repr(previous_statement_number))
        manager.current_position = previous_region.begin()


class CoqStopCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view
        manager.output_view.window().run_command('close')
        coqfile_view.settings().set('coqtop_running', False)
        for number in range(0, manager.current_comment_number):
            coqfile_view.erase_regions('comment: ' + repr(number))
        for number in range(0, manager.current_statement_number):
            coqfile_view.erase_regions('statement: ' + repr(number))
        for number in range(0, manager.current_proof_number):
            coqfile_view.erase_regions('proof: ' + repr(number))

        manager.stop()

class RunCoqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coq_syntax = self.view.settings().get('syntax')
        window = self.view.window()
        editor_group = window.active_group()
        self.view.settings().set('coqtop_running', True)

        manager.current_position = 0
        manager.current_comment_number = 0
        manager.current_statement_number = 0
        manager.current_proof_number = 0
        manager.proof_mode = False

        window.run_command('new_pane', {"move": False})
        window.focus_group(editor_group)
        coq_group = window.num_groups() - 1
        coqtop_view = window.active_view_in_group(coq_group)
        coqtop_view.set_syntax_file(coq_syntax)
        coqtop_view.set_name('*COQTOP*')
        coqtop_view.set_read_only(True)
        coqtop_view.set_scratch(True)
        coqtop_view.settings().set('coqtop_running', True)

        manager.file_view = self.view
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

    def on_selection_modified(self, view):
        if view.settings().get('coqtop_running') == True:
            regions = []
            for number in range(0, manager.current_statement_number):
                regions += view.get_regions('statement: ' + repr(number))
            for number in range(0, manager.current_proof_number):
                regions += view.get_regions('proof: ' + repr(number))

            selection = view.sel()

            view.set_read_only(False)
            for region in regions:
                for selected in selection:
                    if region.intersects(selected):
                        view.set_read_only(True)
                        break
