# encoding: utf-8

# Copyright 2018 Taras Zakharko (taras.zakharko)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from observing import *

from GUI import Window, ModalDialog, Dialog, Label, Button, Task, application

class SpanHeaderDialog(Window):

    def __init__(self, span, spanView):
        Window.__init__(self, style='modal_dialog')
        self.title = "Edit utterance data"
        self.span = span
        self.spanView = spanView
        
        # controls
        utterance_label = Label("Utterance ID")
        speaker_label = Label("Speaker code")

        self.place(utterance_label, left = 20, top=20)
        self.place(speaker_label, left = 20, top=utterance_label + 20)
        # self.place(Button("Confirm", action = "ok", enabled = True), left =20, top = speaker_label+20)
        # self.place(Button("Cancel", action = "cancel", enabled = True), right =20, top = speaker_label+20)
        #
        self.shrink_wrap(padding = (20, 20))
        
        
    def ok(self):
        self.destroy()

    def cancel(self):
        self.destroy()        
        

def editSpanHeader(span, spanView):
  # print "Editing header for", span.headerLabel
  # dialog = SpanHeaderDialog(span, spanView)
  # spanView.dialog = dialog
  # dialog.show()
  # dialog.show()
  # dialog.show()
  print "NYI"
  
  



