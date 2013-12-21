import re
import sublime, sublime_plugin
from SublimeCoq.coqtop import Coqtop


class CoqNextStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_position = self.view.settings().get('current_position')
        current_position = self.view.find('\\s*', current_position).end()

        indicator = self.view.substr(current_position) + self.view.substr(current_position + 1)

        if indicator == '(*':
            r = self.view.find('\\(\\*(.|\\n)*?\\*\\)', current_position)
            current_comment_number = self.view.settings().get('current_comment_number')
            name = 'comment: ' + repr(current_comment_number)
            self.view.settings().set('current_comment_number', current_comment_number + 1)
        else:
            r = self.view.find('(.|\\n)*?\\.', current_position)
            text = self.view.substr(r)

            if self.view.scope_name(current_position) == 'source.coq keyword.source.coq ':
                if text == 'Proof.':
                    self.view.settings().set('proof_mode', True)

            if self.view.settings().get('proof_mode'):
                if text == 'Qed.' or text == 'Admitted.' or text == 'Save.' or text == 'Defined.':
                    self.view.settings().set('proof_mode', False)
                current_proof_number = self.view.settings().get('current_proof_number')
                name = 'proof: ' + repr(current_proof_number)
                self.view.settings().set('current_proof_number', current_proof_number + 1)
            else:
                current_statement_number = self.view.settings().get('current_statement_number')
                name = 'statement: ' + repr(current_statement_number)
                self.view.settings().set('current_statement_number', current_statement_number + 1)
            
        self.view.show(r)
        self.view.settings().set('current_position', r.end())
        self.view.add_regions(name, [r], 'comment')

class CoqUndoStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.settings().get('proof_mode'):
            previous_proof_number = self.view.settings().get('current_proof_number') - 1
            previous_region = self.view.get_regions('proof: ' + repr(previous_proof_number))[0]
            if self.view.substr(previous_region) == 'Proof.':
                print('Abort and resend.')
                self.view.settings().set('proof_mode', False)
            else:
                print('Undo.')
            self.view.settings().set('current_proof_number', previous_proof_number)
            self.view.erase_regions('proof: ' + repr(previous_proof_number))
        else:
            no_comment = False
            no_statement = False
            try:
                previous_comment_number = self.view.settings().get('current_comment_number') - 1
                previous_comment_region = self.view.get_regions('comment: ' + repr(previous_comment_number))[0]
            except IndexError:
                no_comment = True
            try:
                previous_statement_number = self.view.settings().get('current_statement_number') - 1
                previous_statement_region = self.view.get_regions('statement: ' + repr(previous_statement_number))[0]
            except IndexError:
                no_statement = True
            if no_statement or (not no_comment and previous_comment_region.begin() > previous_statement_region.begin()):
                previous_region = previous_comment_region
                self.view.erase_regions('comment: ' + repr(previous_comment_number))
                self.view.settings().set('current_comment_number', previous_comment_number)
            else:
                previous_region = previous_statement_region
                name = self.view.substr(self.view.word(self.view.word(previous_region.begin()).end() + 1))
                print('Reset ' + name)
                while True:
                    previous_proof_number = self.view.settings().get('current_proof_number') - 1
                    if previous_proof_number == -1:
                        break
                    else:
                        previous_proof_region = self.view.get_regions('proof: ' + repr(previous_proof_number))[0]
                        if previous_proof_region.begin() < previous_region.begin():
                            break
                        else:
                            self.view.erase_regions('proof: ' + repr(previous_proof_number))
                            self.view.settings().set('current_proof_number', previous_proof_number)
                self.view.settings().set('current_statement_number', previous_statement_number)
                self.view.erase_regions('statement: ' + repr(previous_statement_number))
        self.view.settings().set('current_position', previous_region.begin())




class RunCoqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coq_syntax = self.view.settings().get('syntax')
        program = self.view.substr(sublime.Region(0, self.view.size()))
        window = self.view.window()
        editor_group = window.active_group()
        coqfile_view = window.new_file()
        coqfile_view.insert(edit, 0, program)
        coqfile_view.set_read_only(True)
        coqfile_view.set_scratch(True)
        coqfile_view.set_syntax_file(coq_syntax)
        coqfile_view.set_name('*COQTOP*')
        coqfile_view.settings().set('coqtop_running', True)
        coqfile_view.settings().set('current_position', 0)
        coqfile_view.settings().set('current_comment_number', 0)
        coqfile_view.settings().set('current_statement_number', 0)
        coqfile_view.settings().set('current_proof_number', 0)
        coqfile_view.settings().set('proof_mode', False)
        coqfile_view.sel().clear()
        coqfile_view.sel().add(sublime.Region(0,0))

        window.run_command('new_pane', {"move": False})
        window.focus_group(editor_group)
        coq_group = window.num_groups() - 1
        coqtop_view = window.active_view_in_group(coq_group)
        coqtop_view.set_read_only(True)
        coqtop_view.set_scratch(True)
        coqtop_view.settings().set('coqtop_running', True)
        
        coqtop_view.settings().set('coqfile_group', editor_group)
        coqfile_view.settings().set('coqtop_group', coq_group)

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