from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QGraphicsView
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
import mysql.connector
import numpy as np


class VisaoGeral(QWidget):
    estacao_selecionada = Signal(str)

    def __init__(self, login):
        super().__init__()

        self.login = login
        self.numero_estacoes = self.obter_numero_estacoes()

        self.layout = QGridLayout(self)
        self.configurar_interface()
        self.setLayout(self.layout)

    def obter_numero_estacoes(self):
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="CARSTE"
        )
        cursor = conexao.cursor()
    
        cursor.execute(f"SELECT * FROM usuarios WHERE LOGIN = '{self.login}'")
        resultado = cursor.fetchone()
    
        # Obter os nomes das colunas
        colunas = [i[0] for i in cursor.description]
    
        numero_estacoes = 0
        for i in range(1, 11):
            # Encontrar o índice da coluna "LIMITE ESTACAO {i}"
            indice_coluna = colunas.index(f"LIMITE ESTACAO {i}")
    
            # Verificar se a coluna "LIMITE ESTACAO {i}" contém um valor
            if resultado[indice_coluna]:
                numero_estacoes += 1
            else:
                break
    
        conexao.close()
        return numero_estacoes


    def configurar_interface(self):
        num_estacoes = self.numero_estacoes
    
        def get_posicao_grafico(indice, num_estacoes):
            if num_estacoes <= 2:
                return indice, 0
            elif num_estacoes <= 4:
                return indice // 2, indice % 2
            elif num_estacoes <= 6:
                return indice // 3, indice % 3
            else:
                if indice < 6:
                    return indice // 3, indice % 3
                else:
                    return (indice - 6) * 2 + 1, 4 if indice % 2 == 0 else 0
    
        for i in range(num_estacoes):
            estacao_layout = QVBoxLayout()
    
            titulo = QLabel(f"Estação {i + 1}")
            titulo.setAlignment(Qt.AlignCenter)
            estacao_layout.addWidget(titulo)
    
            figura = Figure(figsize=(5, 4), dpi=100)
            grafico = FigureCanvas(figura)
            estacao_layout.addWidget(grafico)
    
            self.criar_grafico_waveform(figura, i + 1)
    
            row, col = get_posicao_grafico(i, num_estacoes)
            self.layout.addLayout(estacao_layout, row, col)
    
        # Adicionar o mapa no centro do layout

        self.imagem = QWebEngineView()
        web_page = self.imagem.page()
        web_page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        mapa_html_file = self.gerar_mapa_html()
        self.imagem.load(QUrl.fromLocalFile(mapa_html_file))
        self.layout.addWidget(self.imagem, 1, 2, 1, 2)
    
        # Configurar esticamentos de linhas e colunas
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(4, 1)
        self.layout.setColumnStretch(5, 1)


    def criar_grafico_waveform(self, figura, estacao_atual):
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="CARSTE"
        )
        cursor = conexao.cursor()
    
        # Obter o SerialNumber da estação atual
        cursor.execute(f"SELECT `SERIAL ESTACAO {estacao_atual}` FROM usuarios WHERE LOGIN = '{self.login}'")
        serial_number = cursor.fetchone()[0]
    
        # Consulta waveform filtrando pelo SerialNumber e ordenando pelo EventTime
        consulta_waveform = f"SELECT `SerialNumber`, `EventTime`, `Transversal`, `Longitudinal`, `Vertical` FROM dados_waveform WHERE `SerialNumber` = '{serial_number}' ORDER BY `EventTime` DESC"
        cursor.execute(consulta_waveform)
        resultado_waveform = cursor.fetchall()
    
        if resultado_waveform:
            recent_event_time = resultado_waveform[0][1]
            recent_waveform_data = [row for row in resultado_waveform if row[1] == recent_event_time]
            serial_number = recent_waveform_data[0][0]
    
            estacao = f'ESTACAO{estacao_atual}'
            recent_waveform_data = np.array(recent_waveform_data)
            transversal = recent_waveform_data[:, 2].astype(float)
            longitudinal = recent_waveform_data[:, 3].astype(float)
            vertical = recent_waveform_data[:, 4].astype(float)

            num_linhas = len(recent_waveform_data)
            delta_t = 10 / num_linhas
            eixo_x = np.arange(0, 10, delta_t)

            resultante = np.sqrt(transversal**2 + longitudinal**2 + vertical**2)

            # Gráfico de waveform
            ax = figura.add_subplot(4, 1, 1)
            ax.plot(eixo_x, transversal, color='red')
            ax.set_ylabel("T")
            ax.set_xticklabels([])
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            ax.tick_params(axis='y', which='both', pad=5)

            ax = figura.add_subplot(4, 1, 2)
            ax.plot(eixo_x, longitudinal, color='red')
            ax.set_ylabel("L")
            ax.set_xticklabels([])
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            ax.tick_params(axis='y', which='both', pad=5)

            ax = figura.add_subplot(4, 1, 3)
            ax.plot(eixo_x, vertical, color='red')
            ax.set_ylabel("V")
            ax.set_xticklabels([])
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            ax.tick_params(axis='y', which='both', pad=5)

            ax = figura.add_subplot(4, 1, 4)
            ax.plot(eixo_x, resultante, color='black')
            ax.set_ylabel("VS")
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            ax.tick_params(axis='y', which='both', pad=5)

            figura.subplots_adjust(hspace=0.5, bottom=0.15)
    
        conexao.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            estacao_clicada = self.layout.itemAtPosition(event.y() // 100, event.x() // 100)
            if estacao_clicada:
                titulo = estacao_clicada.itemAt(0).widget().text()
                self.estacao_selecionada.emit(titulo)
                # Aqui você pode enviar o sinal para a aba sismograma com o valor de `titulo`.
                # Por exemplo, você pode usar um sinal personalizado do PyQt5.

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
