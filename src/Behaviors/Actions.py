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


from UIToolkit import *


# Dispatched when a view is hovered
# if sender is note, it means that no view is currently being hovered
ViewHoweved   = Events.action("viewHovered")

# Dispatched when a view is selected (by clicking)
# if sender is note, it means that no view is currently selected
ViewSelected  = Events.action("viewSelected")

# Dispatched when an editable component is interacted with. This will usually
# invoke an edit controller
EditableActivated  = Events.action("editableActivated")

# Dispatched when a span menu needs to be opened
SpanMenuClicked  = Events.action("spanMenuClicked")



