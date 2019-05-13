from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QSize, QRect, pyqtSignal, QObject
import logging
from enum import Enum

class AnimationEvent(Enum):
	NEW_SEQUENCE = 1
	SEQUENCE_DELETED = 2
	NEW_FRAME = 3
	FRAME_DELETED = 4
	FRAME_ALTERED = 5
	ACTIVE_SEQUENCE_CHANGED = 6
	ACTIVE_FRAME_CHANGED = 7
	FRAME_SELECTION_CHANGED = 8
	SEQUENCE_SELECTION_CHANGED = 9

class AnimationData(QObject):

	active_sequence_changed = pyqtSignal()
	active_frame_changed = pyqtSignal()
	data_changed = pyqtSignal(object)

	def __init__(self, spritesheet_fname):
		QObject.__init__(self)
		self.spritesheet_path = spritesheet_fname
		self.spritesheet_fname = self.spritesheet_path.split("/")[-1][:-4]
		self.sequences = []
		self._active_sequence = None
		self.selected = []

	def new_sequence(self, name=None, active=False):
		if name is None:
			name = "Sequence_" + str(len(self.sequences))

		sequence = AnimationSequence(name=name)
		sequence.active_frame_changed.connect(self.active_frame_changed.emit)

		if active:
			self.active_sequence = sequence
			self.selected = [sequence]

		self.sequences.append(sequence)
		self.data_changed.emit(AnimationEvent.NEW_SEQUENCE)

	def get_sequence(self, name):
		for sequence in self.sequences:
			if sequence.name == name:
				return sequence
		return None

	def del_sequence(self, sequence):
		if sequence == self.active_sequence:
			self.active_sequence = None
		self.sequences.remove(sequence)
		self.data_changed.emit(AnimationEvent.SEQUENCE_DELETED)

	@property
	def active_sequence(self):
		return self._active_sequence

	@active_sequence.setter
	def active_sequence(self, sequence):
		self._active_sequence = sequence
		self.active_sequence_changed.emit()
		self.data_changed.emit(AnimationEvent.ACTIVE_SEQUENCE_CHANGED)
		print("active sequence changed")

	@active_sequence.deleter
	def active_sequence(self):
		for frame in self._active_sequence.frames:
			del frame
		self.sequences.remove(self._active_sequence)
		self.selected.remove(self._active_sequence)
		self._active_sequence = None
		self.data_changed.emit(AnimationEvent.SEQUENCE_DELETED)
		self.data_changed.emit(AnimationEvent.SEQUENCE_SELECTION_CHANGED)
		self.data_changed.emit(AnimationEvent.ACTIVE_SEQUENCE_CHANGED)

	@property
	def active_frame(self):
		if self.active_sequence is not None:
			return self.active_sequence.active_frame
		else:
			return None

	@active_frame.setter
	def active_frame(self, frame):
		self.active_sequence.active_frame = frame

	@active_frame.deleter
	def active_frame(self):
		if self.active_sequence.active_frame is not None:
			self.active_sequence.remove_frame(self.active_frame)

	def select(self, name):
		seq = self.get_sequence(name)
		if seq not in self.selected:
			self.selected.append(seq)
			self.data_changed.emit(AnimationEvent.SEQUENCE_SELECTION_CHANGED)
	
	def selected_frames(self):
		frames = []
		for sequence in self.selected:
			for frame in sequence.selected:
				frames.append(frame)
				
		return frames
	
	def deselect(self, name):
		seq = self.get_sequence(name)
		if seq in self.selected:
			self.selected.remove(seq)
			self.data_changed.emit(AnimationEvent.SEQUENCE_SELECTION_CHANGED)

	def select_all(self):
		self.selected = self.sequences
		self.data_changed.emit(AnimationEvent.SEQUENCE_SELECTION_CHANGED)

	def deselect_all(self):
		self.selected = []
		self.active_sequence = None
		self.data_changed.emit(AnimationEvent.SEQUENCE_SELECTION_CHANGED)


	def export_data(self):
		sequence_data = []
		for sequence in self.sequences:
			frame_data = []
			for frame in sequence.frames:
				frame_data.append({
					"pos": (frame.topLeft().x(), frame.topLeft().y()),
					"size": (frame.size().width(), frame.size().height()),
					"shift": (frame.shift.x(), frame.shift.y())
				})
			sequence_data.append({
				"name": sequence.name,
				"speed": sequence.speed,
				"frames": frame_data
			})

		output = {
			"fpath": self.spritesheet_path,
			"sequences": sequence_data
		}

		return output

	@staticmethod
	def import_data(data):
		animation_data = AnimationData(data['fpath'])
		for sequence in data['sequences']:
			animation_data.new_sequence(sequence['name'], active=True)
			animation_data.active_sequence.speed = sequence['speed']
			for frame in sequence['frames']:
				animation_data.active_sequence.add_frame(
					AnimationFrame(QPoint(frame['pos'][0], frame['pos'][1]),
								   QSize(frame['size'][0], frame['size'][1]),
								   QPoint(frame['shift'][0], frame['shift'][1])))
			animation_data.active_sequence.active_frame_changed.connect(animation_data.active_frame_changed.emit)

		return animation_data


class AnimationSequence(QObject):

	active_frame_changed = pyqtSignal()

	def __init__(self, name):
		QObject.__init__(self)
		self.name = name
		self.frames = []
		self._active_frame = None
		self.selected = []
		self.speed = 20 #Frames per second

	@property
	def active_frame(self):
		return self._active_frame

	@active_frame.setter
	def active_frame(self, frame):
		if frame is None:
			self._active_frame = None
			self.active_frame_changed.emit()
			return

		for s_frame in self.frames:
			if s_frame == frame:
				self._active_frame = frame
				self.active_frame_changed.emit()
				return

		raise Exception('active frame assignment failed. Frame was not found in sequence .' % self.active_sequence.name)


	def select(self, arg):
		# TODO finish exception handling
		if type(arg) == AnimationFrame:
			if arg not in self.frames:
				raise Exception("Tried to select frame that was not in the sequence")

			if arg not in self.selected:
				self.selected.append(arg)
				self.active_frame = arg

		elif type(arg) == int:
			try:
				if self.frames[arg] not in self.selected:
					self.selected.append(self.frames[arg])
					self.active_frame = self.frames[arg]
			except:
				pass

	def deselect(self, arg):
		if type(arg) == AnimationFrame:
			if arg in self.selected:
				self.selected.remove(arg)
				if arg == self.active_frame:
					self.active_frame = None
		elif type(arg) == int:
			try:
				if self.frames[arg] in self.selected:
					self.selected.remove(self.frames[arg])
			except:
				pass

	def select_all(self):
		self.selected = self.frames

	def deselect_all(self):
		self.selected = []

	def add_frame(self, frame):
		self.frames.append(frame)
		self.active_frame = frame
		self.selected = [frame]
		
	def remove_frame(self, frame):
		self.frames.remove(frame)

		if frame in self.selected:
			self.selected.remove(frame)

		if frame == self.active_frame:
			self.active_frame = None

	def frame_at_pos(self, pos):
		for frame in self.frames:
			if frame.contains(pos):
				return frame

		return None

	def set_sole(self, frame):
		if frame in self.frames:
			self.active_frame = frame
			self.selected = [frame]

	def get_frame_after(self, index):
		if len(self.frames) > index + 1:
			return None
		else:
			return self.frames[index + 1]



	def get_frame_before(self, index):
		if index == 0:
			return None
		else:
			return self.frames[index + 1]

	def next_frame(self):
		# Sets the active frame to frame after the current active frame
		if self.active_frame is None:
			if len(self.frames) > 0:
				self.active_frame = self.frames[0]
			else:
				self.active_frame = None

		else:
			active_frame_index = self.frames.index(self.active_frame)
			if active_frame_index == len(self.frames) - 1:
				self.active_frame = self.frames[0]
			else:
				self.active_frame = self.frames[active_frame_index + 1]
			
	def prev_frame(self):
		if self.active_frame is None:
			if len(self.frames) > 0:
				self.active_frame = self.frames[0]
			else:
				self.active_frame = None

		else:
			# Sets the active frame to frame before the current active frame
			active_frame_index = self.frames.index(self.active_frame)
			if active_frame_index == 0:
				self.active_frame = self.frames[len(self.frames) - 1]
			else:
				self.active_frame = self.frames[active_frame_index - 1]




	# def get_next_frame(self):
	# 	if self.active_frame is None:
	# 		if len(self.frames) > 0:
	# 			return self.frames[0]
	# 		else:
	# 			return None
	#
	# 	else:
	# 		active_frame_index = self.frames.index(self.active_frame)
	# 		if active_frame_index == len(self.frames) - 1:
	# 			return self.frames[0]
	# 		else:
	# 			return self.frames[active_frame_index + 1]
	#
	# def get_previous_frame(self):
	# 	if self.active_frame is None:
	# 		if len(self.frames) > 0:
	# 			return self.frames[0]
	# 		else:
	# 			return None

		# else:
		# 	active_frame_index = self.frames.index(self.active_frame)
		# 	if active_frame_index == 0:
		# 		return self.frames[len(self.frames) - 1]
		# 	else:
		# 		return self.frames[active_frame_index - 1]

	def frame_index(self, frame):
		try:
			return self.frames.index(frame)
		except:
			return None

	def active_frame_index(self):
		if self._active_frame is not None:
			return self.frames.index(self._active_frame)
		else:
			return None


	
class AnimationFrame(QRect):
	def __init__(self, pos, size=QSize(0, 0), shift=None):
		QRect.__init__(self, pos, size)
		if shift is None:
			self.shift = QPoint(0,0)
		else:
			self.shift = shift
	
	def normalize(self):
		if self.width() < 0:
			left = self.left() - 1
			self.setLeft(self.right() + 1)
			self.setRight(left)

		if self.height() < 0:
			top = self.top() - 1
			self.setTop(self.bottom() + 1)
			self.setBottom(top)
			
	# def with_shift(self):
	# 	return QRect( self.left() - self.padding.left,
	# 				self.top() - self.padding.top,
	# 				self.width() + self.padding.left + self.padding.right,
	# 				self.height() + self.padding.top + self.padding.bottom )
