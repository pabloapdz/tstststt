# app.py
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from sismograma import Sismograma
from visao_geral import VisaoGeral
import sys
import os
import qdarkstyle

def main():
    login = 'PABLO'
    app = QApplication(sys.argv)

    janela = QMainWindow()
    janela.setWindowTitle("Interface de Engenharia")
    janela.setGeometry(100, 100, 800, 600)

    abas = QTabWidget()
    janela.setCentralWidget(abas)

    sismograma = Sismograma.create()
    abas.addTab(sismograma, "Sismograma")

    #histograma = Histograma.create()
    #abas.addTab(histograma, "Histograma")

    visao_geral = VisaoGeral(login)
    abas.addTab(visao_geral, "Visão Geral")
    visao_geral.estacao_selecionada.connect(sismograma.atualizar_selecao_ponto)

    # Comente a linha abaixo
    os.environ["QT_API"] = "pyside6"
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    janela.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
