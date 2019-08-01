import sys, os
from collections import deque, Counter
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import re
import time
import numpy as np

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.initUI()

	def initUI(self):

		# Init class objects
		self.txt = TextFinder(self)

		self.mainMenu = self.menuBar()
		self.rsearch = QWidget()
		self.setCentralWidget(self.rsearch)

		self.setWindowTitle('Regex Search')
		self.resize(800,500)

		self.tabTextSearchUI()
		self.rsearch.show()

	def closeEvent(self, *args):
		pass

	def tabTextSearchUI(self):

		glayout = QGridLayout()
		hlayout = QHBoxLayout()
		hlayout2 = QHBoxLayout()
		splitter = QSplitter()
		vsplitter = QSplitter(Qt.Vertical)
		splitter2 = QSplitter()

		hlayout2.addWidget(self.txt.searchLabel)
		hlayout2.addWidget(self.txt.lineEdit)
		hlayout2.addWidget(self.txt.replaceLabel)
		hlayout2.addWidget(self.txt.replaceLineEdit)
		hlayout2.addWidget(self.txt.replaceLabel2)
		hlayout2.addWidget(self.txt.replaceLineEdit2)
		hlayout2.addWidget(self.txt.splitLabel)
		hlayout2.addWidget(self.txt.splitLineEdit)
		glayout.addLayout(hlayout2, 0, 0)
		splitter.addWidget(self.txt.textEdit)
		splitter.addWidget(self.txt.textReplace)
		splitter.addWidget(self.txt.textSplit)
		vsplitter.addWidget(self.txt.textMatches)
		vsplitter.addWidget(self.txt.textReplace2)
		vsplitter.addWidget(self.txt.textSplit2)
		vsplitter.addWidget(splitter)
		vsplitter.addWidget(self.txt.textCaptures)
		splitter2.addWidget(splitter)
		splitter2.addWidget(vsplitter)
		glayout.addWidget(splitter2, 1, 0)
		glayout.addWidget(self.txt.optionMenu, 1, 3)
		glayout.setRowStretch(1, 8)
		glayout.setColumnStretch(0, 8)
		glayout.addLayout(hlayout, 10, 0)
		hlayout.addWidget(self.txt.captureLabel)
		hlayout.addWidget(self.txt.matchLabel)
		hlayout.addWidget(self.txt.subLabel)
		hlayout.addWidget(self.txt.modeLabel)

		self.txt.textMatches.hide()
		self.txt.textMatches.hide()
		self.txt.textCaptures.hide()
		self.txt.replaceLineEdit.hide()
		self.txt.replaceLineEdit2.hide()
		self.txt.splitLineEdit.hide()
		self.txt.textReplace.hide()
		self.txt.textReplace2.hide()
		self.txt.textSplit.hide()
		self.txt.textSplit2.hide()
		self.txt.subLabel.hide()
		self.txt.splitLabel.hide()
		self.txt.replaceLabel.hide()
		self.txt.replaceLabel2.hide()
		#self.txt.optionMenu.hide()
		
		self.rsearch.setLayout(glayout)

		self.showSearchMenu()

	def showSearchMenu(self):

		mainMenu = self.menuBar()
		mainMenu.clear()
		fileMenu = mainMenu.addMenu('File')
		#editMenu = mainMenu.addMenu('Edit')
		viewMenu = mainMenu.addMenu('View')
		#searchMenu = mainMenu.addMenu('Search')
		toolsMenu = mainMenu.addMenu('Tools')
		#helpMenu = mainMenu.addMenu('Help')

		viewMatch = QAction('View Matches', self)
		viewMatch.triggered.connect(self.txt.viewMatches)
		viewMenu.addAction(viewMatch)

		viewCapture = QAction('View Captures', self)
		viewCapture.triggered.connect(self.txt.viewCaptures)
		viewMenu.addAction(viewCapture)

		'''
		viewDoc = QAction('Toggle Search View', self)
		viewDoc.triggered.connect(self.hideDoc)
		viewMenu.addAction(viewDoc)

		viewReplace = QAction('Toggle Replace View', self)
		viewReplace.triggered.connect(self.hideReplace)
		viewMenu.addAction(viewReplace)

		viewSplit = QAction('Toggle Split View', self)
		viewSplit.triggered.connect(self.hideSplit)
		viewMenu.addAction(viewSplit)
		'''
		viewOptionMenu = QAction('Toggle Options', self)
		viewOptionMenu.triggered.connect(self.txt.viewOptions)
		viewMenu.addAction(viewOptionMenu)

		openFile = QAction(QIcon('open.png'), 'Open', self)
		openFile.setShortcut('Ctrl+O')
		openFile.setStatusTip('Open new File')
		openFile.triggered.connect(self.txt.loadTextFile)
		fileMenu.addAction(openFile)

		exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
		exitButton.setShortcut('Ctrl+Q')
		exitButton.setStatusTip('Exit application')
		exitButton.triggered.connect(self.close)
		fileMenu.addAction(exitButton)

	def makeWidget(self, name, obj):
		setattr(self, name, obj)
		return obj

	def makeQt(self, obj, *args, **attrs):
		bound = obj(','.join(args))
		for k, v in attrs.items():
			getattr(bound, "add%s%s" % (k[0].upper(), k[1:]))(v)
		return bound

	def saveFile(self):
		fname = QFileDialog.getSaveFileName(self, 'Save File')
		data = self.textEdit.toPlainText()

		file = open(fname[0], 'w')
		file.write(data)
		file.close()

	def hideDoc(self):
		if self.txt.textEdit.isVisible():
			self.txt.textEdit.hide()
		else:
			self.txt.textEdit.show()

	def hideReplace(self):
		if self.txt.textReplace2.isVisible():
			self.txt.textReplace2.hide()
			self.txt.replaceLabel.hide()
			self.txt.replaceLineEdit.hide()
			self.txt.replaceLineEdit2.hide()
		else:
			self.txt.textReplace.show()
			self.txt.textReplace2.show()
			self.txt.replaceLabel.show()
			self.txt.replaceLineEdit.show()
			self.txt.replaceLineEdit2.show()

	def hideSplit(self):
		if self.txt.textSplit2.isVisible():
			self.txt.textSplit2.hide()
			self.txt.splitLineEdit.hide()
			self.txt.splitLabel.hide()
		else:
			self.txt.textSplit2.show()
			self.txt.splitLineEdit.show()
			self.txt.splitLabel.show()


class TextFinder(QWidget):
	def __init__(self, parent):
		super(TextFinder, self).__init__(parent)

		font = QFont()
		font.setPointSize(11)

		te = self.makeWidget('te', QTextEdit)
		pte = self.makeWidget('pte', QPlainTextEdit)
		le = self.makeWidget('le', QLineEdit)
		lbl = self.makeWidget('lbl', QLabel)
		
		self.textEdit = self.makeQt(te, font=font)
		self.document = self.textEdit.document()
		self.textMatches = self.makeQt(te, font=font)
		self.textCaptures = self.makeQt(pte, font=font)
		self.textReplace = self.makeQt(pte, font=font)
		self.textReplace2 = self.makeQt(pte, font=font)
		self.textSplit = self.makeQt(pte, font=font)
		self.textSplit2 = self.makeQt(pte, font=font)
		self.lineEdit = self.makeQt(le)
		self.replaceLineEdit = self.makeQt(le)
		self.replaceLineEdit2 = self.makeQt(le)
		self.splitLineEdit = self.makeQt(le)
		self.searchLabel = self.makeQt(lbl, text='Search')
		self.replaceLabel = self.makeQt(lbl, text='Replace')
		self.replaceLabel2 = self.makeQt(lbl, text='Replace2')
		self.splitLabel = self.makeQt(lbl, text='Split')
		self.captureLabel = self.makeQt(lbl)
		self.matchLabel = self.makeQt(lbl)
		self.modeLabel = self.makeQt(lbl, text='Search View')
		self.subLabel = self.makeQt(lbl)

		self.textReplace2.selectionChanged.connect(self.applyReplace)
		self.lineEdit.textChanged.connect(self.textMatches.clear)
		self.lineEdit.textChanged.connect(self.textCaptures.clear)
		self.lineEdit.textChanged.connect(self.updateInput)
		self.lineEdit.textChanged.connect(self.applyHighlight)
		self.replaceLineEdit.textChanged.connect(self.applyReplace)
		self.replaceLineEdit2.textChanged.connect(self.applyReplace)
		self.splitLineEdit.textChanged.connect(self.applySplit)

		self.createOptionMenu()

		self.lineEdit.setFocus()

	def makeWidget(self, name, obj):
		setattr(self, name, obj)
		return obj

	def makeQt(self, obj, *args, **attrs):
		bound = obj(','.join(args))
		for k, v in attrs.items():
			getattr(bound, "set%s%s" % (k[0].upper(), k[1:]))(v)
		return bound

	def findIter(self, pat, it):
		mp = [i.group() for i in pat.finditer(it.toPlainText())]
		return mp

	def updateInput(self, text):
		self.inputData = text

	def applyHighlight(self):
		
		# Used for speed testing purposes
		start = time.time()
		
		document = self.textEdit.document()
		matchDoc = self.textMatches.document()
		cur = self.textEdit.textCursor()

		cursor = QTextCursor(document)
		cursor2 = QTextCursor(matchDoc)
		hlCursor = QTextCursor(cur)
		hlCursor2 = QTextCursor(document)
		plainFormat = QTextCharFormat(hlCursor.charFormat())
		colorFormat = QTextCharFormat(plainFormat)
		colorFormat2 = QTextCharFormat(plainFormat)
		colorFormat3 = QTextCharFormat(plainFormat)
		colorFormat4 = QTextCharFormat(plainFormat)
		colorFormat5 = QTextCharFormat(plainFormat)

		# Green
		colorFormat.setBackground(QColor(0, 255, 0, 127))
		# Blue
		colorFormat2.setBackground(QColor(0, 0, 255, 127))
		# Violet
		colorFormat3.setBackground(QColor(148, 0, 211, 127))
		# Orange
		colorFormat4.setBackground(QColor(255, 127, 0, 127))
		# Yellow
		colorFormat5.setBackground(QColor(0, 0, 255, 127))

		# Undo previous text highlights/modifications to allow update
		#document.undo()
	
		# Avoid escape errors
		pattern = r'{}'.format(self.inputData).replace(
			'\\', r'\\').replace(
			r'\\w', r'\w').replace(
			r'\\W', r'\W').replace(
			r'\\d', r'\d').replace(
			r'\\D', r'\D').replace(
			r'\\b', r'\b').replace(
			r'\\B', r'\B').replace(
			r'\\s', r'\s').replace(
			r'\\S', r'\S')
		
		pat = re.compile('', flags=self.SEARCH_FLAGS)
		try:
			pat = re.compile(self.inputData, flags=self.SEARCH_FLAGS)
		except Exception:
			pass

		match_list = deque()
		rx = QRegularExpression(self.lineEdit.text())

		extraSelections = []

		cursor.beginEditBlock()
		# Iterate over the document
		for i in pat.finditer(document.toPlainText()):

			# Add current match to list
			match_list.append(i)

			# Select text from the beginning to the end of current match
			hlCursor.setPosition(i.start(), QTextCursor.MoveAnchor)
			hlCursor.setPosition(i.end(), QTextCursor.KeepAnchor)
			extra = QTextEdit.ExtraSelection()
			extra.format.setBackground(QColor(0, 255, 0, 127))
			extra.cursor = hlCursor
			extraSelections.append(extra)

			# Change highlight color depending on capture group number
			# if capture group exists
			try:
				hlCursor.setPosition(i.start(1), QTextCursor.MoveAnchor)
				hlCursor.setPosition(i.end(1), QTextCursor.KeepAnchor)
				extra = QTextEdit.ExtraSelection()
				extra.format.setBackground(QColor(0, 0, 255, 127))
				extra.cursor = hlCursor
				extraSelections.append(extra)
			except IndexError:
				pass

			try:
				hlCursor.setPosition(i.start(2), QTextCursor.MoveAnchor)
				hlCursor.setPosition(i.end(2), QTextCursor.KeepAnchor)
				extra = QTextEdit.ExtraSelection()
				extra.format.setBackground(QColor(148, 0, 211, 127))
				extra.cursor = hlCursor
				extraSelections.append(extra)
			except IndexError:
				pass

			try:
				hlCursor.setPosition(i.start(3), QTextCursor.MoveAnchor)
				hlCursor.setPosition(i.end(3), QTextCursor.KeepAnchor)
				extra = QTextEdit.ExtraSelection()
				extra.format.setBackground(QColor(255, 127, 0, 127))
				extra.cursor = hlCursor
				extraSelections.append(extra)
			except IndexError:
				pass

			try:
				hlCursor.setPosition(i.start(4), QTextCursor.MoveAnchor)
				hlCursor.setPosition(i.end(4), QTextCursor.KeepAnchor)
				extra = QTextEdit.ExtraSelection()
				extra.format.setBackground(QColor(0, 0, 255, 127))
				extra.cursor = hlCursor
				extraSelections.append(extra)
			except IndexError:
				pass

		hlCursor.setPosition(QTextCursor.Start)
		self.textEdit.setExtraSelections(extraSelections)

		# End highlighting block
		cursor.endEditBlock()
		

		# Append a list of all matched items in search to be displayed
		# in match view		
		for i, m in enumerate(match_list):
			if i and self.inputData:
				self.textMatches.append('{}. {}'.format(i, m.group()))
			else:
				pass

		# Append a list of all captured groups to be displayed in
		# capture view
		for group in range(pat.groups):
			self.textCaptures.appendPlainText('\nCapture Group {}:\n'.format(group))
			for j, match in enumerate(match_list):
				self.textCaptures.appendPlainText('  {}. {}'.format(j, match))

		# Create a counter label at the bottom of the window
		# displaying total matches
		if self.lineEdit.text() == '':
			self.matchLabel.setText((str('Matches: {}'.format(0))))
		else:
			self.matchLabel.setText((str('Matches: {}'.format(len(match_list)))))

		# Create a label displaying capture count
		self.captureLabel.setText(
			str('Captures: {}'.format(pat.groups)))

		# For speed testing purposes
		end = time.time()
		print(end - start)

	# Replace text function
	def applyReplace(self):
		
		# For speed testing
		start = time.time()
		
		document = self.textEdit.document()
		document2 = self.textReplace2.document()
		input1 = self.replaceLineEdit.text()
		input2 = self.replaceLineEdit2.text()

		# Avoid escape errors
		pattern = r'{}'.format(input1).replace(
			'\\', r'\\').replace(
			r'\\w', r'\w').replace(
			r'\\W', r'\W').replace(
			r'\\d', r'\d').replace(
			r'\\D', r'\D').replace(
			r'\\b', r'\b').replace(
			r'\\B', r'\B').replace(
			r'\\s', r'\s').replace(
			r'\\S', r'\S')

		pattern2 = r'{}'.format(input2).replace(
			'\\', r'\\').replace(
			r'\\w', r'\w').replace(
			r'\\W', r'\W').replace(
			r'\\d', r'\d').replace(
			r'\\D', r'\D').replace(
			r'\\b', r'\b').replace(
			r'\\B', r'\B').replace(
			r'\\s', r'\s').replace(
			r'\\S', r'\S')
		
		pat = re.compile('', flags=self.SEARCH_FLAGS)
		pat2 = re.compile('', flags=self.SEARCH_FLAGS)
			
		pat = re.compile(pattern, flags=self.SEARCH_FLAGS)
		pat2 = re.compile(pattern2, flags=self.SEARCH_FLAGS)

		matches = []
		match_list = []

		rp = pat.subn(input2, document.toPlainText())
		self.subLabel.setText('{} Substitutions'.format(rp[1]))
		self.textReplace2.setPlainText(rp[0])

		# For testing
		end = time.time()
		print(end - start)

	# Split text function
	def applySplit(self):
		document = self.textEdit.document()
		document2 = self.textSplit2.document()
		input1 = self.splitLineEdit.text()
		
		# Avoid escape errors
		pattern = r'{}'.format(input1).replace(
			'\\', r'\\').replace(
			r'\\w', r'\w').replace(
			r'\\W', r'\W').replace(
			r'\\d', r'\d').replace(
			r'\\D', r'\D').replace(
			r'\\b', r'\b').replace(
			r'\\B', r'\B').replace(
			r'\\s', r'\s').replace(
			r'\\S', r'\S')

			
		pat = re.compile(pattern, flags=self.SEARCH_FLAGS)

		# Avoid regex exceptions such as no input, bad input
		try:
			rp = pat.split(document.toPlainText())
			try:
				re.sub(self.replaceLineEdit, self.replaceLineEdit2, str(rp))
			except TypeError:
				pass
		except ValueError:
			self.textSplit2.clear()	

		i = 0
		try:
			document2.setPlainText(str(rp))
		except UnboundLocalError:
			pass

		cursor = QTextCursor(document)
		cursor2 = QTextCursor(document2)

		hlCursor = QTextCursor(document)
		hlCursor2 = QTextCursor(document2)
		plainFormat = QTextCharFormat(hlCursor.charFormat())
		colorFormat = QTextCharFormat(plainFormat)
		colorFormat2 = QTextCharFormat(plainFormat)
		colorFormat.setBackground(QColor(0, 255, 0, 127))
		colorFormat2.setBackground(QColor(0, 0, 255, 127))


	def viewMatches(self):
		if self.textMatches.isVisible():
			self.textMatches.hide()
		else:
			self.textMatches.show()

	def viewCaptures(self):
		if self.textCaptures.isVisible():
			self.textCaptures.hide()
		else:
			self.textCaptures.show()

	def viewOptions(self):
		if self.optionMenu.isVisible():
			self.optionMenu.hide()
		else:
			self.optionMenu.show()

	def createOptionMenu(self):

		self.formGroupBox = QGroupBox('Search Options')
		self.optionMenu = QDialog()
		self.buttonBox = QGroupBox()
		optionMenuLayout = QVBoxLayout()
		vlayout = QVBoxLayout()

		layout = QFormLayout()
		ascii_label = QLabel('ASCII')
		debug_label = QLabel('Debug')
		case_label = QLabel('IgnoreCase')
		locale_label = QLabel('Locale')
		multi_label = QLabel('Multiline')
		dot_label = QLabel('Dotall')
		verbose_label = QLabel('Verbose')

		layout = QFormLayout()
		self.ascii_cb = QCheckBox()
		self.ascii_cb.stateChanged.connect(self.setSearchFlags)
		self.debug_cb = QCheckBox()
		self.debug_cb.stateChanged.connect(self.setSearchFlags)
		self.case_cb = QCheckBox()
		self.case_cb.stateChanged.connect(self.setSearchFlags)
		self.case_cb.setChecked(True)
		self.locale_cb = QCheckBox()
		self.locale_cb.stateChanged.connect(self.setSearchFlags)
		self.multi_cb = QCheckBox()
		self.multi_cb.stateChanged.connect(self.setSearchFlags)
		self.multi_cb.setChecked(True)
		self.dot_cb = QCheckBox()
		self.dot_cb.stateChanged.connect(self.setSearchFlags)
		self.verbose_cb = QCheckBox()
		self.verbose_cb.stateChanged.connect(self.setSearchFlags)

		self.option_cb = {'ascii_cb': 'A', 'debug_cb': 'DEBUG',
		 'case_cb': 'I', 'locale_cb': 'L', 'multi_cb': 'M', 
		 'dot_cb': 'S', 'verbose_cb': 'X'}

		self.search_btn = QRadioButton('Search')
		self.search_btn.setCheckable(True)
		self.search_btn.setChecked(True)
		self.search_btn.toggled.connect(self.changeSearchMode)
		self.replace_btn = QRadioButton('Replace')
		self.replace_btn.setCheckable(True)
		self.replace_btn.toggled.connect(self.changeSearchMode)
		self.split_btn = QRadioButton('Split')
		self.split_btn.setCheckable(True)
		self.split_btn.toggled.connect(self.changeSearchMode)

		vlayout.addWidget(self.search_btn)
		vlayout.addWidget(self.replace_btn)
		vlayout.addWidget(self.split_btn)
		self.buttonBox.setLayout(vlayout)

		self.searchMode = ['search_btn', 'replace_btn', 'split_btn']

		layout.addRow(ascii_label, self.ascii_cb)
		layout.addRow(debug_label, self.debug_cb)
		layout.addRow(case_label, self.case_cb)
		layout.addRow(locale_label, self.locale_cb)
		layout.addRow(multi_label, self.multi_cb)
		layout.addRow(dot_label, self.dot_cb)
		layout.addRow(verbose_label, self.verbose_cb)

		optionMenuLayout.addWidget(self.formGroupBox)
		optionMenuLayout.addWidget(self.buttonBox)
		self.formGroupBox.setLayout(layout)
		self.optionMenu.setLayout(optionMenuLayout)

		self.setSearchFlags(self.option_cb)

	def changeSearchMode(self):
		for i in self.searchMode:
			a = getattr(self, i)
			b = a.isChecked()
			if b:
				mode = i
			
		if mode == 'search_btn':
			self.setSearchView()
		elif mode == 'replace_btn':
			self.setReplaceView()
		elif mode == 'split_btn':
			self.setSplitView()

	def setSearchView(self):
		self.searchLabel.show()
		self.replaceLineEdit.hide()
		self.replaceLineEdit2.hide()
		self.splitLineEdit.hide()
		self.textReplace.hide()
		self.textReplace2.hide()
		self.textSplit.hide()
		self.textSplit2.hide()
		self.splitLabel.hide()
		self.replaceLabel.hide()
		self.subLabel.hide()
		self.lineEdit.show()
		self.textEdit.show()
		self.captureLabel.show()
		self.matchLabel.show()
		self.optionMenu.show()
		self.modeLabel.setText('Search View')

	def setReplaceView(self):
		self.lineEdit.hide()
		self.splitLineEdit.hide()
		#self.textEdit.hide()
		self.textMatches.hide()
		self.textSplit.hide()
		self.textSplit2.hide()
		self.matchLabel.hide()
		self.captureLabel.hide()
		self.splitLabel.hide()
		self.searchLabel.hide()
		self.replaceLabel.show()
		self.replaceLineEdit.show()
		self.replaceLineEdit2.show()
		#self.textReplace.show()
		self.textReplace2.show()
		self.subLabel.show()
		self.optionMenu.show()
		self.modeLabel.setText('Replace View')

	def setSplitView(self):
		self.lineEdit.hide()
		self.replaceLineEdit.hide()
		self.replaceLineEdit2.hide()
		#self.textEdit.hide()
		self.textReplace.hide()
		self.textReplace2.hide()
		self.matchLabel.hide()
		self.captureLabel.hide()
		self.subLabel.hide()
		self.searchLabel.hide()
		self.replaceLabel.hide()
		self.splitLabel.show()
		self.splitLineEdit.show()
		#self.textSplit.show()
		self.textSplit2.show()
		self.optionMenu.show()
		self.modeLabel.setText('Split View')

	def setSearchFlags(self, items):
		self.SEARCH_FLAGS = 0
		try:
			for i in self.option_cb.keys():
				# getattr allows variable i to run as bitwise list
				cb = getattr(self, i)
				if cb.checkState():
					bw = getattr(re, self.option_cb[i])
					self.SEARCH_FLAGS |= bw
		except Exception:
			pass

	def searchOpenFile(self):
		
		fname = QFileDialog.getOpenFileName(self, 'Open file', os.getcwd())

		return fname[0]

	def loadTextFile(self):
		inputFile = QFile(self.searchOpenFile())
		#inputFile = QFile('input_long.txt')
		inputFile.open(QIODevice.ReadOnly)
		j = QTextStream(inputFile)
		j.setCodec('UTF-8')
		self.textEdit.setText(j.readAll())


if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = MainWindow()
	win.show()
	sys.exit(app.exec_())