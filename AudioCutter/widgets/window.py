"""
Your favorite Audio Cutter.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Artist : Alfredo Hernández
Website : https://github.com/bil-elmoussaoui/Audio-Cutter
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of AudioCutter.
AudioCutter is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
AudioCutter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with AudioCutter. If not, see <http://www.gnu.org/licenses/>.
"""

from os import path
from gettext import gettext as _
from .headerbar import HeaderBar
from .actionbar import ActionBar
from .soundconfig import SoundConfig
from ..modules import Logger, Settings
from ..const import AUDIO_MIMES

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk


class Window(Gtk.ApplicationWindow):
    """Main Window Object."""
    instance = None

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect("delete-event", lambda x, y: self._on_close())
        self._main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._setup_window()
        self._setup_widgets()
        self._restore_state()

    @staticmethod
    def get_default():
        """Return the dafault instance of Window."""
        if Window.instance is None:
            Window.instance = Window()
        return Window.instance

    def _setup_window(self):
        self.set_resizable(False)
        self.set_default_size(600, 300)

    def _setup_widgets(self):
        """Setup the main widgets."""
        # Main widget
        self.add(self._main)
        # Headerbar
        headerbar = HeaderBar.get_default()
        headerbar.connect("open-file", self._open_file)
        self.set_titlebar(headerbar)

        # Action Bar
        actionbar = ActionBar.get_default()
        self._main.pack_end(actionbar, False, False, 0)

        # Audio Graph.

        # Config Box
        sound_config = SoundConfig.get_default()
        self._main.pack_end(sound_config, False, False, 0)


    def _open_file(self, *args):
        """Open an open file dialog to select an audio file."""
        dialog = Gtk.FileChooserDialog(_("Please choose an audio file"),
                                       self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self._add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            opened_file = dialog.get_filename()
            self._set_open_file(opened_file)
            Logger.debug("File Selected {}".format(opened_file))
        else:
            Logger.debug("Open file dialog closed without selecting a file.")
        dialog.destroy()

    def _add_filters(self, dialog):
        """Add audio filters to the open file dialog."""
        filters = Gtk.FileFilter()
        filters.set_name(_("Audio Files"))
        for mimetype in AUDIO_MIMES.keys():
            filters.add_mime_type(mimetype)
        dialog.add_filter(filters)

    def _set_open_file(self, filepath):
        """Set a filename as opened."""
        HeaderBar.get_default().set_open_file(filepath)
        ActionBar.get_default().set_state(True)
        SoundConfig.get_default().set_state(True)
        SoundConfig.get_default().set_open_file(filepath)
        Settings.get_default().last_file = filepath

    def _restore_state(self):
        """Restore the latest position and opened file."""
        settings = Settings.get_default()
        pos_x, pos_y = settings.window_position
        if pos_x != 0 and pos_y != 0:
            self.move(pos_x, pos_y)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)

        last_file = settings.last_file
        if last_file and path.exists(last_file):
            self._set_open_file(last_file)

    def _on_close(self):
        """Window delete event handler."""
        # TODO: ask the user if he wants to save the current modification?
        # Save the latest window position
        Settings.get_default().window_position = self.get_position()