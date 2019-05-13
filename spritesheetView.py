# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QSize, QRect, Qt, pyqtSignal
import logging
import math
from enum import Enum

from animationTypes import AnimationData, AnimationSequence, AnimationFrame

btn_rect = QSize(30, 30)
btn_icon_size = QSize(20, 20)

class ViewerMode(Enum):
	NEW_FRAME = 1
	ALTER_SELECTION = 2
	ZOOM = 3

class SizingMode(Enum):
	TOP_LEFT = 0
	TOP = 1
	TOP_RIGHT = 2
	RIGHT = 3
	BOTTOM_RIGHT = 4
	BOTTOM = 5
	BOTTOM_LEFT = 6
	LEFT = 7
	MOVE_FRAME = 8


class SpritesheetWidget(QtWidgets.QVBoxLayout):
	""" The main container. 
		Holds the tool bar, spritesheet viewer, and spritesheet viewer status bar. """
	
	def __init__(self):
		super(SpritesheetWidget, self).__init__()
		
		self.init_ui()
		self.zoom_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("z"), self.view)
		self.zoom_shortcut.activated.connect(self.manip_toolbar.zoom_btn_clicked)

	def init_ui(self):
		self.setSpacing(0)
		self.setObjectName("verticalLayout_2")
		
		""" Manipulation tools"""
		
		self.manip_toolbar = SpriteSheetToolbar()
		self.manip_toolbar.tool_changed_signal.connect(self.change_mode)
		self.manip_toolbar.new_sequence_signal.connect(self.create_new_sequence)
		self.addLayout(self.manip_toolbar)
		
		""" Spritesheet view"""
		
		self.view = SpritesheetViewer()
		self.view.setMinimumSize(QSize(250, 250))
		self.view.scale_changed_signal.connect(self.update_zoom_label)
		self.addWidget(self.view)
		
		""" Spritesheet location, zoom level """
		
		self.horizontalLayout_B = QtWidgets.QHBoxLayout()
		self.horizontalLayout_B.setContentsMargins(6, -1, 6, -1)
		self.horizontalLayout_B.setSpacing(6)
		self.horizontalLayout_B.setObjectName("horizontalLayout_B")
		
		self.spritesheet_dir_label = QtWidgets.QLabel()
		self.spritesheet_dir_label.setMaximumSize(QSize(400, 20))
		self.horizontalLayout_B.addWidget(self.spritesheet_dir_label)
		
		spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalLayout_B.addItem(spacerItem)
		self.addLayout(self.horizontalLayout_B)
		
		self.zoom_label = QtWidgets.QLabel("100%")
		self.zoom_label.setMaximumSize(QSize(400, 20))
		self.horizontalLayout_B.addWidget(self.zoom_label)

	def change_mode(self, mode):
		if mode == ViewerMode.ALTER_SELECTION:
			self.view.calc_sizing_handles()

		self.view.mode = mode
		self.view.reset_cursor()
		self.view.update()

	def load_animation_data(self, animation_data):
		self.view.load_animation_data(animation_data)
		self.manip_toolbar.enable_buttons()
	
	def renew(self):
		self.view.renew()
	
	def update_zoom_label(self, zoom):
		self.zoom_label.setText(str(int(zoom * 10) * 10) + "%")

	def create_new_sequence(self):
		self.view.animation_data.new_sequence(active=True)
		self.view.animation_data_changed_signal.emit()



class SpriteSheetToolbar(QtWidgets.QHBoxLayout):
	
	tool_changed_signal = pyqtSignal(object)
	new_sequence_signal = pyqtSignal()

	def __init__(self):
		super(SpriteSheetToolbar, self).__init__()
		
		self.init_ui()
		
	def init_ui(self):
		
		self.setContentsMargins(6, 2, 6, 2)
		self.setSpacing(0)
		
		self.rect_select_btn = QtWidgets.QPushButton(QtGui.QIcon("icons/rect_select.png"), "")
		self.rect_select_btn.setMaximumSize(btn_rect)
		self.rect_select_btn.setIconSize(btn_icon_size)
		self.rect_select_btn.setObjectName("button")
		self.rect_select_btn.setCheckable(True)
		self.rect_select_btn.clicked.connect(self.rect_select_btn_clicked)
		self.rect_select_btn.setToolTip("Draw a new frame")
		self.addWidget(self.rect_select_btn)
		
		self.move_btn = QtWidgets.QPushButton(QtGui.QIcon("icons/move.png"), "")
		self.move_btn.setMaximumSize(btn_rect)
		self.move_btn.setIconSize(btn_icon_size)
		self.move_btn.setObjectName("button")
		self.move_btn.setCheckable(True)
		self.move_btn.clicked.connect(self.move_btn_clicked)
		self.move_btn.setToolTip("Alter a frame")
		self.addWidget(self.move_btn)
		
		self.zoom_btn = QtWidgets.QPushButton(QtGui.QIcon("icons/zoom.png"), "")
		self.zoom_btn.setObjectName("button")
		self.zoom_btn.setMaximumSize(btn_rect)
		self.zoom_btn.setIconSize(btn_icon_size)
		self.zoom_btn.setCheckable(True)
		self.zoom_btn.clicked.connect(self.zoom_btn_clicked)
		self.zoom_btn.setToolTip("Zoom in/out")
		self.addWidget(self.zoom_btn)

		self.seperator_A = QtWidgets.QFrame()
		self.seperator_A.setMinimumSize(QSize(20, 0))
		self.seperator_A.setFrameShape(QtWidgets.QFrame.VLine)
		self.seperator_A.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.addWidget(self.seperator_A)

		self.new_sqnc_btn = QtWidgets.QPushButton(QtGui.QIcon("icons/new_sequence.png"), "")
		self.new_sqnc_btn.setMaximumSize(btn_rect)
		self.new_sqnc_btn.setIconSize(btn_icon_size)
		self.new_sqnc_btn.setObjectName("button")
		self.new_sqnc_btn.clicked.connect(self.new_sequence_signal.emit)
		self.new_sqnc_btn.setToolTip("New Sequence")
		self.addWidget(self.new_sqnc_btn)

		spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.addItem(spacerItem)
		
		self.disable_buttons()
	
	def enable_buttons(self):
		self.rect_select_btn.setEnabled(True)
		self.move_btn.setEnabled(True)
		#self.move_select_btn.setEnabled(True)
		self.zoom_btn.setEnabled(True)
		self.new_sqnc_btn.setEnabled(True)
		
	def disable_buttons(self):
		self.rect_select_btn.setEnabled(False)
		self.move_btn.setEnabled(False)
		#self.move_select_btn.setEnabled(False)
		self.zoom_btn.setEnabled(False)
		self.new_sqnc_btn.setEnabled(False)
		
		
	def uncheck_buttons(self):
		self.rect_select_btn.setChecked(False)
		self.move_btn.setChecked(False)
		#self.move_select_btn.setChecked(False)
		self.zoom_btn.setChecked(False)
		
	def rect_select_btn_clicked(self):
		self.uncheck_buttons() # Toggle off all buttons
		self.rect_select_btn.toggle() # Toggle Rectangle select button 
		self.tool_changed_signal.emit(ViewerMode.NEW_FRAME)
				
	def move_btn_clicked(self):
		self.uncheck_buttons() # Toggle off all buttons
		self.move_btn.toggle() # Toggle Rectangle select button
		self.tool_changed_signal.emit(ViewerMode.ALTER_SELECTION)
		
	# def move_select_btn_clicked(self):
	# 	# 	self.uncheck_buttons()
	# 	# 	self.move_select_btn.toggle()
	# 	# 	self.tool_changed_signal.emit(ViewerMode.MOVE_SELECTION)
		
	def zoom_btn_clicked(self):
		self.uncheck_buttons()
		self.zoom_btn.toggle()
		self.tool_changed_signal.emit(ViewerMode.ZOOM)


class SpritesheetViewer(QtWidgets.QFrame):
	
	left_mouse_down = False
	mouse_press_pos = None
	last_mouse_pos = QPoint(0, 0)
	
	spritesheet_image = None
	animation_data = None

	bg_image = None
	bg_tile_num = (120, 108)
	bg_tile_size = 10

	SCALE_DELTA = 1
	SCALE_MAX = 10
	SCALE_MIN = 1
	SCALE_DEFAULT = 1

	BOX_SIZE = 10
	
	isPanning = False
	camera = QPoint(0, 0)
	sheet_margin = QSize(10, 10)

	mode = None
	sizing_handles = None
	sizing_mode = None
	
	scale_changed_signal = pyqtSignal(float)
	animation_data_changed_signal = pyqtSignal()

	sizing_handle_cursors = [
		Qt.SizeFDiagCursor,
		Qt.SizeVerCursor,
		Qt.SizeBDiagCursor,
		Qt.SizeHorCursor,
		Qt.SizeFDiagCursor,
		Qt.SizeVerCursor,
		Qt.SizeBDiagCursor,
		Qt.SizeHorCursor
	]

	move_frame_cursor = Qt.SizeAllCursor


	def __init__(self, parent=None):
		super(SpritesheetViewer, self).__init__()

		self.setParent(parent)
		self.draw_bg_image()
		self.update()
		self.show()

		self.zoom_cursor = QtGui.QCursor(QtGui.QPixmap("icons/zoom.png"))
		self.zoom_in_cursor = QtGui.QCursor(QtGui.QPixmap("icons/zoom_in.png"))
		self.zoom_out_cursor = QtGui.QCursor(QtGui.QPixmap("icons/zoom_out.png"))

		self.scale_label = QtWidgets.QLabel("")

		self.setMouseTracking(True)
		self.setFocusPolicy(Qt.ClickFocus)

		self._scale = self.SCALE_DEFAULT
		
		self.original_frame_positions = []
		
	def load_animation_data(self, animation_data):
		self.animation_data = animation_data
		self.animation_data.active_sequence_changed.connect(self.handle_sequence_signal)
		self.animation_data.active_frame_changed.connect(self.handle_frame_signal)
		self.reset_spritesheet()

	def renew(self):
		if self.animation_data is None:
			return

		self.calc_sizing_handles()
		self.update()
	
	def reset_spritesheet(self):
		self.scale = self.SCALE_DEFAULT
		self.spritesheet_image = QtGui.QImage(self.animation_data.spritesheet_path)
		self.center_sequence()
		self.update()

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, scale):
		# Get coordinates of mouse relative to viewer
		scale = max(round(scale, 1), self.SCALE_MIN)
		scale = min(round(scale, 1), self.SCALE_MAX)

		scale_diff = scale - self._scale

		old_camera_size = self.size() / self.scale
		new_camera_size = self.size() / (self.scale + scale_diff)
		size_ratio = new_camera_size.width() / old_camera_size.width()

		mouse = self.view2sheet(self.last_mouse_pos)
		mouse_ratio_x = (mouse.x() - self.camera.x()) / old_camera_size.width()
		mouse_ratio_y = (mouse.y() - self.camera.y()) / old_camera_size.height()

		camera_x = mouse.x() - (new_camera_size.width() * mouse_ratio_x)
		camera_y = mouse.y() - (new_camera_size.height() * mouse_ratio_y)

		self._scale = scale
		self.camera = QPoint(camera_x, camera_y)


		self.constrain_camera()
		self.calc_sizing_handles()
		self.update()
		self.scale_changed_signal.emit(scale)

		
	def draw_bg_image(self):
		# Prepare an image of background tiles
		self.bg_image = QtGui.QImage(self.bg_tile_num[0] * self.bg_tile_size,
									 self.bg_tile_num[1] * self.bg_tile_size,
									 QtGui.QImage.Format_Grayscale8)
		
		qp = QtGui.QPainter()
		qp.begin(self.bg_image)
		
		for x in range(0, self.bg_tile_num[0]):
			for y in range(0, self.bg_tile_num[1]):
				if ((y + x) % 2) == 1:
					qp.fillRect(x * self.bg_tile_size,
								y *self.bg_tile_size,
								self.bg_tile_size,
								self.bg_tile_size,
								QtGui.QColor(255, 255, 255))
				else:
					qp.fillRect(x * self.bg_tile_size,
								y * self.bg_tile_size,
								self.bg_tile_size,
								self.bg_tile_size,
								QtGui.QColor(200, 200, 200))
	
		qp.end()

	def zoom_in(self):
		self.scale = self.scale + self.SCALE_DELTA

	def zoom_out(self):
		self.scale = self.scale - self.SCALE_DELTA

	def handle_sequence_signal(self):
		self.center_sequence()

	def handle_frame_signal(self):
		self.calc_sizing_handles()


	""" EVENTS """
	def paintEvent(self, event):
		
		qp = QtGui.QPainter()
		
		qp.begin(self)
		qp.setClipRect(0, 0, self.size().width(), self.size().height())

		# BACKGROUND tiles
		if self.bg_image:
			qp.drawImage(0, 0, self.bg_image)


		# SPRITESHEET, cut and scaled
		cutout_size = (math.ceil(self.frameRect().width() / self.scale), math.ceil(self.frameRect().height() / self.scale))
		if self.spritesheet_image:
			ss_cut = self.spritesheet_image.copy(self.camera.x(),
												 self.camera.y(),
												 cutout_size[0],
												 cutout_size[1])
			ss_cut = ss_cut.scaled(cutout_size[0] * self.scale, cutout_size[1] * self.scale)
			qp.drawImage(0, 0, ss_cut)
			
		# SELECTION BOXES around frames of sequence
		if self.animation_data and self.animation_data.active_sequence and self.animation_data.active_sequence.frames:
			self.draw_frames(qp)

					
		#draw MOUSE CROSSHAIR when creating new frames
		if self.mode == ViewerMode.NEW_FRAME:
			if self.last_mouse_pos is not None and self.underMouse():
				self.draw_crosshair(qp)


		qp.end()

	def snap_to_pixels(self, cord):
		return QPoint(cord.x() - cord.x() % self.scale, cord.y() - cord.y() % self.scale)

	def draw_crosshair(self, qp):
		cord = self.snap_to_pixels(self.last_mouse_pos)

		qp.drawLine(cord.x(), 0, cord.x(), self.size().height())
		qp.drawLine(0, cord.y(), self.size().width(), cord.y())

		# Debug: draw dot where cursor actualy is
		qp.drawEllipse(self.last_mouse_pos, 1, 1)

		rCord = self.view2sheet(self.last_mouse_pos)
		qp.drawText(cord.x() + 2, cord.y() + 10, "X: %s Y: %s" % (cord.x(), cord.y()))
		qp.drawText(cord.x() + 2, cord.y() + 20, "rX: %s rY: %s" % (rCord.x(), rCord.y()))

	def draw_frames(self, qp):
		qp.setBackgroundMode(Qt.OpaqueMode)
		black_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
		white_pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
		grey_pen = QtGui.QPen(QtGui.QColor("gray"))

		for sequence in self.animation_data.selected:
			i = 0
			for frame in sequence.frames:
				# Draw frame border


				# REPEAT 1
				pos = self.sheet2view(frame.topLeft())
				size = QSize(round(frame.width() * self.scale), round(frame.height() * self.scale))
				
				qp.setPen(white_pen)
				qp.setBackground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

				#qp.drawText(pos.x(), pos.y() - 2, "POS(%s, %s) SIZE(%s, %s)" % (frame.x(), frame.y(), frame.width(), frame.height()))
				qp.drawText(pos.x() + 1, pos.y() + 12, str(i))
				
				qp.drawText( pos.x() + 1, pos.y() + size.height() + 12,
							 "WIDTH: %s HEIGHT: %s" % (frame.width(), frame.height()) )

				qp.setPen(black_pen)
				qp.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
				
				# Draw frame border
				qp.setBackgroundMode(Qt.TransparentMode)
				qp.drawRect(pos.x(), pos.y(), size.width(), size.height()) # Rect
				qp.setBackgroundMode(Qt.OpaqueMode)


				# Highlight the selected frames
				if self.mode == ViewerMode.ALTER_SELECTION:
					# REPEAT 3
					a_pos = self.sheet2view(frame.topLeft())
					a_size = QSize(round(frame.width() * self.scale), round(frame.height() * self.scale))

					if frame in sequence.selected:
						
						if frame == sequence.active_frame:
							colour = QtGui.QColor(180, 215, 255, 100)
							qp.drawText(a_pos.x(), a_pos.y() - 10, "ACTIVE")
						else:
							colour = QtGui.QColor(255, 255, 0, 100)
							qp.drawText(a_pos.x(), a_pos.y() - 10, "SELECTED")



						qp.fillRect(a_pos.x() + 1, a_pos.y() + 1, a_size.width() - 1, a_size.height() - 1, colour)

				i += 1

		if self.mode == ViewerMode.ALTER_SELECTION:
			a_frame = self.animation_data.active_frame
			
			mods = QtWidgets.QApplication.keyboardModifiers()
			if mods & Qt.ControlModifier:
				shift = self.sheet2view( QPoint( a_frame.x() + a_frame.shift.x(), a_frame.y() + a_frame.shift.y() ) )
				
				circle_radius = 5
				qp.drawEllipse( shift.x() - circle_radius, shift.y() - circle_radius, circle_radius * 2,
								circle_radius * 2 )
				qp.drawLine( shift.x(), shift.y() + 4, shift.x(), shift.y() - 4 )
				qp.drawLine( shift.x() + 4, shift.y(), shift.x() - 4, shift.y() )
			else:
				self.draw_sizing_handles(qp)
				

	def calc_sizing_handles(self):
		if self.animation_data.active_frame is None:
			return

		active_frame = self.animation_data.active_frame

		pos = self.sheet2view(active_frame.topLeft())
		size = active_frame.size() * self.scale

		box_size = self.BOX_SIZE
		self.sizing_handles = [
			QRect(pos.x() - box_size/2, pos.y() - box_size/2, box_size, box_size), # Top Left
			QRect(pos.x() + size.width()/2 - box_size/2, pos.y() - box_size/2, box_size, box_size), # Top
			QRect(pos.x() + size.width() - box_size/2, pos.y() - box_size/2, box_size, box_size), # Top Right
			QRect(pos.x() + size.width() - box_size/2, pos.y() + size.height()/2 - box_size/2, box_size, box_size), # Right
			QRect(pos.x() + size.width() - box_size/2, pos.y() + size.height() - box_size/2, box_size, box_size), # Bottom Right
			QRect(pos.x() + size.width()/2 - box_size/2, pos.y() + size.height() - box_size/2, box_size, box_size), # Bottom
			QRect(pos.x() - box_size/2, pos.y() + size.height() - box_size/2, box_size, box_size), # Bottom Left
			QRect(pos.x() - box_size/2, pos.y() + size.height()/2 - box_size/2, box_size, box_size) # Left
		]

	def draw_sizing_handles(self, qp):
		if self.sizing_handles is None:
			return

		if self.animation_data.active_frame is None or self.animation_data.active_frame not in self.animation_data.active_sequence.selected:
			return

		qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

		for handle in self.sizing_handles:
			qp.drawRect(handle)

		qp.setBrush(QtGui.QBrush())

	def focus_selected(self):
		i = 0
		pos_sum = QPoint(0 ,0)
		for sequence in self.animation_data.selected:
			for frame in sequence.selected:
				pos_sum = frame.center()
				i += 1

		self.center_camera(pos_sum / i)

	def center_sequence(self):
		if self.animation_data.active_frame is not None:
			self.center_camera(self.animation_data.active_frame.center())

	def center_camera(self, point: QPoint) -> None:
		""" Centers the camera on a point on the spritesheet"""
		self.camera = QPoint(point.x() - self.width()/(2*self.scale), point.y() - self.height()/(2*self.scale))
		self.constrain_camera()

	def constrain_camera(self):
		if self.spritesheet_image is None:
			return

		if self.camera.x() < 0:
			self.camera.setX(0)

		if self.camera.x() > self.spritesheet_image.width() - (self.frameRect().width() / self.scale):
			self.camera.setX(self.spritesheet_image.width() - (self.frameRect().width() / self.scale))

		if self.camera.y() < 0:
			self.camera.setY(0)

		if self.camera.y() > self.spritesheet_image.height() - (self.frameRect().height() / self.scale):
			self.camera.setY(self.spritesheet_image.height() - (self.frameRect().height() / self.scale))

	def focus_alter_frame(self, frame=None):
		if frame is None:
			frame = self.animation_data.active_frame
			if frame is None:
				return

		self.center_camera(frame.center())

		self.mode = ViewerMode.ALTER_SELECTION
		self.calc_sizing_handles()
		self.update()

	def wheelEvent(self, event):
		""" Zoom in or out """
		
		# If a spritesheet has not been loaded, do nothing
		if self.spritesheet_image is None:
			return
		
		# Zoom in / Out of the spritesheet
		if event.angleDelta().y() > 0:
			self.zoom_in()
		else:
			self.zoom_out()
				
	def mousePressEvent(self, mouse):
		""" Controls for spritesheet manipulation """
		if self.isPanning is True or self.spritesheet_image is None:
			return

		# Zooming in / out with mouse wheel
		if mouse.button() == Qt.MidButton or mouse.button() == Qt.RightButton:
			self.mouse_press_pos = mouse.pos()
			self.setCursor(Qt.SizeAllCursor)
			self.camera_old = self.camera
			self.isPanning = True
		
		# Selection of spritesheet pixels
		if mouse.button() == Qt.LeftButton:

			self.left_mouse_down = True
			self.mouse_press_pos = mouse.pos()
			
			if self.mode == ViewerMode.ALTER_SELECTION and self.animation_data.active_sequence is not None:
				
				mouse_rel = self.view2sheet(mouse.pos())

				# If sizing handle or move frame selected,
				# set sizing mode and save current frame for its position
				if self.animation_data.active_frame is not None:
					for i in range(0, len(self.sizing_handles)):
						if self.sizing_handles[i].contains(mouse.pos()):
							self.sizing_mode = SizingMode(i)
							self.original_frame_positions = [self.animation_data.active_frame.translated(0, 0)]
							return

					if self.animation_data.active_frame.contains(mouse_rel):
						self.sizing_mode = SizingMode.MOVE_FRAME
						
						self.original_frame_positions = []
						for frame in self.animation_data.selected_frames():
							self.original_frame_positions.append(frame.translated(0, 0))
						return


				# If another frame was selected, set as active frame.
				key_mods = QtGui.QGuiApplication.queryKeyboardModifiers()
				frame = self.animation_data.active_sequence.frame_at_pos(mouse_rel)
				if self.animation_data.active_sequence is None:
					print("No active sequence")


				if frame is None:
					self.animation_data.active_sequence.selected = []
					self.animation_data.active_frame = None
				else:

					if key_mods == Qt.ControlModifier:
						# Select an additional frame
						self.animation_data.active_sequence.select(frame)

					elif key_mods == Qt.ShiftModifier:
						# Select a range of frames
						index_a = self.animation_data.active_sequence.active_frame_index()
						index_b = self.animation_data.active_sequence.frame_index(frame)
						if index_a > index_b:
							index_a, index_b = index_b, index_a
						for i in range(index_a, index_b + 1):
							self.animation_data.active_sequence.select(self.animation_data.active_sequence.frames[i])

					else:
						# Clear selection and add new frame
						self.animation_data.active_sequence.set_sole(frame)

					self.animation_data.active_frame = frame

					#if key_mods
					self.animation_data_changed_signal.emit()
					# Click once to select, click once again to move frame
					self.left_mouse_down = False

				self.update()


			if self.mode == ViewerMode.NEW_FRAME:
				# If no active sequence, createa a new one
				if self.animation_data.active_sequence is None:
					self.animation_data.new_sequence(active=True)
					logging.info("New sequence created")

				# Create a new frame
				cord = self.view2sheet(mouse.pos())
				self.animation_data.active_sequence.add_frame(AnimationFrame(cord))
				self.animation_data_changed_signal.emit()
				logging.info("New frame created at X:%s Y:%s" % (cord.x(), cord.y()))
		
		
		# Zooming in / out with zoom tool
		if self.mode == ViewerMode.ZOOM:
			if mouse.button() == Qt.LeftButton:
				self.setCursor(self.zoom_in_cursor)
			elif mouse.button() == Qt.RightButton:
				self.setCursor(self.zoom_out_cursor)

	def mouseReleaseEvent(self, mouse):
		if self.animation_data is None:
			return


		if mouse.button() == Qt.MidButton or mouse.button() == Qt.RightButton:
			self.isPanning = False
			self.reset_cursor()
			
		# Zooming in / out with zoom tool
		if self.mode == ViewerMode.ZOOM:
			if mouse.button() == Qt.LeftButton:
				self.zoom_in()
				self.reset_cursor()
			elif mouse.button() == Qt.RightButton:
				self.zoom_out()
				self.reset_cursor()

		if mouse.button() == Qt.LeftButton:
			self.left_mouse_down = False
			if (self.mode == ViewerMode.ALTER_SELECTION or self.mode == ViewerMode.NEW_FRAME) and self.animation_data.active_frame is not None:
				self.sizing_mode = None
				self.animation_data.active_frame.normalize()

				frame_start = self.view2sheet(self.mouse_press_pos)
				frame_end = self.view2sheet(mouse)

				self.update()

		#Delete active frame if size is zero
		if self.animation_data.active_frame is not None:
			frame = self.animation_data.active_frame
			if frame.width() == 0 or frame.height() == 0:
				del self.animation_data.active_frame
				self.animation_data_changed_signal.emit()

	def mouseMoveEvent(self, mouse):
		self.last_mouse_pos = mouse.pos()

		if self.isPanning:
			# Move spritesheet frame according to mouse displacement
			mouse_pos_change = (mouse.pos() - self.mouse_press_pos) / self.scale

			self.camera = self.camera_old - mouse_pos_change

			self.constrain_camera()
			self.calc_sizing_handles()

		# Creating a new frame
		if self.mode == ViewerMode.NEW_FRAME:
			if self.left_mouse_down:
				# Adjust size of new frame selection
				clicked_pos = self.view2sheet(self.mouse_press_pos)
				mouse_pos = self.view2sheet(mouse.pos())

				frame = self.animation_data.active_frame
				frame.setTopLeft(clicked_pos)
				frame.setBottomRight(QPoint(mouse_pos.x()-1, mouse_pos.y()-1))

				self.animation_data_changed_signal.emit()

		# Altering an existing frame
		elif self.mode == ViewerMode.ALTER_SELECTION:
			if self.animation_data.active_frame is not None and self.animation_data.active_frame in self.animation_data.active_sequence.selected:

				a_frame = self.animation_data.active_frame
				mouse_rel = self.view2sheet(mouse.pos())

				if self.sizing_mode is None:
					# self.sizing_handles -> contains 8 rects
					self.setCursor(Qt.ArrowCursor)

					if a_frame.contains(mouse_rel):
						self.setCursor(self.move_frame_cursor)

					for i in range(0, len(self.sizing_handles)):
						if self.sizing_handles[i].contains(mouse.pos()):
							self.setCursor(self.sizing_handle_cursors[i])

				elif self.left_mouse_down:
					# Position = original + (mouse_click_pos - mouse_current_pos)
					delta_mouse = self.view2sheet(self.mouse_press_pos) - self.view2sheet(mouse.pos())
					if self.sizing_mode is SizingMode.MOVE_FRAME:
						selected_frames = self.animation_data.selected_frames()
						i = 0
						for frame in self.original_frame_positions:
							selected_frames[i].moveTo(frame.topLeft() - delta_mouse)
							i += 1
					elif self.sizing_mode is SizingMode.TOP_LEFT:
						a_frame.setTopLeft(self.original_frame.topLeft() - delta_mouse)
					elif self.sizing_mode is SizingMode.TOP:
						a_frame.setTop(self.original_frame.top() - delta_mouse.y())
					elif self.sizing_mode is SizingMode.TOP_RIGHT:
						a_frame.setTopRight(self.original_frame.topRight() - delta_mouse)
					elif self.sizing_mode is SizingMode.RIGHT:
						a_frame.setRight(self.original_frame.right() - delta_mouse.x())
					elif self.sizing_mode is SizingMode.BOTTOM_RIGHT:
						a_frame.setBottomRight(self.original_frame.bottomRight() - delta_mouse)
					elif self.sizing_mode is SizingMode.BOTTOM:
						a_frame.setBottom(self.original_frame.bottom() - delta_mouse.y())
					elif self.sizing_mode is SizingMode.BOTTOM_LEFT:
						a_frame.setBottomLeft(self.original_frame.bottomLeft() - delta_mouse)
					elif self.sizing_mode is SizingMode.LEFT:
						a_frame.setLeft(self.original_frame.left() - delta_mouse.x())

					self.animation_data_changed_signal.emit()
					self.calc_sizing_handles()


		self.update()

	def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
		print("keypress")
		
		a_frame = self.animation_data.active_frame
		self.setFocus()
		# Theres got to be a better way to do this
		
		
		modifiers = QtWidgets.QApplication.keyboardModifiers()
		if modifiers & Qt.ControlModifier:
			if e.key() == Qt.Key_Up:
				a_frame.shift.setY(a_frame.shift.y() - 1)
			if e.key() == Qt.Key_Down:
				a_frame.shift.setY(a_frame.shift.y() + 1)
			if e.key() == Qt.Key_Left:
				a_frame.shift.setX(a_frame.shift.x() - 1)
			if e.key() == Qt.Key_Right:
				a_frame.shift.setX(a_frame.shift.x() + 1)
				
		else:
			# Move all frames selected
			for sequence in self.animation_data.selected:
				for frame in sequence.selected:
					if e.key() == Qt.Key_Up:
						frame.translate( 0, -1 )
					elif e.key() == Qt.Key_Down:
						frame.translate(0, 1)
					elif e.key() == Qt.Key_Left:
						frame.translate(-1, 0)
					elif e.key() == Qt.Key_Right:
						frame.translate(1, 0)
					elif e.key() == Qt.Key_F:
						self.focus_selected()
						
					self.calc_sizing_handles()

		self.update()
		self.animation_data_changed_signal.emit()

	def enterEvent(self, event):
		self.update()
		
	def leaveEvent(self, event):
		self.update()
	
	def reset_cursor(self):
		if self.mode == ViewerMode.NEW_FRAME:
			self.setCursor(Qt.BlankCursor)
		elif self.mode == ViewerMode.ALTER_SELECTION:
			self.setCursor(Qt.ArrowCursor)
		elif self.mode == ViewerMode.ZOOM:
			self.setCursor(self.zoom_cursor)
		else:
			self.setCursor(Qt.ArrowCursor)

	def view2sheet(self, cord):
		#Get mouse position relative to the spritesheet
		return QPoint(math.floor(cord.x() / self.scale) + self.camera.x(), math.floor(cord.y() / self.scale) + self.camera.y())

	def sheet2view(self, cord):
		#Get spritesheet position relative to mouse position
		return QPoint(math.floor((cord.x() - self.camera.x()) * self.scale), math.floor((cord.y() - self.camera.y()) * self.scale))
