# --------------------------------------------
# Classeviva Client 
# By James Capelli
# Dependencies: python 3.8+, kivy, matplotlib
# --------------------------------------------

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
import classeviva
from datetime import datetime, timedelta
import threading
import asyncio
import json
import os


class ResponsiveLayout:
    """Classe helper per gestire dimensioni responsive"""
    
    @staticmethod
    def is_tablet():
        """Determina se il dispositivo è un tablet (larghezza > 600dp)"""
        return Window.width > dp(600)
    
    @staticmethod
    def get_font_size(base_size):
        """Calcola dimensione font responsive"""
        if ResponsiveLayout.is_tablet():
            return sp(base_size * 1.3)
        return sp(base_size)
    
    @staticmethod
    def get_spacing():
        """Ritorna spacing appropriato"""
        return dp(15) if ResponsiveLayout.is_tablet() else dp(10)
    
    @staticmethod
    def get_padding():
        """Ritorna padding appropriato"""
        return dp(20) if ResponsiveLayout.is_tablet() else dp(15)
    
    @staticmethod
    def get_height(base_height):
        """Calcola altezza responsive"""
        if ResponsiveLayout.is_tablet():
            return dp(base_height * 1.2)
        return dp(base_height)


class LoginScreen(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.orientation = 'vertical'
        self.padding = ResponsiveLayout.get_padding()
        self.spacing = ResponsiveLayout.get_spacing()
        
        Window.bind(on_resize=self.on_window_resize)
        
        # Spacer top
        self.add_widget(Widget(size_hint=(1, 0.1)))
        
        # Titolo
        title = Label(
            text='Classeviva Client',
            size_hint=(1, None),
            height=ResponsiveLayout.get_height(60),
            font_size=ResponsiveLayout.get_font_size(24),
            bold=True
        )
        self.add_widget(title)
        
        # Container centrale con larghezza massima per tablet
        container = BoxLayout(
            orientation='vertical',
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_x=None,
            width=min(Window.width - dp(40), dp(500)) if ResponsiveLayout.is_tablet() else Window.width - dp(40)
        )
        container.pos_hint = {'center_x': 0.5}
        
        # Campo username
        self.username_input = TextInput(
            hint_text='Username (es. S1234567C)',
            multiline=False,
            size_hint=(1, None),
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(16),
            padding=[dp(15), dp(15)]
        )
        container.add_widget(self.username_input)
        
        # Campo password
        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(16),
            padding=[dp(15), dp(15)]
        )
        container.add_widget(self.password_input)
        
        # Pulsante login
        login_btn = Button(
            text='Accedi',
            size_hint=(1, None),
            height=ResponsiveLayout.get_height(55),
            font_size=ResponsiveLayout.get_font_size(18),
            bold=True,
            on_press=self.do_login
        )
        container.add_widget(login_btn)
        
        # Label per messaggi di errore
        self.error_label = Label(
            text='',
            size_hint=(1, None),
            height=ResponsiveLayout.get_height(60),
            font_size=ResponsiveLayout.get_font_size(14),
            color=(1, 0, 0, 1)
        )
        container.add_widget(self.error_label)
        
        # Wrapper per centrare il container
        wrapper = BoxLayout(orientation='horizontal')
        wrapper.add_widget(Widget())
        wrapper.add_widget(container)
        wrapper.add_widget(Widget())
        
        self.add_widget(wrapper)
        self.add_widget(Widget(size_hint=(1, 0.2)))
    
    def on_window_resize(self, instance, width, height):
        """Aggiorna layout quando la finestra viene ridimensionata"""
        Clock.schedule_once(lambda dt: self.update_layout(), 0.1)
    
    def update_layout(self):
        """Ricostruisce il layout con nuove dimensioni"""
        pass
    
    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.error_label.text = 'Inserisci username e password'
            return
        
        self.error_label.text = 'Accesso in corso...'
        self.error_label.color = (0, 1, 0, 1)
        
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
        
        Window.bind(on_resize=self.on_window_resize)
        
        # Header con nome utente e logout
        header_height = ResponsiveLayout.get_height(60)
        header = BoxLayout(
            size_hint=(1, None),
            height=header_height,
            padding=ResponsiveLayout.get_padding()
        )
        self.user_label = Label(
            text='',
            size_hint=(0.7, 1),
            font_size=ResponsiveLayout.get_font_size(16),
            halign='left',
            valign='middle'
        )
        self.user_label.bind(size=self.user_label.setter('text_size'))
        
        logout_btn = Button(
            text='Logout',
            size_hint=(0.3, 1),
            font_size=ResponsiveLayout.get_font_size(14),
            on_press=self.logout
        )
        header.add_widget(self.user_label)
        header.add_widget(logout_btn)
        self.add_widget(header)
        
        # Tab panel con altezza tab responsiva
        self.tabs = TabbedPanel(
            do_default_tab=False,
            tab_height=ResponsiveLayout.get_height(50)
        )
        
        # Imposta dimensione font per i tab
        tab_font_size = ResponsiveLayout.get_font_size(14)
        
        # Tab Voti
        self.voti_tab = TabbedPanelItem(text='Voti')
        self.voti_content = ScrollView()
        self.voti_layout = GridLayout(
            cols=1,
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            padding=ResponsiveLayout.get_padding()
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
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            padding=ResponsiveLayout.get_padding()
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
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            padding=ResponsiveLayout.get_padding()
        )
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
        self.stats_content.add_widget(self.stats_layout)
        self.stats_tab.add_widget(self.stats_content)
        self.tabs.add_widget(self.stats_tab)
        
        # Tab Assenze
        self.assenze_tab = TabbedPanelItem(text='Assenze')
        self.assenze_content = ScrollView()
        self.assenze_layout = BoxLayout(
            orientation='vertical',
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            padding=ResponsiveLayout.get_padding()
        )
        self.assenze_layout.bind(minimum_height=self.assenze_layout.setter('height'))
        self.assenze_content.add_widget(self.assenze_layout)
        self.assenze_tab.add_widget(self.assenze_content)
        self.tabs.add_widget(self.assenze_tab)
        
        self.add_widget(self.tabs)
        
        self.data_loaded = False
        self.voti_data = []
        self.assenze_data = []
    
    def on_window_resize(self, instance, width, height):
        """Aggiorna layout quando cambia orientamento"""
        if self.data_loaded:
            Clock.schedule_once(lambda dt: self.refresh_all_data(), 0.1)
    
    def refresh_all_data(self):
        """Ricarica tutti i dati con nuove dimensioni"""
        if self.voti_data:
            self.display_voti(self.voti_data)
            self.display_media(self.voti_data)
            self.display_statistics(self.voti_data)
        if self.assenze_data:
            self.display_assenze(self.assenze_data)
    
    def logout(self, instance):
        self.app.do_logout()
    
    def update_user_info(self, name):
        self.user_label.text = f'Benvenuto, {name}'
    
    def _calcola_giorni_scuola(self):
        """Calcola i giorni di scuola dell'anno scolastico"""
        oggi = datetime.now()
        
        if oggi.month >= 9:
            inizio_anno = datetime(oggi.year, 9, 1)
            fine_anno = datetime(oggi.year + 1, 6, 30)
        else:
            inizio_anno = datetime(oggi.year - 1, 9, 1)
            fine_anno = datetime(oggi.year, 6, 30)
        
        giorni_totali = 0
        giorni_trascorsi = 0
        
        festivita = [
            (11, 1), (12, 8), (12, 25), (12, 26),
            (1, 1), (1, 6), (4, 25), (5, 1), (6, 2),
        ]
        
        data_corrente = inizio_anno
        while data_corrente <= fine_anno:
            if data_corrente.weekday() < 5:
                if (data_corrente.month, data_corrente.day) not in festivita:
                    if not (data_corrente.month == 12 and data_corrente.day >= 23) and \
                       not (data_corrente.month == 1 and data_corrente.day <= 6):
                        if not (data_corrente.month == 4 and 10 <= data_corrente.day <= 17):
                            giorni_totali += 1
                            if data_corrente <= oggi:
                                giorni_trascorsi += 1
            
            data_corrente += timedelta(days=1)
        
        giorni_rimanenti = giorni_totali - giorni_trascorsi
        return giorni_totali, giorni_trascorsi, giorni_rimanenti
    
    def _determina_quadrimestre(self, data_str):
        """Determina il quadrimestre basandosi sulla data del voto"""
        try:
            if isinstance(data_str, str):
                data = datetime.strptime(data_str, '%Y-%m-%d')
            else:
                data = data_str
            
            mese = data.month
            
            if mese >= 9 or mese == 1:
                return 1
            elif mese >= 2 and mese <= 6:
                return 2
            else:
                return None
        except:
            return None
    
    def _create_expandable_voto_card(self, voto):
        """Crea una card voto espandibile"""
        materia = voto.get('subjectDesc', voto.get('materia', 'N/A'))
        valore_str = voto.get('displayValue', voto.get('decimalValue', voto.get('voto', 'N/A')))
        data = voto.get('evtDate', voto.get('data', 'N/A'))
        tipo = voto.get('componentDesc', voto.get('tipo', 'N/A'))
        nota = voto.get('notesForFamily', voto.get('nota', ''))
        
        colore_codice = voto.get('color', '')
        voto_non_conta = (colore_codice == 'blue')
        
        quadrimestre = self._determina_quadrimestre(data)
        quadrimestre_str = f' [Q{quadrimestre}]' if quadrimestre else ''
        
        if voto_non_conta:
            colore = (0.3, 0.5, 1, 1)
        else:
            try:
                valore_num = float(str(valore_str).replace(',', '.').replace('+', '').replace('-', '').replace('½', '.5'))
                colore = (0, 0.8, 0, 1) if valore_num >= 6 else (1, 0, 0, 1)
            except (ValueError, TypeError):
                colore = (0.5, 0.5, 0.5, 1)
        
        # Determina se il testo è lungo
        testo_lungo = len(tipo) > 30 or (nota and len(nota) > 50)
        
        # Container principale
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(110)
        )
        
        # Box principale con voto e info
        voto_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(110),
            padding=ResponsiveLayout.get_padding(),
            spacing=ResponsiveLayout.get_spacing()
        )
        
        # Box voto (sinistra)
        voto_left = BoxLayout(
            orientation='vertical',
            size_hint_x=0.25,
            padding=dp(5)
        )
        voto_left.add_widget(Label(
            text=f'[b]{valore_str}[/b]',
            markup=True,
            font_size=ResponsiveLayout.get_font_size(28),
            color=colore,
            size_hint_y=0.6
        ))
        voto_left.add_widget(Label(
            text=data + quadrimestre_str,
            font_size=ResponsiveLayout.get_font_size(10),
            size_hint_y=0.4
        ))
        
        # Box dettagli (destra)
        voto_right = BoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            padding=dp(5),
            spacing=dp(2)
        )
        
        # Label materia
        materia_label = Label(
            text=f'[b]{materia}[/b]',
            markup=True,
            font_size=ResponsiveLayout.get_font_size(14),
            size_hint_y=None,
            height=ResponsiveLayout.get_height(25),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        materia_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
        )
        voto_right.add_widget(materia_label)
        
        # Label tipo (troncato se lungo)
        tipo_display = tipo if len(tipo) <= 50 else tipo[:47] + '...'
        tipo_label = Label(
            text=tipo_display,
            font_size=ResponsiveLayout.get_font_size(12),
            size_hint_y=None,
            height=ResponsiveLayout.get_height(20),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        tipo_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
        )
        voto_right.add_widget(tipo_label)
        
        # Note (troncate se lunghe)
        if nota:
            nota_display = nota if len(nota) <= 80 else nota[:77] + '...'
            nota_label = Label(
                text=nota_display,
                font_size=ResponsiveLayout.get_font_size(10),
                size_hint_y=None,
                height=ResponsiveLayout.get_height(30),
                color=(0.7, 0.7, 0.7, 1),
                halign='left',
                valign='top',
                text_size=(None, None)
            )
            nota_label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
            )
            voto_right.add_widget(nota_label)
        
        voto_box.add_widget(voto_left)
        voto_box.add_widget(voto_right)
        card_container.add_widget(voto_box)
        
        # Box espandibile (inizialmente nascosto)
        expanded_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=0,
            padding=[ResponsiveLayout.get_padding(), 0, ResponsiveLayout.get_padding(), ResponsiveLayout.get_padding()],
            spacing=dp(5),
            opacity=0
        )
        
        if testo_lungo:
            # Tipo completo
            if len(tipo) > 50:
                tipo_full = Label(
                    text=f'[b]Tipo:[/b] {tipo}',
                    markup=True,
                    font_size=ResponsiveLayout.get_font_size(12),
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    text_size=(None, None)
                )
                tipo_full.bind(
                    size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
                )
                tipo_full.bind(
                    texture_size=lambda instance, value: setattr(instance, 'height', value[1])
                )
                expanded_box.add_widget(tipo_full)
            
            # Note complete
            if nota and len(nota) > 80:
                nota_full = Label(
                    text=f'[b]Note:[/b] {nota}',
                    markup=True,
                    font_size=ResponsiveLayout.get_font_size(11),
                    size_hint_y=None,
                    color=(0.7, 0.7, 0.7, 1),
                    halign='left',
                    valign='top',
                    text_size=(None, None)
                )
                nota_full.bind(
                    size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
                )
                nota_full.bind(
                    texture_size=lambda instance, value: setattr(instance, 'height', value[1])
                )
                expanded_box.add_widget(nota_full)
        
        card_container.add_widget(expanded_box)
        
        # Pulsante espandi/comprimi (solo se necessario)
        if testo_lungo:
            expand_btn = Button(
                text='Mostra tutto',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(35),
                font_size=ResponsiveLayout.get_font_size(11),
                background_color=(0.2, 0.2, 0.2, 1)
            )
            
            # Stato espansione
            expand_btn.is_expanded = False
            
            def toggle_expand(instance):
                if instance.is_expanded:
                    # Comprimi
                    instance.is_expanded = False
                    instance.text = 'Mostra tutto'
                    expanded_box.height = 0
                    expanded_box.opacity = 0
                    card_container.height = ResponsiveLayout.get_height(110 + 35)
                else:
                    # Espandi
                    instance.is_expanded = True
                    instance.text = 'Nascondi'
                    # Calcola altezza necessaria
                    total_height = sum(child.height for child in expanded_box.children) + dp(10)
                    expanded_box.height = total_height
                    expanded_box.opacity = 1
                    card_container.height = ResponsiveLayout.get_height(110 + 35) + total_height
            
            expand_btn.bind(on_press=toggle_expand)
            card_container.add_widget(expand_btn)
            card_container.height = ResponsiveLayout.get_height(110 + 35)
        
        return card_container
    
    def display_voti(self, voti_data):
        self.voti_layout.clear_widgets()
        self.voti_data = voti_data
        
        if not voti_data:
            self.voti_layout.add_widget(Label(
                text='Nessun voto disponibile',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                font_size=ResponsiveLayout.get_font_size(14)
            ))
            self.data_loaded = True
            return
        
        for voto in voti_data:
            # Crea card espandibile
            card = self._create_expandable_voto_card(voto)
            self.voti_layout.add_widget(card)
            self.voti_layout.add_widget(card)
            
            # Separatore
            separator = Widget(size_hint_y=None, height=dp(1))
            with separator.canvas:
                Color(0.3, 0.3, 0.3, 0.5)
                separator.rect = Rectangle(pos=separator.pos, size=separator.size)
            separator.bind(pos=lambda instance, value: setattr(instance.rect, 'pos', instance.pos))
            separator.bind(size=lambda instance, value: setattr(instance.rect, 'size', instance.size))
            self.voti_layout.add_widget(separator)
        
        self.data_loaded = True

    def display_voti(self, voti_data):
        self.voti_layout.clear_widgets()
        self.voti_data = voti_data
        
        if not voti_data:
            self.voti_layout.add_widget(Label(
                text='Nessun voto disponibile',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                font_size=ResponsiveLayout.get_font_size(14)
            ))
            self.data_loaded = True
            return
        
        for voto in voti_data:
            # Calcola altezza dinamica in base alla presenza di note
            nota = voto.get('notesForFamily', voto.get('nota', ''))
            card_height = ResponsiveLayout.get_height(140) if nota else ResponsiveLayout.get_height(110)
            
            voto_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=card_height,
                padding=ResponsiveLayout.get_padding(),
                spacing=ResponsiveLayout.get_spacing()
            )
            
            materia = voto.get('subjectDesc', voto.get('materia', 'N/A'))
            valore_str = voto.get('displayValue', voto.get('decimalValue', voto.get('voto', 'N/A')))
            data = voto.get('evtDate', voto.get('data', 'N/A'))
            tipo = voto.get('componentDesc', voto.get('tipo', 'N/A'))
            
            colore_codice = voto.get('color', '')
            voto_non_conta = (colore_codice == 'blue')
            
            quadrimestre = self._determina_quadrimestre(data)
            quadrimestre_str = f' [Q{quadrimestre}]' if quadrimestre else ''
            
            if voto_non_conta:
                colore = (0.3, 0.5, 1, 1)
            else:
                try:
                    valore_num = float(str(valore_str).replace(',', '.').replace('+', '').replace('-', '').replace('½', '.5'))
                    colore = (0, 0.8, 0, 1) if valore_num >= 6 else (1, 0, 0, 1)
                except (ValueError, TypeError):
                    colore = (0.5, 0.5, 0.5, 1)
            
            # Box voto (sinistra)
            voto_left = BoxLayout(
                orientation='vertical',
                size_hint_x=0.25,
                padding=dp(5)
            )
            voto_left.add_widget(Label(
                text=f'[b]{valore_str}[/b]',
                markup=True,
                font_size=ResponsiveLayout.get_font_size(28),
                color=colore,
                size_hint_y=0.6
            ))
            voto_left.add_widget(Label(
                text=data + quadrimestre_str,
                font_size=ResponsiveLayout.get_font_size(10),
                size_hint_y=0.4
            ))
            
            # Box dettagli (destra)
            voto_right = BoxLayout(
                orientation='vertical',
                size_hint_x=0.75,
                padding=dp(5),
                spacing=dp(2)
            )
            
            # Label materia con text wrapping
            materia_label = Label(
                text=f'[b]{materia}[/b]',
                markup=True,
                font_size=ResponsiveLayout.get_font_size(14),
                size_hint_y=None,
                height=ResponsiveLayout.get_height(25),
                halign='left',
                valign='middle',
                text_size=(None, None)  # Inizialmente None
            )
            # Bind per impostare text_size alla larghezza effettiva del widget
            materia_label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
            )
            voto_right.add_widget(materia_label)
            
            # Label tipo con text wrapping
            tipo_label = Label(
                text=tipo,
                font_size=ResponsiveLayout.get_font_size(12),
                size_hint_y=None,
                height=ResponsiveLayout.get_height(20),
                halign='left',
                valign='middle',
                text_size=(None, None)
            )
            tipo_label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
            )
            voto_right.add_widget(tipo_label)
            
            # Note (se presenti)
            if nota:
                nota_label = Label(
                    text=nota,
                    font_size=ResponsiveLayout.get_font_size(10),
                    size_hint_y=None,
                    height=ResponsiveLayout.get_height(40),
                    color=(0.7, 0.7, 0.7, 1),
                    halign='left',
                    valign='top',
                    text_size=(None, None)
                )
                nota_label.bind(
                    size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None))
                )
                voto_right.add_widget(nota_label)
            
            voto_box.add_widget(voto_left)
            voto_box.add_widget(voto_right)
            
            self.voti_layout.add_widget(voto_box)
            
            # Separatore
            separator = Widget(size_hint_y=None, height=dp(1))
            with separator.canvas:
                Color(0.3, 0.3, 0.3, 0.5)
                separator.rect = Rectangle(pos=separator.pos, size=separator.size)
            separator.bind(pos=lambda instance, value: setattr(instance.rect, 'pos', instance.pos))
            separator.bind(size=lambda instance, value: setattr(instance.rect, 'size', instance.size))
            self.voti_layout.add_widget(separator)
        
        self.data_loaded = True
    
    def display_media(self, voti_data):
        self.media_layout.clear_widgets()
        
        if not voti_data:
            self.media_layout.add_widget(Label(
                text='Nessun dato disponibile',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                font_size=ResponsiveLayout.get_font_size(14)
            ))
            return
        
        materie_q1 = {}
        materie_q2 = {}
        materie_totale = {}
        
        for voto in voti_data:
            colore_codice = voto.get('color', '')
            if colore_codice == 'blue':
                continue
                
            materia = voto.get('subjectDesc', voto.get('materia', 'N/A'))
            data = voto.get('evtDate', voto.get('data', 'N/A'))
            quadrimestre = self._determina_quadrimestre(data)
            
            try:
                valore = float(voto.get('decimalValue', voto.get('voto', 0)))
                if valore > 0:
                    if materia not in materie_totale:
                        materie_totale[materia] = []
                    materie_totale[materia].append(valore)
                    
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
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(18)
        ))
        
        # Determina se usare 4 colonne (tablet) o layout compatto (phone)
        use_compact = not ResponsiveLayout.is_tablet()
        
        if not use_compact:
            # Layout tablet - tabella completa
            header_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                padding=dp(5)
            )
            header_box.add_widget(Label(text='[b]Materia[/b]', markup=True, size_hint_x=0.4, font_size=ResponsiveLayout.get_font_size(14)))
            header_box.add_widget(Label(text='[b]Q1[/b]', markup=True, size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14)))
            header_box.add_widget(Label(text='[b]Q2[/b]', markup=True, size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14)))
            header_box.add_widget(Label(text='[b]Totale[/b]', markup=True, size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14)))
            self.media_layout.add_widget(header_box)
        
        tutte_medie_q1 = []
        tutte_medie_q2 = []
        tutte_medie_totale = []
        
        for materia in sorted(materie_totale.keys()):
            if use_compact:
                # Layout compatto per smartphone
                media_box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=ResponsiveLayout.get_height(80),
                    padding=dp(10),
                    spacing=dp(5)
                )
                
                media_box.add_widget(Label(
                    text=f'[b]{materia}[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=dp(25),
                    font_size=ResponsiveLayout.get_font_size(13),
                    halign='left',
                    valign='middle'
                ))
                
                values_box = BoxLayout(orientation='horizontal', spacing=dp(10))
                
                if materia in materie_q1:
                    media_q1 = sum(materie_q1[materia]) / len(materie_q1[materia])
                    tutte_medie_q1.append(media_q1)
                    values_box.add_widget(Label(text=f'Q1: {media_q1:.2f}', font_size=ResponsiveLayout.get_font_size(12)))
                
                if materia in materie_q2:
                    media_q2 = sum(materie_q2[materia]) / len(materie_q2[materia])
                    tutte_medie_q2.append(media_q2)
                    values_box.add_widget(Label(text=f'Q2: {media_q2:.2f}', font_size=ResponsiveLayout.get_font_size(12)))
                
                media_totale = sum(materie_totale[materia]) / len(materie_totale[materia])
                tutte_medie_totale.append(media_totale)
                values_box.add_widget(Label(
                    text=f'[b]Tot: {media_totale:.2f}[/b]',
                    markup=True,
                    font_size=ResponsiveLayout.get_font_size(13)
                ))
                
                media_box.add_widget(values_box)
            else:
                # Layout tabella per tablet
                media_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=ResponsiveLayout.get_height(50),
                    padding=dp(5)
                )
                
                materia_label = Label(
                    text=materia,
                    size_hint_x=0.4,
                    halign='left',
                    valign='middle',
                    font_size=ResponsiveLayout.get_font_size(13)
                )
                materia_label.bind(width=lambda *x: materia_label.setter('text_size')(materia_label, (materia_label.width, None)))
                media_box.add_widget(materia_label)
                
                if materia in materie_q1:
                    media_q1 = sum(materie_q1[materia]) / len(materie_q1[materia])
                    tutte_medie_q1.append(media_q1)
                    media_box.add_widget(Label(text=f'{media_q1:.2f}', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14)))
                else:
                    media_box.add_widget(Label(text='-', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14), color=(0.5, 0.5, 0.5, 1)))
                
                if materia in materie_q2:
                    media_q2 = sum(materie_q2[materia]) / len(materie_q2[materia])
                    tutte_medie_q2.append(media_q2)
                    media_box.add_widget(Label(text=f'{media_q2:.2f}', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14)))
                else:
                    media_box.add_widget(Label(text='-', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(14), color=(0.5, 0.5, 0.5, 1)))
                
                media_totale = sum(materie_totale[materia]) / len(materie_totale[materia])
                tutte_medie_totale.append(media_totale)
                media_box.add_widget(Label(
                    text=f'[b]{media_totale:.2f}[/b]',
                    markup=True,
                    size_hint_x=0.2,
                    font_size=ResponsiveLayout.get_font_size(14)
                ))
            
            self.media_layout.add_widget(media_box)
        
        # Medie generali
        if tutte_medie_totale:
            self.media_layout.add_widget(Label(
                text='',
                size_hint_y=None,
                height=dp(20)
            ))
            
            if use_compact:
                # Layout compatto
                generale_box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=ResponsiveLayout.get_height(100),
                    padding=dp(10),
                    spacing=dp(5)
                )
                
                generale_box.add_widget(Label(
                    text='[b]MEDIA GENERALE[/b]',
                    markup=True,
                    font_size=ResponsiveLayout.get_font_size(16)
                ))
                
                values_box = BoxLayout(orientation='horizontal', spacing=dp(10))
                
                if tutte_medie_q1:
                    media_gen_q1 = sum(tutte_medie_q1) / len(tutte_medie_q1)
                    values_box.add_widget(Label(text=f'Q1: [b]{media_gen_q1:.2f}[/b]', markup=True, font_size=ResponsiveLayout.get_font_size(15)))
                
                if tutte_medie_q2:
                    media_gen_q2 = sum(tutte_medie_q2) / len(tutte_medie_q2)
                    values_box.add_widget(Label(text=f'Q2: [b]{media_gen_q2:.2f}[/b]', markup=True, font_size=ResponsiveLayout.get_font_size(15)))
                
                media_gen_totale = sum(tutte_medie_totale) / len(tutte_medie_totale)
                values_box.add_widget(Label(
                    text=f'Tot: [b]{media_gen_totale:.2f}[/b]',
                    markup=True,
                    font_size=ResponsiveLayout.get_font_size(16),
                    color=(0, 0.7, 1, 1)
                ))
                
                generale_box.add_widget(values_box)
            else:
                # Layout tabella
                generale_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=ResponsiveLayout.get_height(60),
                    padding=dp(5)
                )
                
                generale_box.add_widget(Label(
                    text='[b]MEDIA GENERALE[/b]',
                    markup=True,
                    size_hint_x=0.4,
                    font_size=ResponsiveLayout.get_font_size(16)
                ))
                
                if tutte_medie_q1:
                    media_gen_q1 = sum(tutte_medie_q1) / len(tutte_medie_q1)
                    generale_box.add_widget(Label(
                        text=f'[b]{media_gen_q1:.2f}[/b]',
                        markup=True,
                        size_hint_x=0.2,
                        font_size=ResponsiveLayout.get_font_size(18)
                    ))
                else:
                    generale_box.add_widget(Label(text='-', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(18)))
                
                if tutte_medie_q2:
                    media_gen_q2 = sum(tutte_medie_q2) / len(tutte_medie_q2)
                    generale_box.add_widget(Label(
                        text=f'[b]{media_gen_q2:.2f}[/b]',
                        markup=True,
                        size_hint_x=0.2,
                        font_size=ResponsiveLayout.get_font_size(18)
                    ))
                else:
                    generale_box.add_widget(Label(text='-', size_hint_x=0.2, font_size=ResponsiveLayout.get_font_size(18)))
                
                media_gen_totale = sum(tutte_medie_totale) / len(tutte_medie_totale)
                generale_box.add_widget(Label(
                    text=f'[b]{media_gen_totale:.2f}[/b]',
                    markup=True,
                    size_hint_x=0.2,
                    font_size=ResponsiveLayout.get_font_size(18),
                    color=(0, 0.7, 1, 1)
                ))
            
            self.media_layout.add_widget(generale_box)
    
    def display_statistics(self, voti_data):
        self.stats_layout.clear_widgets()
        
        if not voti_data:
            self.stats_layout.add_widget(Label(
                text='Nessun dato disponibile per le statistiche',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                font_size=ResponsiveLayout.get_font_size(14)
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
                    if materia not in materie_data:
                        materie_data[materia] = []
                    materie_data[materia].append(valore)
                    
                    voto_arrotondato = round(valore)
                    distribuzione_voti[voto_arrotondato] = distribuzione_voti.get(voto_arrotondato, 0) + 1
                    
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
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(20)
        ))
        
        # Card: Statistiche generali
        stats_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(200),
            padding=dp(10),
            spacing=dp(10)
        )
        
        stats_grid = GridLayout(
            cols=2,
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            height=ResponsiveLayout.get_height(180)
        )
        
        # Totale voti
        total_voti = sum(len(v) for v in materie_data.values())
        stats_grid.add_widget(self._create_stat_box('Voti Totali', str(total_voti), (0.2, 0.6, 1, 1)))
        
        # Materie
        stats_grid.add_widget(self._create_stat_box('Materie', str(len(materie_data)), (0.4, 0.7, 0.3, 1)))
        
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
            height=ResponsiveLayout.get_height(40),
            font_size=ResponsiveLayout.get_font_size(16)
        ))

        
        materie_ordinate = sorted(materie_data.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
        for materia, voti in materie_ordinate:
            if len(voti) > 0:
                media = sum(voti) / len(voti)
                self.stats_layout.add_widget(self._create_bar_chart(materia, media, len(voti)))
        
        # Grafico: Distribuzione voti
        if distribuzione_voti:
            self.stats_layout.add_widget(Label(
                text='[b]Distribuzione Voti[/b]',
                markup=True,
                size_hint_y=None,
                height=ResponsiveLayout.get_height(50),
                font_size=ResponsiveLayout.get_font_size(16)
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
            padding=ResponsiveLayout.get_padding()
        )
        
        with box.canvas.before:
            Color(*color, 0.3)
            box.rect = Rectangle(pos=box.pos, size=box.size)
        
        box.bind(pos=lambda *args: setattr(box.rect, 'pos', box.pos))
        box.bind(size=lambda *args: setattr(box.rect, 'size', box.size))
        
        box.add_widget(Label(
            text=label,
            font_size=ResponsiveLayout.get_font_size(12),
            size_hint_y=0.4,
            color=(0.7, 0.7, 0.7, 1)
        ))
        box.add_widget(Label(
            text=f'[b]{value}[/b]',
            markup=True,
            font_size=ResponsiveLayout.get_font_size(24),
            size_hint_y=0.6,
            color=color
        ))
        
        return box
    
    def _create_bar_chart(self, materia, media, count):
        """Crea una barra per il grafico delle medie"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(50),
            padding=dp(5),
            spacing=ResponsiveLayout.get_spacing()
        )
        
        # Nome materia
        materia_label = Label(
            text=materia[:25],
            size_hint_x=0.4,
            halign='left',
            valign='middle',
            font_size=ResponsiveLayout.get_font_size(12)
        )
        materia_label.bind(width=lambda *x: materia_label.setter('text_size')(materia_label, (materia_label.width, None)))
        box.add_widget(materia_label)
        
        # Barra grafico
        bar_container = BoxLayout(size_hint_x=0.4)
        bar_widget = Widget()
        
        def draw_bar(*args):
            bar_widget.canvas.clear()
            with bar_widget.canvas:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=bar_widget.pos, size=bar_widget.size)
                
                if media >= 6:
                    Color(0, 0.8, 0, 1)
                else:
                    Color(1, 0.2, 0.2, 1)
                
                bar_width = (media / 10.0) * bar_widget.width
                Rectangle(pos=bar_widget.pos, size=(bar_width, bar_widget.height))
                
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
            font_size=ResponsiveLayout.get_font_size(13)
        ))
        
        return box
    
    def _create_histogram_bar(self, voto, count, max_count):
        """Crea una barra per l'istogramma della distribuzione"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(40),
            padding=dp(5),
            spacing=ResponsiveLayout.get_spacing()
        )
        
        # Voto
        box.add_widget(Label(
            text=str(voto),
            size_hint_x=0.1,
            font_size=ResponsiveLayout.get_font_size(16),
            bold=True
        ))
        
        # Barra
        bar_container = BoxLayout(size_hint_x=0.7)
        bar_widget = Widget()
        
        def draw_hist_bar(*args):
            bar_widget.canvas.clear()
            with bar_widget.canvas:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=bar_widget.pos, size=bar_widget.size)
                
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
            font_size=ResponsiveLayout.get_font_size(14)
        ))
        
        return box
    
    def display_assenze(self, assenze_data):
        self.assenze_layout.clear_widgets()
        self.assenze_data = assenze_data
        
        if not assenze_data:
            self.assenze_layout.add_widget(Label(
                text='Nessun dato sulle assenze disponibile',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(40),
                font_size=ResponsiveLayout.get_font_size(14)
            ))
            return
        
        # Conta le assenze
        assenze_totali = 0
        ritardi = 0
        uscite_anticipate = 0
        
        for assenza in assenze_data:
            evento_codice = assenza.get('evtCode', '')
            if evento_codice == 'ABA0':
                assenze_totali += 1
            elif evento_codice == 'ABR0':
                ritardi += 1
            elif evento_codice == 'ABU0':
                uscite_anticipate += 1
        
        # Calcola giorni scuola
        giorni_totali, giorni_trascorsi, giorni_rimanenti = self._calcola_giorni_scuola()
        
        # Limite assenze (25% dei giorni totali)
        limite_assenze = int(giorni_totali * 0.25)
        assenze_disponibili = limite_assenze - assenze_totali
        percentuale_assenze = (assenze_totali / giorni_trascorsi * 100) if giorni_trascorsi > 0 else 0
        percentuale_limite = (assenze_totali / limite_assenze * 100) if limite_assenze > 0 else 0
        
        # Titolo
        self.assenze_layout.add_widget(Label(
            text='[b]REPORT ASSENZE (APPROSSIMATO!)[/b]',
            markup=True,
            size_hint_y=None,
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(20)
        ))
        
        # Card: Statistiche assenze
        stats_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(280),
            padding=dp(10),
            spacing=dp(10)
        )
        
        stats_grid = GridLayout(
            cols=2,
            spacing=ResponsiveLayout.get_spacing(),
            size_hint_y=None,
            height=ResponsiveLayout.get_height(260)
        )
        
        # Assenze totali
        color_assenze = (1, 0.3, 0.3, 1) if assenze_totali > limite_assenze * 0.7 else (0.2, 0.6, 1, 1)
        stats_grid.add_widget(self._create_stat_box('Assenze', str(assenze_totali), color_assenze))
        
        # Ritardi
        stats_grid.add_widget(self._create_stat_box('Ritardi', str(ritardi), (1, 0.7, 0.2, 1)))
        
        # Uscite anticipate
        stats_grid.add_widget(self._create_stat_box('Uscite Antic.', str(uscite_anticipate), (0.9, 0.5, 0.2, 1)))
        
        # Percentuale assenze
        stats_grid.add_widget(self._create_stat_box('% Assenze', f'{percentuale_assenze:.1f}%', color_assenze))
        
        # Percentuale anno trascorso
        percentuale_anno = (giorni_trascorsi / giorni_totali * 100) if giorni_totali > 0 else 0
        stats_grid.add_widget(self._create_stat_box('% Anno Trascorso', f'{percentuale_anno:.1f}%', (0.5, 0.7, 0.9, 1)))
        
        # Spazio vuoto per simmetria
        stats_grid.add_widget(BoxLayout())
        
        stats_card.add_widget(stats_grid)
        self.assenze_layout.add_widget(stats_card)
        
        # Sezione giorni scolastici
        self.assenze_layout.add_widget(Label(
            text='[b]Anno Scolastico[/b]',
            markup=True,
            size_hint_y=None,
            height=ResponsiveLayout.get_height(40),
            font_size=ResponsiveLayout.get_font_size(16)
        ))
        
        giorni_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(150),
            padding=dp(10),
            spacing=dp(5)
        )
        
        for text, color in [
            (f'Giorni scolastici totali: [b]{giorni_totali}[/b]', (1, 1, 1, 1)),
            (f'Giorni trascorsi: [b]{giorni_trascorsi}[/b]', (1, 1, 1, 1)),
            (f'Giorni rimanenti: [b]{giorni_rimanenti}[/b]', (1, 1, 1, 1)),
            (f'Limite assenze (25%): [b]{limite_assenze}[/b]', (1, 0.6, 0, 1))
        ]:
            label = Label(
                text=text,
                markup=True,
                size_hint_y=None,
                height=ResponsiveLayout.get_height(35),
                font_size=ResponsiveLayout.get_font_size(14),
                halign='left',
                color=color
            )
            label.bind(width=lambda *x: label.setter('text_size')(label, (label.width, None)))
            giorni_box.add_widget(label)
        
        self.assenze_layout.add_widget(giorni_box)
        
        # Barra progresso assenze
        self.assenze_layout.add_widget(Label(
            text='[b]Limite Annuale Assenze[/b]',
            markup=True,
            size_hint_y=None,
            height=ResponsiveLayout.get_height(40),
            font_size=ResponsiveLayout.get_font_size(16)
        ))
        
        # Messaggio stato
        if assenze_disponibili > 0:
            stato_text = f'Puoi ancora fare [b]{assenze_disponibili}[/b] assenze'
            stato_color = (0, 0.8, 0, 1) if assenze_disponibili > limite_assenze * 0.3 else (1, 0.6, 0, 1)
        else:
            stato_text = f'HAI SUPERATO IL LIMITE DI {abs(assenze_disponibili)} ASSENZE!'
            stato_color = (1, 0, 0, 1)
        
        self.assenze_layout.add_widget(Label(
            text=stato_text,
            markup=True,
            size_hint_y=None,
            height=ResponsiveLayout.get_height(40),
            font_size=ResponsiveLayout.get_font_size(15),
            color=stato_color
        ))
        
        # Barra progresso
        progress_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(100),
            padding=dp(10),
            spacing=dp(5)
        )
        
        bar_container = BoxLayout(size_hint_y=None, height=ResponsiveLayout.get_height(50))
        bar_widget = Widget()
        
        def draw_progress_bar(*args):
            bar_widget.canvas.clear()
            with bar_widget.canvas:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=bar_widget.pos, size=bar_widget.size)
                
                if percentuale_limite <= 70:
                    Color(0, 0.8, 0, 0.8)
                elif percentuale_limite <= 90:
                    Color(1, 0.7, 0, 0.8)
                else:
                    Color(1, 0.2, 0.2, 0.8)
                
                bar_width = min(percentuale_limite / 100.0, 1.0) * bar_widget.width
                Rectangle(pos=bar_widget.pos, size=(bar_width, bar_widget.height))
                
                Color(1, 0.7, 0, 0.5)
                line_x = bar_widget.x + 0.7 * bar_widget.width
                Line(points=[line_x, bar_widget.y, line_x, bar_widget.y + bar_widget.height], width=2)
                
                Color(1, 0, 0, 0.7)
                line_x = bar_widget.x + bar_widget.width
                Line(points=[line_x, bar_widget.y, line_x, bar_widget.y + bar_widget.height], width=2)
        
        bar_widget.bind(pos=draw_progress_bar, size=draw_progress_bar)
        bar_container.add_widget(bar_widget)
        progress_box.add_widget(bar_container)
        
        progress_box.add_widget(Label(
            text=f'{assenze_totali} / {limite_assenze} assenze ({percentuale_limite:.1f}%)',
            size_hint_y=None,
            height=ResponsiveLayout.get_height(30),
            font_size=ResponsiveLayout.get_font_size(14)
        ))
        
        self.assenze_layout.add_widget(progress_box)
        
        # Lista dettagliata assenze
        self.assenze_layout.add_widget(Label(
            text='[b]Dettaglio Assenze[/b]',
            markup=True,
            size_hint_y=None,
            height=ResponsiveLayout.get_height(50),
            font_size=ResponsiveLayout.get_font_size(16)
        ))
        
        # Ordina per data
        assenze_ordinate = sorted(assenze_data, key=lambda x: x.get('evtDate', ''), reverse=True)
        
        for assenza in assenze_ordinate[:20]:
            evento_codice = assenza.get('evtCode', '')
            data = assenza.get('evtDate', 'N/A')
            giustificata = assenza.get('isJustified', False)
            
            if evento_codice == 'ABA0':
                tipo = 'Assenza'
                colore = (1, 0.3, 0.3, 1)
            elif evento_codice == 'ABR0':
                tipo = 'Ritardo'
                colore = (1, 0.7, 0.2, 1)
            elif evento_codice == 'ABU0':
                tipo = 'Uscita Anticipata'
                colore = (0.9, 0.5, 0.2, 1)
            else:
                tipo = 'Altro'
                colore = (0.5, 0.5, 0.5, 1)
            
            stato = 'Giustificata' if giustificata else 'Da giustificare'
            stato_colore = (0, 0.8, 0, 1) if giustificata else (1, 0.5, 0, 1)
            
            assenza_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=ResponsiveLayout.get_height(60),
                padding=ResponsiveLayout.get_padding(),
                spacing=ResponsiveLayout.get_spacing()
            )
            
            # Data e tipo
            left_box = BoxLayout(orientation='vertical', size_hint_x=0.4)
            left_box.add_widget(Label(
                text=data,
                font_size=ResponsiveLayout.get_font_size(12),
                size_hint_y=0.4,
                color=(0.6, 0.6, 0.6, 1)
            ))
            left_box.add_widget(Label(
                text=tipo,
                font_size=ResponsiveLayout.get_font_size(14),
                size_hint_y=0.6,
                color=colore
            ))
            assenza_box.add_widget(left_box)
            
            # Stato giustificazione
            stato_label = Label(
                text=stato,
                size_hint_x=0.6,
                font_size=ResponsiveLayout.get_font_size(13),
                color=stato_colore,
                halign='right',
                valign='middle'
            )
            stato_label.bind(width=lambda *x: stato_label.setter('text_size')(stato_label, (stato_label.width, None)))
            assenza_box.add_widget(stato_label)
            
            self.assenze_layout.add_widget(assenza_box)


class ClassevivaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.utente = None
        self.login_screen = None
        self.main_screen = None
        self.credentials_file = os.path.join(os.path.expanduser('~'), '.classeviva_credentials.json')
    
    def save_credentials(self, username, password):
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump({'username': username, 'password': password}, f)
        except Exception as e:
            print(f'Errore salvataggio credenziali: {e}')

    def load_credentials(self):
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f'Errore caricamento credenziali: {e}')
        return None
    
    def build(self):
        saved_creds = self.load_credentials()
        if saved_creds:
            self.login_screen = LoginScreen(self)
            threading.Thread(
                target=self.login,
                args=(saved_creds['username'], saved_creds['password'])
            ).start()
            return self.login_screen
        else:
            self.login_screen = LoginScreen(self)
            return self.login_screen
    
    def login(self, username, password):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    
            try:
                self.utente = classeviva.Utente(username, password)
                loop.run_until_complete(self.utente.accedi())
            except Exception as e:
                error_msg = str(e)
                Clock.schedule_once(
                    lambda dt: self.show_error(f'Login fallito: {error_msg}'),
                    0
                )
                return
    
            self.save_credentials(username, password)
    
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
            if loop:
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
            
            # Caricamento voti
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
            
            # Caricamento assenze
            assenze = None
            for attempt in range(3):
                try:
                    assenze = loop.run_until_complete(self.utente.assenze())
                    if assenze is not None:
                        break
                except Exception as e:
                    print(f'Tentativo {attempt + 1} caricamento assenze fallito: {e}')
                    if attempt < 2:
                        Clock.schedule_once(lambda dt: None, 0.5)
            
            if assenze is not None:
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_assenze(assenze),
                    0
                )
            else:
                Clock.schedule_once(
                    lambda dt: self.main_screen.display_assenze([]),
                    0
                )
                
        except Exception as e:
            print(f'Errore caricamento dati: {e}')
        finally:
            if loop:
                loop.close()

    def do_logout(self):
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
        except Exception as e:
            print(f'Errore eliminazione credenziali: {e}')

        self.utente = None
        self.login_screen = LoginScreen(self)
        self.root.clear_widgets()
        self.root.add_widget(self.login_screen)


if __name__ == '__main__':
    ClassevivaApp().run()
