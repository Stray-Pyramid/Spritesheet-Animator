# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QSize, QRect, Qt, pyqtSignal, QItemSelection, QItemSelectionModel
import logging

from animationTypes import *

# TODO alot.

class SpritesheetAnimationList(QtWidgets.QTreeView):

	animation_data_changed = pyqtSignal()

	def __init__(self, parent):
		super(SpritesheetAnimationList, self).__init__()

		self.init_ui()
		self.setParent(parent)
		self.setObjectName("treeView")
		self.setHeaderHidden(True)
		self.setItemsExpandable(True)
		self.setFocusPolicy(Qt.ClickFocus)
		self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)

		self.model = QtGui.QStandardItemModel()
		self.model.insertColumn(0)
		self.setModel(self.model)
		
		#Import available sprite sequences 
		self.model.setRowCount(0)
		
		self.animation_data = None
		self.clicked_item = None

	def init_ui(self):
		""" How this object looks """
		
		self.setMinimumSize(QSize(200, 0))
		self.setMaximumSize(QSize(200, 2000))		
		
	def load_animation_data(self, animation_data):
		self.animation_data = animation_data
		self.animation_data.data_changed.connect(self.renew)
		self.update_tree()
		
	def renew(self, e):
		if e == AnimationEvent.NEW_SEQUENCE or e == AnimationEvent.SEQUENCE_DELETED:
			self.update_tree()

	def update_tree(self):
		active_seq_item = None

		self.model.clear()
		for sequence in self.animation_data.sequences:
			sequence_item = QtGui.QStandardItem(sequence.name)
			if sequence == self.animation_data.active_sequence:
				active_seq_item = sequence_item

			self.model.appendRow(sequence_item)

		if active_seq_item is not None:
			self.setCurrentIndex(active_seq_item.index())


	""" EVENTS """
	def dataChanged(self, QModelIndex, _, roles, p_int=None, *args, **kwargs):
		#Something gets renamed or deleted
		item = self.model.itemFromIndex(QModelIndex)
		self.animation_data.active_sequence.name = item.text()


	def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
		# WARNING: selectionChanged will be called before init()
		if not hasattr(self, "animation_data"):
			return


		for index in selected.indexes():
			name = self.model.itemFromIndex(index).text()
			self.animation_data.select(name)

		for index in deselected.indexes():
			name = self.model.itemFromIndex(index).text()
			self.animation_data.deselect(name)

		for sequence in self.animation_data.selected:
			sequence.select_all()

		self.animation_data_changed.emit()

		#
		# for index in deselected.indexes():
		# 	item = self.model.itemFromIndex(index)
		# 	if item.parent() is None:
		# 		pass
		# 	else:
		# 		deselected_frames.append(item)
		#
		# if len(selected_sequences) != 0:
		# 	# Change to this sequence
		# 	self.animation_data.active_sequence = self.animation_data.get_sequence(selected_sequences[0].text())
		# 	self.animation_data_changed_signal.emit()
		# 	self.clearSelection()
		# 	#self.selectionModel().select(selected_sequences[0].index(), QItemSelectionModel.Select)
		#
		# elif len(selected_frames) != 0 or len(deselected_frames) != 0:
		# 	# Only frames have been selected
		# 	for index in selected.indexes():
		# 		# Add frames to selection
		# 		item = self.model.itemFromIndex(index)
		# 		if item.parent() is not None:
		# 			self.animation_data.active_sequence.select(int(item.text()))
		#
		# 	for index in deselected.indexes():
		# 		# Remove frames from selection
		# 		item = self.model.itemFromIndex(index)
		# 		if item.parent() is not None:
		# 			self.animation_data.active_sequence.deselect(int(item.text()))
		#
		# 	self.animation_data_changed_signal.emit()

		super(SpritesheetAnimationList, self).selectionChanged(selected, deselected)



	def mousePressEvent(self, mouse):

		index = self.indexAt(mouse.pos())
		if index is not None:
			self.clicked_item = self.model.itemFromIndex(index)
			if self.clicked_item is not None:
				# Set Sequence as active
				sequence = self.animation_data.get_sequence(self.clicked_item.text())
				self.animation_data.active_sequence = sequence
				self.animation_data.active_sequence.select_all()
				self.animation_data_changed.emit()
			else:
				self.animation_data.deselect_all()
		else:
			self.animation_data.deselect_all()


		super(SpritesheetAnimationList, self).mousePressEvent(mouse)


	# def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
	# 	item = self.model.itemFromIndex(self.indexAt(e.pos()))
	# 	if item is not None:
	# 		if item.parent() is not None:
	# 			self.focus_frame_signal.emit()
	# 		else:
	# 			# Edit sequence name
	# 			self.edit(item.index())
