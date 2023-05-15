from PySide6.QtCore import Qt, QDateTime, QUrl
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QGraphicsView, QSizePolicy, QGroupBox, QCheckBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
import sys
from PySide6.QtWebEngineCore import QWebEngineSettings
import mysql.connector
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QSplitterHandle

# Importar as bibliotecas necessárias para os gráficos
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import FormatStrFormatter
import matplotlib.dates as mdates


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class InvisibleSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet("background-color:black;")

    def paintEvent(self, event):
        pass

class CustomSplitter(QSplitter):
    def createHandle(self):
        return InvisibleSplitterHandle(self.orientation(), self)

class Sismograma(QWidget):
    def __init__(self):
        super().__init__()

        self.testes = True

        # Adicione essa linha para criar o atributo resultado
        self.resultado = []

        # Layout principal
        layout_principal = QVBoxLayout()

        # Divisores
        splitter_principal = QSplitter(Qt.Horizontal)
        splitter_waveform = QSplitter(Qt.Vertical)
        splitter_dispersao = QSplitter(Qt.Vertical)
        splitter_histograma = QSplitter(Qt.Horizontal)
        splitter_histograma_2 = QSplitter(Qt.Vertical)

        

        # Seção do mapa
        self.imagem = QWebEngineView()
        self.imagem.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        web_page = self.imagem.page()
        web_page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        mapa_html_file = self.gerar_mapa_html()
        self.imagem.load(QUrl.fromLocalFile(mapa_html_file))
        splitter_principal.addWidget(self.imagem)

        
        # Seção 1.2 - 1° Gráfico waveform
        self.figura_grafico2 = plt.figure(facecolor='#19232d')
        self.grafico2 = FigureCanvas(self.figura_grafico2)
        self.grafico2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico2.setFixedHeight(240)
        splitter_waveform.addWidget(self.grafico2)  # Adicione o segundo gráfico ao QSplitter


        # Seção 1.2 - 2° Gráfico waveform
        self.figura_grafico2_wf = plt.figure(facecolor='#19232d')
        self.grafico2_wf = FigureCanvas(self.figura_grafico2_wf)
        self.grafico2_wf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico2_wf.setFixedHeight(270)
        splitter_waveform.addWidget(self.grafico2_wf)  # Adicione o segundo gráfico ao QSplitter


        # Seção 2 - Gráfico dispersao 1wf
        self.figura_grafico_1_disp = plt.figure(facecolor='#19232d')
        self.grafico_1_disp = FigureCanvas(self.figura_grafico_1_disp)
        self.grafico_1_disp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico_1_disp.setFixedHeight(240)
        splitter_dispersao.addWidget(self.grafico_1_disp)  # Adicione o segundo gráfico ao QSplitter

        # Seção 2 - Gráfico dispersao 2wf
        self.figura_grafico_2_disp = plt.figure(facecolor='#19232d')
        self.grafico_2_disp = FigureCanvas(self.figura_grafico_2_disp)
        self.grafico_2_disp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico_2_disp.setFixedHeight(270)
        splitter_dispersao.addWidget(self.grafico_2_disp)  # Adicione o segundo gráfico ao QSplitter




        # Seção 2 - GRÁFICO HISTOGRAMA
        self.figura_grafico1 = plt.figure(facecolor='#19232d')
        self.grafico1 = FigureCanvas(self.figura_grafico1)
        self.grafico1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico1.setFixedHeight(360)
        splitter_histograma.addWidget(self.grafico1)

        # Seção 2 - GRÁFICO HISTOGRAMA
        self.figura_grafico2_2 = plt.figure(facecolor='#19232d')
        self.grafico2_2 = FigureCanvas(self.figura_grafico2_2)
        self.grafico2_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grafico2_2.setFixedHeight(360)
        splitter_histograma.addWidget(self.grafico2_2)



        # Adicione o QSplitter do mapa e do segundo gráfico ao QSplitter principal
        splitter_principal.addWidget(splitter_waveform)
        splitter_principal.addWidget(splitter_dispersao)

        # Adicione o QSplitter principal ao layout principal
        layout_principal.addWidget(splitter_principal)

        # Adicione o QSplitter principal ao layout principal
        layout_principal.addWidget(splitter_histograma)
        #layout_principal.addWidget(splitter_histograma_2)

        # Espaçamento
        layout_principal.addSpacing(10)

        # Adicionar o QLabel para exibir o texto intermediário
        self.texto_intermediario = QLabel()
        layout_principal.addWidget(self.texto_intermediario)

        # Seleção de ponto e tempo
        layout_selecao = QHBoxLayout()
        self.selecao_ponto = QComboBox()
        self.selecao_ponto.addItems(["ESTACAO 1", "ESTACAO 2", "ESTACAO 3", "ESTACAO 4", "ESTACAO 5"])
        layout_selecao.addWidget(self.selecao_ponto)
    
        self.selecao_tempo = QComboBox()
        self.selecao_tempo.addItems(["Uma hora", "Um minuto", "Um dia"])
        layout_selecao.addWidget(self.selecao_tempo)
    
        layout_principal.addLayout(layout_selecao)
    
        self.setLayout(layout_principal)
    
        self.selecao_ponto.currentIndexChanged.connect(self.atualizar_graficos)
        self.selecao_tempo.currentIndexChanged.connect(self.atualizar_graficos)
    
        self.atualizar_texto_intermediario()
        self.atualizar_graficos()
        self.inicializar_temporizador()
        self.personalizar_cores()

    
    @staticmethod
    def create():
        return Sismograma()

    def atualizar_selecao_ponto(self, novo_ponto):
        index = self.selecao_ponto.findText(novo_ponto)
        if index != -1:
            self.selecao_ponto.setCurrentIndex(index)
            # Atualize o gráfico do sismograma aqui, se necessário.

    def personalizar_cores(self):
        # Personalizar as cores dos gráficos e mapa
        import matplotlib
        matplotlib.rcParams['text.color'] = 'white'
        matplotlib.rcParams['axes.labelcolor'] = 'white'
        matplotlib.rcParams['xtick.color'] = 'white'
        matplotlib.rcParams['ytick.color'] = 'white'
        matplotlib.rcParams['axes.edgecolor'] = 'white'
        matplotlib.rcParams['figure.facecolor'] = 'white'
        matplotlib.rcParams['axes.facecolor'] = 'white'
    
    def atualizar_texto_intermediario(self):
        ponto_escolhido = self.selecao_ponto.currentText()
        tempo_escolhido = self.selecao_tempo.currentText()
        data_hora_atual = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm")
        texto = f"{tempo_escolhido} a partir de {data_hora_atual} {ponto_escolhido}"
        self.texto_intermediario.setText(texto)
        self.atualizar_graficos()



    def atualizar_graficos(self):
    
        def buscar_estacao(serial_number):
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="CARSTE"
            )
            cursor = conexao.cursor()
    
            estacao = None
            for i in range(1, 11):
                coluna = f"SERIAL ESTACAO {i}"
                cursor.execute(f"SELECT `{coluna}` FROM usuarios WHERE `{coluna}` = {serial_number}")
                resultado = cursor.fetchone()
                if resultado:
                    estacao = f"ESTACAO {i}"
                    break
    
            conexao.close()
            return estacao
    
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="CARSTE"
        )
    
        cursor = conexao.cursor()
    
        ponto_escolhido = self.selecao_ponto.currentText()
        tempo_escolhido = self.selecao_tempo.currentText()
    
        consulta_sql = f"SELECT `SerialNumber`, `Transversal`, `Vertical`, `Longitudinal`, `EventTime` FROM dados_histograma"
    
        cursor.execute(consulta_sql)
        resultado = cursor.fetchall()
    
        self.figura_grafico1.clear()
        ax_transversal = self.figura_grafico1.add_subplot(3, 1, 1)
        ax_vertical = self.figura_grafico1.add_subplot(3, 1, 2)
        ax_longitudinal = self.figura_grafico1.add_subplot(3, 1, 3)
    
        tempos = []
        valores_transversal = []
        valores_vertical = []
        valores_longitudinal = []
    
        for row in resultado:
            serial_number, transversal, vertical, longitudinal, event_time = row
            estacao = buscar_estacao(serial_number)
    
            if estacao == ponto_escolhido:
                tempos.append(event_time)
                valores_transversal.append(transversal)
                valores_vertical.append(vertical)
                valores_longitudinal.append(longitudinal)
    
        largura_barras = 0.5
        indices = np.arange(len(tempos))
    
        ax_transversal.bar(indices, valores_transversal, width=largura_barras, color='blue', edgecolor='black')
        ax_vertical.bar(indices, valores_vertical, width=largura_barras, color='green', edgecolor='black')
        ax_longitudinal.bar(indices, valores_longitudinal, width=largura_barras, color='red', edgecolor='black')

        ax_transversal.set_ylabel('Transversal')
        ax_transversal.set_xticklabels([])
    
        ax_vertical.set_ylabel('Vertical')
        ax_vertical.set_xticklabels([])
    
        ax_longitudinal.set_ylabel('Longitudinal')
    
        for ax in [ax_longitudinal]:
            ax.set_xticks(indices[::5])
            ax.set_xticklabels([mdates.num2date(mdates.datestr2num(t.strftime('%Y-%m-%d %H:%M:%S'))).strftime('%H:%M:%S') for t in tempos[::5]], fontsize=6)
            ax.tick_params(axis='x', which='major', labelsize=6, rotation=45)
    
        maximo_valor = max(max(valores_transversal), max(valores_vertical), max(valores_longitudinal))





        self.grafico1.draw()
    
    
        #conexao.close()

    
        # Atualizar o gráfico 2
        self.figura_grafico2.clear()
    
        # Consultar os dados da tabela `dados_waveform`
        cursor = conexao.cursor()
        consulta_waveform = "SELECT `SerialNumber`, `EventTime`, `Transversal`, `Longitudinal`, `Vertical` FROM dados_waveform ORDER BY `EventTime` DESC"
        cursor.execute(consulta_waveform)
        resultado_waveform = cursor.fetchall()        
        if resultado_waveform:
            recent_event_time = resultado_waveform[0][1]
            recent_waveform_data = [row for row in resultado_waveform if row[1] == recent_event_time]        
            # Verificar se a estação do SerialNumber corresponde à estação selecionada
            serial_number = recent_waveform_data[0][0]
            estacao = buscar_estacao(serial_number)
            if estacao != ponto_escolhido:
                print(f"Estação do SerialNumber {serial_number} ({estacao}) não corresponde à estação selecionada ({ponto_escolhido}).")
                self.figura_grafico2.clear()
                self.grafico2.draw()
            else:
                recent_waveform_data = np.array(recent_waveform_data)
                transversal = recent_waveform_data[:, 2].astype(float)
                longitudinal = recent_waveform_data[:, 3].astype(float)
                vertical = recent_waveform_data[:, 4].astype(float)
    
            
                num_linhas = len(recent_waveform_data)
                delta_t = 10 / num_linhas
                eixo_x = np.arange(0, 10, delta_t)
            
                resultante = np.sqrt(transversal**2 + longitudinal**2 + vertical**2)
            
                # Gráfico de waveform
                ax_grafico2 = self.figura_grafico2.add_subplot(4, 1, 1)
                ax_grafico2.plot(eixo_x, transversal, color='red')
                ax_grafico2.set_ylabel("T")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2.add_subplot(4, 1, 2)
                ax_grafico2.plot(eixo_x, longitudinal, color='red')
                ax_grafico2.set_ylabel("L")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2.add_subplot(4, 1, 3)
                ax_grafico2.plot(eixo_x, vertical, color='red')
                ax_grafico2.set_ylabel("V")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2.add_subplot(4, 1, 4)
                ax_grafico2.plot(eixo_x, resultante, color='black')
                ax_grafico2.set_ylabel("VS")
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
    
                # Ajuste o espaçamento entre as subplots
                self.figura_grafico2.subplots_adjust(hspace=0.5, bottom=0.15)  # Ajuste o espaçamento vertical entre as subplots
            
                # Atualizar o gráfico 2
                self.grafico2.draw()
    

        # Atualizar o 2° gráfico de waveform
        self.figura_grafico2_wf.clear()
    
        # Consultar os dados da tabela `dados_waveform`
        consulta_waveform = "SELECT `SerialNumber`, `EventTime`, `Transversal`, `Longitudinal`, `Vertical` FROM dados_waveform ORDER BY `EventTime` ASC"
        cursor.execute(consulta_waveform)
        resultado_waveform = cursor.fetchall()        
        if resultado_waveform:
            recent_event_time = resultado_waveform[0][1]
            recent_waveform_data = [row for row in resultado_waveform if row[1] == recent_event_time]        
            # Verificar se a estação do SerialNumber corresponde à estação selecionada
            serial_number = recent_waveform_data[0][0]
            estacao = buscar_estacao(serial_number)
            if estacao != ponto_escolhido:
                print(f"Estação do SerialNumber {serial_number} ({estacao}) não corresponde à estação selecionada ({ponto_escolhido}).")
                self.figura_grafico2_wf.clear()
                self.grafico2_wf.draw()
            else:
                recent_waveform_data = np.array(recent_waveform_data)
                transversal = recent_waveform_data[:, 2].astype(float)
                longitudinal = recent_waveform_data[:, 3].astype(float)
                vertical = recent_waveform_data[:, 4].astype(float)
            
                num_linhas = len(recent_waveform_data)
                delta_t = 10 / num_linhas
                eixo_x = np.arange(0, 10, delta_t)
            
                resultante = np.sqrt(transversal**2 + longitudinal**2 + vertical**2)
            
                # Gráfico de waveform
                ax_grafico2 = self.figura_grafico2_wf.add_subplot(4, 1, 1)
                ax_grafico2.plot(eixo_x, transversal, color='red')
                ax_grafico2.set_ylabel("T")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2_wf.add_subplot(4, 1, 2)
                ax_grafico2.plot(eixo_x, longitudinal, color='red')
                ax_grafico2.set_ylabel("L")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2_wf.add_subplot(4, 1, 3)
                ax_grafico2.plot(eixo_x, vertical, color='red')
                ax_grafico2.set_ylabel("V")
                ax_grafico2.set_xticklabels([])
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
            
                ax_grafico2 = self.figura_grafico2_wf.add_subplot(4, 1, 4)
                ax_grafico2.plot(eixo_x, resultante, color='black')
                ax_grafico2.set_xlabel("Tempo (s)")
                ax_grafico2.set_ylabel("VS")
                ax_grafico2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Formatar rótulos do eixo y com 2 casas decimais
                ax_grafico2.tick_params(axis='y', which='both', pad=5)  # Ajustar espaço entre rótulos e ticks do eixo y
    
                # Ajuste o espaçamento entre as subplots
                self.figura_grafico2_wf.subplots_adjust(hspace=0.5, bottom=0.15)  # Ajuste o espaçamento vertical entre as subplots
            
                # Atualizar o gráfico 2
                self.grafico2_wf.draw()
        # Obter o valor do limite da estação selecionada
        estacao_selecionada = self.selecao_ponto.currentText()
        cursor.execute(f"SELECT `LIMITE {estacao_selecionada}` FROM usuarios")
        limite_estacao = cursor.fetchone()[0]
        '''
        # Atualizar o gráfico de dispersão
        self.figura_grafico_1_disp.clear()
        
        if dados_grafico1.size > 0:
            print(dados_grafico1)
            # Dados para o gráfico de dispersão
            tran_ppv = dados_grafico1[:, 0].astype(float)
            vert_ppv = dados_grafico1[:, 1].astype(float)
            long_ppv = dados_grafico1[:, 2].astype(float)
        
            ax_grafico_disp = self.figura_grafico_1_disp.add_subplot(1, 1, 1)
        
            # Criar o gráfico de dispersão
            ax_grafico_disp.scatter(tran_ppv, vert_ppv, c='red', label='Transversal')
            ax_grafico_disp.scatter(tran_ppv, long_ppv, c='green', label='Longitudinal')
            ax_grafico_disp.scatter(vert_ppv, long_ppv, c='blue', label='Vertical')
        
            # Desenhar a linha de limite
            ax_grafico_disp.axhline(y=limite_estacao, color='black', linestyle='--', label=f'Limite {estacao_selecionada}')
        
            # Configurar rótulos e legenda
            ax_grafico_disp.set_xlabel('Valor 1')
            ax_grafico_disp.set_ylabel('Valor 2')
            ax_grafico_disp.legend()
        
            # Atualizar o gráfico de dispersão
            self.grafico_1_disp.draw()
        
        '''
        # Fechar a conexão com o banco de dados
        conexao.close()


    
    def gerar_mapa_html(self):
        # Conectar ao banco de dados
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="CARSTE"
        )
    
        cursor = conexao.cursor()
    
        # Consulta para obter as coordenadas das estações
        consulta_sql = "SELECT `COORDENADA ESTACAO 1`, `COORDENADA ESTACAO 2`, `COORDENADA ESTACAO 3`, `COORDENADA ESTACAO 4`, `COORDENADA ESTACAO 5`, `COORDENADA ESTACAO 6`, `COORDENADA ESTACAO 7`, `COORDENADA ESTACAO 8`, `COORDENADA ESTACAO 9`, `COORDENADA ESTACAO 10` FROM usuarios"
    
        cursor.execute(consulta_sql)
        resultado = cursor.fetchall()
    
        coordenadas = []
    
        # Extrair as coordenadas das estações e adicioná-las à lista de coordenadas
        for row in resultado:
            for estacao in row:
                if estacao:
                    coordenadas.append([float(coord) for coord in estacao.split("; ")])
    
        # Gerar o código HTML do mapa com as coordenadas das estações
        mapa_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Mapa</title>
          <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
          <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
          <style>
            body, #mapid {{
              margin: 0;
              top: 0;
              padding: 0;
              width: 100%;
              height:100%;
              overflow: hidden;
            }}
          </style>
        </head>
        <body>
          <div id="mapid"></div>
          <script>
          document.getElementById('mapid').style.height = (window.innerHeight) + 'px';
    
          var map = L.map('mapid', {{
            zoomControl: false,
            attributionControl: false
          }});
    
          L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.esri.com/en-us/home" target="_blank">Esri</a>'
                }}).addTo(map);

         var coordenadas = {coordenadas};

         var bounds = L.latLngBounds(coordenadas);

         for (var i = 0; i < coordenadas.length; i++) {{
           L.circle(coordenadas[i], {{
             color: 'yellow',
             fillColor: 'yellow',
             fillOpacity: 1,
             radius: 5
           }}).addTo(map);
         }}

         map.fitBounds(bounds);
         map.setZoom(map.getZoom() - 1);

         window.addEventListener('resize', function() {{
           map.invalidateSize();
         }});
       </script>
     </body>
     </html>
        """
        # Criar um arquivo temporário com o conteúdo do mapa
        import tempfile
        mapa_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
        mapa_temp_file.write(mapa_html)
        mapa_temp_file.close()

        return mapa_temp_file.name


    def atualizar_grafico1(self):
        # Atualizar o gráfico 1
        self.figura_grafico1.clear()
        dados_grafico1 = np.array(self.resultado)
    
        if dados_grafico1.size > 0:
            tran_ppv = dados_grafico1[:, 0].astype(np.float)
            vert_ppv = dados_grafico1[:, 1].astype(np.float)
            long_ppv = dados_grafico1[:, 2].astype(np.float)
            tran_zc_freq = dados_grafico1[:, 3].astype(np.float)
            vert_zc_freq = dados_grafico1[:, 4].astype(np.float)
            long_zc_freq = dados_grafico1[:, 5].astype(np.float)
    
            eixo_x = np.concatenate((tran_ppv, vert_ppv, long_ppv, tran_zc_freq, vert_zc_freq, long_zc_freq))
    
            # Histograma
            ax = self.figura_grafico1.add_subplot(1, 1, 1)
            ax.hist(eixo_x, bins=30, density=True, alpha=0.75, color='blue', edgecolor='black')

    
            # Atualizar o gráfico 1
            self.grafico1.draw()
    
    def atualizar_grafico2(self):
        # Atualizar o gráfico 2
        self.figura_grafico2.clear()
        dados_grafico2 = np.array(self.resultado)
    
        if dados_grafico2.size > 0:
            seis_gain = dados_grafico2[:, 6].astype(np.float)
    
            # Gráfico de dispersão
            ax = self.figura_grafico2.add_subplot(1, 1, 1)
            ax.scatter(np.arange(len(seis_gain)), seis_gain, color='red', marker='o')

    
            # Atualizar o gráfico 2
            self.grafico2.draw()

    def inicializar_temporizador(self):
        from PySide6.QtCore import QTimer
        temporizador = QTimer(self)
        temporizador.timeout.connect(self.atualizar_graficos)
        if self.testes == True:
            temporizador.start(100000)  # Atualiza a cada 1 segundo
        else:
            temporizador.start(4500000)  # Atualiza a cada 1h15m
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.atualizar_graficos()
    
