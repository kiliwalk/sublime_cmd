import os
import sublime
import sublime_plugin


class ConEmuOpenCommand():

    def get_project(self):
        has_project = 0
        if self.window.project_file_name():  # try project file name first
            project_dir, project_name = os.path.split(
                self.window.project_file_name())
            project_name, ext = os.path.splitext('st:' + project_name)
            project_dir = self.window.folders()[0]
            has_project = 1
        elif self.window.folders():  # if no project, use the top folder
            project_dir = self.window.folders()[0]
            project_name = project_dir
        # If no folder, use current folder
        elif self.window.active_view().file_name():
            project_dir, _ = os.path.split(
                self.window.active_view().file_name())
            project_name = project_dir
        else:  # then exit
            return (None, None, 0)
        return (project_name, project_dir, has_project)

    def open_conemu(self, dirname, title):
        """Open ConEmu function.

        Run ConEmu in different modes. Support custom terminals.

        Arguments:
            dirname — current directory.
            title — current file title.
        """
        # Get settings
        settings = sublime.load_settings(
            "ConEmu.sublime-settings")
        # Get values for keys conemu_mode and custom_terminal
        cmd_options = settings.get(
            "conemu_mode")
        custom_terminal = settings.get(
            "custom_terminal")
        # Get Windows bitness
        # If Windows 64-bit, run conemu64.exe, if 32-bit — conemu.exe
        get_bitness = sublime.arch()
        if get_bitness == 'x64':
            bitness = 'conemu64.exe'
        else:
            bitness = 'conemu.exe'
        # Far mode
        # https://superuser.com/a/1188693/572069
        if cmd_options == 'far':
            command = "start " + bitness + " /Single /Dir \"" + dirname + \
                "\" /cmdlist far . -new_console:t:\"" + title + "\""
        # PowerShell mode
        elif cmd_options == 'powershell':
            command = "start " + bitness + " /Single /Dir \"" + dirname + \
                "\" /cmdlist powershell -new_console:t:\"" + title + "\""
        # Custom terminal
        elif cmd_options == 'custom':
            command = "start " + bitness + " /Single /Dir \"" + dirname + \
                "\" /cmdlist " + custom_terminal + \
                " -new_console:t:\"" + title + "\""
        # cmd.exe mode — default
        else:
            command = "start " + bitness + " /Single /Dir \"" + dirname + \
                "\" /cmdlist cmd -new_console:t:\"" + title + "\""
        os.system(command)

# open project folder


class OpenConemuProjectCommand(
        sublime_plugin.WindowCommand, ConEmuOpenCommand):

    def run(self):
        project_name, project_dir, has_project = self.get_project()
        if not project_name:
            return

        self.open_conemu(project_dir, project_name)

# open "here" folder


class OpenConemuHereCommand(sublime_plugin.WindowCommand, ConEmuOpenCommand):

    def run(self, paths=[]):
        project_name, project_dir, has_project = self.get_project()
        if not project_name:
            return

        if paths:
            heredir = paths[0]
            if os.path.isfile(heredir):
                heredir = os.path.dirname(heredir)
        elif self.window.active_view().file_name():
            heredir = os.path.dirname(self.window.active_view().file_name())
        else:  # if no active file open, then try to open project folder
            heredir = project_dir

        # get the tab title
        title = heredir
        if has_project:
            rel_path = os.path.relpath(heredir, project_dir)
            if rel_path == '.':
                title = project_name
            elif rel_path[:2] == '..':  # not in project, show the whole path
                title = heredir
            else:
                title = project_name + ': ' + rel_path

        self.open_conemu(heredir, title)
