import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict
import math

# --- 1. SISTEMA DE DESIGN (CONFIGURAÇÕES GLOBAIS) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Paleta de Cores
COLORS = {
    "bg_card": "#2b2b2b",       # Fundo dos cartões
    "border": "#3a3a3a",        # Borda sutil
    "accent": "#1f6aa5",        # Azul padrão do tema
    "accent_hover": "#144870",  # Azul mais escuro
    "success": "#2CC985",       # Verde Vitória
    "danger": "#d63031",        # Vermelho Derrota
    "warning": "#f39c12",       # Amarelo/Laranja (para Challenge/Ultimate)
    "highlight": "#4aa3df",     # Ciano destaque
    "text_main": "white",
    "text_muted": "gray70",
    "separator": "#444444"
}

# Tipografia
FONTS = {
    "h1": ("Roboto", 36, "bold"),       
    "h2": ("Roboto", 22, "bold"),       
    "h3": ("Roboto Medium", 16),        
    "body": ("Roboto", 13),             
    "body_bold": ("Roboto", 13, "bold"),
    "mono": ("Roboto Medium", 10),           
    "card_label": ("Roboto", 11, "bold"), 
    "card_value": ("Roboto", 18, "bold"),
    "stat_big": ("Roboto", 28, "bold"), # Novo para stats globais
    "dashboard_row": ("Roboto Medium", 13)
}

# --- 2. DADOS DO JOGO (Mantidos) ---
HEROES_DATA = {
    "Legacy": ["Base", "America's Greatest", "Young", "Freedom Five"],
    "Bunker": ["Base", "G.I.", "Freedom Five", "Termi-Nation", "Engine of War"],
    "Wraith": ["Base", "Rook City", "Freedom Five", "Price of Freedom"],
    "Tachyon": ["Base", "Super Scientific", "Freedom Five", "Team Leader (Freedom Six)"],
    "Absolute Zero": ["Base", "Elemental", "Freedom Five", "Termi-Nation"],
    "Unity": ["Base", "Termi-Nation", "Golem"],
    "Haka": ["Base", "Eternal", "Prime Wardens", "XTREME Prime Wardens"],
    "Fanatic": ["Base", "Redeemer", "Prime Wardens", "XTREME Prime Wardens"],
    "Tempest": ["Base", "Sacrifice", "Prime Wardens", "XTREME Prime Wardens"],
    "Argent Adept": ["Base", "Dark Conductor", "Prime Wardens", "XTREME Prime Wardens"],
    "Captain Cosmic": ["Base", "Prime Wardens", "Requital", "XTREME Prime Wardens"],
    "Expatriette": ["Base", "Dark Watch"],
    "Setback": ["Base", "Dark Watch"],
    "Nightmist": ["Base", "Dark Watch"],
    "Mr. Fixer": ["Base", "Dark Watch"],
    "Harpy": ["Base", "Dark Watch"],
    "Ra": ["Base", "Setting Sun", "Horus"],
    "Visionary": ["Base", "Dark", "Unleashed"],
    "Chrono-Ranger": ["Base", "Best of Times"],
    "Omnitron-X": ["Base", "Omnitron-U"],
    "Sky-Scraper": ["Base", "Extremist"],
    "K.N.Y.F.E.": ["Base", "Rogue Agent"],
    "Parse": ["Base", "Fugue State"],
    "Naturalist": ["Base", "Hunted"],
    "Sentinels": ["Base", "Adamant"],
    "Guise": ["Base", "Santa", "Completionist"],
    "Scholar": ["Base", "Infinite"],
    "Stuntman": ["Base", "Action Hero"],
    "Benchmark": ["Base", "Supply and Demand"],
    "La Comodora": ["Base", "Curse of the Black Spot"],
    "Lifeline": ["Base", "Blood Mage"],
    "Akash'Thriya": ["Base", "Spirit of the Void"],
    "Luminary": ["Base", "Heroic (Ivana)"],
    "Doctor Medico": ["Base", "Malpractice"],
    "Idealist": ["Base", "Super Sentai"],
    "Mainstay": ["Base", "Road Warrior"],
    "Writhe": ["Base","Cosmic Inventor"],
    "Bowman": ["Base", "Golden Age"],
    "Captain Thunder": ["Base", "Rookie"],
    "Daedalus": ["Base", "Forge"],
    "Doctor Metropolis": ["Base", "One With Freedom"],
    "Johnny Rocket": ["Base", "Maximum Speed"],
    "Lady Liberty": ["Base", "The All-New"],
    "Pseudo": ["Base", "Space Infiltrator"],
    "Raven": ["Base", "Silver Age"],
    "Siren": ["Base", "Beneath the Sea"],
    "Star Knight": ["Base", "Hashik"],
    "Eldritch": ["Base"],
    "Lantern Jack": ["Base"]
}

SOLO_VILLAINS_DATA = {
    "Baron Blade": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Mad Bomber Blade": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Citizen Dawn": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Grand Warlord Voss": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Omnitron": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Cosmic Omnitron": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Ambuscade": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Spite": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Agent of Gloom Spite": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Chairman": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Akash'Bhuta": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "GloomWeaver": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Skinwalker GloomWeaver": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Matriarch": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Miss Information": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Plague Rat": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Ennead": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Apostate": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Iron Legacy": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Kismet": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Unstable Kismet": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "La Capitan": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Dreamer": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Kaargra Warfang": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Progeny": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Deadline": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Wager Master": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Infinitor": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Tormented Infinitor": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Chokepoint": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Argo": ["Normal", "Advanced"],
    "Meta-Mind": ["Normal", "Advanced"],
    "Hades": ["Normal", "Advanced"],
    "Omega": ["Normal", "Advanced"],
    "Malador": ["Normal", "Advanced"],
    "OblivAeon": ["Normal", "Advanced"]
}

TEAM_VILLAINS_LIST = [
    "Baron Blade", "Friction", "Fright Train", "Proletariat", "Ermine",
    "Ambuscade", "Biomancer", "Bugbear", "Hammer & Anvil", "Greazer", 
    "La Capitan", "Miss Information", "Plague Rat", "Sergeant Steel", "The Operative"
]
TEAM_VILLAINS_LIST.sort()

AMBIENTES = [
    "Megalopolis", "Insula Primalis", "Ruins of Atlantis", 
    "Wagner Mars Base", "Rook City", "Pike Industrial Complex",
    "Tomb of Anubis", "Realm of Discord", "Nexus of the Void", "The Block",
    "Time Cataclysm", "Silver Gulch", "Final Wasteland", "Omnitron-IV",
    "Celestial Tribunal", "Magmaria", "Freedom Tower", "Mobile Defense Platform",
    "Dok'Thorath Capital", "Enclave of the Endlings", "Court of Blood", "Madame Mittermeier's",
    "Temple of Zhu Long", "Champion Studios", "Fort Adamant", "Maerynian Refuge",
    "Mordengrad", "Farside City", "Freedom City", "Tartarus",
    "Terminus", "Sub-Terra"
]
AMBIENTES.sort()

# --- 3. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('sentinels_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  villain TEXT,
                  environment TEXT,
                  result TEXT,
                  heroes TEXT,
                  game_type TEXT DEFAULT 'SOLO')''')
    try:
        c.execute("ALTER TABLE games ADD COLUMN game_type TEXT DEFAULT 'SOLO'")
    except:
        pass
    conn.commit()
    conn.close()

# --- 4. COMPONENTES VISUAIS ---

class GridSelectionModal(ctk.CTkToplevel):
    def __init__(self, parent, title, item_list, callback, item_stats=None):
        super().__init__(parent)
        self.callback = callback
        self.title(title)
        self.geometry("1000x650")
        self.transient(parent) 
        self.grab_set() 
        self.focus_set()

        ctk.CTkLabel(self, text=f"{title.upper()}", font=FONTS["h2"]).pack(pady=15)

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        columns = 4
        for i in range(columns):
            scroll.grid_columnconfigure(i, weight=1)

        for i, item_name in enumerate(item_list):
            display_text = item_name
            if item_stats and item_name in item_stats:
                stats = item_stats[item_name]
                display_text = f"{item_name}\n🎮 {stats[0]}  |  🏆 {stats[1]:.0f}%"

            btn = ctk.CTkButton(
                scroll, 
                text=display_text, 
                font=FONTS["body_bold"],
                fg_color=COLORS["bg_card"],
                border_width=1,
                border_color=COLORS["border"],
                hover_color=COLORS["accent"],
                height=55 if item_stats else 45,
                command=lambda x=item_name: self.on_select(x)
            )
            btn.grid(row=i//columns, column=i%columns, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color=COLORS["danger"]).pack(pady=10)

    def on_select(self, item_name):
        # AQUI O BUG FIX: Destroi a janela ANTES de chamar o callback
        # Isso impede que o novo modal (se houver) fique "preso" atrás deste
        self.withdraw() # Esconde imediatamente
        self.destroy()  # Destroi
        self.callback(item_name) # Executa ação

class VillainSelector(ctk.CTkFrame):
    def __init__(self, master, index, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.selected_villain = None
        lbl = ctk.CTkLabel(self, text=f"Vilão {index}", font=("Roboto", 12, "bold"), text_color=COLORS["text_muted"], width=60)
        lbl.pack(side="left", padx=10)
        self.btn_select = ctk.CTkButton(self, text="Selecionar...", command=self.open_grid, width=200, font=FONTS["body"],
            fg_color="#333333", border_width=1, border_color="#555")
        self.btn_select.pack(side="left", fill="x", expand=True, padx=10, pady=8)

    def open_grid(self):
        GridSelectionModal(self.winfo_toplevel(), "Selecione o Vilão", TEAM_VILLAINS_LIST, self.update_selection)

    def update_selection(self, name):
        self.selected_villain = name
        self.btn_select.configure(text=name, fg_color=COLORS["accent"])
        self.configure(border_color=COLORS["accent"])

    def get_selection(self): return self.selected_villain
    def reset(self):
        self.selected_villain = None
        self.btn_select.configure(text="Selecionar...", fg_color="#333333")
        self.configure(border_color=COLORS["border"])

class HeroSelector(ctk.CTkFrame):
    def __init__(self, master, index, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.selected_hero_name = None 
        self.selected_variant = None
        self.lbl_idx = ctk.CTkLabel(self, text=f"{index}", font=("Arial", 20, "bold"), text_color=COLORS["text_muted"], width=30)
        self.lbl_idx.pack(side="left", padx=(10, 5))
        self.combo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.combo_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.btn_select_hero = ctk.CTkButton(self.combo_frame, text="Selecionar Herói...", command=self.open_hero_grid, width=200, 
            font=FONTS["body_bold"], fg_color="#333333", border_width=1, border_color="#555")
        self.btn_select_hero.pack(pady=(0, 2), fill="x")
        self.lbl_variant = ctk.CTkLabel(self.combo_frame, text="-", font=("Roboto", 12), text_color="gray")
        self.lbl_variant.pack(pady=(2, 0))

    def open_hero_grid(self):
        hero_names = sorted(list(HEROES_DATA.keys()))
        GridSelectionModal(self.winfo_toplevel(), "Selecione um Herói", hero_names, self.update_hero_selection)

    def update_hero_selection(self, hero_name):
        self.selected_hero_name = hero_name
        self.btn_select_hero.configure(text=hero_name, fg_color=COLORS["accent"])
        self.configure(border_color=COLORS["accent"])
        self.open_variant_grid()

    def open_variant_grid(self):
        if not self.selected_hero_name: return
        variants = HEROES_DATA.get(self.selected_hero_name, ["Base"])
        self.after(150, lambda: GridSelectionModal(self.winfo_toplevel(), f"Variante de {self.selected_hero_name}", variants, self.update_variant_selection))

    def update_variant_selection(self, variant):
        self.selected_variant = variant
        display_text = "Base" if variant == "Base" else variant
        self.lbl_variant.configure(text=f"Var: {display_text}", text_color=COLORS["highlight"])

    def get_selection(self):
        if not self.selected_hero_name: return None
        v = self.selected_variant if self.selected_variant else "Base"
        return self.selected_hero_name if v == "Base" else f"{self.selected_hero_name} ({v})"
    
    def reset(self):
        self.selected_hero_name = None
        self.selected_variant = None
        self.btn_select_hero.configure(text="Selecionar Herói...", fg_color="#333333")
        self.configure(border_color=COLORS["border"])
        self.lbl_variant.configure(text="-", text_color="gray")

# --- APLICAÇÃO PRINCIPAL ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Tracker v1.1.2")
        self.geometry("1280x850")
        
        # Estado
        self.selected_villain = None
        self.selected_env = None
        self.selected_analysis_hero = None
        self.selected_villain_diff = None 
        
        # Refs
        self.insight_labels = [] 
        self.insight_titles = [] 
        self.seg_stats_mode = None
        self.combo_variant_analysis = None
        self.combo_diff_filter = None
        self.dash_cards_frames = {} # Para atualizar o dashboard rows
        self.global_stat_labels = {} # Para labels de stats globais

        self.main_container = ctk.CTkTabview(self, corner_radius=15)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)
        self.main_container._segmented_button.configure(font=FONTS["body_bold"])

        self.tab_reg = self.main_container.add("  NOVA PARTIDA  ")
        self.tab_overview = self.main_container.add("  DASHBOARD  ")
        self.tab_heroes = self.main_container.add("  HERÓIS & ESTATÍSTICAS  ")
        self.tab_stats = self.main_container.add("  TABELAS GERAIS  ")

        self.setup_register_tab()
        self.setup_overview_tab()
        self.setup_stats_tab()
        self.setup_hero_tab_structure()
        
        self.after(500, self.refresh_all_data) 

    # --- ABA 1: REGISTRO (Layout Corrigido) ---
    def setup_register_tab(self):
        self.tab_reg.grid_columnconfigure(0, weight=1, uniform="g1") 
        self.tab_reg.grid_columnconfigure(1, weight=1, uniform="g1") 
        self.tab_reg.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.tab_reg, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 1. Modo
        self.card_mode = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_mode.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_mode, text="MODO DE JOGO", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(12, 5))
        self.seg_gamemode = ctk.CTkSegmentedButton(self.card_mode, values=["Solo", "Time de Vilões"], 
                                                   command=self.toggle_villain_mode, font=FONTS["body_bold"], height=32)
        self.seg_gamemode.set("Solo")
        self.seg_gamemode.pack(pady=(0, 15), padx=20, fill="x")

        # 2. Setup (CONTAINER PRINCIPAL)
        self.card_setup = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_setup.pack(fill="x", pady=(0, 15), ipady=10)
        
        # Container Vilão (Fixo)
        self.container_villain = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_villain.pack(fill="x", padx=0, pady=0)

        # Frame Solo
        self.frame_solo = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_solo, text="VILÃO", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_villain = ctk.CTkButton(self.frame_solo, text="Selecionar Vilão...", command=self.open_villain_grid, 
                                                width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_villain.pack(padx=20, pady=(5, 5), fill="x")
        self.lbl_villain_diff = ctk.CTkLabel(self.frame_solo, text="Modo: Normal", font=FONTS["body"], text_color="gray")
        self.lbl_villain_diff.pack(padx=20, pady=(0, 10))
        
        # Frame Team
        self.frame_team = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_team, text="TIME DE VILÕES (3-5)", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.team_selectors = []
        for i in range(5):
            sel = VillainSelector(self.frame_team, index=i+1)
            sel.pack(padx=20, pady=4, fill="x")
            self.team_selectors.append(sel)
        
        # Inicia mostrando Solo
        self.frame_solo.pack(fill="x")

        # Separador (Fixo)
        ctk.CTkFrame(self.card_setup, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=20, pady=15)

        # Container Ambiente (Fixo - Não muda de lugar)
        self.container_env = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_env.pack(fill="x")
        ctk.CTkLabel(self.container_env, text="AMBIENTE", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_env = ctk.CTkButton(self.container_env, text="Selecionar Ambiente...", command=self.open_env_grid, 
                                            width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_env.pack(padx=20, pady=5, fill="x")

        # 3. Resultado
        self.card_result = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_result.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_result, text="RESULTADO DA BATALHA", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(12, 5))
        self.seg_result = ctk.CTkSegmentedButton(self.card_result, values=["Vitória", "Derrota"], selected_color=COLORS["success"], selected_hover_color="#209662", font=FONTS["body_bold"], height=40)
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=(0, 20), padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.left_panel, text="SALVAR DADOS DA PARTIDA", command=self.save_game, fg_color=COLORS["accent"], hover_color="#144870", height=55, font=("Roboto", 15, "bold"), corner_radius=12)
        self.btn_save.pack(side="bottom", fill="x", pady=10)

        # Right Panel
        self.right_panel = ctk.CTkFrame(self.tab_reg, corner_radius=12, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_panel, text="EQUIPE DE HERÓIS", font=FONTS["h2"]).pack(pady=(0, 15), anchor="w")
        self.hero_selectors = []
        for i in range(5):
            sel = HeroSelector(self.right_panel, index=i+1)
            sel.pack(padx=0, pady=6, fill="x")
            self.hero_selectors.append(sel)

    # --- ABA 2: DASHBOARD (Alinhado com Rows) ---
    def setup_overview_tab(self):
        self.frame_total = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.frame_total.pack(fill="x", pady=20, padx=20)
        ctk.CTkButton(self.frame_total, text="⟳ Atualizar", command=self.refresh_all_data, height=28, width=80, fg_color="#333", font=FONTS["body"]).pack(side="right", anchor="n")
        ctk.CTkLabel(self.frame_total, text="TOTAL DE PARTIDAS", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack()
        self.lbl_total_games = ctk.CTkLabel(self.frame_total, text="0", font=FONTS["h1"], text_color=COLORS["success"])
        self.lbl_total_games.pack()

        self.grid_overview = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.grid_overview.pack(fill="both", expand=True, padx=10, pady=10)
        for i in range(3): self.grid_overview.grid_columnconfigure(i, weight=1)
        for i in range(2): self.grid_overview.grid_rowconfigure(i, weight=1)

        self.card_hero_played = self.create_stat_card(0, 0, "HERÓIS MAIS JOGADOS", "hero_played")
        self.card_hero_best = self.create_stat_card(0, 1, "MELHORES HERÓIS (WINRATE)", "hero_best")
        self.card_hero_worst = self.create_stat_card(0, 2, "PIORES HERÓIS (WINRATE)", "hero_worst")
        self.card_villain_played = self.create_stat_card(1, 0, "VILÕES MAIS COMUNS", "villain_played")
        self.card_villain_hardest = self.create_stat_card(1, 1, "VILÕES MAIS DIFÍCEIS", "villain_hard")
        self.card_env_played = self.create_stat_card(1, 2, "AMBIENTES MAIS JOGADOS", "env_played")

    def create_stat_card(self, row, col, title, key_id):
        frame = ctk.CTkFrame(self.grid_overview, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(frame, text=title, font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(15, 5))
        ctk.CTkFrame(frame, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=20, pady=(0, 10))
        
        # Container Scrollável para as linhas
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Armazena referência para atualizar depois
        self.dash_cards_frames[key_id] = content_frame
        return frame

    # --- ABA 3: HERÓIS (ESTRUTURA) ---
    def setup_hero_tab_structure(self):
        self.tab_hero_internal = ctk.CTkTabview(self.tab_heroes)
        self.tab_hero_internal.pack(fill="both", expand=True, padx=10, pady=10)
        self.subtab_analysis = self.tab_hero_internal.add(" Análise Específica ")
        self.subtab_summary = self.tab_hero_internal.add(" Resumo do Herói (Base+Vars) ")
        self.subtab_global = self.tab_hero_internal.add(" Estatísticas Globais ")

        self.setup_subtab_analysis()
        self.setup_subtab_summary()
        self.setup_subtab_global()

    # >>> SUB-ABA 1: ANÁLISE ESPECÍFICA
    def setup_subtab_analysis(self):
        self.subtab_analysis.grid_columnconfigure(0, weight=1)
        self.subtab_analysis.grid_columnconfigure(1, weight=3)
        self.subtab_analysis.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.subtab_analysis, corner_radius=12, fg_color=COLORS["bg_card"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(left_frame, text="SELEÇÃO", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(20, 10))
        self.btn_select_analysis_hero = ctk.CTkButton(left_frame, text="Selecionar Herói...", command=self.open_analysis_hero_grid, 
                                                      width=220, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_analysis_hero.pack(pady=5)
        self.combo_variant_analysis = ctk.CTkComboBox(left_frame, values=["Base"], command=lambda x: self.display_hero_insights(), width=220, font=FONTS["body"])
        self.combo_variant_analysis.pack(pady=(5, 20))
        self.combo_variant_analysis.configure(state="disabled") 
        ctk.CTkFrame(left_frame, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(left_frame, text="FILTRAR DIFICULDADE", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(10, 5))
        self.combo_diff_filter = ctk.CTkComboBox(left_frame, values=["Todos", "Normal", "Advanced", "Challenge", "Ultimate"],
                                                 command=lambda x: self.display_hero_insights(), width=220, font=FONTS["body"])
        self.combo_diff_filter.set("Todos")
        self.combo_diff_filter.pack(pady=5)

        right_frame = ctk.CTkFrame(self.subtab_analysis, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.stats_header_frame = ctk.CTkFrame(right_frame, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.stats_header_frame.pack(fill="x", pady=(0, 15))
        self.lbl_hero_wr = ctk.CTkLabel(self.stats_header_frame, text="WR: --%", font=FONTS["h1"], text_color=COLORS["success"])
        self.lbl_hero_wr.pack(side="left", padx=40, pady=25)
        self.lbl_hero_games = ctk.CTkLabel(self.stats_header_frame, text="0 Partidas", font=FONTS["h2"], text_color=COLORS["text_muted"])
        self.lbl_hero_games.pack(side="right", padx=40, pady=25)

        self.insights_scroll_frame = ctk.CTkScrollableFrame(right_frame, corner_radius=12, fg_color="transparent", label_text="ANÁLISE ESTRATÉGICA (VARIANTE)", label_font=FONTS["h3"])
        self.insights_scroll_frame.pack(fill="both", expand=True)
        self.insight_titles = [] 
        self.insight_labels = [] 
        for i in range(5):
            card = ctk.CTkFrame(self.insights_scroll_frame, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=8, padx=5)
            lbl_t = ctk.CTkLabel(card, text="TÍTULO", justify="center", font=FONTS["card_label"], text_color=COLORS["text_muted"])
            lbl_t.pack(fill="x", padx=10, pady=(15, 5))
            self.insight_titles.append(lbl_t)
            ctk.CTkFrame(card, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=50)
            lbl_c = ctk.CTkLabel(card, text="...", justify="center", font=FONTS["card_value"], text_color=COLORS["highlight"])
            lbl_c.pack(fill="x", padx=10, pady=(10, 20))
            self.insight_labels.append(lbl_c)

    # >>> SUB-ABA 2: RESUMO DO HERÓI (AGREGADO)
    def setup_subtab_summary(self):
        # Header + Botão de troca
        self.frame_agg_header = ctk.CTkFrame(self.subtab_summary, corner_radius=12, fg_color=COLORS["bg_card"])
        self.frame_agg_header.pack(fill="x", padx=20, pady=20)
        
        top_bar = ctk.CTkFrame(self.frame_agg_header, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 0))
        
        self.lbl_agg_name = ctk.CTkLabel(top_bar, text="SELECIONE UM HERÓI", font=FONTS["h1"])
        self.lbl_agg_name.pack(side="left")
        
        self.btn_agg_change = ctk.CTkButton(top_bar, text="Trocar Herói", command=self.open_analysis_hero_grid,
                                            width=120, fg_color="#333", border_width=1, border_color="#555")
        self.btn_agg_change.pack(side="right")

        self.lbl_agg_stats = ctk.CTkLabel(self.frame_agg_header, text="-- Jogos | --% WR Total", font=FONTS["h2"], text_color="gray")
        self.lbl_agg_stats.pack(pady=(10, 20))

        self.scroll_agg_vars = ctk.CTkScrollableFrame(self.subtab_summary, label_text="DESEMPENHO POR VARIANTE", label_font=FONTS["h3"])
        self.scroll_agg_vars.pack(fill="both", expand=True, padx=20, pady=10)
        self.lbl_agg_content = ctk.CTkLabel(self.scroll_agg_vars, text="...", font=FONTS["dashboard_row"], justify="left")
        self.lbl_agg_content.pack(anchor="w", padx=20, pady=10)

    # >>> SUB-ABA 3: ESTATÍSTICAS GLOBAIS (ESTILIZADA)
    def setup_subtab_global(self):
        self.frame_global_grid = ctk.CTkFrame(self.subtab_global, fg_color="transparent")
        self.frame_global_grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.frame_global_grid.grid_columnconfigure(0, weight=1)
        self.frame_global_grid.grid_columnconfigure(1, weight=1)
        self.frame_global_grid.grid_columnconfigure(2, weight=1)
        
        # Win Rate Card (Grande)
        card_wr = ctk.CTkFrame(self.frame_global_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_wr.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(card_wr, text="WIN RATE TOTAL", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(15, 5))
        self.global_stat_labels["wr"] = ctk.CTkLabel(card_wr, text="--%", font=FONTS["h1"], text_color=COLORS["success"])
        self.global_stat_labels["wr"].pack(pady=(0, 15))

        # Stats Básicos
        self.create_global_card(1, 0, "TOTAL DE PARTIDAS", "total", "white")
        self.create_global_card(1, 1, "VITÓRIAS", "wins", COLORS["success"])
        self.create_global_card(1, 2, "DERROTAS", "losses", COLORS["danger"])

        # Dificuldades
        ctk.CTkLabel(self.frame_global_grid, text="PARTIDAS POR DIFICULDADE", font=FONTS["h3"]).grid(row=2, column=0, columnspan=3, pady=(20, 10))
        self.create_global_card(3, 0, "NORMAL", "diff_normal", COLORS["highlight"])
        self.create_global_card(3, 1, "ADVANCED", "diff_advanced", COLORS["warning"])
        self.create_global_card(3, 2, "CHALLENGE/ULTIMATE", "diff_hard", COLORS["danger"])

    def create_global_card(self, r, c, title, key, color):
        f = ctk.CTkFrame(self.frame_global_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        f.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(f, text=title, font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(15, 5))
        lbl = ctk.CTkLabel(f, text="0", font=FONTS["stat_big"], text_color=color)
        lbl.pack(pady=(0, 15))
        self.global_stat_labels[key] = lbl

    # --- ABA 4: DETALHES ---
    def setup_stats_tab(self):
        top_bar = ctk.CTkFrame(self.tab_stats, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=15, pady=15)
        self.seg_stats_mode = ctk.CTkSegmentedButton(top_bar, values=["Stats Solo", "Stats Time"], 
                                                     command=lambda x: self.calculate_details(), width=300, font=FONTS["body_bold"])
        self.seg_stats_mode.set("Stats Solo")
        self.seg_stats_mode.pack(side="left")

        self.stats_grid = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.stats_grid.pack(fill="both", expand=True, padx=5, pady=5)
        for i in range(4): self.stats_grid.grid_columnconfigure(i, weight=1); self.stats_grid.grid_rowconfigure(0, weight=1)

        def create_col(title, col_idx):
            frame = ctk.CTkFrame(self.stats_grid, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
            frame.grid(row=0, column=col_idx, sticky="nsew", padx=5)
            ctk.CTkLabel(frame, height=40, text=title, font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=10)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=5, pady=5)
            lbl = ctk.CTkLabel(scroll, text="...", justify="left", font=FONTS["mono"])
            lbl.pack(anchor="w")
            return lbl

        self.lbl_stats_v = create_col("VILÕES", 0)
        self.lbl_stats_e = create_col("AMBIENTES", 1)
        self.lbl_stats_s = create_col("TAMANHO DO TIME", 2)
        self.lbl_stats_h = create_col("HERÓIS", 3)

    # --- LÓGICA ---
    def toggle_villain_mode(self, mode):
        self.frame_solo.pack_forget(); self.frame_team.pack_forget()
        if mode == "Solo": self.frame_solo.pack(fill="x")
        else: self.frame_team.pack(fill="x")

    def open_villain_grid(self):
        villains = sorted(list(SOLO_VILLAINS_DATA.keys()))
        GridSelectionModal(self, "Selecionar Vilão", villains, self.on_villain_selected)

    def on_villain_selected(self, villain):
        self.selected_villain = villain
        self.btn_select_villain.configure(text=villain, fg_color=COLORS["accent"])
        self.open_diff_grid(villain)

    def open_diff_grid(self, villain):
        modes = SOLO_VILLAINS_DATA.get(villain, ["Normal"])
        # Delay corrigido para garantir que o primeiro modal feche completamente
        self.after(200, lambda: GridSelectionModal(self, f"Dificuldade: {villain}", modes, self.on_diff_selected))

    def on_diff_selected(self, diff):
        self.selected_villain_diff = diff
        self.lbl_villain_diff.configure(text=f"Modo: {diff}", text_color=COLORS["highlight"])
        self.combo_solo_mode.set(diff)

    def open_env_grid(self):
        GridSelectionModal(self, "Selecionar Ambiente", AMBIENTES, self.on_env_selected)

    def on_env_selected(self, env):
        self.selected_env = env
        self.btn_select_env.configure(text=env, fg_color=COLORS["accent"])

    def open_analysis_hero_grid(self):
        hero_stats_map = self.get_all_heroes_stats_map()
        sorted_heroes = sorted(list(HEROES_DATA.keys()), 
                               key=lambda x: (hero_stats_map.get(x, (0,0))[0], hero_stats_map.get(x, (0,0))[1]), 
                               reverse=True)
        GridSelectionModal(self, "Analisar Herói", sorted_heroes, self.on_analysis_hero_selected, item_stats=hero_stats_map)

    def on_analysis_hero_selected(self, hero_name):
        self.selected_analysis_hero = hero_name
        self.btn_select_analysis_hero.configure(text=hero_name, fg_color=COLORS["accent"])
        self.update_hero_variants_analysis(hero_name)
        self.calculate_aggregate_hero_stats(hero_name)

    def update_hero_variants_analysis(self, hero_name):
        variants = HEROES_DATA.get(hero_name, ["Base"])
        self.combo_variant_analysis.configure(values=variants, state="normal")
        self.combo_variant_analysis.set("Base")
        self.display_hero_insights()

    def get_all_heroes_stats_map(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT heroes, result FROM games")
        rows = c.fetchall()
        conn.close()
        stats = defaultdict(lambda: [0, 0])
        for h_str, res in rows:
            win = 1 if res == "Vitória" else 0
            for h_full in h_str.split(","):
                h_base = h_full.split(" (")[0]
                stats[h_base][0] += win; stats[h_base][1] += 1
        return {h: (v[1], (v[0]/v[1])*100 if v[1]>0 else 0) for h, v in stats.items()}

    def display_hero_insights(self):
        hero_base = self.selected_analysis_hero
        variant = self.combo_variant_analysis.get()
        diff_filter = self.combo_diff_filter.get() 
        if not hero_base or not self.insight_labels: return
        hero_target_str = hero_base if variant == "Base" else f"{hero_base} ({variant})"
        stats_data = self.calculate_hero_insights(hero_target_str, diff_filter, exact_match=True)
        total_games, win_rate, *insights = stats_data
        self.lbl_hero_games.configure(text=f"{total_games} PARTIDAS")
        self.lbl_hero_wr.configure(text=f"{win_rate:.1f}%", text_color=COLORS["success"] if win_rate >= 50 else COLORS["danger"])
        titles = ["VILÃO MAIS FÁCIL", "VILÃO MAIS DIFÍCIL", "PARCEIRO FREQUENTE", "AMBIENTE FREQUENTE", "CONSISTÊNCIA (DP)"]
        for i, (title, content) in enumerate(zip(titles, insights)):
            self.insight_titles[i].configure(text=title)
            self.insight_labels[i].configure(text=content)

    def calculate_hero_insights(self, target_hero_str, difficulty="Todos", exact_match=False):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes, game_type FROM games")
        rows = c.fetchall()
        conn.close()
        filtered_rows = []
        for r in rows:
            v_str, env, res, h_str, g_type = r
            h_list = h_str.split(",")
            if exact_match:
                if target_hero_str not in h_list: continue
            else:
                if not any(target_hero_str in h for h in h_list): continue
            if difficulty != "Todos":
                if g_type == "SOLO":
                    is_normal = not any(x in v_str for x in ["(Advanced)", "(Challenge)", "(Ultimate)"])
                    if difficulty == "Normal" and not is_normal: continue
                    if difficulty != "Normal" and f"({difficulty})" not in v_str: continue
            filtered_rows.append(r)
        
        total_games = len(filtered_rows)
        if total_games == 0: return [0, 0.0, "Sem dados.", "Sem dados.", "-", "-", "-"]
        total_wins = sum(1 for r in filtered_rows if r[2] == "Vitória")
        win_rate_perc = (total_wins / total_games) * 100
        v_stats, t_stats, e_stats, wins_list = defaultdict(lambda: [0, 0]), defaultdict(int), defaultdict(int), []
        for v_str, env, res, h_str, g_type in filtered_rows:
            win = 1 if res == "Vitória" else 0
            wins_list.append(win); e_stats[env] += 1
            v_list = v_str.split(",") if g_type == "TEAM" else [v_str]
            for v in v_list: v_stats[v][0] += win; v_stats[v][1] += 1
            for h in h_str.split(","):
                if h != target_hero_str: t_stats[h] += 1
        valid_vs = [x for x in v_stats.items() if x[1][1] >= 1]
        if valid_vs:
            sorted_vs = sorted(valid_vs, key=lambda x: (x[1][0]/x[1][1], x[1][1]), reverse=True)
            i1 = f"{sorted_vs[0][0]} ({sorted_vs[0][1][0]/sorted_vs[0][1][1]*100:.0f}%)"
            i2 = f"{sorted_vs[-1][0]} ({sorted_vs[-1][1][0]/sorted_vs[-1][1][1]*100:.0f}%)"
        else: i1 = i2 = "Jogue mais."
        i3 = max(t_stats.items(), key=lambda x: x[1])[0] if t_stats else "-"
        i4 = max(e_stats.items(), key=lambda x: x[1])[0] if e_stats else "-"
        if len(wins_list) >= 2:
            mean = sum(wins_list)/len(wins_list)
            std_dev = math.sqrt(sum([(x-mean)**2 for x in wins_list])/len(wins_list))
            i5 = f"DP: {std_dev:.2f}"
        else: i5 = "Min 2 jogos"
        return [total_games, win_rate_perc, i1, i2, i3, i4, i5]

    def calculate_aggregate_hero_stats(self, base_name):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT result, heroes FROM games")
        rows = c.fetchall()
        conn.close()
        total_g = 0; total_w = 0; var_stats = defaultdict(lambda: [0, 0])
        for res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            h_list = h_str.split(",")
            hero_in_game = False
            for h in h_list:
                if h.split(" (")[0] == base_name:
                    hero_in_game = True; var_stats[h][0] += win; var_stats[h][1] += 1
            if hero_in_game: total_w += win; total_g += 1
        wr = (total_w/total_g)*100 if total_g > 0 else 0
        self.lbl_agg_name.configure(text=base_name.upper())
        self.lbl_agg_stats.configure(text=f"{total_g} JOGOS TOTAIS  |  {wr:.1f}% WR GERAL")
        txt = ""
        for v_name, stats in sorted(var_stats.items(), key=lambda x: x[1][1], reverse=True):
            v_wr = (stats[0]/stats[1])*100
            txt += f"{v_wr:>5.1f}% WR  |  {stats[1]:>3} Jogos  |  {v_name}\n" + "─"*60 + "\n"
        if not txt: txt = "Nenhuma partida registrada."
        self.lbl_agg_content.configure(text=txt)

    def calculate_global_stats(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT result, game_type, villain FROM games")
        rows = c.fetchall()
        conn.close()
        total = len(rows)
        wins = sum(1 for r in rows if r[0] == "Vitória")
        wr = (wins/total)*100 if total > 0 else 0
        
        diff_counts = {"Normal": 0, "Advanced": 0, "Hard": 0} # Hard = Challenge/Ultimate
        for r in rows:
            v_str = r[2]
            if "(Advanced)" in v_str: diff_counts["Advanced"] += 1
            elif "(Challenge)" in v_str or "(Ultimate)" in v_str: diff_counts["Hard"] += 1
            else: diff_counts["Normal"] += 1

        self.global_stat_labels["total"].configure(text=str(total))
        self.global_stat_labels["wins"].configure(text=str(wins))
        self.global_stat_labels["losses"].configure(text=str(total - wins))
        self.global_stat_labels["wr"].configure(text=f"{wr:.1f}%", text_color=COLORS["success"] if wr >= 50 else COLORS["danger"])
        self.global_stat_labels["diff_normal"].configure(text=str(diff_counts["Normal"]))
        self.global_stat_labels["diff_advanced"].configure(text=str(diff_counts["Advanced"]))
        self.global_stat_labels["diff_hard"].configure(text=str(diff_counts["Hard"]))

    def save_game(self):
        mode = self.seg_gamemode.get()
        g_type = "SOLO" if mode == "Solo" else "TEAM"
        env = self.selected_env
        if not env: return messagebox.showwarning("Atenção", "Selecione um Ambiente.")
        res = self.seg_result.get()
        if g_type == "SOLO":
            v = self.selected_villain
            if not v: return messagebox.showwarning("Atenção", "Selecione um Vilão.")
            m = self.selected_villain_diff if self.selected_villain_diff else "Normal"
            v_str = v if m == "Normal" else f"{v} ({m})"
        else:
            lst = []
            for sel in self.team_selectors:
                val = sel.get_selection()
                if val: lst.append(val)
            if len(lst) < 3: return messagebox.showwarning("Atenção", "Selecione 3+ vilões.")
            if len(lst) != len(set(lst)): return messagebox.showwarning("Atenção", "Vilões duplicados.")
            v_str = ",".join(lst)
        h_list = []
        for s in self.hero_selectors:
            x = s.get_selection()
            if x: h_list.append(x)
        if len(h_list) < 3: return messagebox.showwarning("Atenção", "Selecione 3+ heróis.")
        if len(set([h.split(" (")[0] for h in h_list])) != len(h_list): return messagebox.showerror("Regra do Multiverso", "Herói duplicado.")
        try:
            conn = sqlite3.connect('sentinels_history.db')
            c = conn.cursor()
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO games (date, villain, environment, result, heroes, game_type) VALUES (?, ?, ?, ?, ?, ?)", (dt, v_str, env, res, ",".join(h_list), g_type))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Partida registrada!")
            for s in self.hero_selectors: s.reset()
            self.selected_env = None; self.btn_select_env.configure(text="Selecionar Ambiente...", fg_color="#333")
            self.selected_villain = None; self.btn_select_villain.configure(text="Selecionar Vilão...", fg_color="#333")
            self.selected_villain_diff = None; self.lbl_villain_diff.configure(text="Modo: Normal", text_color="gray")
            for s in self.team_selectors: s.reset()
            self.refresh_all_data()
        except Exception as e: messagebox.showerror("Erro", str(e))

    def refresh_all_data(self):
        self.calculate_overview()
        self.calculate_details()
        self.display_hero_insights()
        self.calculate_global_stats()
        if self.selected_analysis_hero: self.calculate_aggregate_hero_stats(self.selected_analysis_hero)

    def calculate_overview(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        try:
            c.execute("SELECT villain, environment, result, heroes, game_type FROM games")
            rows = c.fetchall()
        except: rows = []
        conn.close()
        self.lbl_total_games.configure(text=str(len(rows)))
        if not rows: return
        h_stats, v_stats, e_stats = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        for v_s, e, r, h_s, g_t in rows:
            w = 1 if r == "Vitória" else 0
            for h in h_s.split(","): h_stats[h][0]+=w; h_stats[h][1]+=1
            e_stats[e][0]+=w; e_stats[e][1]+=1
            v_lst = v_s.split(",") if g_t == "TEAM" else [v_s]
            for v in v_lst: v_stats[v][0]+=w; v_stats[v][1]+=1

        def update_card(card_id, data_list, is_wr=False):
            frame = self.dash_cards_frames[card_id]
            for widget in frame.winfo_children(): widget.destroy()
            for name, stats in data_list:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                # NOME NA ESQUERDA
                ctk.CTkLabel(row, text=name, font=FONTS["dashboard_row"], width=180, anchor="w").pack(side="left")
                # VALOR NA DIREITA (FIXADO)
                val_text = f"{stats[0]/stats[1]*100:.0f}%" if is_wr else f"{stats[1]}"
                color = COLORS["highlight"] if is_wr else "white"
                ctk.CTkLabel(row, text=val_text, font=FONTS["body_bold"], text_color=color, width=50, anchor="e").pack(side="right")

        top_h = sorted(h_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        update_card("hero_played", top_h)
        
        valid_h = [x for x in h_stats.items() if x[1][1]>=3]
        update_card("hero_best", sorted(valid_h, key=lambda x: (x[1][0]/x[1][1], x[1][1]), reverse=True)[:5], True)
        update_card("hero_worst", sorted(valid_h, key=lambda x: (x[1][0]/x[1][1], x[1][1]))[:5], True)

        top_v = sorted(v_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        update_card("villain_played", top_v)

        valid_v = [x for x in v_stats.items() if x[1][1]>=3]
        update_card("villain_hard", sorted(valid_v, key=lambda x: (x[1][0]/x[1][1], x[1][1]))[:5], True)

        top_e = sorted(e_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        update_card("env_played", top_e)

    def calculate_details(self):
        mode = "SOLO" if self.seg_stats_mode and self.seg_stats_mode.get() == "Stats Solo" else "TEAM"
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        try:
            c.execute("SELECT villain, environment, result, heroes FROM games WHERE game_type=?", (mode,))
            rows = c.fetchall()
        except: rows = []
        conn.close()
        if not rows: 
            for l in [self.lbl_stats_v, self.lbl_stats_e, self.lbl_stats_s, self.lbl_stats_h]: l.configure(text="-")
            return
        sv, se, sh, ss = defaultdict(lambda:[0,0]), defaultdict(lambda:[0,0]), defaultdict(lambda:[0,0]), defaultdict(lambda:[0,0])
        for v, e, r, h in rows:
            w = 1 if r == "Vitória" else 0
            se[e][0]+=w; se[e][1]+=1
            hl = h.split(",")
            for x in hl: sh[x][0]+=w; sh[x][1]+=1
            ss[len(hl)][0]+=w; ss[len(hl)][1]+=1
            vl = v.split(",") if mode=="TEAM" else [v]
            for x in vl: sv[x][0]+=w; sv[x][1]+=1
        def f(d, sk=False):
            l = sorted(d.items(), key=lambda x: x[0] if sk else x[1][1], reverse=not sk)
            t = ""
            for k, val in l: t+=f"{val[0]/val[1]*100:>6.1f}%  ({val[0]:>2}/{val[1]:<2})  {k}\n"
            return t
        self.lbl_stats_v.configure(text=f(sv)); self.lbl_stats_e.configure(text=f(se))
        self.lbl_stats_h.configure(text=f(sh)); self.lbl_stats_s.configure(text=f(ss, True))

if __name__ == "__main__":
    try:
        init_db()
        app = TrackerApp()
        app.mainloop()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw()
        messagebox.showerror("Erro Fatal", str(e))