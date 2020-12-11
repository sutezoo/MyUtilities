import sys
import random
import pickle
import pandas as pd
import numpy as np
from PySide2.QtWidgets import QApplication,QWidget,QPushButton,QGridLayout,QLabel,QTextEdit,QLineEdit,\
    QCompleter,QVBoxLayout,QAction,QHeaderView,QHBoxLayout,QMainWindow,QTableWidget,QComboBox,QCompleter,QTableWidgetItem,\
    QGridLayout,QSizePolicy,QDialog
    
from PySide2.QtCore import Qt,Slot
from PySide2.QtGui import QPainter
from PySide2 import QtGui
from PySide2.QtCharts import QtCharts


class mainwidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items=0
        with open('today_meal.pickle','rb') as f:
            self._data = pickle.load(f)
        self.nutrients_df = pd.read_csv('nutrients_table.csv',index_col=0)
        goal_value = np.load('goal.npy')
        self.goal_calorie = goal_value[0]
        self.goal_protein = goal_value[1]
        self.goal_fat = goal_value[2]
        self.goal_carbon = goal_value[3]
        self.total_calorie = 0
        self.total_protein = 0
        self.total_fat = 0
        self.total_carbon = 0
            
        #左側上部（食べたものリスト）
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['品目','量','カロリー','たんぱく質','脂質','炭水化物'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fill_table()
        #左側下部（合計値）
        self.total_indicator = QVBoxLayout()
        self.tcal_indicator = QHBoxLayout()
        self.tp_indicator = QHBoxLayout()
        self.tf_indicator = QHBoxLayout()
        self.tc_indicator = QHBoxLayout()
        self.tcal_label = QLabel('カロリー')
        self.tcal_label.setFont(QtGui.QFont('Arial',20,QtGui.QFont.Black))
        self.tcal_value = QLabel('')
        self.tp_label = QLabel('たんぱく質')
        self.tp_label.setFont(QtGui.QFont('Arial',20,QtGui.QFont.Black))
        self.tp_value = QLabel('')
        self.tf_label = QLabel('脂質')
        self.tf_label.setFont(QtGui.QFont('Arial',20,QtGui.QFont.Black))
        self.tf_value = QLabel('')
        self.tc_label = QLabel('炭水化物')
        self.tc_label.setFont(QtGui.QFont('Arial',20,QtGui.QFont.Black))
        self.tc_value = QLabel('')
        self.tcal_label.setAlignment(Qt.AlignCenter)
        self.tp_label.setAlignment(Qt.AlignCenter)
        self.tf_label.setAlignment(Qt.AlignCenter)
        self.tc_label.setAlignment(Qt.AlignCenter)
        self.tcal_indicator.addWidget(self.tcal_label,3)
        self.tcal_indicator.addWidget(self.tcal_value,7)
        self.tp_indicator.addWidget(self.tp_label,3)
        self.tp_indicator.addWidget(self.tp_value,7)
        self.tf_indicator.addWidget(self.tf_label,3)
        self.tf_indicator.addWidget(self.tf_value,7)
        self.tc_indicator.addWidget(self.tc_label,3)
        self.tc_indicator.addWidget(self.tc_value,7)
        self.total_indicator.addLayout(self.tcal_indicator)
        self.total_indicator.addLayout(self.tp_indicator)
        self.total_indicator.addLayout(self.tf_indicator)
        self.total_indicator.addLayout(self.tc_indicator)
        self.refresh_total(mode='initialize')

        #右側
        #入力フォーム
        model = QtGui.QStandardItemModel(self)
        for elm in self.nutrients_df.index.tolist():
            name = QtGui.QStandardItem(elm)
            model.setItem(model.rowCount(),0,name)
        self.foodname = QComboBox(self)
        self.foodname.setLineEdit(QLineEdit())
        self.foodname.setCompleter(QCompleter())
        self.foodname.setModel(model)
        self.foodname.completer().setModel(model)
        self.foodname.lineEdit().setText('')
        self.foodamount = QLineEdit()
        #ボタン
        self.foodname_label = QLabel('品目')
        self.foodname_label.setFont(QtGui.QFont('Arial',14,QtGui.QFont.Black))
        self.foodname_label.setAlignment(Qt.AlignCenter)
        self.foodamount_label = QLabel('分量')
        self.foodamount_label.setFont(QtGui.QFont('Arial',14,QtGui.QFont.Black))
        self.foodamount_label.setAlignment(Qt.AlignCenter)
        self.add = QPushButton('＋')
        self.add.setFont(QtGui.QFont('Arial',30,QtGui.QFont.Black))
        self.add.clicked.connect(self.add_data)
        self.delete = QPushButton('末尾のデータを削除')
        self.delete.setFont(QtGui.QFont('Arial',14,QtGui.QFont.Black))
        self.delete.clicked.connect(self.delete_data)
        self.delete_all = QPushButton('全てのデータを削除')
        self.delete_all.setFont(QtGui.QFont('Arial',14,QtGui.QFont.Black))
        self.delete_all.clicked.connect(self.delete_all_func)
        # self.plot = QPushButton('プロット')
        # self.plot.setFont(QtGui.QFont('Arial',26,QtGui.QFont.Black))
        # self.plot.clicked.connect(self.plot_data)
        self.save = QPushButton('保存')
        self.save.setFont(QtGui.QFont('Arial',14,QtGui.QFont.Black))
        # self.save.setStyleSheet('border : 2px solid black;\
        #                          border-radius : 20px;')
        self.save.clicked.connect(self.save_data)
        #チャート
        self.chartview = QtCharts.QChartView()
        self.chartview.setRenderHint(QPainter.Antialiasing)
        
        #ウィジェットの追加
        #左側
        self.left = QVBoxLayout()
        self.left.addWidget(self.table,7)
        self.left.addLayout(self.total_indicator,3)
        #右側
        self.right = QVBoxLayout()
        self.right.setMargin(10)
        self.input_form = QHBoxLayout()
        self.input_form_labels = QVBoxLayout()
        self.input_form_editor = QVBoxLayout()
        self.input_form_labels.addWidget(self.foodname_label)
        self.input_form_labels.addWidget(self.foodamount_label)
        self.input_form_editor.addWidget(self.foodname)
        self.input_form_editor.addWidget(self.foodamount)
        self.input_form.addSpacing(1)
        self.input_form.addLayout(self.input_form_labels,1)
        self.input_form.addLayout(self.input_form_editor,5)
        self.input_form.addWidget(self.add,2)
        # self.input_form.addWidget(self.plot,1.5)
        self.input_form.addSpacing(1)
        self.right.addLayout(self.input_form)
        self.right.addWidget(self.chartview)
        self.delete_save_button = QHBoxLayout()
        self.delete_save_button.addWidget(self.delete)
        self.delete_save_button.addWidget(self.delete_all)
        self.delete_save_button.addWidget(self.save)
        self.right.addLayout(self.delete_save_button)
        #レイアウト
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.left,6)
        self.layout.addLayout(self.right,4)
        self.setLayout(self.layout)
        self.plot_data()

    @Slot()
    def add_data(self):
        ref = self.nutrients_df
        name = self.foodname.lineEdit().text()
        amount = float(self.foodamount.text())
        self._data.append([name,amount])
        self.table.insertRow(self.items)
        cal = amount*ref.at[name,'calorie']
        p = amount*ref.at[name,'protein']
        f = amount*ref.at[name,'fat']
        c = amount*ref.at[name,'carbon']
        self.total_calorie+=cal
        self.total_protein+=p
        self.total_fat+=f
        self.total_carbon+=c
        name_item = QTableWidgetItem(name)
        amount_item = QTableWidgetItem(str(amount))
        cal_item = QTableWidgetItem(str(int(cal)))
        p_item = QTableWidgetItem(str(round(p,2)))
        f_item = QTableWidgetItem(str(round(f,2)))
        c_item = QTableWidgetItem(str(round(c,2)))
        name_item.setTextAlignment(Qt.AlignCenter)
        amount_item.setTextAlignment(Qt.AlignCenter)
        cal_item.setTextAlignment(Qt.AlignCenter)
        p_item.setTextAlignment(Qt.AlignCenter)
        f_item.setTextAlignment(Qt.AlignCenter)
        c_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(self.items,0,name_item)
        self.table.setItem(self.items,1,amount_item)
        self.table.setItem(self.items,2,cal_item)
        self.table.setItem(self.items,3,p_item)
        self.table.setItem(self.items,4,f_item)
        self.table.setItem(self.items,5,c_item)
        self.foodname.lineEdit().setText(''); self.foodamount.setText('')
        self.items+=1
        self.refresh_total()
        self.plot_data()

    @Slot()
    def delete_all_func(self):
        self.items=0
        self.table.setRowCount(0)
        self._data = []
        self.total_calorie=0; self.total_protein=0
        self.total_fat=0; self.total_carbon=0
        self.refresh_total()
        self.plot_data()

    @Slot()
    def delete_data(self):
        self.items-=1
        self.table.setRowCount(self.items)
        name = self._data[-1][0]
        amount = self._data[-1][1]
        ref = self.nutrients_df
        cal = amount*ref.at[name,'calorie']
        p = amount*ref.at[name,'protein']
        f = amount*ref.at[name,'fat']
        c = amount*ref.at[name,'carbon']
        self.total_calorie-=cal
        self.total_protein-=p
        self.total_fat-=f
        self.total_carbon-=c
        self._data.pop(-1)
        self.refresh_total()
        self.plot_data()

    @Slot()
    def save_data(self):
        with open('today_meal.pickle','wb') as f:
            pickle.dump(self._data,f)
    
    @Slot()
    def plot_data(self):
        presence = QtCharts.QBarSet('現在')
        goal = QtCharts.QBarSet('目標')
        presence.append([self.total_calorie/self.goal_calorie,self.total_protein/self.goal_protein,\
            self.total_fat/self.goal_fat,self.total_carbon/self.goal_carbon])
        goal.append([1,1,1,1])
        series = QtCharts.QBarSeries()
        series.append(presence); series.append(goal)
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        labels = ['カロリー','たんぱく質','脂質','炭水化物']
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(labels)
        chart.addAxis(axisX,Qt.AlignBottom)
        chart.legend().setVisible(True)
        chart.legend().setFont(QtGui.QFont('Arial',10,QtGui.QFont.Bold))
        chart.setTheme(QtCharts.QChart.ChartThemeHighContrast)
        self.chartview.setChart(chart)

    @Slot()
    def refresh_total(self,mode=None):
        cal_diff = str(round(self.total_calorie-self.goal_calorie,2))
        p_diff = str(round(self.total_protein-self.goal_protein,2))
        f_diff = str(round(self.total_fat-self.goal_fat,2))
        c_diff = str(round(self.total_carbon-self.goal_carbon,2))
        if self.total_calorie>self.goal_calorie: cal_diff='+'+cal_diff
        if self.total_protein>self.goal_protein: p_diff='+'+p_diff
        if self.total_fat>self.goal_fat: f_diff='+'+f_diff
        if self.total_carbon>self.goal_carbon: c_diff='+'+c_diff
        tcal = str(int(self.total_calorie))+' kcal / '+str(self.goal_calorie)+' kcal ('+cal_diff+' kcal)'
        tp = str(round(self.total_protein,2))+' g / '+str(self.goal_protein)+' g ('+p_diff+' g)'
        tf = str(round(self.total_fat,2))+' g / '+str(self.goal_fat)+' g ('+f_diff+' g)'
        tc = str(round(self.total_carbon,2))+' g / '+str(self.goal_carbon)+' g ('+c_diff+' g)'
        self.tcal_value.setText(tcal)
        self.tp_value.setText(tp)
        self.tf_value.setText(tf)
        self.tc_value.setText(tc)
        self.tcal_value.setFont(QtGui.QFont('Arial',24,QtGui.QFont.Bold))
        self.tp_value.setFont(QtGui.QFont('Arial',24,QtGui.QFont.Bold))
        self.tf_value.setFont(QtGui.QFont('Arial',24,QtGui.QFont.Bold))
        self.tc_value.setFont(QtGui.QFont('Arial',24,QtGui.QFont.Bold))
        self.tcal_value.setAlignment(Qt.AlignCenter)
        self.tp_value.setAlignment(Qt.AlignCenter)
        self.tf_value.setAlignment(Qt.AlignCenter)
        self.tc_value.setAlignment(Qt.AlignCenter)

    @Slot()
    def register_food_ok_button(self,name,unit,calorie,protein,fat,carbon):
        self.nutrients_df.loc[name] = [unit,calorie,protein,fat,carbon]
        self.nutrients_df.to_csv('nutrients_table.csv')

    def fill_table(self,data=None):
        ref = self.nutrients_df
        data = self._data if not data else data
        for food in data:
            cal = food[1]*ref.at[food[0],'calorie']
            p = food[1]*ref.at[food[0],'protein']
            f = food[1]*ref.at[food[0],'fat']
            c = food[1]*ref.at[food[0],'carbon']
            self.total_calorie+=cal
            self.total_protein+=p
            self.total_fat+=f
            self.total_carbon+=c
            name_item = QTableWidgetItem(food[0])
            amount_item = QTableWidgetItem(str(food[1]))
            cal_item = QTableWidgetItem(str(int(cal)))
            p_item = QTableWidgetItem(str(round(p,2)))
            f_item = QTableWidgetItem(str(round(f,2)))
            c_item = QTableWidgetItem(str(round(c,2)))
            name_item.setTextAlignment(Qt.AlignCenter)
            amount_item.setTextAlignment(Qt.AlignCenter)
            cal_item.setTextAlignment(Qt.AlignCenter)
            p_item.setTextAlignment(Qt.AlignCenter)
            f_item.setTextAlignment(Qt.AlignCenter)
            c_item.setTextAlignment(Qt.AlignCenter)
            self.table.insertRow(self.items)
            self.table.setItem(self.items,0,name_item)
            self.table.setItem(self.items,1,amount_item)
            self.table.setItem(self.items,2,cal_item)
            self.table.setItem(self.items,3,p_item)
            self.table.setItem(self.items,4,f_item)
            self.table.setItem(self.items,5,c_item)
            self.items+=1

class mainwindow(QMainWindow):
    EXIT_CODE_REBOOT = -87654321
    def __init__(self,mainwidget):
        QMainWindow.__init__(self)
        self.set_up_goal_window = SetUpGoal()
        self.set_up_goal_window.move(1000,600)
        self.register_food_window = RegisterNewFood()
        self.register_food_window.move(1000,600)
        self.setWindowTitle('栄養成分計算機')
        
        #メニューバーの設定
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('ファイル')
        self.reboot_menu = self.menu.addMenu('再起動')

        #目標の設定
        setting_goal = QAction('目標を設定',self)
        setting_goal.triggered.connect(self.goal_is_here)
        self.file_menu.addAction(setting_goal)
        #新しい食品の追加
        register_food = QAction('新しい食品を追加',self)
        register_food.triggered.connect(self.new_comer)
        self.file_menu.addAction(register_food)

        #再起動
        reboot_action = QAction('再起動',self)
        reboot_action.setShortcut('Ctrl+R')
        reboot_action.triggered.connect(self.reboot_app)
        self.reboot_menu.addAction(reboot_action)
        
        #退出
        exit_action = QAction('終了',self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exit_app)
        self.file_menu.addAction(exit_action)

        self.setCentralWidget(mainwidget)

    @Slot()
    def exit_app(self,checked):
        QApplication.exit(-1234)

    @Slot()
    def goal_is_here(self,checked):
        self.set_up_goal_window.show()

    @Slot()
    def new_comer(self,checked):
        self.register_food_window.show()

    @Slot()
    def reboot_app(self,checked):
        QApplication.exit(mainwindow.EXIT_CODE_REBOOT)



class SetUpGoal(QWidget):
    def __init__(self):
        super().__init__()
        whole_window = QVBoxLayout()
        self.inputform = QGridLayout()
        self.buttons = QHBoxLayout()
        self.label1 = QLabel('カロリー')
        self.label2 = QLabel('たんぱく質')
        self.label3 = QLabel('脂質')
        self.label4 = QLabel('炭水化物')
        self.value1 = QLineEdit()
        self.value2 = QLineEdit()
        self.value3 = QLineEdit()
        self.value4 = QLineEdit()
        self.inputform.addWidget(self.label1,0,0)
        self.inputform.addWidget(self.label2,1,0)
        self.inputform.addWidget(self.label3,2,0)
        self.inputform.addWidget(self.label4,3,0)
        self.inputform.addWidget(self.value1,0,1)
        self.inputform.addWidget(self.value2,1,1)
        self.inputform.addWidget(self.value3,2,1)
        self.inputform.addWidget(self.value4,3,1)
        self.ok = QPushButton("決定")
        self.ok.clicked.connect(self.okbutton)
        self.cancel = QPushButton("キャンセル")
        self.cancel.clicked.connect(self.cancelbutton)
        self.buttons.addWidget(self.ok)
        self.buttons.addWidget(self.cancel)
        whole_window.addLayout(self.inputform)
        whole_window.addLayout(self.buttons)
        self.setLayout(whole_window)
        
    @Slot()
    def okbutton(self):
        cal = float(self.value1.text())
        p = float(self.value2.text())
        f = float(self.value3.text())
        c = float(self.value4.text())
        new_goal = np.array([cal,p,f,c])
        np.save('goal',new_goal)
        self.close()
    
    @Slot()
    def cancelbutton(self):
        self.close()


class RegisterNewFood(QWidget):
    def __init__(self):
        super().__init__()
        whole_window = QVBoxLayout()
        self.inputform = QGridLayout()
        self.buttons = QHBoxLayout()
        self.label1 = QLabel('品目')
        self.label2 = QLabel('単位')
        self.label3 = QLabel('カロリー')
        self.label4 = QLabel('たんぱく質')
        self.label5 = QLabel('脂質')
        self.label6 = QLabel('炭水化物')
        self.label1.setAlignment(Qt.AlignCenter)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label4.setAlignment(Qt.AlignCenter)
        self.label5.setAlignment(Qt.AlignCenter)
        self.label6.setAlignment(Qt.AlignCenter)
        self.value1 = QLineEdit()
        self.value2 = QLineEdit()
        self.value3 = QLineEdit()
        self.value4 = QLineEdit()
        self.value5 = QLineEdit()
        self.value6 = QLineEdit()
        self.inputform.addWidget(self.label1,0,0)
        self.inputform.addWidget(self.label2,1,0)
        self.inputform.addWidget(self.label3,2,0)
        self.inputform.addWidget(self.label4,3,0)
        self.inputform.addWidget(self.label5,4,0)
        self.inputform.addWidget(self.label6,5,0)
        self.inputform.addWidget(self.value1,0,1)
        self.inputform.addWidget(self.value2,1,1)
        self.inputform.addWidget(self.value3,2,1)
        self.inputform.addWidget(self.value4,3,1)
        self.inputform.addWidget(self.value5,4,1)
        self.inputform.addWidget(self.value6,5,1)
        self.ok = QPushButton('追加')
        self.ok.clicked.connect(self.okbutton)
        self.cancel = QPushButton('キャンセル')
        self.cancel.clicked.connect(self.cancelbutton)
        self.buttons.addWidget(self.ok)
        self.buttons.addWidget(self.cancel)
        whole_window.addLayout(self.inputform)
        whole_window.addLayout(self.buttons)
        self.setLayout(whole_window)

    @Slot()
    def okbutton(self):
        connection = mainwidget()
        id = self.value1.text()
        un = self.value2.text()
        cal = float(self.value3.text())
        pro = float(self.value4.text())
        f = float(self.value5.text())
        car = float(self.value6.text())
        connection.register_food_ok_button(id,un,cal,pro,f,car)
        self.close()

    @Slot()
    def cancelbutton(self):
        self.close()



if __name__=='__main__':
    currentExitCode = mainwindow.EXIT_CODE_REBOOT
    app = QApplication(sys.argv)
    while currentExitCode==mainwindow.EXIT_CODE_REBOOT:
        core =  mainwidget()
        machine = mainwindow(core)
        machine.resize(1600,800)
        machine.move(400,300)
        machine.show()
        # sys.exit(app.exec_())
        currentExitCode = app.exec_()
        app = QApplication.instance()