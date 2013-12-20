import re
import sublime, sublime_plugin
from SublimeCoq.coqtop import Coqtop


class PrintDownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_position = self.view.settings().get('current_position')
        current_position = self.view.find('\\s*', current_position).end()

        indicator = self.view.substr(current_position) + self.view.substr(current_position + 1)

        if indicator == '(*':
            r = self.view.find('\\(\\*(.|\\n)*?\\*\\)', current_position)
        else:
            r = self.view.find('(.|\\n)*?\\.', current_position)
        self.view.settings().set('current_position', r.end())
        self.view.add_regions(repr(current_position), [r], 'comment')

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