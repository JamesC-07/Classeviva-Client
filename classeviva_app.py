from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
import classeviva
from datetime import datetime
import threading
import asyncio


class LoginScreen(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        # Titolo
        title = Label(
            text='Classeviva Client',
            size_hint=(1, 0.2),
            font_size='24sp',
            bold=True
        )
        self.add_widget(title)
        
        # Campo username
        self.username_input = TextInput(
            hint_text='Username (es. S1234567C)',
            multiline=False,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.username_input)
        
        # Campo password
        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.password_input)
        
        # Pulsante login
        login_btn = Button(
            text='Accedi',
            size_hint=(1, 0.15),
            on_press=self.do_login
        )
        self.add_widget(login_btn)
        
        # Label per messaggi di errore
        self.error_label = Label(
            text='',
            size_hint=(1, 0.2),
            color=(1, 0, 0, 1)
        )
        self.add_widget(self.error_label)
    
    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.error_label.text = 'Inserisci username e password'
            return
        
        self.error_label.text = 'Accesso in corso...'
        self.error_label.color = (0, 1, 0, 1)
        
        # Login in thread separato
        thread = threading.Thread(
            target=self.app.login,
            args=(username, password)
        )
        thread.start()


class MainScreen(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.orientation = 'vertical'
        
        # Header con nome utente e logout
        header = BoxLayout(size_hint=(1, 0.08), padding=dp(10))
        self.user_label = Label(text='', size_hint=(0.7, 1))
        logout_btn = Button(
            text='Logout',
            size_hint=(0.3, 1),
            on_press=self.logout
        )
        header.add_widget(self.user_label)
        header.add_widget(logout_btn)
        self.add_widget(header)
        
        # Tab panel
        self.tabs = TabbedPanel(do_default_tab=False)
        
        # Tab Voti
        self.voti_tab = TabbedPanelItem(text='Voti')
        self.voti_content = ScrollView()
        self.voti_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(10)
        )
        self.voti_layout.bind(minimum_height=self.voti_layout.setter('height'))
        self.voti_content.add_widget(self.voti_layout)
        self.voti_tab.add_widget(self.voti_content)
        self.tabs.add_widget(self.voti_tab)
        
        # Tab Media
        self.media_tab = TabbedPanelItem(text='Media')
        self.media_content = ScrollView()
        self.media_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(10)
        )
        self.media_layout.bind(minimum_height=self.media_layout.setter('height'))
        self.media_content.add_widget(self.media_layout)
        self.media_tab.add_widget(self.media_content)
        self.tabs.add_widget(self.media_tab)
        
        # Tab Statistiche
        self.stats_tab = TabbedPanelItem(text='Statistiche')
        self.stats_content = ScrollView()
        self.stats_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
        self.stats_content.add_widget(self.stats_layout)
        self.stats_tab.add_widget(self.stats_content)
        self.tabs.add_widget(self.stats_tab)
        
        self.add_widget(self.tabs)
        
        self.data_loaded = False
        self.voti_data = []
    
    def logout(self, instance):
        self.app.do_logout()
    
    def update_user_info(self, name):
        self.user_label.text = f'Benvenuto, {name}'
    
    def _determina_quadrimestre(self, data_str):
        """Determina il quadrimestre basandosi sulla data del voto"""
        try:
            if isinstance(data_str, str):
                data = datetime.strptime(data_str, '%Y-%m-%d')
            else:
                data = data_str
            
            anno = data.year
            mese = data.month
            
            # Primo quadrimestre: settembre-gennaio
            # Secondo quadrimestre: febbraio-giugno
            if mese >= 9 or mese == 1:
                return 1
            elif mese >= 2 and mese <= 6:
                return 2
            else:
                # Luglio-agosto considerati periodo estivo (ignora)
                return None
        except:
            return None
    
    def display_voti(self, voti_data):
        self.voti_layout.clear_widgets()
        self.voti_data = voti_data
        
        if not voti_data:
            self.voti_layout.add_widget(Label(
                text='Nessun voto disponibile',
                size_hint_y=None,
                height=dp(40)
            ))
            self.data_loaded = True
            return
        
        for voto in voti_data:
            voto_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                padding=dp(10),
                spacing=dp(10)
            )
            
            # Estrai dati voto
            materia = voto.get('subjectDesc', voto.get('materia', 'N/A'))
            valore_str = voto.get('displayValue', voto.get('decimalValue', voto.get('voto', 'N/A')))
            data = voto.get('evtDate', voto.get('data', 'N/A'))
            tipo = voto.get('componentDesc', voto.get('tipo', 'N/A'))
            nota = voto.get('notesForFamily', voto.get('nota', ''))
            
            # Controlla se è un voto blu (non conta per la media)
            colore_codice = voto.get('color', '')
            voto_non_conta = (colore_codice == 'blue')
            
            # Determina quadrimestre
            quadrimestre = self._determina_quadrimestre(data)
            quadrimestre_str = f' [Q{quadrimestre}]' if quadrimestre else ''
            
            # Determina colore in base al voto
            if voto_non_conta:
                colore = (0.3, 0.5, 1, 1)  # Blu per voti che non contano
            else:
                try:
                    valore_num = float(str(valore_str).replace(',', '.').replace('+', '').replace('-', '').replace('½', '.5'))
                    colore = (0, 0.8, 0, 1) if valore_num >= 6 else (1, 0, 0, 1)
                except (ValueError, TypeError):
                    colore = (0.5, 0.5, 0.5, 1)
            
            # Box voto (sinistra)
            voto_left = BoxLayout(
                orientation='vertical',
                size_hint_x=0.3,
                padding=dp(5)
            )
            voto_left.add_widget(Label(
                text=f'[b]{valore_str}[/b]',
                markup=True,
                font_size='32sp',
                color=colore,
                size_hint_y=0.6
            ))
            voto_left.add_widget(Label(
                text=data + quadrimestre_str,
                font_size='12sp',
                size_hint_y=0.4
            ))
            
            # Box dettagli (destra)
            voto_right = BoxLayout(
                orientation='vertical',
                size_hint_x=0.7,
                padding=dp(5)
            )
            voto_right.add_widget(Label(
                text=f'[b]{materia}[/b]',
                markup=True,
                font_size='16sp',
                size_hint_y=0.4,
                halign='left',
                valign='middle',
                text_size=(Window.width * 0.6, None)
            ))
            voto_right.add_widget(Label(
                text=tipo,
                font_size='14sp',
                size_hint_y=0.3,
                halign='left',
                valign='middle',
                text_size=(Window.width * 0.6, None)
            ))
            if nota:
                voto_right.add_widget(Label(
                    text=nota,
                    font_size='12sp',
                    size_hint_y=0.3,
                    color=(0.7, 0.7, 0.7, 1),
                    halign='left',
                    valign='top',
                    text_size=(Window.width * 0.6, None)
                ))
            
            voto_box.add_widget(voto_left)
            voto_box.add_widget(voto_right)
            
            self.voti_layout.add_widget(voto_box)
        
        self.data_loaded = True
    
    def display_media(self, voti_data):
        self.media_layout.clear_widgets()
        
        if not voti_data:
            self.media_layout.add_widget(Label(
                text='Nessun dato disponibile',
                size_hint_y=None,
                height=dp(40)
            ))
            return
        
        # Calcola medie per materia divise per quadrimestre
        materie_q1 = {}
        materie_q2 = {}
        materie_totale = {}
        
        for voto in voti_data:
            # Salta i voti blu
            colore_codice = voto.get('color', '')
            if colore_codice == 'blue':
                continue
                
            materia = voto.get('subjectDesc', voto.get('materia', 'N/A'))
            data = voto.get('evtDate', voto.get('data', 'N/A'))
            quadrimestre = self._determina_quadrimestre(data)
            
            try:
                valore = float(voto.get('decimalValue', voto.get('voto', 0)))
                if valore > 0:
                    # Aggiungi al totale
                    if materia not in materie_totale:
                        materie_totale[materia] = []
                    materie_totale[materia].append(valore)
                    
                    # Aggiungi al quadrimestre specifico
                    if quadrimestre == 1:
                        if materia not in materie_q1:
                            materie_q1[materia] = []
                        materie_q1[materia].append(valore)
                    elif quadrimestre == 2:
                        if materia not in materie_q2:
                            materie_q2[materia] = []
                        materie_q2[materia].append(valore)
            except (ValueError, TypeError):
                continue
        
        # Header
        self.media_layout.add_widget(Label(
            text='[b]MEDIE PER MATERIA[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(40),
            font_size='18sp'
        ))
        
        # Tabella header
        header_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=dp(5)
        )
        header_box.add_widget(Label(
            text='[b]Materia[/b]',
            markup=True,
            size_hint_x=0.4,
            font_size='14sp'
        ))
        header_box.add_widget(Label(
            text='[b]Q1[/b]',
            markup=True,
            size_hint_x=0.2,
            font_size='14sp'
        ))
        header_box.add_widget(Label(
            text='[b]Q2[/b]',
            markup=True,
            size_hint_x=0.2,
            font_size='14sp'
        ))
        header_box.add_widget(Label(
            text='[b]Totale[/b]',
            markup=True,
            size_hint_x=0.2,
            font_size='14sp'
        ))
        self.media_layout.add_widget(header_box)
        
        # Medie per materia
        tutte_medie_q1 = []
        tutte_medie_q2 = []
        tutte_medie_totale = []
        
        for materia in sorted(materie_totale.keys()):
            media_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                padding=dp(5)
            )
            
            # Nome materia
            media_box.add_widget(Label(
                text=materia,
                size_hint_x=0.4,
                halign='left',
                valign='middle',
                text_size=(Window.width * 0.35, None),
                font_size='13sp'
            ))
            
            # Media Q1
            if materia in materie_q1:
                media_q1 = sum(materie_q1[materia]) / len(materie_q1[materia])
                tutte_medie_q1.append(media_q1)
                media_box.add_widget(Label(
                    text=f'{media_q1:.2f}',
                    size_hint_x=0.2,
                    font_size='14sp'
                ))
            else:
                media_box.add_widget(Label(
                    text='-',
                    size_hint_x=0.2,
                    font_size='14sp',
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            # Media Q2
            if materia in materie_q2:
                media_q2 = sum(materie_q2[materia]) / len(materie_q2[materia])
                tutte_medie_q2.append(media_q2)
                media_box.add_widget(Label(
                    text=f'{media_q2:.2f}',
                    size_hint_x=0.2,
                    font_size='14sp'
                ))
            else:
                media_box.add_widget(Label(
                    text='-',
                    size_hint_x=0.2,
                    font_size='14sp',
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            # Media totale
            media_totale = sum(materie_totale[materia]) / len(materie_totale[materia])
            tutte_medie_totale.append(media_totale)
            media_box.add_widget(Label(
                text=f'[b]{media_totale:.2f}[/b]',
                markup=True,
                size_hint_x=0.2,
                font_size='14sp'
            ))
            
            self.media_layout.add_widget(media_box)
        
        # Medie generali
        if tutte_medie_totale:
            self.media_layout.add_widget(Label(
                text='',
                size_hint_y=None,
                height=dp(20)
            ))
            
            generale_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(60),
                padding=dp(5)
            )
            
            generale_box.add_widget(Label(
                text='[b]MEDIA GENERALE[/b]',
                markup=True,
                size_hint_x=0.4,
                font_size='16sp'
            ))
            
            if tutte_medie_q1:
                media_gen_q1 = sum(tutte_medie_q1) / len(tutte_medie_q1)
                generale_box.add_widget(Label(
                    text=f'[b]{media_gen_q1:.2f}[/b]',
                    markup=True,
                    size_hint_x=0.2,
                    font_size='18sp'
                ))
            else:
                generale_box.add_widget(Label(text='-', size_hint_x=0.2))
            
            if tutte_medie_q2:
                media_gen_q2 = sum(tutte_medie_q2) / len(tutte_medie_q2)
                generale_box.add_widget(Label(
                    text=f'[b]{media_gen_q2:.2f}[/b]',
                    markup=True,
                    size_hint_x=0.2,
                    font_size='18sp'
                ))
            else:
                generale_box.add_widget(Label(text='-', size_hint_x=0.2))
            
            media_gen_totale = sum(tutte_medie_totale) / len(tutte_medie_totale)
            generale_box.add_widget(Label(
                text=f'[b]{media_gen_totale:.2f}[/b]',
                markup=True,
                size_hint_x=0.2,
                font_size='18sp',
                color=(0, 0.7, 1, 1)
            ))
            
            self.media_layout.add_widget(generale_box)
    
    def display_statistics(self, voti_data):
        self.stats_layout.clear_widgets()
        
        if not voti_data:
            self.stats_layout.add_widget(Label(
                text='Nessun dato disponibile per le statistiche',
                size_hint_y=None,
                height=dp(40)
            ))
            return
        
        # Prepara dati per i grafici
        materie_data = {}
        distribuzione_voti = {}
        voti_q1 = []
        voti_q2 = []
        
        for voto in voti_data:
            colore_codice = voto.get('color', '')
            if colore_codice == 'blue':
                continue
            
            materia = voto.get('subjectDesc', 'N/A')
            data = voto.get('evtDate', 'N/A')
            quadrimestre = self._determina_quadrimestre(data)
            
            try:
                valore = float(voto.get('decimalValue', 0))
                if valore > 0:
                    # Dati per materia
                    if materia not in materie_data:
                        materie_data[materia] = []
                    materie_data[materia].append(valore)
                    
                    # Distribuzione voti
                    voto_arrotondato = round(valore)
                    distribuzione_voti[voto_arrotondato] = distribuzione_voti.get(voto_arrotondato, 0) + 1
                    
                    # Voti per quadrimestre
                    if quadrimestre == 1:
                        voti_q1.append(valore)
                    elif quadrimestre == 2:
                        voti_q2.append(valore)
            except (ValueError, TypeError):
                continue
        
        # Titolo sezione
        self.stats_layout.add_widget(Label(
            text='[b]STATISTICHE[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(50),
            font_size='20sp'
        ))
        
        # Card: Statistiche generali
        stats_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            padding=dp(10),
            spacing=dp(10)
        )
        
        stats_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        
        # Totale voti
        total_voti = sum(len(v) for v in materie_data.values())
        stats_grid.add_widget(self._create_stat_box('📊 Voti Totali', str(total_voti), (0.2, 0.6, 1, 1)))
        
        # Materie
        stats_grid.add_widget(self._create_stat_box('📚 Materie', str(len(materie_data)), (0.4, 0.7, 0.3, 1)))
        
        # Media Q1
        if voti_q1:
            media_q1 = sum(voti_q1) / len(voti_q1)
            color_q1 = (0, 0.8, 0, 1) if media_q1 >= 6 else (1, 0.3, 0.3, 1)
            stats_grid.add_widget(self._create_stat_box('Q1 Media', f'{media_q1:.2f}', color_q1))
        else:
            stats_grid.add_widget(self._create_stat_box('Q1 Media', '-', (0.5, 0.5, 0.5, 1)))
        
        # Media Q2
        if voti_q2:
            media_q2 = sum(voti_q2) / len(voti_q2)
            color_q2 = (0, 0.8, 0, 1) if media_q2 >= 6 else (1, 0.3, 0.3, 1)
            stats_grid.add_widget(self._create_stat_box('Q2 Media', f'{media_q2:.2f}', color_q2))
        else:
            stats_grid.add_widget(self._create_stat_box('Q2 Media', '-', (0.5, 0.5, 0.5, 1)))
        
        stats_card.add_widget(stats_grid)
        self.stats_layout.add_widget(stats_card)
        
        # Grafico: Media per materia
        self.stats_layout.add_widget(Label(
            text='[b]Media per Materia[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(40),
            font_size='16sp'
        ))
        
        materie_ordinate = sorted(materie_data.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
        for materia, voti in materie_ordinate[:10]:  # Top 10 materie
            if len(voti) > 0:
                media = sum(voti) / len(voti)
                self.stats_layout.add_widget(self._create_bar_chart(materia, media, len(voti)))
        
        # Grafico: Distribuzione voti
        if distribuzione_voti:
            self.stats_layout.add_widget(Label(
                text='[b]Distribuzione Voti[/b]',
                markup=True,
                size_hint_y=None,
                height=dp(50),
                font_size='16sp'
            ))
            
            max_count = max(distribuzione_voti.values())
            for voto in range(1, 11):
                count = distribuzione_voti.get(voto, 0)
                if count > 0:
                    self.stats_layout.add_widget(
                        self._create_histogram_bar(voto, count, max_count)
                    )
    
    def _create_stat_box(self, label, value, color):
        """Crea un box per una statistica"""
        box = BoxLayout(
            orientation='vertical',
            padding=dp(10)
        )
        
        # Sfondo colorato
        with box.canvas.before:
            Color(*color, 0.3)
            box.rect = Rectangle(pos=box.pos, size=box.size)
        
        box.bind(pos=lambda *args: setattr(box.rect, 'pos', box.pos))
        box.bind(size=lambda *args: setattr(box.rect, 'size', box.size))
        
        box.add_widget(Label(
            text=label,
            font_size='12sp',
            size_hint_y=0.4,
            color=(0.7, 0.7, 0.7, 1)
        ))
        box.add_widget(Label(
            text=f'[b]{value}[/b]',
            markup=True,
            font_size='24sp',
            size_hint_y=0.6,
            color=color
        ))
        
        return box
    
    def _create_bar_chart(self, materia, media, count):
        """Crea una barra per il grafico delle medie"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=dp(5),
            spacing=dp(10)
        )
        
        # Nome materia
        box.add_widget(Label(
            text=materia[:25],
            size_hint_x=0.4,
            halign='left',
            valign='middle',
            text_size=(Window.width * 0.35, None),
            font_size='12sp'
        ))
        
        # Barra grafico
        bar_container = BoxLayout(size_hint_x=0.4)
        bar_widget = Widget()
        
        def draw_bar(*args):
            bar_widget.canvas.clear()
            with bar_widget.canvas:
                # Sfondo grigio chiaro
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=bar_widget.pos, size=bar_widget.size)
                
                # Barra colorata
                if media >= 6:
                    Color(0, 0.8, 0, 1)
                else:
                    Color(1, 0.2, 0.2, 1)
                
                bar_width = (media / 10.0) * bar_widget.width
                Rectangle(pos=bar_widget.pos, size=(bar_width, bar_widget.height))
                
                # Linea del 6
                Color(1, 0.6, 0, 0.5)
                line_x = bar_widget.x + (6.0 / 10.0) * bar_widget.width
                Line(points=[line_x, bar_widget.y, line_x, bar_widget.y + bar_widget.height], width=1.5)
        
        bar_widget.bind(pos=draw_bar, size=draw_bar)
        bar_container.add_widget(bar_widget)
        box.add_widget(bar_container)
        
        # Valore media
        box.add_widget(Label(
            text=f'[b]{media:.2f}[/b]\n({count})',
            markup=True,
            size_hint_x=0.2,
            font_size='13sp'
        ))
        
        return box
    
    def _create_histogram_bar(self, voto, count, max_count):
        """Crea una barra per l'istogramma della distribuzione"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=dp(5),
            spacing=dp(10)
        )
        
        # Voto
        box.add_widget(Label(
            text=str(voto),
            size_hint_x=0.1,
            font_size='16sp',
            bold=True
        ))
        
        # Barra
        bar_container = BoxLayout(size_hint_x=0.7)
        bar_widget = Widget()
        
        def draw_hist_bar(*args):
            bar_widget.canvas.clear()
            with bar_widget.canvas:
                # Sfondo
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=bar_widget.pos, size=bar_widget.size)
                
                # Barra colorata
                if voto >= 6:
                    Color(0, 0.8, 0, 0.8)
                else:
                    Color(1, 0.2, 0.2, 0.8)
                
                bar_width = (count / max_count) * bar_widget.width
                Rectangle(pos=bar_widget.pos, size=(bar_width, bar_widget.height))
        
        bar_widget.bind(pos=draw_hist_bar, size=draw_hist_bar)
        bar_container.add_widget(bar_widget)
        box.add_widget(bar_container)
        
        # Conteggio
        box.add_widget(Label(
            text=str(count),
            size_hint_x=0.2,
            font_size='14sp'
        ))
        
        return box


class ClassevivaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.utente = None
        self.login_screen = None
        self.main_screen = None
    
    def build(self):
        self.login_screen = LoginScreen(self)
        return self.login_screen
    
    def login(self, username, password):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.utente = classeviva.Utente(username, password)
            loop.run_until_complete(self.utente.accedi())
            
            try:
                carta = loop.run_until_complete(self.utente.carta())
                name = carta.get('firstName', username)
            except:
                name = username
            
            Clock.schedule_once(lambda dt: self.show_main_screen(name), 0)
            
        except Exception as e:
            error_msg = f'Errore di login: {str(e)}'
            Clock.schedule_once(
                lambda dt: self.show_error(error_msg),
                0
            )
        finally:
            loop.close()
    
    def show_main_screen(self, name):
        self.main_screen = MainScreen(self)
        self.main_screen.update_user_info(name)
        self.root.clear_widgets()
        self.root.add_widget(self.main_screen)
        
        threading.Thread(target=self.load_data).start()
    
    def show_error(self, message):
        self.login_screen.error_label.text = message
        self.login_screen.error_label.color = (1, 0, 0, 1)
    
    def load_data(self):
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Carica voti con retry
            voti = None
            for attempt in range(3):
                try:
                    voti = loop.run_until_complete(self.utente.voti())
                    if voti:
                        break
                except Exception as e:
                    print(f'Tentativo {attempt + 1} caricamento voti fallito: {e}')
                    if attempt < 2:
                        Clock.schedule_once(lambda dt: None, 0.5)
            
            if voti:
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_voti(voti),
                    0
                )
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_media(voti),
                    0
                )
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_statistics(voti),
                    0
                )
            else:
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_voti([]),
                    0
                )
                
        except Exception as e:
            print(f'Errore caricamento dati: {e}')
        finally:
            if loop:
                loop.close()
    
    def do_logout(self):
        self.utente = None
        self.login_screen = LoginScreen(self)
        self.root.clear_widgets()
        self.root.add_widget(self.login_screen)


if __name__ == '__main__':
    ClassevivaApp().run()