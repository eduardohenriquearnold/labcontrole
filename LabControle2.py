# -*- coding: utf-8 -*-
#==============================================================================
# This file is part of LabControle 2.
# 
# LabControle 2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
# 
# LabControle 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with LabControle 2.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================
#==============================================================================
# Este arquivo é parte do programa LabControle 2
# 
# LabControle 2 é um software livre; você pode redistribui-lo e/ou 
# modifica-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 3 da 
# Licença.
# Este programa é distribuido na esperança que possa ser  util, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a 
# qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral
# GNU para maiores detalhes.
# 
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#==============================================================================
#
# Developed by Miguel Moreto
# Florianopolis, Brazil, 2015

from PyQt4 import QtCore,QtGui, QtSvg

import matplotlib
matplotlib.use("Qt4Agg")

from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

import MainWindow
import MySystem
import utils
import numpy
import subprocess
import pickle
#import encript
import base64

           
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

MESSAGE = _translate("MainWindow", "<p><b>Sobre o LabControle2</b></p>" \
            "<p>O LabControle é um software desenvolvido " \
            "para ser utilizado em atividades de laboratório de " \
            "disciplinas de Sistemas de Controle.</p>" \
            "<p>O LabControle2 foi desenvolvido por Miguel Moreto, " \
            "professor do Departamento de Engenharia Elétrica da UFSC "\
            "para uso nos laboratórios da disciplina EEL7063 - Sistemas "\
            "de Controle.</p>" \
            "<p>O LabControle2 foi desenvolvido em linguagem Python "\
            "e seu código é livre, podendo ser acessado no site:</p>"\
            "<p><b><a href=\"https://github.com/miguelmoreto/labcontrole\">https://github.com/miguelmoreto/labcontrole</a></b></p>"\
            "<p>Contribua enviando sugestões e relatórios de bugs (issues)!</p>"\
            "<p>Florianópolis, SC, 2015</p>", None)

class LabControle2(QtGui.QMainWindow,MainWindow.Ui_MainWindow):
    """
    hwl is inherited from both QtGui.QDialog and hw.Ui_Dialog
    """
    def __init__(self,parent=None):
        self.init = 0
        super(LabControle2,self).__init__(parent)
        
        # Init variables:
        self.SVGRect = QtCore.QRectF()
        self.GraphSize = QtCore.QSize()
        
        self.currentComboIndex = 0
        
        self.setupUi(self)
        
        # Adding toolbar spacer and a Hidden system label:
        empty = QtGui.QWidget()
        self.labelHide = QtGui.QLabel()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.labelHide.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelHide.setFont(font)
        self.labelHide.setText('')
        self.labelHide.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        empty.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        self.toolBar.insertWidget(self.actionClose,empty)
        self.toolBar.insertWidget(self.actionClose,self.labelHide)
        
        # Set diagram the current tab:
        self.tabWidget.setCurrentIndex(0)
        
        
        self.image = QtGui.QImage()        
        self.graphicsView.setScene(QtGui.QGraphicsScene(self))
        self.graphicsView.setViewport(QtGui.QWidget())
        
        # Load initial SVG file
        svg_file = QtCore.QFile('diagram1Opened.svg')
        if not svg_file.exists():
            QtGui.QMessageBox.critical(self, "Open SVG File",
                    "Could not open file '%s'." % 'diagram1Opened.svg')

            self.outlineAction.setEnabled(False)
            self.backgroundAction.setEnabled(False)
            return        
        self.scene = self.graphicsView.scene()
        self.scene.clear()
        self.graphicsView.resetTransform()
        
        self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())        
        self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        #self.svgItem.setZValue(0)
        
        #self.backgroundItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
        #self.backgroundItem.setBrush(QtCore.Qt.gray)
        #self.backgroundItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        #self.backgroundItem.setVisible(True)
        #self.backgroundItem.setZValue(-1)

        self.scene.addItem(self.svgItem)
        
        
        # Initial definitions:
        self.checkBoxPert.setDisabled(True) # Perturbation is disabled by default
        self.checkBoxControle.setDisabled(True) # Control signal is disabled by default

        # Adding toolbars
        self.mpltoolbarSimul = NavigationToolbar(self.mplSimul, self)
        self.mpltoolbarLGR = NavigationToolbar(self.mplLGR, self)
        self.mpltoolbarBode = NavigationToolbar(self.mplBode, self)
        self.mpltoolbarNyquist = NavigationToolbar(self.mplNyquist, self)
        self.VBoxLayoutSimul.addWidget(self.mpltoolbarSimul)
        self.VBoxLayoutLGR.addWidget(self.mpltoolbarLGR)
        self.VBoxLayoutBode.addWidget(self.mpltoolbarBode)
        self.VBoxLayoutNyquist.addWidget(self.mpltoolbarNyquist)
        
        # MATPLOTLIB API AXES CONFIG
        self.mplSimul.figure.set_facecolor('0.90')
        self.mplSimul.figure.set_tight_layout(True)
        self.mplLGR.figure.set_facecolor('0.90')
        self.mplLGR.figure.set_tight_layout(True)
        self.mplBode.figure.set_facecolor('0.90')
        self.mplBode.figure.set_tight_layout(True)
        
        #self.mplSimul.axes.plot(x,y)
        self.mplSimul.axes.set_xlabel(_translate("MainWindow", "Tempo [s]", None))
        self.mplSimul.axes.set_ylabel(_translate("MainWindow", "Valor", None))
        self.mplSimul.axes.set_title(_translate("MainWindow", "Simulação no tempo", None))
        self.mplSimul.axes.set_xlim(0, self.doubleSpinBoxTmax.value())
        self.mplSimul.axes.set_ylim(0, 1)
        self.mplSimul.axes.grid(True)
        #self.mplSimul.axes.autoscale(True)
        self.mplSimul.draw()
        
        self.mplBode.figure.clf()
        self.mplNyquist.figure.clf()
        
        # Initializing system
        self.sys = MySystem.MySystem()
        # Updating values from GUI:
        self.sys.Fmin = self.doubleSpinFmin.value()
        self.sys.Fmax = self.doubleSpinFmax.value()
        self.sys.Fpontos = self.doubleSpinBodeRes.value()
                
        self.init = 1
                
        # Connecting events:
        QtCore.QObject.connect(self.radioBtnOpen, QtCore.SIGNAL("clicked()"), self.feedbackOpen)
        QtCore.QObject.connect(self.radioBtnClose, QtCore.SIGNAL("clicked()"), self.feedbackClose)
        QtCore.QObject.connect(self.verticalSliderK, QtCore.SIGNAL("valueChanged(int)"), self.onSliderMove)
        QtCore.QObject.connect(self.comboBoxSys, QtCore.SIGNAL("currentIndexChanged(int)"), self.onChangeSystem)
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL("currentChanged (int)"), self.onTabChange)
        # Spinboxes:
        QtCore.QObject.connect(self.doubleSpinBoxKmax, QtCore.SIGNAL("valueChanged(double)"), self.onKmaxChange)
        QtCore.QObject.connect(self.doubleSpinBoxKmin, QtCore.SIGNAL("valueChanged(double)"), self.onKminChange)
        QtCore.QObject.connect(self.doubleSpinBoxKlgr, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.connect(self.doubleSpinBoxK, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.connect(self.doubleSpinBoxTmax, QtCore.SIGNAL("valueChanged(double)"), self.onTmaxChange)
        QtCore.QObject.connect(self.doubleSpinBoxRtime, QtCore.SIGNAL("valueChanged(double)"), self.onRtimeChange)
        QtCore.QObject.connect(self.doubleSpinBoxRnoise, QtCore.SIGNAL("valueChanged(double)"), self.onRnoiseChange)
        QtCore.QObject.connect(self.doubleSpinBoxWtime, QtCore.SIGNAL("valueChanged(double)"), self.onWtimeChange)
        QtCore.QObject.connect(self.doubleSpinBoxWnoise, QtCore.SIGNAL("valueChanged(double)"), self.onWnoiseChange)
        QtCore.QObject.connect(self.doubleSpinFmin, QtCore.SIGNAL("valueChanged(double)"), self.onBodeFminChange)
        QtCore.QObject.connect(self.doubleSpinFmax, QtCore.SIGNAL("valueChanged(double)"), self.onBodeFmaxChange)
        QtCore.QObject.connect(self.doubleSpinBodeRes, QtCore.SIGNAL("valueChanged(double)"), self.onBodeResChange)
        QtCore.QObject.connect(self.doubleSpinFminNyq, QtCore.SIGNAL("valueChanged(double)"), self.onNyquistFminChange)
        QtCore.QObject.connect(self.doubleSpinFmaxNyq, QtCore.SIGNAL("valueChanged(double)"), self.onNyquistFmaxChange)        
        QtCore.QObject.connect(self.doubleSpinNyqRes, QtCore.SIGNAL("valueChanged(double)"), self.onNyquistResChange)
        QtCore.QObject.connect(self.doubleSpinBoxResT, QtCore.SIGNAL("valueChanged(double)"), self.onSimluResChange)
        QtCore.QObject.connect(self.doubleSpinBoxLGRpontos, QtCore.SIGNAL("valueChanged(double)"), self.onResLGRchange)
        QtCore.QObject.connect(self.doubleSpinBoxDeltaR, QtCore.SIGNAL("valueChanged(double)"), self.onRvarChange)
        QtCore.QObject.connect(self.doubleSpinBoxDeltaRtime, QtCore.SIGNAL("valueChanged(double)"), self.onRvarInstChange)
        QtCore.QObject.connect(self.doubleSpinBoxTk, QtCore.SIGNAL("valueChanged(double)"), self.onTkChange)
        QtCore.QObject.connect(self.spinBoxPtTk, QtCore.SIGNAL("valueChanged(int)"), self.onPointsTkChange)

        # LineEdits:
        QtCore.QObject.connect(self.lineEditRvalue, QtCore.SIGNAL("textEdited(QString)"), self.onRvalueChange)
        QtCore.QObject.connect(self.lineEditWvalue, QtCore.SIGNAL("textEdited(QString)"), self.onWvalueChange)
        QtCore.QObject.connect(self.lineEditGnum, QtCore.SIGNAL("textEdited(QString)"), self.onGnumChange)
        QtCore.QObject.connect(self.lineEditGden, QtCore.SIGNAL("textEdited(QString)"), self.onGdenChange)
        QtCore.QObject.connect(self.lineEditCnum, QtCore.SIGNAL("textEdited(QString)"), self.onCnumChange)
        QtCore.QObject.connect(self.lineEditCden, QtCore.SIGNAL("textEdited(QString)"), self.onCdenChange)
        QtCore.QObject.connect(self.lineEditHnum, QtCore.SIGNAL("textEdited(QString)"), self.onHnumChange)
        QtCore.QObject.connect(self.lineEditHden, QtCore.SIGNAL("textEdited(QString)"), self.onHdenChange)
        # Group Boxes:
        QtCore.QObject.connect(self.groupBoxC, QtCore.SIGNAL("toggled(bool)"), self.onGroupBoxCcheck)
        QtCore.QObject.connect(self.groupBoxG, QtCore.SIGNAL("toggled(bool)"), self.onGroupBoxGcheck)
        QtCore.QObject.connect(self.groupBoxH, QtCore.SIGNAL("toggled(bool)"), self.onGroupBoxHcheck)
        QtCore.QObject.connect(self.groupBoxWt, QtCore.SIGNAL("toggled(bool)"), self.onGroupBoxWcheck)
        # Buttons:
        QtCore.QObject.connect(self.btnSimul, QtCore.SIGNAL("clicked()"), self.onBtnSimul)
        QtCore.QObject.connect(self.btnContinuar, QtCore.SIGNAL("clicked()"), self.onBtnContinue)
        QtCore.QObject.connect(self.btnLimparSimul, QtCore.SIGNAL("clicked()"), self.onBtnClearSimul)
        QtCore.QObject.connect(self.btnPlotLGR, QtCore.SIGNAL("clicked()"), self.onBtnLGR)
        QtCore.QObject.connect(self.btnLGRclear, QtCore.SIGNAL("clicked()"), self.onBtnLGRclear)
        QtCore.QObject.connect(self.btnPlotBode, QtCore.SIGNAL("clicked()"), self.onBtnPlotBode)
        QtCore.QObject.connect(self.btnBodeClear, QtCore.SIGNAL("clicked()"), self.onBtnBodeClear)
        QtCore.QObject.connect(self.btnPlotNyquist, QtCore.SIGNAL("clicked()"), self.onBtnNyquist)
        QtCore.QObject.connect(self.btnClearNyquist, QtCore.SIGNAL("clicked()"), self.onBtnNyquistClear)
        # Actions
        QtCore.QObject.connect(self.actionHelp, QtCore.SIGNAL("triggered()"), self.onAboutAction)
        QtCore.QObject.connect(self.actionCalc, QtCore.SIGNAL("triggered()"), self.onCalcAction)
        QtCore.QObject.connect(self.actionSalvar_sistema, QtCore.SIGNAL("triggered()"), self.onSaveAction)
        QtCore.QObject.connect(self.actionCarregar_sistema, QtCore.SIGNAL("triggered()"), self.onLoadAction)
        QtCore.QObject.connect(self.actionReset, QtCore.SIGNAL("triggered()"), self.onResetAction)
        #QtCore.QObject.connect(self.actionSysInfo, QtCore.SIGNAL("triggered()"), self.onSysInfoAction)
        
        self.statusBar().showMessage(_translate("MainWindow", "Pronto.", None))        
        
               
    def feedbackOpen(self):
        """Open Feedback """ 

        self.sys.Malha = 'Aberta'
        
        # Change SVG accordingly:        
        self.updateSystemSVG()
        
        self.statusBar().showMessage(_translate("MainWindow", "Malha aberta.", None))
    
    def feedbackClose(self):
        """Close Feedback """

        self.sys.Malha = 'Fechada'
        
        # Change SVG accordingly:        
        self.updateSystemSVG()        
        
        self.statusBar().showMessage(_translate("MainWindow", "Malha fechada.", None))

    def onChangeSystem(self,sysindex):
        """
        Whem user change system topology using the combo box.
        Update block diagram and anable/disable input groupboxes.
        """
        
        # Check prvious system type and disable unecessary itens:
        if (self.sys.Type == 4 and sysindex != 4):
            self.lineEditGden.show()
            self.labelGden.show()
            self.groupBoxG.setTitle(_translate("MainWindow", "Planta G(s)", None))
            self.labelGnum.setText(_translate("MainWindow", "Num:", None))
            # Restoring saved G(s)
            self.sys.Type = sysindex
            self.lineEditGnum.setText(self.sys.GnumStr)
            # Re-enable buttons:
            self.btnPlotBode.setEnabled(True)
            self.btnPlotLGR.setEnabled(True)
            self.btnPlotNyquist.setEnabled(True)

        elif (self.sys.Type == 3 and sysindex != 3):
            self.labelTk.setEnabled(False)
            self.doubleSpinBoxTk.setEnabled(False)
            self.labelPtTk.setEnabled(False)
            self.spinBoxPtTk.setEnabled(False)
            self.doubleSpinBoxResT.setEnabled(True)
            self.groupBoxC.setTitle(_translate("MainWindow", "Controlador C(s)", None))
            # Re-enable buttons:
            self.btnPlotBode.setEnabled(True)
            self.btnPlotLGR.setEnabled(True)
            self.btnPlotNyquist.setEnabled(True)
            
        # Check current system choice and enable necessary itens:
        if (sysindex == 0): # LTI system 1 (without C(s))
            self.groupBoxC.setEnabled(False)
            self.sys.Type = 0
            # Disable C(s):
            self.sys.Cnum = [1]
            self.sys.Cden = [1]
            self.sys.Atualiza()            
        elif (sysindex == 1): # LTI system 2 (with C(s))
            self.sys.Type = 1
            self.groupBoxC.setEnabled(True)
            # Update system if C(s) group box is checked or not.
            self.onGroupBoxCcheck(self.groupBoxC.isChecked())
        elif (sysindex == 2): # LTI system 3 (with G(s) after W(s))
            self.sys.Type = 2
            # in this case, G(s) goes to G2(s) in Sistema class while G(s)=1/1
            self.sys.G2num = self.sys.Gnum
            self.sys.G2den = self.sys.Gden
            self.sys.Gnum = [1]
            self.sys.Gden = [1]
            self.sys.Atualiza()
            self.groupBoxC.setEnabled(True)
            self.onGroupBoxCcheck(self.groupBoxC.isChecked())
            self.onGroupBoxGcheck(self.groupBoxG.isChecked())
            # Update system if C(s) group box is checked or not.
#==============================================================================
#         elif (sysindex == 3): # Discrete time controller
#             self.sys.Type = 3
#             self.labelTk.setEnabled(True)
#             self.doubleSpinBoxTk.setEnabled(True)
#             self.labelPtTk.setEnabled(True)
#             self.spinBoxPtTk.setEnabled(True)
#             self.groupBoxC.setEnabled(True)
#             self.onGroupBoxCcheck(self.groupBoxC.isChecked())
#             self.doubleSpinBoxResT.setEnabled(False)
#             self.btnPlotBode.setEnabled(False)
#             self.btnPlotLGR.setEnabled(False)
#             self.btnPlotNyquist.setEnabled(False)            
#             self.groupBoxC.setTitle(_translate("MainWindow", "Controlador C(z)", None))
#==============================================================================
        elif (sysindex == 4): # Non-linear system
            self.sys.Type = 4
            self.groupBoxC.setEnabled(True)
            self.groupBoxH.setEnabled(False)
            self.onGroupBoxCcheck(self.groupBoxC.isChecked())
            self.lineEditGden.hide()
            # Disable buttons:
            self.btnPlotBode.setEnabled(False)
            self.btnPlotLGR.setEnabled(False)
            self.btnPlotNyquist.setEnabled(False)
            self.labelGden.hide()
            # Saving previous Gnum string:
            self.sys.GnumStr = str(self.lineEditGnum.text())
            self.lineEditGnum.setText(self.sys.sysInputString)
            self.onGnumChange(self.sys.sysInputString)
            self.groupBoxG.setTitle(_translate("MainWindow", "EDO não linear", None))
            self.labelGnum.setText(_translate("MainWindow", "f(y,u)=", None))
            self.lineEditGnum.setText(self.sys.sysInputString)
            self.onGnumChange(self.sys.sysInputString)
            self.groupBoxG.updateGeometry()
        else:
            QtGui.QMessageBox.information(self,_translate("MainWindow", "Aviso!", None), _translate("MainWindow", "Sistema ainda não implementado!", None))
            self.comboBoxSys.setCurrentIndex(self.currentComboIndex)
            return
        
        self.updateSystemSVG()
        self.statusBar().showMessage(_translate("MainWindow", "Sistema alterado.", None))
        self.currentComboIndex = sysindex

    
    def onSliderMove(self,value):
        """Slider change event. 
        This event is called also when setSliderPosition is called during 
        Kmax and Kmin changes. Changes in Kmax and Kmin only alters position
        of the slider and not the gain. This is why there is this test.
        """

        gain = float(value)*float((self.sys.Kmax)-(self.sys.Kmin))/float(self.sys.Kpontos) + self.sys.Kmin        
        self.sys.K = gain
        # Disconnect events to not enter in a event loop:
        QtCore.QObject.disconnect(self.doubleSpinBoxKlgr, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.disconnect(self.doubleSpinBoxK, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        # Update spinboxes
        self.doubleSpinBoxKlgr.setValue(gain)
        self.doubleSpinBoxK.setValue(gain)
        # Draw Closed Loop Poles:
        self.DrawCloseLoopPoles(gain)
        # Reconect events:
        QtCore.QObject.connect(self.doubleSpinBoxKlgr, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.connect(self.doubleSpinBoxK, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)      
        
    def onKmaxChange(self,value):
        #self.KmaxminChangeFlag = True # To signal onSliderMove that it is a Kmax change
        self.sys.Kmax = value
        self.updateSliderPosition()
    
    def onKminChange(self,value):
        #self.KmaxminChangeFlag = True # To signal onSliderMove that it is a Kmin change
        self.sys.Kmin = value
        self.updateSliderPosition() # update slider position, this call also the event slider move.
    
    def onKChange(self,value):
        # Save K value in the LTI system.
        self.sys.K = value
        # Disconnect events to not enter in a event loop:
        QtCore.QObject.disconnect(self.doubleSpinBoxKlgr, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.disconnect(self.doubleSpinBoxK, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        # Update spinboxes
        self.doubleSpinBoxKlgr.setValue(value)
        self.doubleSpinBoxK.setValue(value)
        # Draw Closed Loop Poles:
        self.DrawCloseLoopPoles(value)
        # Reconect events:
        QtCore.QObject.connect(self.doubleSpinBoxKlgr, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)
        QtCore.QObject.connect(self.doubleSpinBoxK, QtCore.SIGNAL("valueChanged(double)"), self.onKChange)        
        # Update slider position.
        self.updateSliderPosition()

    def onBtnSimul(self):
        
        self.sys.X0r = None
        self.sys.X0w = None
        
        self.statusBar().showMessage(_translate("MainWindow", "Simulando, aguarde...", None))
        # Create the input vectors r(t) and w(t):
        t,r,w = self.sys.CriaEntrada(0, self.doubleSpinBoxResT.value())
        self.sys.N = len(t)
        
        # Perform a time domain simulation:
        if (self.sys.Type < 3):
            y = self.sys.Simulacao(t, r, w)
        elif (self.sys.Type == 4):
            if (self.sys.NLsysParseString(self.sys.sysInputString) == 0):
                self.statusBar().showMessage(_translate("MainWindow", "Erro na função f(y,u)!", None))
                return
            self.sys.NLsysReset()
            #print self.sys.sysString
            y = self.sys.NLsysSimulate(r)
        elif (self.sys.Type == 3):
            print "Discrete simul Not ready yet"
            return
        
        self.statusBar().showMessage(_translate("MainWindow", "Simulação concluída.", None))
        self.mplSimul.axes.autoscale(True)        
        
        # Clear matplotlib toolbar history:
        self.mpltoolbarSimul._views.clear()
        self.mpltoolbarSimul._positions.clear()
        self.mpltoolbarSimul._update_view()        
        
        #self.mplSimul.figure.clf()
        self.mplSimul.axes.cla()
        self.mplSimul.axes.hold(True)
        #ax = self.mplSimul.figure.add_subplot(111)
        legend = []
        flag = 0

        if (self.checkBoxEntrada.isChecked()):
            self.mplSimul.axes.plot(t,r,'b')
            self.mplSimul.axes.plot([0, 0],[0,r[0]], label="_nolegend_", color='b')
            legend.append(_translate("MainWindow", "Entrada: u(t)", None))
            flag = 1
        if (self.checkBoxSaida.isChecked()):
            self.mplSimul.axes.plot(t,y,'r')
            legend.append(_translate("MainWindow", "Saída: y(t)", None))
            flag = 1
        if (self.checkBoxErro.isChecked()):
            self.mplSimul.axes.plot(t,r-y,'g')
            legend.append(_translate("MainWindow", "Erro: e(t)", None))
            flag = 1
        if (self.checkBoxPert.isChecked()):
            self.mplSimul.axes.plot(t,w,'m')
            legend.append(_translate("MainWindow", "Perturbação: w(t)", None))
            flag = 1
        
        if (flag == 0):
            self.statusBar().showMessage(_translate("MainWindow", "Nenhum sinal selecionado!", None))
            return
        
        self.mplSimul.axes.grid()
        
        ylim = self.mplSimul.axes.get_ylim()
        
        # Set a new y limit, adding 1/10 of the total.
        self.mplSimul.axes.set_ylim(ymax=(ylim[1]+(ylim[1]-ylim[0])/10))
        self.mplSimul.axes.set_xlim([0,t[-1]])
        
        # Add legend:
        self.mplSimul.axes.legend(legend, loc=0)
        self.mplSimul.axes.set_ylabel(_translate("MainWindow", "Valor", None))
        self.mplSimul.axes.set_xlabel(_translate("MainWindow", "Tempo [s]", None))
        self.mplSimul.axes.set_title(_translate("MainWindow", "Simulação no tempo", None))
        
        # Enable continue button:
        self.btnContinuar.setEnabled(True)
        
        
        self.mplSimul.draw()
        
    def onBtnContinue(self):
        """
        Continue simulation button
        """        
        
        Tinic = self.sys.tfinal
        
        # Create time and input vector:
        t,r,w = self.sys.CriaEntrada(Tinic, self.doubleSpinBoxResT.value(), 
                            self.sys.Rfinal, self.sys.Wfinal)
        self.sys.N = len(t)
        #r[0] = self.
        self.statusBar().showMessage(_translate("MainWindow", "Simulando, aguarde...", None))

        # Perform a time domain simulation:
        if (self.sys.Type < 3):
            y = self.sys.Simulacao(t, r, w)
        elif (self.sys.Type == 4):
            if (self.sys.NLsysParseString(self.sys.sysInputString) == 0):
                self.statusBar().showMessage(_translate("MainWindow", "Erro na função f(y,u)!", None))
                return
            #self.sys.NLsysReset()
            #print self.sys.sysString
            y = self.sys.NLsysSimulate(r)
        elif (self.sys.Type == 3):
            print "Discrete simul Not ready yet"
            return
        
        # Simulate the system:
        #y = self.sys.Simulacao(t, r, w)
        
        self.statusBar().showMessage(_translate("MainWindow", "Simulação concluída.", None))
        
        self.mplSimul.axes.autoscale(True)        
        
        legend = []
        
        flag = 0

        if (self.checkBoxEntrada.isChecked()):
            self.mplSimul.axes.plot(t,r,'b')
            # Draw line
            self.mplSimul.axes.plot([Tinic, Tinic],[y[0],r[0]], label="_nolegend_", color='b')
            legend.append(_translate("MainWindow", "Entrada: u(t)", None))
            flag = 1
        if (self.checkBoxSaida.isChecked()):
            self.mplSimul.axes.plot(t,y,'r')
            legend.append(_translate("MainWindow", "Saída: y(t)", None))
            flag = 1
        if (self.checkBoxErro.isChecked()):
            self.mplSimul.axes.plot(t,r-y,'g')
            legend.append(_translate("MainWindow", "Erro: e(t)", None))
            flag = 1
        if (self.checkBoxPert.isChecked()):
            self.mplSimul.axes.plot(t,w,'m')
            legend.append(_translate("MainWindow", "Perturbação: w(t)", None))
            flag = 1
        
        if (flag == 0):
            self.statusBar().showMessage(_translate("MainWindow", "Nenhum sinal selecionado!", None))
            return        
        
        self.mplSimul.axes.grid(True)
        
        ylim = self.mplSimul.axes.get_ylim()
        # Set a new y limit, adding 1/10 of the total.
        self.mplSimul.axes.set_ylim(ymax=(ylim[1]+(ylim[1]-ylim[0])/10))
        self.mplSimul.axes.set_xlim([0,t[-1]])
        # Add legend:
        self.mplSimul.axes.legend(legend, loc=0)
        
        # Draw the graphic:
        self.mplSimul.draw()

    
    def onBtnClearSimul(self):
        """
        Clear simulation graphic button
        """
        # Clear figure:
        #self.mplSimul.figure.clf()
        self.mplSimul.axes.cla()
        self.mplSimul.axes.set_xlim(0, self.sys.Tmax)
        self.mplSimul.axes.set_ylim(0, 1)
        self.mplSimul.axes.set_ylabel(_translate("MainWindow", "Valor", None))
        self.mplSimul.axes.set_xlabel(_translate("MainWindow", "Tempo [s]", None))
        self.mplSimul.axes.set_title(_translate("MainWindow", "Simulação no tempo", None))        
        self.mplSimul.axes.grid()
        self.mplSimul.draw()
        # Disable continue button:
        self.btnContinuar.setEnabled(False)
        
        # Reset initial conditions:
        self.sys.X0r = None
        self.sys.X0w = None
        
        # Reset non-linear system:
        self.sys.NLsysReset()
    
    def onSimluResChange(self,value):
        """
        Changed simulation resolution handler
        """
        if (value > 0):
            self.sys.delta_t = self.doubleSpinBoxResT.value()
            # Update total number of samples:
            self.sys.N = self.sys.Tmax/self.sys.delta_t
            # Update discrete time points per dT.
            QtCore.QObject.disconnect(self.spinBoxPtTk, QtCore.SIGNAL("valueChanged(int)"), self.onPointsTkChange)
            self.sys.Npts_dT = self.sys.dT/self.sys.delta_t
            self.spinBoxPtTk.setValue(int(self.sys.Npts_dT))
            QtCore.QObject.connect(self.spinBoxPtTk, QtCore.SIGNAL("valueChanged(int)"), self.onPointsTkChange)
            #
            
    def onPointsTkChange(self, value):
        """
        Changed number of points per dT in discrete time simul.
        """
        if (value > 0):
            self.sys.Npts_dT = value
            QtCore.QObject.disconnect(self.doubleSpinBoxResT, QtCore.SIGNAL("valueChanged(double)"), self.onSimluResChange)
            # Change simulation resolution system and UI:
            self.sys.delta_t = self.sys.dT/value
            self.sys.N = self.sys.Tmax/self.sys.delta_t
            self.doubleSpinBoxResT.setValue(self.sys.delta_t)
            QtCore.QObject.connect(self.doubleSpinBoxResT, QtCore.SIGNAL("valueChanged(double)"), self.onSimluResChange)
            
    def onTkChange(self, value):
        """
        Changed the number of the sample period (dT)
        """
        if (value > 0):
            self.sys.dT = value
            self.sys.NdT = int(self.sys.Tmax/value)
            # Change simulation resolution:
            QtCore.QObject.disconnect(self.doubleSpinBoxResT, QtCore.SIGNAL("valueChanged(double)"), self.onSimluResChange)
            # Change simulation resolution system and UI:
            self.sys.delta_t = value/self.sys.Npts_dT
            self.sys.N = self.sys.Tmax/self.sys.delta_t
            self.doubleSpinBoxResT.setValue(self.sys.delta_t)
            QtCore.QObject.connect(self.doubleSpinBoxResT, QtCore.SIGNAL("valueChanged(double)"), self.onSimluResChange)

            
        
    def onBtnLGR(self):
        """
        Plot LGR graphic.
        """
        self.statusBar().showMessage(_translate("MainWindow", "Plotando LGR...", None))
        
        # Clear matplotlib toolbar history:
        self.mpltoolbarLGR._views.clear()
        self.mpltoolbarLGR._positions.clear()
        self.mpltoolbarLGR._update_view() 
        # Plot LGR:
        self.sys.LGR(self.mplLGR.figure)
        
        self.statusBar().showMessage(_translate("MainWindow", "Concluído.", None))
        
        self.axesLGR = self.mplLGR.figure.gca()
        self.axesLGR.grid(True)
        self.axesLGR.set_xlabel(_translate("MainWindow", "Eixo real", None))
        self.axesLGR.set_ylabel(_translate("MainWindow", "Eixo imaginário", None))
        self.axesLGR.set_title(_translate("MainWindow", "Lugar Geométrico das raízes de C(s)*G(s)*H(s)", None))

        # Tenta apagar a instância dos pólos em malha fechada na figura. Se já
        # existirem, apaga, senão não faz nada.
        try:
            del self.polosLGR
        except AttributeError:
            pass        
        
        # Draw closed loop poles with current gain:
        self.DrawCloseLoopPoles(self.sys.K)
        
        # Forbidden regions:
        # GUI parameters:
        Ribd = abs(self.doubleSpinBoxRibd.value())
        Rebd = abs(self.doubleSpinBoxRebd.value())
        Imbd = abs(self.doubleSpinBoxImbd.value())
        
        xlimites = self.axesLGR.get_xlim()
        ylimites = self.axesLGR.get_ylim()
        
        if (abs(xlimites[0]-xlimites[1])<0.1):
            #xlimites[0] = xlimites[0]-1
            #xlimites[1] = xlimites[1]+1
            self.axesLGR.set_xlim((xlimites[0]-1,xlimites[1]+1))
            xlimites = self.axesLGR.get_xlim()

        if (abs(ylimites[0]-ylimites[1])<0.1):
            #ylimites[0] = ylimites[0]-1
            #ylimites[1] = ylimites[1]+1
            self.axesLGR.set_ylim((ylimites[0]-1,ylimites[1]+1))
            ylimites = self.axesLGR.get_ylim()


        if Rebd > 0:
            if Rebd < 0.5:
                inic = Rebd + 0.5
            else:
                inic = 0
            y = [ylimites[0],ylimites[1],ylimites[1],ylimites[0]]
            x = [-Rebd,-Rebd,inic,inic]
            self.axesLGR.fill(x,y,facecolor=(1,0.6,0.5),linewidth=0)            
        
        if Ribd > 0:
            # R = Ribd * I
            y = [0,ylimites[1],ylimites[1],0,ylimites[0],ylimites[0]]
            x = [0,-Ribd*ylimites[1],0,0,0,Ribd*ylimites[0]]
            self.axesLGR.fill(x,y,facecolor=(1,0.6,0.5),linewidth=0)            
        
        if Imbd > 0:
            x = [xlimites[0],xlimites[1],xlimites[1],xlimites[0]]
            y = [-Imbd,-Imbd,Imbd,Imbd]
            self.axesLGR.fill(x,y,facecolor=(1,0.6,0.5),linewidth=0)        
        
        self.mplLGR.draw()

    def onBtnLGRclear(self):
        """
        Clear figure of the Root Locus diagram. Button handler.
        """        
        # Clear figure:
        self.mplLGR.figure.clf()
        self.mplLGR.draw()
    
    def onResLGRchange(self,value):
        """
        Chage the number of LGR gain points (resolution).
        """
        self.sys.Kpontos = self.doubleSpinBoxLGRpontos.value()
        
    def DrawCloseLoopPoles(self,gain):
            
        # Calcula raízes do polinômio 1+k*TF(s):
        raizes = self.sys.RaizesRL(gain)
        txt = ''
        for r in raizes:
            if (txt == ''):
                txt = self.createRootString(r)
            else:
                txt = txt + '; ' + self.createRootString(r)
        
        if not self.sys.Hide:
            txt = _translate("MainWindow", "Pólos em MF: ", None) + txt
            self.statusBar().showMessage(txt)
        
        # Plotando pólos do sist. realimentado:
        
        try: # Se nenhum LGR foi traçado, não faz mais nada.
            self.polosLGR[0].set_xdata(numpy.real(raizes))
            self.polosLGR[0].set_ydata(numpy.imag(raizes))
        except AttributeError:
            try: # Se nenhum polo foi desenhado, desenha então:
                self.polosLGR = self.axesLGR.plot(numpy.real(raizes), numpy.imag(raizes),
                                'xb',ms=7,mew=3)
            except AttributeError:

                return
            else:
                self.mplLGR.draw()
        else:
            self.mplLGR.draw()

        finally:
            pass
        
        return        
    
    def onBtnNyquist(self):
        """
        Plot nyquist diagram Button handler
        """
        self.statusBar().showMessage(_translate("MainWindow", "Traçando Nyquist...", None))
        
        # Clear matplotlib toolbar history:
        self.mpltoolbarNyquist._views.clear()
        self.mpltoolbarNyquist._positions.clear()
        self.mpltoolbarNyquist._update_view()         
        
        self.sys.Nyquist(self.mplNyquist.figure,completo=self.checkBoxNyqNegFreq.isChecked(),comcirculo=self.checkBoxNyqCirc.isChecked())
        
        [ax] = self.mplNyquist.figure.get_axes()
        # Setting labels and title:
        ax.set_xlabel('$Re[KC(j\omega)G(j\omega)H(j\omega)]$')
        ax.set_ylabel('$Im[KC(j\omega)G(j\omega)H(j\omega)]$')
        ax.set_title('Diagrama de Nyquist')
        
        self.mplNyquist.draw()
        
        self.statusBar().showMessage(_translate("MainWindow", "Concluído.", None))

    
    def onBtnNyquistClear(self):
        """
        Clear figure of the Nyquist diagram. Button handler.
        """
        self.mplNyquist.figure.clf()
        self.mplNyquist.draw()
        pass
    
    def onNyquistFminChange(self, value):
        """
        Nyquist Fmin edited handler
        """
        self.sys.NyqFmin = self.doubleSpinFminNyq.value()

    def onNyquistFmaxChange(self, value):
        """
        Nyquist Fmax edited handler
        """
        self.sys.NyqFmax = self.doubleSpinFmaxNyq.value()
    
    def onNyquistResChange(self, value):
        """
        Nyquist Resolution edited handler
        """
        self.sys.NyqFpontos = self.doubleSpinNyqRes.value()
   
    
    def onBtnPlotBode(self):
        
        self.statusBar().showMessage(_translate("MainWindow", "Traçando Bode...", None))

        # Clear matplotlib toolbar history:
        self.mpltoolbarBode._views.clear()
        self.mpltoolbarBode._positions.clear()
        self.mpltoolbarBode._update_view()
        
        # Plotting Bode:
        self.sys.Bode(self.mplBode.figure)
        [ax1,ax2] = self.mplBode.figure.get_axes()
        # Ajusting labels e title:
        
        ax1.set_ylabel(_translate("MainWindow", "Magnitude [dB]", None))
        ax2.set_ylabel(_translate("MainWindow", "Fase [graus]", None))
        ax2.set_xlabel(_translate("MainWindow", "Frequência [Hz]", None))
        ax1.set_title(_translate("MainWindow", "Diagrama de Bode de K*C(s)*G(s)", None))
        
        self.mplBode.draw()
        
        self.statusBar().showMessage(_translate("MainWindow", "Concluído.", None))
    
    def onBtnBodeClear(self):
        # Clear Bode figure:

        self.mplBode.figure.clf()
        #self.mplSimul.axes.set_xlim(0, self.sys.Tmax)
        #self.mplSimul.axes.set_ylim(0, 1)
        #self.mplSimul.axes.set_ylabel(_translate("MainWindow", "Valor", None))
        #self.mplSimul.axes.set_xlabel(_translate("MainWindow", "Tempo [s]", None))
        #self.mplSimul.axes.set_title(_translate("MainWindow", "Simulação no tempo", None))        
        #self.mplSimul.axes.grid()
        self.mplBode.draw() 


    def onBodeFminChange(self,value):
        """
        Bode Fmin edited handler
        """
        self.sys.Fmin = self.doubleSpinFmin.value()


    def onBodeFmaxChange(self,value):
        """
        Bode Fmax edited handler
        """
        self.sys.Fmax = self.doubleSpinFmax.value()

    def onBodeResChange(self,value):
        """
        Bode Resolution edited handler
        """
        self.sys.Fpontos = self.doubleSpinBodeRes.value()

    def onTmaxChange(self,value):
        """
        Tmax edited handler
        """
        self.sys.Tmax = value
        # Update total number of samples:
        self.sys.N = self.sys.Tmax/self.sys.delta_t
        # Update spinboxes maximum values:
        self.doubleSpinBoxRtime.setMaximum(value)
        self.doubleSpinBoxWtime.setMaximum(value)
        self.doubleSpinBoxDeltaRtime.setMaximum(value)
        # Update the number of discrete sample periods:
        self.sys.NdT = int(self.sys.Tmax/self.sys.dT)

    def onRtimeChange(self,value):
        """
        r(t) input time edited handler
        """
        self.sys.InstRt = value
        
    def onRnoiseChange(self,value):
        """
        r(t) noise edited
        """
        self.sys.ruidoRt = value
    
    def onRvarChange(self, value):
        """
        r(t) input variation value changed
        """
        self.sys.RtVar = value

    def onRvarInstChange(self, value):
        """
        r(t) input variation time value changed
        """
        self.sys.RtVarInstant = value

    def onWtimeChange(self,value):
        """
        r(t) input time edited handler
        """
        self.sys.InstWt = value

    def onWnoiseChange(self,value):
        """
        w(t) noise edited
        """
        self.sys.ruidoWt = value
    
    def onRvalueChange(self,value):
        """
        r(t) string input edited handler
        """
        if not value:
            self.lineEditRvalue.setStyleSheet("QLineEdit { background-color: rgb(255, 170, 170) }")
            return
        else:
            self.lineEditRvalue.setStyleSheet("QLineEdit { background-color: rgb(95, 211, 141) }")
        
        value.replace(',','.')        
        
        #if (int(value) == 2):
        #    self.lineEditRvalue.setStyleSheet("QLineEdit { background-color: yellow }")
        self.sys.Rt = str(value)
 

    def onWvalueChange(self,value):
        """
        r(t) string input edited handler
        """

        if not value:
            self.lineEditWvalue.setStyleSheet("QLineEdit { background-color: rgb(255, 170, 170) }")
            return
        else:
            self.lineEditWvalue.setStyleSheet("QLineEdit { background-color: rgb(95, 211, 141) }")
        
        value.replace(',','.')   
        
        self.sys.Wt = str(value)

    def onGroupBoxCcheck(self,flag):
        
        if (flag == False):
            self.statusBar().showMessage(_translate("MainWindow", "C(s) desativada.", None))
            self.sys.Cnum = [1]
            self.sys.Cden = [1]
            self.sys.Atualiza()
        else:
            self.onCnumChange(self.lineEditCnum.text())
            self.onCdenChange(self.lineEditCden.text())
            self.statusBar().showMessage(_translate("MainWindow", "C(s) ativada.", None))
    
    def onGroupBoxGcheck(self,flag):
        
        if (flag == False):
            self.statusBar().showMessage(_translate("MainWindow", "G(s) desativada.", None))
            self.sys.Gnum = [1]
            self.sys.Gden = [1]
            self.sys.G2num = [1]
            self.sys.G2den = [1]
            self.sys.Atualiza()
        else:
            self.onGnumChange(self.lineEditGnum.text())
            self.onGdenChange(self.lineEditGden.text())
            self.statusBar().showMessage(_translate("MainWindow", "G(s) ativada.", None))
            
    def onGroupBoxHcheck(self,flag):
        
        if (flag == False):
            self.statusBar().showMessage(_translate("MainWindow", "H(s) desativada.", None))
            self.sys.Hnum = [1]
            self.sys.Hden = [1]
            self.sys.Atualiza()
        else:
            self.onHnumChange(self.lineEditHnum.text())
            self.onHdenChange(self.lineEditHden.text())
            self.statusBar().showMessage(_translate("MainWindow", "H(s) ativada.", None))

    def onGroupBoxWcheck(self,flag):
        
        if (flag == False):
            self.statusBar().showMessage(_translate("MainWindow", "Perturbação desativada.", None))
            self.sys.Wt = '0'
            self.sys.InstWt = 0
            self.sys.ruidoWt = 0
            self.checkBoxPert.setDisabled(True)
        else:
            self.statusBar().showMessage(_translate("MainWindow", "Perturbação ativada.", None))
            self.sys.Wt = str(self.lineEditWvalue.text())
            self.sys.InstWt = self.doubleSpinBoxWtime.value()
            self.sys.ruidoWt = self.doubleSpinBoxWnoise.value()
            self.checkBoxPert.setDisabled(False)
            

    def onGnumChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditGnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
        
        # If is a linear or discrete system, uses G(s):
        if (self.sys.Type < 4):
            Gnum = self.checkTFinput(value)
            
            if (Gnum == 0):
                # Change color ro red:
                self.lineEditGnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            else:
                # Change color to green:
                self.lineEditGnum.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
                self.sys.GnumStr = str(value)
                if self.sys.Type == 2:
                    self.sys.G2num = Gnum
                else:
                    self.sys.Gnum = Gnum
                self.sys.Atualiza()
        elif (self.sys.Type == 4):
            # Parse and check NL system input string:
            sysstr = self.sys.NLsysParseString(str(value))
            
            if (sysstr):
                # Change color to green:
                self.statusBar().showMessage(_translate("MainWindow", "Expressão válida!", None))
                self.lineEditGnum.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            else:
                # Wrong input, change color ro red:
                self.statusBar().showMessage(_translate("MainWindow", "Expressão inválida!", None))
                self.lineEditGnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
                
    
    def onGdenChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditGden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
            
        Gden = self.checkTFinput(value)
        
        if (Gden == 0):
            self.lineEditGden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
        else:
            self.lineEditGden.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            self.sys.GdenStr = str(value)
            if self.sys.Type == 2:
                self.sys.G2den = Gden
            else:
                self.sys.Gden = Gden
            self.sys.Atualiza()

    def onCnumChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditCnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
            
        Cnum = self.checkTFinput(value)
        
        if (Cnum == 0):
            self.lineEditCnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
        else:
            self.lineEditCnum.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            self.sys.CnumStr = str(value)
            self.sys.Cnum = Cnum
            self.sys.Atualiza()
    
    def onCdenChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditCden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
            
        Cden = self.checkTFinput(value)
        
        if (Cden == 0):
            self.lineEditCden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
        else:
            self.lineEditCden.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            self.sys.CdenStr = str(value)
            self.sys.Cden = Cden
            self.sys.Atualiza()  
      
    def onHnumChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditHnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
            
        Hnum = self.checkTFinput(value)
        
        if (Hnum == 0):
            self.lineEditHnum.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
        else:
            self.lineEditHnum.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            self.sys.HnumStr = str(value)
            self.sys.Hnum = Hnum
            self.sys.Atualiza()
    
    def onHdenChange(self,value):
        """
        When user enters a character.
        """
        if not value:
            self.lineEditHden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
            return
            
        Hden = self.checkTFinput(value)
        
        if (Hden == 0):
            self.lineEditHden.setStyleSheet("QLineEdit { background-color:  rgb(255, 170, 170) }")
        else:
            self.lineEditHden.setStyleSheet("QLineEdit { background-color:  rgb(95, 211, 141) }")
            self.sys.HdenStr = str(value)
            self.sys.Hden = Hden
            self.sys.Atualiza()
    
    def checkTFinput(self, value):
        """
        Check if input string is correct.
        
        Return 0 if it has an error.
        Otherwise, returns a list with polynomial coefficients
        """
        value.remove(' ') # remove spaces
        value.replace(',','.') # change , to .
        value.replace(')(',')*(') # insert * between parentesis
        
        retorno = None
        
        if value.startsWith('['):
            try:
                retorno = eval(str(value))
            except:
                retorno = 0
        else:
            try:
                equacao = utils.parseexpr(str(value))
                retorno = equacao.c.tolist()
                #self.lineEditRvalue.setStyleSheet("QLineEdit { background-color: green }")
            except:
                #self.lineEditRvalue.setStyleSheet("QLineEdit { background-color: red }")
                retorno = 0
        if retorno == 0:
            self.statusBar().showMessage(_translate("MainWindow", "Expressão inválida.", None))
        else:
            self.statusBar().showMessage(_translate("MainWindow", "Expressão válida.", None))
        
        return retorno

    
    def updateSliderPosition(self):
        position = (float(self.sys.Kpontos) * (self.sys.K - self.sys.Kmin))/(abs(self.sys.Kmax)+abs(self.sys.Kmin))
        # Disconnect events to not enter in a event loop:
        QtCore.QObject.disconnect(self.verticalSliderK, QtCore.SIGNAL("valueChanged(int)"), self.onSliderMove)
        self.verticalSliderK.setSliderPosition(int(position))
        QtCore.QObject.connect(self.verticalSliderK, QtCore.SIGNAL("valueChanged(int)"), self.onSliderMove)
    
    def updateSystemSVG(self):
        svg_file_name = ''        
        
        if (self.sys.Type == 0): # LTI system 1 (without C(s))
            if self.sys.Malha == 'Fechada':
                svg_file_name = 'diagram1Closed.svg'
            else:
                svg_file_name = 'diagram1Opened.svg'
        elif (self.sys.Type == 1): # LTI system 2 (with C(s))
            if self.sys.Malha == 'Fechada':
                svg_file_name = 'diagram2Closed.svg'
            else:
                svg_file_name = 'diagram2Opened.svg'
        elif (self.sys.Type == 2): # LTI system 3 (with C(s) and G(s) after W(s))
            if self.sys.Malha == 'Fechada':
                svg_file_name = 'diagram3Closed.svg'
            else:
                svg_file_name = 'diagram3Opened.svg'
        elif (self.sys.Type == 3):
            if self.sys.Malha == 'Fechada':
                svg_file_name = 'diagram4Closed.svg'
            else:
                svg_file_name = 'diagram4Opened.svg'
        elif (self.sys.Type == 4):
            if self.sys.Malha == 'Fechada':
                svg_file_name = 'diagram5Closed.svg'
            else:
                svg_file_name = 'diagram5Opened.svg'
        else:
            self.statusBar().showMessage(_translate("MainWindow", "Sistema ainda não implementado.", None))
            return

        # Load svg file.
        svg_file = QtCore.QFile(svg_file_name)
        if not svg_file.exists():
            QtGui.QMessageBox.critical(self, "Open SVG File",
                                       "Could not open file '%s'." % svg_file_name)
            self.outlineAction.setEnabled(False)
            self.backgroundAction.setEnabled(False)
            return
        # Update svg image:
        self.scene.clear()
        #self.graphicsView.resetTransform()
        self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())
        #self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        #self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.scene.addItem(self.svgItem)
    
    def onAboutAction(self):
        QtGui.QMessageBox.about(self,"Sobre o LabControle2", MESSAGE)
        
    #def onSysInfoAction(self):
    #    dialog = QtGui.QDialog()
    #    dialog.ui = DialogSysInfo.Ui_DialogSysInfo()
    #    dialog.ui.setupUi(dialog)
    #    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    #    dialog.exec_()
    
    def onCalcAction(self):
        p=subprocess.Popen('calc.exe')
    
    def onSaveAction(self):
        """
        Save system data in an external file with encrypted data.
        
        If the extension of the file is dat, system data is stored with hide flag = False
        If the extension is tst the hide flag is True.
        """
        fileName = QtCore.QString()
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                _translate("MainWindow", "Salvar sistema", None),
                                "sisXX",_translate("MainWindow", "Arquivos LabControle Normal (*.LCN);;Arquivos LabControle Oculto (*.LCO)", None))

        hide = False
        

        if fileName.endsWith("LCN"):
            hide = False
            #pickle.dump(expSys, open(fileName, "wb" ),pickle.HIGHEST_PROTOCOL)
            
        elif fileName.endsWith("LCO"):
            hide = True
        else:
            self.statusBar().showMessage(_translate("MainWindow", "Tipo de arquivo não reconhecido.", None))
            return
        
        expSys = ExportSystem()
        expSys.Gnum = self.lineEditGnum.text()
        expSys.Gden = self.lineEditGden.text()
        expSys.Cnum = self.lineEditCnum.text()
        expSys.Cden = self.lineEditCden.text()
        expSys.Hnum = self.lineEditHnum.text()
        expSys.Hden = self.lineEditHden.text()
        expSys.K = self.doubleSpinBoxK.value()
        expSys.Type = self.sys.Type
        expSys.Malha = self.sys.Malha
        expSys.Hide = hide
        # Store groupbox checked status:
        expSys.Genabled = self.groupBoxG.isChecked()
        expSys.Cenabled = self.groupBoxC.isChecked()
        expSys.Henabled = self.groupBoxH.isChecked()
        
        # Pickle object into a string:
        temp = pickle.dumps(expSys,1)
        # Encode string:
        temp1 = base64.b64encode(temp)
        # Write encoded string to disk:
        f = open(fileName,"wb")
        f.write(temp1)
        f.close()
        
        self.statusBar().showMessage(_translate("MainWindow", "Sistema salvo.", None))
        
    def onLoadAction(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                _translate("MainWindow", "Abrir arquivo de sistema", None),
                'sys',
                _translate("MainWindow", "Arquivos LabControle (*.LCN *.LCO)", None))
        
        if not fileName:
            return
        
        expSys = ExportSystem()
        
        # Read encoded string from file:
        f = open(fileName, 'rb')
        temp1 = f.read()
        f.close()
        # Decode string:
        temp = base64.b64decode(temp1)
        # Unpickle object from string:
        expSys = pickle.loads(temp)
        
        self.sys.Hide = expSys.Hide        
        
        if expSys.Hide == False:
            self.labelHide.setText('')
            # Update feedback switch
            if expSys.Malha == 'Aberta':
                self.radioBtnOpen.setChecked(True)
            else:
                self.radioBtnClose.setChecked(True)            
            # Update system type and SVG:
            self.sys.Type = expSys.Type
            self.sys.Malha = expSys.Malha        
            self.comboBoxSys.setCurrentIndex(expSys.Type)
            self.onChangeSystem(expSys.Type)
            # Update groupboxes checkboxes:
            self.groupBoxG.setChecked(expSys.Genabled)
            self.groupBoxC.setChecked(expSys.Cenabled)
            self.groupBoxH.setChecked(expSys.Henabled)
            # Update UI and call the callbacks to update system.
            self.lineEditGnum.setText(expSys.Gnum)
            self.onGnumChange(expSys.Gnum)
            self.lineEditGden.setText(expSys.Gden)
            self.onGdenChange(expSys.Gden)
            self.lineEditCnum.setText(expSys.Cnum)
            self.onCnumChange(expSys.Cnum)
            self.lineEditCden.setText(expSys.Cden)
            self.onCdenChange(expSys.Cden)
            self.lineEditHnum.setText(expSys.Hnum)
            self.onHnumChange(expSys.Hnum)
            self.lineEditHden.setText(expSys.Hden)
            self.onHdenChange(expSys.Hden)
            
            # Update gain
            self.doubleSpinBoxK.setValue(expSys.K)
            # Enable or re-enable group boxes:
            self.groupBoxG.setEnabled(True)
            self.groupBoxC.setEnabled(True)
            self.groupBoxH.setEnabled(True)
            # Re-enable Root Locus button:
            self.btnPlotLGR.setEnabled(True)
            self.comboBoxSys.setEnabled(True)
        elif expSys.Hide == True:
            self.labelHide.setText(_translate("MainWindow", "Modo Oculto", None))
            # Update feedback switch
            if expSys.Malha == 'Aberta':
                self.radioBtnOpen.setChecked(True)
            else:
                self.radioBtnClose.setChecked(True)                 
            # Update system type and SVG:                        
            self.sys.Type = expSys.Type
            self.sys.Malha = expSys.Malha
            self.comboBoxSys.setCurrentIndex(expSys.Type)
            self.onChangeSystem(expSys.Type)
            # Update groupboxes checkboxes:
            self.groupBoxG.setChecked(expSys.Genabled)
            self.groupBoxC.setChecked(expSys.Cenabled)
            self.groupBoxH.setChecked(expSys.Henabled)            

            # Call the callbacks to update system.
            self.onGnumChange(expSys.Gnum)
            self.onGdenChange(expSys.Gden)
            self.onCnumChange(expSys.Cnum)
            self.onCdenChange(expSys.Cden)
            self.onHnumChange(expSys.Hnum)
            self.onHdenChange(expSys.Hden)
            
            # Update gain
            self.doubleSpinBoxK.setValue(expSys.K)
            
            #self.onChangeSystem(expSys.Type)
       

            # Update UI:
            self.lineEditGnum.setText('*****')
            self.lineEditGden.setText('*****')
            self.lineEditCnum.setText('*****')
            self.lineEditCden.setText('*****')
            self.lineEditHnum.setText('*****')
            self.lineEditHden.setText('*****')
            # Disable groupboxes:
            self.groupBoxG.setEnabled(False) #setHidden
            self.groupBoxC.setEnabled(False)
            self.groupBoxH.setEnabled(False)
            # Disable Root Locus button:
            self.btnPlotLGR.setEnabled(False)

            # Disable change system combo box:
            self.comboBoxSys.setEnabled(False)
        
    def onResetAction(self):
        self.labelHide.setText('')
        self.radioBtnOpen.setChecked(True)        
        self.sys.Type = 0
        self.sys.Malha = 'Aberta'
        self.comboBoxSys.setCurrentIndex(0)
        self.onChangeSystem(0)
        self.groupBoxG.setEnabled(True)
        self.groupBoxC.setEnabled(True)
        self.groupBoxH.setEnabled(True)
        self.groupBoxC.setChecked(False)
        self.lineEditGnum.setText(QtCore.QString('2*s+10'))
        self.onGnumChange(QtCore.QString('2*s+10'))
        self.lineEditGden.setText(QtCore.QString('1*s^2+2*s+10'))
        self.onGdenChange(QtCore.QString('1*s^2+2*s+10'))
        self.lineEditCnum.setText(QtCore.QString('1'))
        self.onCnumChange(QtCore.QString('1'))
        self.lineEditCden.setText(QtCore.QString('1'))
        self.onCdenChange(QtCore.QString('1'))
        self.lineEditHnum.setText(QtCore.QString('1'))
        self.onHnumChange(QtCore.QString('1'))
        self.lineEditHden.setText(QtCore.QString('1'))
        self.onHdenChange(QtCore.QString('1'))
        self.doubleSpinBoxK.setValue(1)
        self.btnPlotLGR.setEnabled(True)
        self.comboBoxSys.setEnabled(True)

    def onTabChange(self, index):
        # Clearing the lists:
        self.listWidgetCLpoles.clear()
        self.listWidgetOLpoles.clear()
        self.listWidgetOLzeros.clear()
        self.listWidgetRLpoints.clear()
        
        if (self.sys.Hide == True or self.sys.Type > 2):
            txt = _translate("MainWindow", "Desabilitado", None)
            item = QtGui.QListWidgetItem()
            item.setText(txt)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.listWidgetCLpoles.addItem(item)
            item = QtGui.QListWidgetItem()
            item.setText(txt)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.listWidgetOLpoles.addItem(item)
            item = QtGui.QListWidgetItem()
            item.setText(txt)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.listWidgetOLzeros.addItem(item)
            item = QtGui.QListWidgetItem()
            item.setText(txt)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.listWidgetRLpoints.addItem(item)
            return
            
        # Check if SysInfo tab:
        if (index == 5):
            # Closed loop poles:
            rootsCL = self.sys.RaizesRL(self.sys.K)
            for root in rootsCL:
                item = QtGui.QListWidgetItem()
                item.setText(self.createRootString(root))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.listWidgetCLpoles.addItem(item)
            
            rootsOL = self.sys.RaizesOL()
            for root in rootsOL:
                item = QtGui.QListWidgetItem()
                item.setText(self.createRootString(root))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.listWidgetOLpoles.addItem(item)
                
            zerosOL = self.sys.ZerosOL()
            for zero in zerosOL:
                item = QtGui.QListWidgetItem()
                item.setText(self.createRootString(zero))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.listWidgetOLzeros.addItem(item)
            
            pontos, ganhos = self.sys.PontosSeparacao()
            i = 0
            for ponto in pontos:
                item = QtGui.QListWidgetItem()
                item.setText(self.createRootString(ponto) + " com Kc =  %0.3f" %(ganhos[i]))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.listWidgetRLpoints.addItem(item)
                i = i + 1
                
    # Given a numpy number (complex or not) return a formatted string.
    def createRootString(self, root):
        root_str = ''
        r_real = numpy.real(root)
        r_imag = numpy.imag(root)
        
        if (r_imag == 0):
            root_str = str(numpy.around(r_real, decimals=3))
        else:
            if (r_imag > 0):
                root_str = str(numpy.around(r_real, decimals=3)) + ' + j'+ str(numpy.around(r_imag, decimals=3))
            else:
                root_str = str(numpy.around(r_real, decimals=3)) + ' - j'+ str(numpy.around(abs(r_imag), decimals=3))
        
        return root_str
    
        
        


class ExportSystem:
    
    Gnum = QtCore.QString()
    Gden = QtCore.QString()
    Cnum = QtCore.QString()
    Cden = QtCore.QString()
    Hnum = QtCore.QString()
    Hden = QtCore.QString()
    Genabled = True
    Cenabled = False
    Henabled = False
    K = 1.0
    Type = 0
    Malha = 'Aberta'
    Hide = False

        
if __name__ == '__main__':
    app = QtGui.QApplication([])
    locale = QtCore.QLocale.system().name()
    # If not portuguese, instal english translator:
    if (locale != 'pt_BR' and locale != 'pt_PT'):
        translator = QtCore.QTranslator()
        translator.load("LabControle2_en.qm")
        app.installTranslator(translator)
    
    win = LabControle2()
    win.show()
    app.exec_()
