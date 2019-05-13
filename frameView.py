# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QSize, QRect, Qt, pyqtSignal, QTimer
import logging

from animationTypes import AnimationData, AnimationSequence, AnimationFrame

btn_rect = QRect(0, 0, 30, 30)
btn_size = QSize(30, 30)

class SpriteAnimatorWidget(QtWidgets.QVBoxLayout):
	
	
	
	def __init__(self):
		super(SpriteAnimatorWidget, self).__init__()
		
		self.play_icon = QtGui.QIcon("icons/play.png")
		self.pause_icon = QtGui.QIcon("icons/pause.png")
		self.prev_frame_icon = QtGui.QIcon("icons/prev_frame.png")
		self.next_frame_icon = QtGui.QIcon("icons/next_frame.png")
		self.loop_icon = QtGui.QIcon("icons/repeat.png")
		self.backandforth_icon = QtGui.QIcon("icons/bandf.png")
		self.fullscreen_icon = QtGui.QIcon("icons/fullscreen.png")
		self.axis_icon = QtGui.QIcon("icons/axis.png")
		self.frame_border_icon = QtGui.QIcon("icons/frame_border.png")
		self.ghost_icon = QtGui.QIcon("icons/ghost.png")
		
		self.init_ui()
		self.disable_buttons()
		
		self.animation_data = None

	def init_ui(self):
		self.setSpacing(0)
		self.setObjectName("verticalLayout_3")
		
		# Widget that shows the frame
		#
		self.view = AnimationPlayer()
		self.view.setMinimumSize(QSize(250, 250))
		
		# Sprite animation controls
		#
		self.tool_bar = QtWidgets.QHBoxLayout()
		
		# Button switches between play and pause icons
		self.play_btn = QtWidgets.QPushButton(self.play_icon, "")
		self.play_btn.clicked.connect(self.toggle_play)
		self.play_btn.setMaximumSize(btn_size)
		self.tool_bar.addWidget(self.play_btn)
		
		self.prev_frame_btn = QtWidgets.QPushButton(self.prev_frame_icon, "")
		self.prev_frame_btn.clicked.connect(self.view.previous_frame)
		self.prev_frame_btn.setMaximumSize(btn_size)
		self.tool_bar.addWidget(self.prev_frame_btn)
		
		self.next_frame_btn = QtWidgets.QPushButton(self.next_frame_icon, "")
		self.next_frame_btn.clicked.connect(self.view.next_frame)
		self.next_frame_btn.setMaximumSize(btn_size)
		self.tool_bar.addWidget(self.next_frame_btn)
		
		# Button switches been loop and back and forth icons
		self.repeat_mode_btn = QtWidgets.QPushButton(self.loop_icon, "")
		self.repeat_mode_btn.clicked.connect(self.toggle_repeat_mode)
		self.repeat_mode_btn.setMaximumSize(btn_size)
		self.tool_bar.addWidget(self.repeat_mode_btn)
		
		self.seperator_A = QtWidgets.QFrame()
		self.seperator_A.setMinimumSize(QSize(20, 0))
		self.seperator_A.setFrameShape(QtWidgets.QFrame.VLine)
		self.seperator_A.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.tool_bar.addWidget(self.seperator_A)
		
		self.toggle_ghost_btn = QtWidgets.QPushButton(self.ghost_icon, "")
		self.toggle_ghost_btn.clicked.connect(self.view.toggle_ghost)
		self.toggle_ghost_btn.setMaximumSize(btn_size)
		self.toggle_ghost_btn.setCheckable(True)
		self.tool_bar.addWidget(self.toggle_ghost_btn)
		
		self.toggle_axis_btn = QtWidgets.QPushButton(self.axis_icon, "")
		self.toggle_axis_btn.clicked.connect(self.view.toggle_axis)
		self.toggle_axis_btn.setMaximumSize(btn_size)
		self.toggle_axis_btn.setCheckable(True)
		self.tool_bar.addWidget(self.toggle_axis_btn)
		
		self.toggle_frame_border_btn = QtWidgets.QPushButton(self.frame_border_icon, "")
		self.toggle_frame_border_btn.clicked.connect(self.view.toggle_frame_border)
		self.toggle_frame_border_btn.setMaximumSize(btn_size)
		self.toggle_frame_border_btn.setCheckable(True)
		self.tool_bar.addWidget(self.toggle_frame_border_btn)
		
		self.seperator_B = QtWidgets.QFrame()
		self.seperator_B.setMinimumSize(QSize(20, 0))
		self.seperator_B.setFrameShape(QtWidgets.QFrame.VLine)
		self.seperator_B.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.tool_bar.addWidget(self.seperator_B)
		
		self.speed_widget = QtWidgets.QSpinBox()
		self.speed_widget.setMinimumSize(QSize(40, btn_size.height()))
		self.speed_widget.setMaximumSize(btn_size)
		self.speed_widget.setMinimum(1)
		self.speed_widget.setMaximum(120)
		self.speed_widget.setValue(30)
		self.speed_widget.valueChanged.connect(self.view.set_sequence_speed)
		self.tool_bar.addWidget(self.speed_widget)
		
		spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.tool_bar.addItem(spacerItem)
		
		#
		# #

		
		# Number of frames, Sprite animation speed
		#
		self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_10.setContentsMargins(6, -1, 6, -1)
		
		self.frame_number_label = QtWidgets.QLabel()
		self.frame_number_label.setMaximumSize(QSize(400, 20))
		self.horizontalLayout_10.addWidget(self.frame_number_label)
		
		spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalLayout_10.addItem(spacerItem1)
		
		self.label_3 = QtWidgets.QLabel()
		self.label_3.setMaximumSize(QSize(400, 20))
		self.horizontalLayout_10.addWidget(self.label_3)
		
		
		self.label_3.setText("Speed")
		#
		# #
		
		self.addLayout(self.tool_bar)
		self.addWidget(self.view)
		self.addLayout(self.horizontalLayout_10)

		
	
	def disable_buttons(self):
		self.play_btn.setEnabled(False)
		self.prev_frame_btn.setEnabled(False)
		self.next_frame_btn.setEnabled(False)
		self.repeat_mode_btn.setEnabled(False)
		self.toggle_axis_btn.setEnabled(False)
		self.toggle_frame_border_btn.setEnabled(False)
		self.toggle_ghost_btn.setEnabled(False)
		self.speed_widget.setEnabled(False)
		
	def enable_buttons(self):
		self.play_btn.setEnabled(True)
		self.prev_frame_btn.setEnabled(True)
		self.next_frame_btn.setEnabled(True)
		self.repeat_mode_btn.setEnabled(True)
		self.toggle_axis_btn.setEnabled(True)
		self.toggle_frame_border_btn.setEnabled(True)
		self.toggle_ghost_btn.setEnabled(True)
		self.speed_widget.setEnabled(True)
	
	def load_animation_data(self, animation_data):
		self.animation_data = animation_data
		self.view.animation_data = animation_data
		self.view.spritesheet = QtGui.QImage(animation_data.spritesheet_path)
		self.animation_data.active_frame_changed.connect(self.reset_view)

		self.renew()

	def reset_view(self):
		self.play_btn.setIcon( self.play_icon )
		self.view.reset()

	def renew(self):
		if self.animation_data is None:
			return

		self.view.update()
		
		if self.animation_data.active_sequence:
			self.enable_buttons()
			self.speed_widget.setValue(self.animation_data.active_sequence.speed)
			
			if len(self.animation_data.active_sequence.frames) == 1:
				self.play_btn.setEnabled(False)
				self.prev_frame_btn.setEnabled(False)
				self.next_frame_btn.setEnabled(False)
				self.repeat_mode_btn.setEnabled(False)
				self.toggle_ghost_btn.setEnabled(False)
				self.speed_widget.setEnabled(False)
			
			elif self.animation_data.active_frame is not None:
				if self.view.state == "PLAY":
					self.prev_frame_btn.setEnabled(False)
					self.next_frame_btn.setEnabled(False)
					
				self.frame_number_label.setText("%s of %s" % (self.animation_data.active_sequence.active_frame_index() + 1, len(self.animation_data.active_sequence.frames)))
				
			else:
				self.disable_buttons()
	
	def toggle_play(self):
		if self.view.state == "STOPPED":
			self.play_btn.setIcon(self.pause_icon)
			self.prev_frame_btn.setEnabled(False)
			self.next_frame_btn.setEnabled(False)
		elif self.view.state == "PLAY":
			self.play_btn.setIcon(self.play_icon)
			self.prev_frame_btn.setEnabled(True)
			self.next_frame_btn.setEnabled(True)
		self.view.toggle_play()
		
	def toggle_repeat_mode(self):
		if self.view.repeat_mode == "LOOP":
			self.repeat_mode_btn.setIcon(self.backandforth_icon)
		elif self.view.repeat_mode == "BACK_AND_FORTH":
			self.repeat_mode_btn.setIcon(self.loop_icon)
		self.view.toggle_repeat_mode()
	
	def toggle_background(self):
		self.view.show_background = self.background_btn.isChecked()


class AnimationPlayer(QtWidgets.QFrame):
	
	animation_data_changed_signal = pyqtSignal()

	def __init__(self, parent=None):
		super(AnimationPlayer, self).__init__()

		self.scale = 1
		self.scale_min = 1
		self.scale_max = 10
		self.scale_inc = .5

		self._current_index = 0

		self.frames_per_second = 30
		self.animation_data = None
		
		self.setParent(parent)
		self.update()
		self.show()
		
		self.state = "STOPPED"
		self.repeat_mode = "LOOP"
		
		#State for back and forth repeat mode
		self.going_forwards = True
		
		#Play timer
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.handle_timer_elapse)
		self.timer.setSingleShot(False)
		
		self.show_axis = False
		self.show_frame_border = False
		self.draw_ghost_frame = False
		
		self.setContextMenuPolicy(Qt.ActionsContextMenu)
		
		toggle_play_action = QtWidgets.QAction("Play", self)
		toggle_play_action.triggered.connect(self.toggle_play)
		self.addAction(toggle_play_action)

		self.setFocusPolicy(Qt.ClickFocus)
		
	def reset(self):
		self.current_index = self.animation_data.active_sequence.active_frame_index()
		self.state = "STOPPED"
		self.timer.stop()
		self.update()
		
	def toggle_play(self):
		
		
		if self.state == "STOPPED":
			self.state = "PLAY"
			#Start timer
			print("Timer started")
			msec_per_frame = (1000 / self.frames_per_second)
			self.timer.start(msec_per_frame)
			
		elif self.state == "PLAY":
			self.state = "STOPPED"
			#Stop timer
			self.timer.stop()

	@property
	def current_index(self):
		return self._current_index

	@current_index.setter
	def current_index(self, index):
		if index is None:
			self._current_index = None
			return

		if index < -1 or index > len(self.animation_data.active_sequence.frames):
			raise Exception("Tried to changed to index that was out of bounds")
		else:
			if index == -1:
				self._current_index = len(self.animation_data.active_sequence.frames) - 1
			elif index == len(self.animation_data.active_sequence.frames):
				self._current_index = 0
			else:
				self._current_index = index


	def toggle_repeat_mode(self):
		if self.repeat_mode == "LOOP":
			self.repeat_mode = "BACK_AND_FORTH"
			
		elif self.repeat_mode == "BACK_AND_FORTH":
			self.repeat_mode = "LOOP"
		
	def set_sequence_speed(self, speed):
		self.frames_per_second = int(speed)
		self.animation_data.active_sequence.speed = speed
		# Loop da loop and OH GOD WHAT IS HAPPENING
		#self.animation_data_changed_signal.emit()

		msec_per_frame = (1000 / self.frames_per_second)
		self.timer.setInterval(msec_per_frame)

	def previous_frame(self):
		self.current_index -= 1
		self.update()

	def next_frame(self):
		self.current_index += 1
		self.update()
		
	def fullscreen(self):
		print("Going fullscreen")
		self.showFullScreen()
	
	def handle_timer_elapse(self):
		#print("Timer trigger")
		if self._current_index is None:
			self._current_index = 0
		
		if self.repeat_mode == "LOOP":
			self.current_index += 1
		elif self.repeat_mode == "BACK_AND_FORTH":
			if self.going_forwards:
				#Get next frame
				if self.current_index == len(self.animation_data.active_sequence.frames) - 1:
					#If reached end, reverse and get previous frame
					self.going_forwards = False
					self.current_index -= 1
				else:
					self.current_index += 1
					
			else: #Going Backwards
				#Get previous frame
				if	self.current_index == 0:
					#If reached beginning, reverse and get next frame.
					self.going_forwards = True
					self.current_index += 1
				else:
					#Else, get previous frame
					self.current_index -= 1

		self.update()
				
	def set_scale(self, scale):
		self.scale = scale
		self.update()
		
	def toggle_axis(self):
		self.show_axis = not self.show_axis
		self.update()
	
	def toggle_frame_border(self):
		self.show_frame_border = not self.show_frame_border
		self.update()
	
	def toggle_ghost(self):
		self.draw_ghost_frame = not self.draw_ghost_frame
		self.update()
	
	""" EVENTS """
	def paintEvent(self, event):
		#logging.debug("Frame viewer updating")

		if self.animation_data is None or self.animation_data.active_sequence is None or len(self.animation_data.active_sequence.frames) <= 0:
			return

		qp = QtGui.QPainter()
		
		qp.begin(self)
		
		qp.scale(self.scale, self.scale)

		sqc = self.animation_data.active_sequence

		if self.current_index is not None:

			frame_current = sqc.frames[self.current_index]
			frame_after = sqc.frames[self.current_index + 1] if (self.current_index != len(sqc.frames) - 1) else sqc.frames[0]
			frame_before = sqc.frames[self.current_index - 1] if (self.current_index != 0) else sqc.frames[-1]

			if self.draw_ghost_frame:
				if self.repeat_mode == "LOOP":
					self.drawFrame(qp, frame_before, 0.2)

				elif self.repeat_mode == "BACK_AND_FORTH":
					if self.going_forwards:
						self.drawFrame(qp, frame_before, 0.2)
					else:
						self.drawFrame(qp, frame_after, 0.2)

			self.drawFrame(qp, frame_current, border=self.show_frame_border)

			
			
		# Draw x, y axis
		if self.show_axis:
			qp.setPen(QtGui.QColor(0, 0, 0, 100))
			qp.drawLine((self.size().width() / 2) / self.scale, 0, (self.size().width() / 2) / self.scale, self.size().height() / self.scale)
			qp.drawLine(0, (self.size().height() / 2) / self.scale, (self.size().width()) / self.scale, (self.size().height() / 2) / self.scale)
		
		
		
			
		qp.end()
	
	def drawFrame(self, painter, frame, opacity=1, border=False):
		painter.setOpacity(opacity)
		sprite = frame.normalized() # Source
		view_rect = QSize(self.rect().width()/self.scale, self.rect().height()/self.scale)
		
		
		# Draw X and Y axis
		# Draw frame
		
		
		target = QPoint(view_rect.width()/2 + frame.shift.x(), view_rect.height()/2 - frame.size().height() + frame.shift.y())
		
		
		
		painter.drawImage(target, self.spritesheet, sprite)
		painter.setOpacity(1)
		
		# Draw border around frame
		if border:	
			painter.setPen(QtGui.QColor(0, 0, 0, 100))
			painter.drawRect(target)

	def mouseDoubleClickEvent(self, *args, **kwargs):
		self.animation_data.active_sequence.set_sole(self.animation_data.active_sequence.frames[self.current_index])
		self.animation_data_changed_signal.emit()
		self.update()

	def wheelEvent(self, event):
		""" Things that happen in relation to the mouse wheel """
		
		# If a spritesheet has not been loaded, do nothing
		if self.animation_data and self.animation_data.active_frame is not None:
			
			if QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
				
				# Next / Previous frame
				if event.angleDelta().y() > 0:
					self.current_index += 1
				else:
					self.current_index -= 1

				self.update()
			
			
			else:
				# Zoom in / Out of the spritesheet
				if event.angleDelta().y() > 0:
					self.set_scale(min(round(self.scale + self.scale_inc, 1), self.scale_max))
				else:
					self.set_scale(max(round(self.scale - self.scale_inc, 1), self.scale_min))
					
					
class FullscreenView(QtWidgets.QMainWindow):
	btn_rect = QRect(0, 0, 30, 30)
	btn_size = QSize(30, 30)

	zoom_max = 20
	zoom_min = 0.1

	def __init__(self, parent):
		super(FullscreenView, self).__init__(parent, flags=None)
		self.init_ui()

		self.animation_data = None
		self.playing = False
		self.zoom = 1

	def init_ui(self):
		#TODO: Shift toolbar to own object
		self.tool_bar = QtWidgets.QHBoxLayout()

		self.play_btn = QtWidgets.QPushButton(self.play_icon, "")
		self.play_btn.clicked.connect(self.toggle_play)
		self.play_btn.setGeometry(btn_rect)
		self.play_btn.setMaximumSize(btn_size)
		self.tool_bar.addWidget(self.play_btn)

		#Frame forward

		#Frame back
		#SEP
		# ZOOM IN
		# ZOOM OUT
		# Show crosshair
		#SEP
		#Add sequence (plus symbol)
		#SEPERATOR
		#Close (red X)

		# self.prev_frame_btn = QtWidgets.QPushButton(self.prev_frame_icon, "")
		# self.prev_frame_btn.clicked.connect(self.view.previous_frame)
		# self.prev_frame_btn.setGeometry(btn_rect)
		# self.prev_frame_btn.setMaximumSize(btn_size)
		# self.tool_bar.addWidget(self.prev_frame_btn)

		self.addWidget(self.tool_bar)


	def load_animation_data(self, data):
		self.animation_data = data

	def toggle_play(self):
		if self.playing is True:
			self.playing = False
			self.timer.stop()
		else:
			self.playing = True
			self.timer.start()



	# def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
	# 	mods = self.keyboardModifiers()
	# 	a_frame = self.animation_data.active_frame
	#
	# 	if mods & Qt.ShiftModifier:
	# 		if e.key() == Qt.Key_Up:
	# 			a_frame.padding.top += 1
	# 		elif e.key() == Qt.Key_Down:
	# 			a_frame.padding.top -= 1
	# 		elif e.key() == Qt.Key_Left:
	# 			a_frame.padding.left += 1
	# 		elif e.key() == Qt.Key_Right:
	# 			a_frame.padding.right -= 1
	#
	# 	else:
	# 		if e.key() == Qt.Key_Right:
	# 			# Frame forward
	# 		elif e.key() == Qt.Key_Left:
	# 			# Frame Back
	#
	# def wheelEvent(self, event):
	# 	""" Zoom in or out """
	#
	# 	# If a spritesheet has not been loaded, do nothing
	# 	#if self.spritesheet_image is None:
	# 	#	return
	#
	# 	# Zoom in / Out of the spritesheet
	# 	if event.angleDelta().y() > 0:
	# 		self.zoom += 1
	# 	else:
	# 		self.zoom -= 1
	# 	self.update()
	# # What do we want?
	#
	# # Full screen sprite view
	# # Zoom func
	# # toolbar in bottom center
	# 	# play, pause, skip frame forward-back, x/y axis show, speed, background set
	# 	# Close window
	#
	# # keyboard shortcuts
	# 	# play, pause, skip forward/back, escape to exit,
	# 	# padding modifier
	#
	# # ANIMATION SEQUENCER
	# 	# Chain together a list of sequences
	# 		# QTreeView -- Drag and drop, double click to change period (or set for length of sequence)
	# 		# Animation timeline
	# 		# How to manage multiple sequences happening at the same time?
	# 	# Two sequences can happen at the same time
	# 	# Speed depends on sequence frame speed
	# 	# Position with arrow keys
	#
	# # https://puu.sh/Dr7KB/d417ae68b9.mp4
	# # 'DISPLAY_WIDTH': screen_info.current_w,
	# # 'DISPLAY_HEIGHT': screen_info.current_h
	# # screen_info = pygame.display.Info()
	#
	# # MS Native res = 304*224