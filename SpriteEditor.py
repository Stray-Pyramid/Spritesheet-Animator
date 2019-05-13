# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SpriteEditor.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QSize, QRect

import logging
import sys
import math
import json
import os

import frameView
import sequenceTree
import spritesheetView
from animationTypes import AnimationData

class MainWindow(QtWidgets.QMainWindow):
	animation_data = None
	unsaved_changes = False

	def __init__(self):
		super(MainWindow, self).__init__()
		
		self.init_ui()
		
		self.retranslate_ui()

		self.save_location = None


	def init_ui(self):
		self.setObjectName("Sprite Editor")
		self.resize(1109, 557)
		
		self.centralwidget = QtWidgets.QWidget(self)
		self.centralwidget.setObjectName("centralwidget")
		self.setCentralWidget(self.centralwidget)
		
		self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.gridLayout.setObjectName("gridLayout")
		
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setSpacing(0)
		self.horizontalLayout.setObjectName("horizontalLayout")
		
		# Animation items viewer
		self.treeView = sequenceTree.SpritesheetAnimationList(self.centralwidget)
		self.horizontalLayout.addWidget(self.treeView)
		
		# Animation spritesheet viewer
		self.spritesheetView = spritesheetView.SpritesheetWidget()
		self.horizontalLayout.addLayout(self.spritesheetView)
		
		# Animation frames viewer
		self.spriteView = frameView.SpriteAnimatorWidget()
		self.horizontalLayout.addLayout(self.spriteView)

		# Connect emitters
		self.treeView.animation_data_changed.connect(self.trigger_update)
		self.spritesheetView.view.animation_data_changed_signal.connect(self.trigger_update)
		#self.spriteView.view.animation_data_changed_signal.connect(self.trigger_update)

		# Add the 3 views to the main layout
		self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
		
		# Menu items
		self.menubar = QtWidgets.QMenuBar(self)
		self.menubar.setGeometry(QRect(0, 0, 1109, 21))
		self.menubar.setObjectName("menubar")
		
		self.menuFile = QtWidgets.QMenu(self.menubar)
		self.menuFile.setObjectName("menuFile")
		self.setMenuBar(self.menubar)
		
		self.actionNew = QtWidgets.QAction(self)
		self.actionNew.setObjectName("actionNew")
		self.actionNew.triggered.connect(self.new_sprite_animation)
		
		self.actionOpen = QtWidgets.QAction(self)
		self.actionOpen.setObjectName("actionOpen")
		self.actionOpen.triggered.connect(self.open_spritesheet_sequence_file)
		
		self.actionSave = QtWidgets.QAction(self)
		self.actionSave.setObjectName("actionSave")
		self.actionSave.triggered.connect(self.save_animation_data)
		self.actionSave.setEnabled(False)
		
		self.actionExit = QtWidgets.QAction(self)
		self.actionExit.setObjectName("actionExit")
		self.actionExit.triggered.connect(self.close)

		self.menuFile.addAction(self.actionNew)
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionExit)
		self.menubar.addAction(self.menuFile.menuAction())

		""" DELETE KEY SHORTCUT """
		self.shortcut_del_frame = QtWidgets.QShortcut(QtGui.QKeySequence("Del"), self)
		self.shortcut_del_frame.activated.connect(self.delete_action)


		# DEBUG
		#self.spritesheetView.spritesheet_dir_label.setText("C:/Users/Anthony_PC/Desktop/Sprite Animator/spritesheets/marco.png")
		#self.spritesheetView.load_spritesheet("C:/Users/Anthony_PC/Desktop/Sprite Animator/spritesheets/marco.png")

	def retranslate_ui(self):
		self.setWindowTitle("SAMP")
		self.menuFile.setTitle("File")
		self.actionNew.setText("New")
		self.actionSave.setText("Save")
		self.actionOpen.setText("Open")
		self.actionExit.setText("Exit")

	def new_sprite_animation(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'spritesheets',"Image files (*.jpg *.png)")[0]

		#path = "C:/Users/Stray/Dropbox/Sprite Animator/spritesheets/marco.png"

		if path:

			if os.path.exists(path) is False:
				logging.error("Tried to open a spritesheet that doesn't exist")
				return

			logging.info("Opening sprite sheet " + path)
			self.save_location = None
			self.spritesheetView.spritesheet_dir_label.setText(path)

			#Spritesheet should appear on spritesheet viewer, be pannable and zoomable
			self.load_animation_data(AnimationData(path))
		
	def open_spritesheet_sequence_file(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'spritesheets',"Json files (*.json)")[0]
		if path:
			logging.info("Opening Animation Data " + path)
			try:
				with open(path, 'r') as infile:
					data = json.load(infile)

				if not os.path.exists(data['fpath']):
					# Spritesheet image not found
					self.displayError("Could not open spritesheet",
									  "Cannot find spritesheet image. Can't find " + data['fpath'])
				else:
					self.save_location = path
					self.load_animation_data(AnimationData.import_data(data))
					self.trigger_update()

			except json.JSONDecodeError as error:
				logging.error("Unable to open JSON file.")
				logging.error(error)

	def save_animation_data(self):
		try:

			if self.save_location is None:
				name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', "spritesheets", "JSON Files(*.json)")
				if name[0] == '':
					return
				else:
					self.save_location = name[0]

			#spritesheet_name = self.animation_data.spritesheet_fname
			data = self.animation_data.export_data()
			with open(self.save_location, 'w') as outfile:
				json.dump(data, outfile)
				logging.info("Animation Data Saved Successfully")
			self.unsaved_changes = False

		except ValueError:
			self.displayError("Could not save", "There was an error while trying to save.")
		except IOError:
			self.displayError("Could not save", "Could not write to the animation data file.")


	def load_animation_data(self, animation_data):
		self.actionSave.setEnabled(True)
		self.animation_data = animation_data

		self.treeView.load_animation_data(animation_data)
		self.spritesheetView.load_animation_data(animation_data)
		self.spriteView.load_animation_data(animation_data)


	def trigger_update(self):
		source = self.sender()

		if source != self.spritesheetView.view:
			self.spritesheetView.renew()
		if source != self.spriteView.view:
			self.spriteView.renew()

		self.unsaved_changes = True


	def delete_action(self):
		if self.spritesheetView.view.hasFocus():
			for sequence in self.animation_data.selected:
				for i in range(0, len(sequence.selected)):
					frame = self.animation_data.active_sequence.selected.pop()
					self.animation_data.active_sequence.remove_frame(frame)

		elif self.treeView.hasFocus():
			for sequence in self.animation_data.selected:
				self.animation_data.del_sequence(sequence)

		elif self.spriteView.view.hasFocus():
			self.animation_data.active_sequence.remove_frame(self.animation_data.active_frame)

		self.trigger_update()

	def displayError(self, title, message):
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Critical)
		box.setWindowTitle(title)
		box.setText(message)
		box.setStandardButtons(QtWidgets.QMessageBox.Ok)
		box.exec_()
		
	""" EVENTS """
	def closeEvent(self, event: QtGui.QCloseEvent) -> None:

		if self.unsaved_changes is False:
			event.accept()
			return

		reply = QtWidgets.QMessageBox()
		reply.setIcon(QtWidgets.QMessageBox.Question)
		reply.setWindowTitle("Save Changes")
		reply.setText("Save changes before exit?")
		reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |QtWidgets.QMessageBox.Cancel)

		save = reply.exec_()

		if save == QtWidgets.QMessageBox.Yes:
			logging.info("Saving and exiting")
			self.save_animation_data()
			event.accept()
		elif save == QtWidgets.QMessageBox.No:
			logging.info("Exiting without saving")
			event.accept()
		else:
			event.ignore()

def generate_app_icon() -> QtGui.QIcon:
	app_icon = QtGui.QIcon()
	app_icon.addFile('icons/16x16.png', QSize(16, 16))
	app_icon.addFile('icons/24x24.png', QSize(24, 24))
	app_icon.addFile('icons/32x32.png', QSize(32, 32))
	app_icon.addFile('icons/48x48.png', QSize(48, 48))
	app_icon.addFile('icons/256x256.png', QSize(256, 256))
	return app_icon

def main():

	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationDisplayName('Spritesheet Animation Manipulator Program')
	app.setWindowIcon(generate_app_icon())
	
	main_window = MainWindow()
	main_window.show()

	sys.exit(app.exec_())


if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

	main()