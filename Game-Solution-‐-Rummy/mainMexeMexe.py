import MexeMexe3 as MMengine

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mexe Mexe Simulator")
        self.maxCol_table = 38
        self.maxRow_table = 4
        self.maxCol_hand = 29
        self.imgSize = 30
        self.resize(1440, 900)
        self.SELECTED_PLAY = None

        self.centralwidget = QWidget(self)

        self.tableScroll = QScrollArea(self.centralwidget)
        self.tableScroll.setGeometry(QRect(10, 10, 1420, 400))
        self.tableScroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1418, 398))
        self.scrollAreaWidgetContents.setStyleSheet("background-color: black;")
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(23)
        self.tableScroll.setWidget(self.scrollAreaWidgetContents)

        self.handScroll = QScrollArea(self.centralwidget)
        self.handScroll.setGeometry(QRect(330, 420, 1100, 100))
        self.handScroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 1098, 98))
        self.scrollAreaWidgetContents_2.setStyleSheet("background-color: black;")
        self.gridLayout2 = QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout2.setContentsMargins(10, 0, 10, 0)
        self.handScroll.setWidget(self.scrollAreaWidgetContents_2)

        self.playSequenceScroll = QScrollArea(self.centralwidget)
        self.playSequenceScroll.setGeometry(QRect(330, 530, 1100, 360))
        self.playSequenceScroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 1098, 358))
        self.scrollAreaWidgetContents_3.setStyleSheet("background-color: black;")
        self.gridLayout3 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout3.setContentsMargins(10, 10, 10, 10)
        self.playSequenceScroll.setWidget(self.scrollAreaWidgetContents_3)

        font = QFont('Times', 11)
        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setGeometry(QRect(10, 420, 90, 100))
        self.startButton.setFont(font)
        self.startButton.setText('START')
        self.startButton.clicked.connect(self.start_pressed)

        self.playButton = QPushButton(self.centralwidget)
        self.playButton.setGeometry(QRect(120, 420, 90, 100))
        self.playButton.setFont(font)
        self.playButton.setText('PLAY')
        self.playButton.clicked.connect(self.play_pressed)
        self.playButton.setEnabled(False)

        self.drawButton = QPushButton(self.centralwidget)
        self.drawButton.setGeometry(QRect(230, 420, 90, 100))
        self.drawButton.setFont(font)
        self.drawButton.setText('DRAW')
        self.drawButton.clicked.connect(self.draw_pressed)
        self.drawButton.setEnabled(False)

        self.playOpportunitiesScroll = QScrollArea(self.centralwidget)
        self.playOpportunitiesScroll.setGeometry(QRect(10, 530, 310, 360))
        self.playOpportunitiesScroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 308, 358))
        self.scrollAreaWidgetContents_4.setStyleSheet("background-color: black;")
        self.gridLayout4 = QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout4.setContentsMargins(25, 15, 10, 10)
        self.playOpportunitiesScroll.setWidget(self.scrollAreaWidgetContents_4)

        self.setCentralWidget(self.centralwidget)

    def image_label(self, name):
        image = QPixmap('img/' + name + '.jpeg').scaledToWidth(self.imgSize)
        label = QLabel()
        label.setPixmap(image)
        return label

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def preset_grid(self, grid, maxCol, maxRow):       
        for col in range(0, maxCol):
            grid.addWidget(self.image_label('empty'), 0, col)
        for row in range(0, maxRow):
            grid.addWidget(self.image_label('empty'), row, 0)




    def routine_check(self):
        PLAYS = MMengine.check_for_plays()
        global PLAY_OPPORTUNITIES
        PLAY_OPPORTUNITIES = MMengine.format_play_opportunities(PLAYS)
        self.arrange_opportunities()

    def play_pressed(self):
        MMengine.actualize_play(PLAY_OPPORTUNITIES[self.SELECTED_PLAY]['SIMPLE PATH'])
        self.arrange_groups()
        self.arrange_hand()
        self.clear_layout(self.gridLayout3) 
        self.clear_layout(self.gridLayout4)
        self.routine_check()

    def draw_pressed(self):
        MMengine.draw_card()
        self.arrange_hand()
        self.routine_check()

    def start_pressed(self):
        global CARDS, TRIOS, DECK, TABLE, GROUPS, COMBINATIONS, HAND
        CARDS, TRIOS, DECK, TABLE, GROUPS, COMBINATIONS, HAND = MMengine.start_game()
        self.drawButton.setEnabled(True)
        self.arrange_hand()
        self.routine_check()

    def opportunity_pressed(self, index):
        self.SELECTED_PLAY = index
        self.playButton.setEnabled(True)
        self.arrange_play_sequence(PLAY_OPPORTUNITIES[index]['PRINT MATRIX'])


    def arrange_groups(self):
        self.clear_layout(self.gridLayout)    
        self.preset_grid(self.gridLayout, self.maxCol_table, self.maxRow_table)
        row, col = 0, 0
        for group in GROUPS:
            if col + len(group) >= self.maxCol_table:
                col = 0
                row += 1
            for suit, number in group:
                self.gridLayout.addWidget(self.image_label(f'{suit}-{number}'), row, col)
                col += 1
            if col != self.maxCol_table-1:
                col += 1

    def arrange_hand(self):
        self.clear_layout(self.gridLayout2) 
        self.preset_grid(self.gridLayout2, self.maxCol_hand, 0)
        for i, [suit, number] in enumerate(HAND):
            self.gridLayout2.addWidget(self.image_label(f'{suit}-{number}'), 0, i)


    def arrange_play_sequence(self, printable_matrix):
        self.clear_layout(self.gridLayout3) 
        self.preset_grid(self.gridLayout3, 30, 5)
        for row, rowCards in enumerate(printable_matrix):
            for col, card in enumerate(rowCards):
                if isinstance(card, str):
                    if card == 'CONSUMED':
                        if row == 2:
                            self.gridLayout3.addWidget(self.image_label('empty_line_cross'), row, col)
                        else:    
                            self.gridLayout3.addWidget(self.image_label('empty_line'), row, col)
                    elif card == 'CREATED':
                        self.gridLayout3.addWidget(self.image_label('empty_line_right2'), row, col)
                    elif card == 'CREATED2':
                        self.gridLayout3.addWidget(self.image_label('empty_line_left2'), row, col)
                    elif row == 2:
                        self.gridLayout3.addWidget(self.image_label('empty_line_h'), row, col)
                else:
                    suit, number = card
                    self.gridLayout3.addWidget(self.image_label(f'{suit}-{number}'), row, col)
                        
    def arrange_opportunities(self):
        self.playButton.setEnabled(False)
        self.clear_layout(self.gridLayout4) 
        self.preset_grid(self.gridLayout4, 6, 5)
        buttons = {}
        for i in range(len(PLAY_OPPORTUNITIES)):
            buttons[i] = QPushButton(f'{i}')
            buttons[i].setFixedSize(QSize(40, 40))
            buttons[i].setStyleSheet("background-color: white")
            buttons[i].setFont(QFont('Times', 10))
            buttons[i].clicked.connect(partial(self.opportunity_pressed, i))
            self.gridLayout4.addWidget(buttons[i], i, 0)
            self.gridLayout4.addWidget(self.image_label('empty'), i, 1)
            for col, [suit, number] in enumerate(PLAY_OPPORTUNITIES[i]['HAND DISCARDS']):
                self.gridLayout4.addWidget(self.image_label(f'{suit}-{number}'), i, col + 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
