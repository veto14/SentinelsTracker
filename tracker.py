import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict
import math

# --- 1. SISTEMA DE DESIGN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_card": "#2b2b2b",       "border": "#3a3a3a",
    "accent": "#1f6aa5",        "accent_hover": "#144870",
    "success": "#2CC985",       "danger": "#d63031",
    "warning": "#f39c12",       "highlight": "#4aa3df",
    "text_main": "white",       "text_muted": "gray70",
    "separator": "#444444",
    # Achievements
    "rank_bronze": "#cd7f32",   "rank_silver": "#c0c0c0",
    "rank_gold": "#ffd700",     "rank_platinum": "#e5e4e2",
    "rank_diamond": "#b9f2ff",  "rank_sentinel": "#a020f0",
    # Mastery
    "mastery_text": "#00e676",  # Verde XP
    # Dificuldade
    "diff_challenge": "#e67e22", "diff_ultimate": "#8e44ad"
}

FONTS = {
    "h1": ("Roboto", 36, "bold"),       "h2": ("Roboto", 22, "bold"),
    "h3": ("Roboto Medium", 16),        "body": ("Roboto", 13),
    "body_bold": ("Roboto", 13, "bold"),"mono": ("Consolas", 13),
    "card_label": ("Roboto", 11, "bold"), "card_value": ("Roboto", 18, "bold"),
    "stat_big": ("Roboto", 28, "bold"), "dashboard_row": ("Roboto Medium", 13)
}

# --- 2. DADOS DO JOGO ---
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

# --- DADOS DE DIFICULDADE (XP) ---
SOLO_VILLAIN_DIFF = {
    "Baron Blade": 1, "Mad Bomber Blade": 2, "Citizen Dawn": 4, "Grand Warlord Voss": 3,
    "Omnitron": 1, "Cosmic Omnitron": 3, "Ambuscade": 1, "Spite": 2, "Agent of Gloom Spite": 3,
    "Chairman": 4, "Akash'Bhuta": 2, "GloomWeaver": 1, "Skinwalker GloomWeaver": 3,
    "Matriarch": 3, "Miss Information": 4, "Plague Rat": 2, "Ennead": 3, "Apostate": 2,
    "Iron Legacy": 4, "Kismet": 1, "Unstable Kismet": 2, "La Capitan": 2, "Dreamer": 3,
    "Kaargra Warfang": 4, "Progeny": 4, "Deadline": 2, "Wager Master": 3, "Infinitor": 3,
    "Tormented Infinitor": 1, "Chokepoint": 1, "Argo": 2, "Meta-Mind": 2, "Hades": 2,
    "Omega": 2, "Malador": 2, "OblivAeon": 20
}

TEAM_VILLAIN_DIFF = {
    "Baron Blade": 3, "Friction": 3, "Fright Train": 2, "Proletariat": 2, "Ermine": 2,
    "Ambuscade": 4, "Biomancer": 3, "Bugbear": 3, "Hammer & Anvil": 3, "Greazer": 2,
    "La Capitan": 1, "Miss Information": 2, "Plague Rat": 3, "Sergeant Steel": 3, "The Operative": 1
}

ENV_DIFF = {
    "Megalopolis": 2, "Insula Primalis": 3, "Ruins of Atlantis": 4, "Wagner Mars Base": 2,
    "Rook City": 5, "Pike Industrial Complex": 3, "Tomb of Anubis": 3, "Realm of Discord": 2,
    "Nexus of the Void": 3, "The Block": 1, "Time Cataclysm": 2, "Silver Gulch": 3,
    "Final Wasteland": 1, "Omnitron-IV": 4, "Celestial Tribunal": 2, "Magmaria": 2,
    "Freedom Tower": 1, "Mobile Defense Platform": 1, "Dok'Thorath Capital": 3,
    "Enclave of the Endlings": 2, "Court of Blood": 3, "Madame Mittermeier's": 3,
    "Temple of Zhu Long": 1, "Champion Studios": 2, "Fort Adamant": 2, "Maerynian Refuge": 3,
    "Mordengrad": 4, "Farside City": 2, "Freedom City": 2, "Tartarus": 2,
    "Terminus": 2, "Sub-Terra": 2
}

# Listas usadas nos menus
SOLO_VILLAINS_DATA = {k: ["Normal", "Advanced", "Challenge", "Ultimate"] for k in SOLO_VILLAIN_DIFF.keys()}
SOLO_VILLAINS_DATA["OblivAeon"] = ["Normal", "Advanced"]
TEAM_VILLAINS_LIST = sorted(list(TEAM_VILLAIN_DIFF.keys()))
AMBIENTES = sorted(list(ENV_DIFF.keys()))


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
    def __init__(self, parent, title, item_list, callback, item_stats=None, style_map=None, mastery_map=None):
        super().__init__(parent)
        self.callback = callback
        self.title(title)
        self.geometry("1100x700")
        self.transient(parent) 
        self.grab_set() 
        self.focus_set()

        ctk.CTkLabel(self, text=f"{title.upper()}", font=FONTS["h2"]).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)
        columns = 4
        for i in range(columns): scroll.grid_columnconfigure(i, weight=1)

        for i, item_name in enumerate(item_list):
            display_text = item_name
            btn_fg = COLORS["bg_card"]
            btn_border = COLORS["border"]
            btn_text_color = "white"
            icon = ""
            border_width = 1

            # Stats line
            stats_line = ""
            if item_stats and item_name in item_stats:
                stats = item_stats[item_name]
                stats_line = f"\n🎮 {stats[0]}  |  🏆 {stats[1]:.0f}%"

            # Mastery Line
            mastery_line = ""
            if mastery_map and item_name in mastery_map:
                m_level, _ = mastery_map[item_name]
                mastery_line = f"  (MR {m_level})"

            # Achievements Style
            if style_map and item_name in style_map:
                style = style_map[item_name]
                if style.get('text_color'): btn_text_color = style['text_color']
                if style.get('border_color'): btn_border = style['border_color']; border_width = 2
                if style.get('icon'): icon = style['icon']

            final_text = f"{item_name}{mastery_line} {icon}{stats_line}"

            btn = ctk.CTkButton(
                scroll, text=final_text, font=FONTS["body_bold"], fg_color=btn_fg,
                border_width=border_width, border_color=btn_border, text_color=btn_text_color,
                hover_color=COLORS["accent"], height=60,
                command=lambda x=item_name: self.on_select(x)
            )
            btn.grid(row=i//columns, column=i%columns, padx=5, pady=5, sticky="ew")
            
            # Mini Barra de XP no botão
            if mastery_map and item_name in mastery_map:
                _, xp = mastery_map[item_name]
                prog = (xp % 1000) / 1000
                xp_bar = ctk.CTkProgressBar(btn, height=3, width=50, progress_color=COLORS["mastery_text"])
                xp_bar.set(prog)
                xp_bar.place(relx=0.5, rely=0.9, anchor="center", relwidth=0.8)

        ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color=COLORS["danger"]).pack(pady=10)

    def on_select(self, item_name):
        self.withdraw()
        self.destroy() 
        self.callback(item_name) 

class VillainSelector(ctk.CTkFrame):
    def __init__(self, master, index, controller=None, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.controller = controller
        self.selected_villain = None
        lbl = ctk.CTkLabel(self, text=f"Vilão {index}", font=("Roboto", 12, "bold"), text_color=COLORS["text_muted"], width=60)
        lbl.pack(side="left", padx=10)
        self.btn_select = ctk.CTkButton(self, text="Selecionar...", command=self.open_grid, width=200, font=FONTS["body"],
            fg_color="#333333", border_width=1, border_color="#555")
        self.btn_select.pack(side="left", fill="x", expand=True, padx=10, pady=8)

    def open_grid(self):
        # Usa self.controller ou self.winfo_toplevel() se controller for None
        parent = self.controller if self.controller else self.winfo_toplevel()
        GridSelectionModal(parent, "Selecione o Vilão", TEAM_VILLAINS_LIST, self.update_selection)

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
    def __init__(self, master, index, controller=None, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.controller = controller # Referência ao app principal
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
        # Usa o controller passado no init para evitar erro de _tkinter.tkapp
        app = self.controller if self.controller else self.winfo_toplevel()
        
        style_map = None
        mastery_map = None
        # Verifica se o app tem os métodos antes de chamar
        if hasattr(app, "get_hero_achievement_styles"):
            style_map = app.get_hero_achievement_styles()
        if hasattr(app, "get_hero_mastery_map"):
            mastery_map = app.get_hero_mastery_map()
            
        hero_names = sorted(list(HEROES_DATA.keys()))
        GridSelectionModal(app, "Selecione um Herói", hero_names, self.update_hero_selection, style_map=style_map, mastery_map=mastery_map)

    def update_hero_selection(self, hero_name):
        self.selected_hero_name = hero_name
        app = self.controller if self.controller else self.winfo_toplevel()
        text_color = "white"
        
        if hasattr(app, "get_hero_achievement_styles"):
            styles = app.get_hero_achievement_styles()
            if hero_name in styles and styles[hero_name].get('text_color'): text_color = styles[hero_name]['text_color']
        
        display_text = hero_name
        if hasattr(app, "get_hero_mastery_map"):
            m_map = app.get_hero_mastery_map()
            if hero_name in m_map:
                display_text = f"{hero_name} (MR {m_map[hero_name][0]})"

        self.btn_select_hero.configure(text=display_text, fg_color=COLORS["accent"], text_color=text_color)
        self.configure(border_color=COLORS["accent"])
        self.open_variant_grid()

    def open_variant_grid(self):
        if not self.selected_hero_name: return
        variants = HEROES_DATA.get(self.selected_hero_name, ["Base"])
        # Usa o controller
        parent = self.controller if self.controller else self.winfo_toplevel()
        self.after(200, lambda: GridSelectionModal(parent, f"Variante de {self.selected_hero_name}", variants, self.update_variant_selection))

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
        self.btn_select_hero.configure(text="Selecionar Herói...", fg_color="#333333", text_color="white")
        self.configure(border_color=COLORS["border"])
        self.lbl_variant.configure(text="-", text_color="gray")

# --- APLICAÇÃO PRINCIPAL ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Tracker v1.2.3")
        self.geometry("1300x850")
        
        # Estado e Refs
        self.selected_villain = None
        self.selected_env = None
        self.selected_analysis_hero = None
        self.selected_villain_diff = None 
        self.insight_labels = [] 
        self.insight_titles = [] 
        self.seg_stats_mode = None
        self.combo_variant_analysis = None
        self.combo_diff_filter = None
        self.dash_cards_frames = {} 
        self.global_stat_labels = {} 
        self.agg_lists_frames = {} 
        self.achievements_frame = None 
        self.mastery_labels = {} 
        self.mastery_history_frame = None 
        self.lbl_mastery_name = None 
        self.lbl_agg_name = None # Inicializar para evitar erro
        self.lbl_achieve_name = None

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

    # --- ABA 1: REGISTRO ---
    def setup_register_tab(self):
        self.tab_reg.grid_columnconfigure(0, weight=1, uniform="g1"); self.tab_reg.grid_columnconfigure(1, weight=1, uniform="g1") 
        self.tab_reg.grid_rowconfigure(0, weight=1)
        self.left_panel = ctk.CTkFrame(self.tab_reg, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.card_mode = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_mode.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_mode, text="MODO DE JOGO", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(12, 5))
        self.seg_gamemode = ctk.CTkSegmentedButton(self.card_mode, values=["Solo", "Time de Vilões"], command=self.toggle_villain_mode, font=FONTS["body_bold"], height=32)
        self.seg_gamemode.set("Solo"); self.seg_gamemode.pack(pady=(0, 15), padx=20, fill="x")

        self.card_setup = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_setup.pack(fill="x", pady=(0, 15), ipady=10)
        self.container_villain = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_villain.pack(fill="x", padx=0, pady=0)

        self.frame_solo = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_solo, text="VILÃO", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_villain = ctk.CTkButton(self.frame_solo, text="Selecionar Vilão...", command=self.open_villain_grid, width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_villain.pack(padx=20, pady=(5, 5), fill="x")
        self.lbl_villain_diff = ctk.CTkLabel(self.frame_solo, text="Modo: Normal", font=FONTS["body"], text_color="gray")
        self.lbl_villain_diff.pack(padx=20, pady=(0, 10))
        
        self.frame_team = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_team, text="TIME DE VILÕES (3-5)", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.team_selectors = []
        for i in range(5):
            # PASSANDO CONTROLLER (SELF)
            sel = VillainSelector(self.frame_team, index=i+1, controller=self)
            sel.pack(padx=20, pady=4, fill="x")
            self.team_selectors.append(sel)
        self.frame_solo.pack(fill="x")

        ctk.CTkFrame(self.card_setup, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=20, pady=15)
        self.container_env = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_env.pack(fill="x")
        ctk.CTkLabel(self.container_env, text="AMBIENTE", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_env = ctk.CTkButton(self.container_env, text="Selecionar Ambiente...", command=self.open_env_grid, width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_env.pack(padx=20, pady=5, fill="x")

        self.card_result = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_result.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_result, text="RESULTADO DA BATALHA", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(12, 5))
        self.seg_result = ctk.CTkSegmentedButton(self.card_result, values=["Vitória", "Derrota"], selected_color=COLORS["success"], selected_hover_color="#209662", font=FONTS["body_bold"], height=40)
        self.seg_result.set("Vitória"); self.seg_result.pack(pady=(0, 20), padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.left_panel, text="SALVAR DADOS DA PARTIDA", command=self.save_game, fg_color=COLORS["accent"], hover_color="#144870", height=55, font=("Roboto", 15, "bold"), corner_radius=12)
        self.btn_save.pack(side="bottom", fill="x", pady=10)

        self.right_panel = ctk.CTkFrame(self.tab_reg, corner_radius=12, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_panel, text="EQUIPE DE HERÓIS", font=FONTS["h2"]).pack(pady=(0, 15), anchor="w")
        self.hero_selectors = []
        for i in range(5):
            # PASSANDO CONTROLLER (SELF)
            sel = HeroSelector(self.right_panel, index=i+1, controller=self)
            sel.pack(padx=0, pady=6, fill="x")
            self.hero_selectors.append(sel)

    # --- ABA 2: DASHBOARD ---
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
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.dash_cards_frames[key_id] = content_frame
        return frame

    # --- ABA 3: HERÓIS ---
    def setup_hero_tab_structure(self):
        self.tab_hero_internal = ctk.CTkTabview(self.tab_heroes)
        self.tab_hero_internal.pack(fill="both", expand=True, padx=10, pady=10)
        self.subtab_analysis = self.tab_hero_internal.add(" Análise Específica ")
        self.subtab_summary = self.tab_hero_internal.add(" Resumo do Herói ")
        self.subtab_achievements = self.tab_hero_internal.add(" Conquistas ")
        self.subtab_mastery = self.tab_hero_internal.add(" Maestria & XP ") # NOVA ABA
        self.subtab_global = self.tab_hero_internal.add(" Estatísticas Globais ")
        
        self.setup_subtab_analysis()
        self.setup_subtab_summary()
        self.setup_subtab_achievements()
        self.setup_subtab_mastery() # SETUP NOVA ABA
        self.setup_subtab_global()

    def setup_subtab_analysis(self):
        self.subtab_analysis.grid_columnconfigure(0, weight=1); self.subtab_analysis.grid_columnconfigure(1, weight=3); self.subtab_analysis.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(self.subtab_analysis, corner_radius=12, fg_color=COLORS["bg_card"])
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(left, text="SELEÇÃO", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(20, 10))
        self.btn_select_analysis_hero = ctk.CTkButton(left, text="Selecionar Herói...", command=self.open_analysis_hero_grid, width=220, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_analysis_hero.pack(pady=5)
        self.combo_variant_analysis = ctk.CTkComboBox(left, values=["Base"], command=lambda x: self.display_hero_insights(), width=220, font=FONTS["body"])
        self.combo_variant_analysis.pack(pady=(5, 20)); self.combo_variant_analysis.configure(state="disabled") 
        ctk.CTkFrame(left, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(left, text="FILTRAR DIFICULDADE", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(10, 5))
        self.combo_diff_filter = ctk.CTkComboBox(left, values=["Todos", "Normal", "Advanced", "Challenge", "Ultimate"], command=lambda x: self.display_hero_insights(), width=220, font=FONTS["body"])
        self.combo_diff_filter.set("Todos"); self.combo_diff_filter.pack(pady=5)

        right = ctk.CTkFrame(self.subtab_analysis, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.stats_header_frame = ctk.CTkFrame(right, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.stats_header_frame.pack(fill="x", pady=(0, 15))
        self.lbl_hero_wr = ctk.CTkLabel(self.stats_header_frame, text="WR: --%", font=FONTS["h1"], text_color=COLORS["success"])
        self.lbl_hero_wr.pack(side="left", padx=40, pady=25)
        self.lbl_hero_games = ctk.CTkLabel(self.stats_header_frame, text="0 Partidas", font=FONTS["h2"], text_color=COLORS["text_muted"])
        self.lbl_hero_games.pack(side="right", padx=40, pady=25)
        self.insights_scroll_frame = ctk.CTkScrollableFrame(right, corner_radius=12, fg_color="transparent", label_text="ANÁLISE ESTRATÉGICA", label_font=FONTS["h3"])
        self.insights_scroll_frame.pack(fill="both", expand=True)
        self.insight_titles, self.insight_labels = [], []
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

    # >>> SUB-ABA 2: RESUMO DO HERÓI
    def setup_subtab_summary(self):
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
        self.lbl_agg_stats.pack(pady=(10, 5))
        
        self.frame_diff_bar = ctk.CTkFrame(self.frame_agg_header, fg_color="transparent")
        self.frame_diff_bar.pack(pady=(0, 20))
        self.lbl_diff_counts = ctk.CTkLabel(self.frame_diff_bar, text="N: 0 | A: 0 | C: 0 | U: 0", font=FONTS["body_bold"], text_color=COLORS["highlight"])
        self.lbl_diff_counts.pack()

        self.frame_agg_content = ctk.CTkFrame(self.subtab_summary, fg_color="transparent")
        self.frame_agg_content.pack(fill="both", expand=True, padx=20, pady=5)
        for i in range(3): self.frame_agg_content.grid_columnconfigure(i, weight=1)
        self.frame_agg_content.grid_rowconfigure(0, weight=1)

        self.scroll_agg_vars = self.create_list_column(0, "VARIANTES")
        self.scroll_agg_vils = self.create_list_column(1, "VILÕES ENFRENTADOS")
        self.scroll_agg_envs = self.create_list_column(2, "AMBIENTES JOGADOS")

    # >>> SUB-ABA 3: CONQUISTAS
    def setup_subtab_achievements(self):
        self.frame_achieve_header = ctk.CTkFrame(self.subtab_achievements, corner_radius=12, fg_color=COLORS["bg_card"])
        self.frame_achieve_header.pack(fill="x", padx=20, pady=20)
        
        top_bar = ctk.CTkFrame(self.frame_achieve_header, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 20))
        
        self.lbl_achieve_name = ctk.CTkLabel(top_bar, text="SELECIONE UM HERÓI", font=FONTS["h1"])
        self.lbl_achieve_name.pack(side="left")
        
        self.btn_achieve_change = ctk.CTkButton(top_bar, text="Trocar Herói", command=self.open_analysis_hero_grid,
                                            width=120, fg_color="#333", border_width=1, border_color="#555")
        self.btn_achieve_change.pack(side="right")

        self.scroll_achieve = ctk.CTkScrollableFrame(self.subtab_achievements, corner_radius=12, fg_color="transparent")
        self.scroll_achieve.pack(fill="both", expand=True, padx=20, pady=10)
    
    # >>> SUB-ABA 4: MAESTRIA & XP (NOVA)
    def setup_subtab_mastery(self):
        # Header com Nível e Botão
        self.frame_mastery_header = ctk.CTkFrame(self.subtab_mastery, corner_radius=12, fg_color=COLORS["bg_card"])
        self.frame_mastery_header.pack(fill="x", padx=20, pady=20)

        top_bar = ctk.CTkFrame(self.frame_mastery_header, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 0))

        self.lbl_mastery_name = ctk.CTkLabel(top_bar, text="SELECIONE UM HERÓI", font=FONTS["h1"])
        self.lbl_mastery_name.pack(side="left")

        self.btn_mastery_change = ctk.CTkButton(top_bar, text="Trocar Herói", command=self.open_analysis_hero_grid,
                                            width=120, fg_color="#333", border_width=1, border_color="#555")
        self.btn_mastery_change.pack(side="right")
        
        # Barra de XP Gigante
        self.mastery_labels["bar_level"] = ctk.CTkLabel(self.frame_mastery_header, text="NÍVEL DE MAESTRIA: 0", font=("Roboto", 20, "bold"), text_color=COLORS["mastery_text"])
        self.mastery_labels["bar_level"].pack(pady=(0, 5))
        
        self.mastery_xp_bar = ctk.CTkProgressBar(self.frame_mastery_header, height=25, corner_radius=12, progress_color=COLORS["mastery_text"])
        self.mastery_xp_bar.pack(fill="x", padx=40, pady=5)
        self.mastery_xp_bar.set(0)
        
        self.mastery_labels["bar_text"] = ctk.CTkLabel(self.frame_mastery_header, text="0 / 1000 XP", font=FONTS["body_bold"], text_color="gray")
        self.mastery_labels["bar_text"].pack(pady=(0, 20))

        # Lista de Histórico
        self.mastery_history_frame = ctk.CTkScrollableFrame(self.subtab_mastery, corner_radius=12, fg_color="transparent", label_text="HISTÓRICO DE BATALHA & XP", label_font=FONTS["h3"])
        self.mastery_history_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def create_list_column(self, col, title):
        frame = ctk.CTkFrame(self.frame_agg_content, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"])
        frame.grid(row=0, column=col, sticky="nsew", padx=5)
        ctk.CTkLabel(frame, text=title, font=FONTS["card_label"], text_color="gray").pack(pady=10, anchor="center")
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        lbl_content = ctk.CTkLabel(scroll, text="...", justify="center", font=FONTS["dashboard_row"])
        lbl_content.pack(anchor="center")
        self.agg_lists_frames[title] = lbl_content
        return lbl_content

    def setup_subtab_global(self):
        self.frame_global_grid = ctk.CTkFrame(self.subtab_global, fg_color="transparent")
        self.frame_global_grid.pack(fill="both", expand=True, padx=20, pady=20)
        for i in range(4): self.frame_global_grid.grid_columnconfigure(i, weight=1)
        
        card_wr = ctk.CTkFrame(self.frame_global_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_wr.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(card_wr, text="WIN RATE TOTAL", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(15, 5))
        self.global_stat_labels["wr"] = ctk.CTkLabel(card_wr, text="--%", font=FONTS["h1"], text_color=COLORS["success"])
        self.global_stat_labels["wr"].pack(pady=(0, 15))

        self.create_global_card(1, 0, "TOTAL DE PARTIDAS", "total", "white", colspan=2)
        self.create_global_card(1, 2, "VITÓRIAS", "wins", COLORS["success"])
        self.create_global_card(1, 3, "DERROTAS", "losses", COLORS["danger"])

        ctk.CTkLabel(self.frame_global_grid, text="PARTIDAS POR DIFICULDADE", font=FONTS["h3"]).grid(row=2, column=0, columnspan=4, pady=(20, 10))
        self.create_global_card(3, 0, "NORMAL", "diff_normal", COLORS["highlight"])
        self.create_global_card(3, 1, "ADVANCED", "diff_advanced", COLORS["warning"])
        self.create_global_card(3, 2, "CHALLENGE", "diff_challenge", COLORS["diff_challenge"])
        self.create_global_card(3, 3, "ULTIMATE", "diff_ultimate", COLORS["diff_ultimate"])

    def create_global_card(self, r, c, title, key, color, colspan=1):
        f = ctk.CTkFrame(self.frame_global_grid, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        f.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(f, text=title, font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(15, 5))
        lbl = ctk.CTkLabel(f, text="0", font=FONTS["stat_big"], text_color=color)
        lbl.pack(pady=(0, 15))
        self.global_stat_labels[key] = lbl

    def setup_stats_tab(self):
        top_bar = ctk.CTkFrame(self.tab_stats, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=15, pady=15)
        self.seg_stats_mode = ctk.CTkSegmentedButton(top_bar, values=["Stats Solo", "Stats Time"], command=lambda x: self.calculate_details(), width=300, font=FONTS["body_bold"])
        self.seg_stats_mode.set("Stats Solo"); self.seg_stats_mode.pack(side="left")
        self.stats_grid = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.stats_grid.pack(fill="both", expand=True, padx=5, pady=5)
        for i in range(4): self.stats_grid.grid_columnconfigure(i, weight=1); self.stats_grid.grid_rowconfigure(0, weight=1)
        self.lbl_stats_v = self.create_table_col("VILÕES", 0)
        self.lbl_stats_e = self.create_table_col("AMBIENTES", 1)
        self.lbl_stats_s = self.create_table_col("TAMANHO DO TIME", 2)
        self.lbl_stats_h = self.create_table_col("HERÓIS", 3)

    def create_table_col(self, title, col_idx):
        frame = ctk.CTkFrame(self.stats_grid, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        frame.grid(row=0, column=col_idx, sticky="nsew", padx=5)
        ctk.CTkLabel(frame, height=40, text=title, font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        lbl = ctk.CTkLabel(scroll, text="...", justify="left", font=FONTS["mono"])
        lbl.pack(anchor="w")
        return lbl

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
        self.after(250, lambda: GridSelectionModal(self, f"Dificuldade: {villain}", modes, self.on_diff_selected))

    def on_diff_selected(self, diff):
        self.selected_villain_diff = diff
        self.lbl_villain_diff.configure(text=f"Modo: {diff}", text_color=COLORS["highlight"])
        self.combo_solo_mode.set(diff)

    def open_env_grid(self): GridSelectionModal(self, "Selecionar Ambiente", AMBIENTES, self.on_env_selected)
    def on_env_selected(self, env): self.selected_env = env; self.btn_select_env.configure(text=env, fg_color=COLORS["accent"])

    def open_analysis_hero_grid(self):
        hero_stats_map = self.get_all_heroes_stats_map()
        style_map = self.get_hero_achievement_styles()
        mastery_map = self.get_hero_mastery_map()
        sorted_heroes = sorted(list(HEROES_DATA.keys()), key=lambda x: (hero_stats_map.get(x, (0,0))[0], hero_stats_map.get(x, (0,0))[1]), reverse=True)
        GridSelectionModal(self, "Analisar Herói", sorted_heroes, self.on_analysis_hero_selected, item_stats=hero_stats_map, style_map=style_map, mastery_map=mastery_map)

    def on_analysis_hero_selected(self, hero_name):
        self.selected_analysis_hero = hero_name
        self.btn_select_analysis_hero.configure(text=hero_name, fg_color=COLORS["accent"])
        self.update_hero_variants_analysis(hero_name)
        self.calculate_aggregate_hero_stats(hero_name)
        # Update Titles
        self.lbl_agg_name.configure(text=hero_name.upper())
        self.lbl_achieve_name.configure(text=hero_name.upper())
        self.lbl_mastery_name.configure(text=hero_name.upper())

    def update_hero_variants_analysis(self, hero_name):
        variants = HEROES_DATA.get(hero_name, ["Base"])
        self.combo_variant_analysis.configure(values=variants, state="normal"); self.combo_variant_analysis.set("Base")
        self.display_hero_insights()

    # --- MASTERY & XP LOGIC ---
    def calculate_match_xp(self, villain_str, env, result, game_type):
        if result != "Vitória": return 0
        
        # 1. Base & Mode
        v_xp_base, env_xp_base = 500, 75
        is_ultimate = "(Ultimate)" in villain_str
        is_challenge = "(Challenge)" in villain_str
        is_advanced = "(Advanced)" in villain_str
        
        if is_ultimate: v_xp_base, env_xp_base = 1000, 125
        elif is_challenge: v_xp_base, env_xp_base = 750, 100
        elif is_advanced: v_xp_base, env_xp_base = 750, 100
        
        # 2. Villain Mult
        v_mult = 1
        if game_type == "SOLO":
            v_name_clean = villain_str.split(" (")[0]
            v_mult = SOLO_VILLAIN_DIFF.get(v_name_clean, 1)
        else:
            team_members = villain_str.split(",")
            total_diff = sum([TEAM_VILLAIN_DIFF.get(tm, 1) for tm in team_members])
            count = len(team_members)
            if count > 0: v_mult = total_diff / count
            
        # 3. Env Mult
        e_mult = ENV_DIFF.get(env, 1)
        
        total_xp = (v_xp_base * v_mult) + (env_xp_base * e_mult)
        return int(total_xp)

    def get_hero_mastery_map(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT heroes, villain, environment, result, game_type FROM games")
        rows = c.fetchall()
        conn.close()
        hero_xp = defaultdict(int)
        for h_str, v_str, env, res, g_type in rows:
            xp = self.calculate_match_xp(v_str, env, res, g_type)
            if xp > 0:
                for h_full in h_str.split(","):
                    h_base = h_full.split(" (")[0]
                    hero_xp[h_base] += xp
        mastery_map = {}
        for h, xp in hero_xp.items():
            level = xp // 1000
            mastery_map[h] = (level, xp)
        return mastery_map

    def update_mastery_history_list(self, hero_name):
        for widget in self.mastery_history_frame.winfo_children(): widget.destroy()
        
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, game_type, heroes FROM games")
        rows = c.fetchall()
        conn.close()

        match_log = []
        total_xp = 0

        for v_str, env, res, g_type, h_str in rows:
            is_in_match = False
            for h in h_str.split(","):
                if h.split(" (")[0] == hero_name:
                    is_in_match = True
                    break
            if is_in_match:
                xp = self.calculate_match_xp(v_str, env, res, g_type)
                total_xp += xp
                if xp > 0:
                    match_log.append((v_str, env, res, xp))

        m_level = total_xp // 1000
        m_curr = total_xp % 1000
        self.mastery_labels["bar_level"].configure(text=f"NÍVEL DE MAESTRIA: {m_level}")
        self.mastery_labels["bar_text"].configure(text=f"{m_curr} / 1000 XP (Total: {total_xp:,})")
        self.mastery_xp_bar.set(m_curr / 1000)

        for v, e, r, x in reversed(match_log):
            row = ctk.CTkFrame(self.mastery_history_frame, fg_color=COLORS["bg_card"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=5)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=1)
            ctk.CTkLabel(row, text=v, font=FONTS["body_bold"], anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(row, text=e, font=FONTS["body"], text_color="gray", anchor="w").grid(row=0, column=1, padx=5, sticky="ew")
            ctk.CTkLabel(row, text=f"+{x} XP", font=FONTS["body_bold"], text_color=COLORS["mastery_text"], anchor="e").grid(row=0, column=2, padx=10, sticky="ew")

        if not match_log:
            ctk.CTkLabel(self.mastery_history_frame, text="Nenhuma partida vitoriosa registrada.", text_color="gray").pack(pady=20)

    # --- ACHIEVEMENTS LOGIC ---
    def get_hero_achievement_styles(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT heroes, villain, result, game_type FROM games")
        rows = c.fetchall()
        conn.close()
        hero_wins, hero_villains_normal, hero_villains_ultimate, hero_variants_wins = defaultdict(int), defaultdict(set), defaultdict(set), defaultdict(int)
        all_villains = set(SOLO_VILLAINS_DATA.keys()) 

        for h_str, v_str, res, g_type in rows:
            is_win = (res == "Vitória")
            if not is_win: continue
            h_list = h_str.split(",")
            villain_base, is_ultimate, is_normal = None, False, False
            if g_type == "SOLO":
                if "(" in v_str:
                    villain_base = v_str.split(" (")[0]
                    if "(Ultimate)" in v_str: is_ultimate = True
                    if not any(x in v_str for x in ["(Ultimate)", "(Challenge)", "(Advanced)"]): is_normal = True
                else: villain_base = v_str; is_normal = True
            for h_full in h_list:
                h_base = h_full.split(" (")[0]
                hero_wins[h_base] += 1
                hero_variants_wins[h_full] += 1
                if villain_base and villain_base in all_villains:
                    if is_normal: hero_villains_normal[h_base].add(villain_base)
                    if is_ultimate: hero_villains_ultimate[h_base].add(villain_base)

        style_map = {}
        for hero in HEROES_DATA.keys():
            style = {}
            wins = hero_wins[hero]
            if wins >= 2500: style['text_color'] = COLORS["rank_sentinel"]
            elif wins >= 1000: style['text_color'] = COLORS["rank_diamond"]
            elif wins >= 500: style['text_color'] = COLORS["rank_platinum"]
            elif wins >= 100: style['text_color'] = COLORS["rank_gold"]
            elif wins >= 25: style['text_color'] = COLORS["rank_silver"]
            elif wins >= 10: style['text_color'] = COLORS["rank_bronze"]
            else: style['text_color'] = "white"

            defeated_norm = len(hero_villains_normal[hero])
            defeated_ult = len(hero_villains_ultimate[hero])
            total_unique = len(all_villains)
            if total_unique > 0:
                if defeated_ult >= total_unique: style['border_color'] = COLORS["rank_gold"]
                elif defeated_norm >= total_unique: style['border_color'] = COLORS["rank_silver"]
            
            variants = HEROES_DATA.get(hero, [])
            if variants:
                star_count = 0
                for v in variants:
                    v_full = hero if v == "Base" else f"{hero} ({v})"
                    if hero_variants_wins[v_full] >= 100: star_count += 1
                if star_count > 0: style['icon'] = "★" * star_count

            if style: style_map[hero] = style
        return style_map

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
        c.execute("SELECT result, heroes, villain, environment, game_type FROM games")
        rows = c.fetchall()
        conn.close()

        total_g, total_w = 0, 0
        var_stats = defaultdict(lambda: [0, 0])
        villain_stats = defaultdict(lambda: [0, 0])
        env_stats = defaultdict(lambda: [0, 0])
        diff_wins = {"Normal": 0, "Advanced": 0, "Challenge": 0, "Ultimate": 0}
        
        unique_villains_norm = set()
        unique_villains_ult = set()

        for res, h_str, v_str, env, g_type in rows:
            win = 1 if res == "Vitória" else 0
            h_list = h_str.split(",")
            
            hero_in_game = False
            for h in h_list:
                if h.split(" (")[0] == base_name:
                    hero_in_game = True
                    var_stats[h][0] += win; var_stats[h][1] += 1
            
            if hero_in_game:
                total_w += win; total_g += 1
                env_stats[env][0] += win; env_stats[env][1] += 1
                
                v_list = v_str.split(",") if g_type == "TEAM" else [v_str]
                current_diff = "Normal"
                
                for v_full in v_list:
                    v_clean = v_full
                    is_ult = False; is_norm = False
                    
                    if g_type == "SOLO":
                        if "(" in v_full:
                            v_clean = v_full.split(" (")[0]
                            if "(Ultimate)" in v_full: current_diff = "Ultimate"; is_ult = True
                            elif "(Challenge)" in v_full: current_diff = "Challenge"
                            elif "(Advanced)" in v_full: current_diff = "Advanced"
                            else: is_norm = True 
                        else: is_norm = True
                    
                    villain_stats[v_clean][0] += win
                    villain_stats[v_clean][1] += 1
                    
                    if win:
                        if is_norm: unique_villains_norm.add(v_clean)
                        if is_ult: unique_villains_ult.add(v_clean)
                
                if win: diff_wins[current_diff] += 1

        wr = (total_w/total_g)*100 if total_g > 0 else 0
        self.lbl_agg_name.configure(text=base_name.upper())
        self.lbl_agg_stats.configure(text=f"{total_g} JOGOS  |  {wr:.1f}% WR GERAL")
        
        diff_txt = f"WINS POR DIFICULDADE:  N:{diff_wins['Normal']}  |  A:{diff_wins['Advanced']}  |  C:{diff_wins['Challenge']}  |  U:{diff_wins['Ultimate']}"
        self.lbl_diff_counts.configure(text=diff_txt)

        # Chama a construção das ABAS extras
        self.build_achievements_view(base_name, total_w, unique_villains_norm, unique_villains_ult, var_stats)
        self.update_mastery_history_list(base_name)

        def update_list(label_key, data_map):
            txt = ""
            sorted_items = sorted(data_map.items(), key=lambda x: x[1][1], reverse=True)
            for name, stats in sorted_items:
                v_wr = (stats[0]/stats[1])*100
                txt += f"{v_wr:>5.0f}% WR | {stats[1]:>3} J | {name}\n"
                txt += "─"*45 + "\n"
            if not txt: txt = "Sem dados."
            self.agg_lists_frames[label_key].configure(text=txt)

        update_list("VARIANTES", var_stats)
        update_list("VILÕES ENFRENTADOS", villain_stats)
        update_list("AMBIENTES JOGADOS", env_stats)

    def build_achievements_view(self, hero_name, total_wins, villains_norm, villains_ult, var_stats):
        # Limpa widgets anteriores
        for widget in self.scroll_achieve.winfo_children(): widget.destroy()

        ranks = [(10, "Bronze", COLORS["rank_bronze"]), (25, "Prata", COLORS["rank_silver"]), 
                 (100, "Ouro", COLORS["rank_gold"]), (500, "Platina", COLORS["rank_platinum"]), 
                 (1000, "Diamante", COLORS["rank_diamond"]), (2500, "SENTINEL", COLORS["rank_sentinel"])]
        
        curr_rank, curr_color, next_goal, next_rank_name = "Sem Ranque", "gray", 10, "Bronze"
        for w, n, c in ranks:
            if total_wins >= w: curr_rank, curr_color = n, c
            else: next_goal, next_rank_name = w, n; break
        
        prog = 1.0 if total_wins >= 2500 else total_wins / next_goal
        disp_next = "MÁXIMO ALCANÇADO" if total_wins >= 2500 else f"Próximo: {next_rank_name}"

        self.create_achievement_card("RANQUE DE HERÓI", f"Atual: {curr_rank}", total_wins, next_goal, prog, curr_color, disp_next)

        all_v = set(SOLO_VILLAINS_DATA.keys())
        missing_n = sorted(list(all_v - villains_norm))
        self.create_achievement_card("MAESTRIA NORMAL (Borda Prata)", f"Derrotou {len(villains_norm)}/{len(all_v)} Vilões", len(villains_norm), len(all_v), len(villains_norm)/len(all_v) if all_v else 0, COLORS["rank_silver"], "Derrote todos os vilões.", missing_n)

        missing_u = sorted(list(all_v - villains_ult))
        self.create_achievement_card("MAESTRIA ULTIMATE (Borda Ouro)", f"Derrotou {len(villains_ult)}/{len(all_v)} Vilões (Ultimate)", len(villains_ult), len(all_v), len(villains_ult)/len(all_v) if all_v else 0, COLORS["rank_gold"], "Derrote todos em Ultimate.", missing_u)

        vars = HEROES_DATA.get(hero_name, [])
        done_vars = 0; miss_vars = []
        for v in vars:
            vf = hero_name if v == "Base" else f"{hero_name} ({v})"
            w = var_stats[vf][0]
            if w >= 100: done_vars += 1
            else: miss_vars.append(f"{v} ({w}/100)")
        
        self.create_achievement_card("ESTRELAS DE VARIANTE (★)", f"Conquistou {done_vars}/{len(vars)} Estrelas", done_vars, len(vars), done_vars/len(vars) if vars else 0, COLORS["highlight"], "1 estrela por variante com 100 vitórias.", miss_vars)

    def create_achievement_card(self, title, status, cur, tgt, prog, color, desc, missing=None):
        card = ctk.CTkFrame(self.scroll_achieve, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=10)
        
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(head, text=title, font=FONTS["h3"], text_color=color).pack(side="left")
        ctk.CTkLabel(head, text=f"{cur}/{tgt}", font=FONTS["body_bold"], text_color="gray").pack(side="right")

        bar = ctk.CTkProgressBar(card, height=15, corner_radius=8)
        bar.pack(fill="x", padx=15, pady=5)
        bar.set(prog); bar.configure(progress_color=color)

        ctk.CTkLabel(card, text=desc, font=FONTS["body"], text_color="gray").pack(fill="x", padx=15, pady=(0, 10), anchor="w")

        if missing:
            det_frame = ctk.CTkFrame(card, fg_color="#222", corner_radius=8)
            lbl_miss = ctk.CTkLabel(det_frame, text=", ".join(missing), font=FONTS["body"], text_color="gray", wraplength=800, justify="left")
            
            def toggle():
                if det_frame.winfo_ismapped():
                    det_frame.pack_forget(); btn.configure(text=f"Mostrar Faltantes ({len(missing)}) 🔽")
                else:
                    det_frame.pack(fill="x", padx=15, pady=(0, 15)); lbl_miss.pack(padx=10, pady=10, fill="x"); btn.configure(text="Ocultar Faltantes 🔼")

            btn = ctk.CTkButton(card, text=f"Mostrar Faltantes ({len(missing)}) 🔽", command=toggle, fg_color="transparent", border_width=1, border_color=COLORS["border"], height=25, font=FONTS["body"])
            btn.pack(padx=15, pady=(0, 15), anchor="w")

    def calculate_global_stats(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT result, game_type, villain FROM games")
        rows = c.fetchall()
        conn.close()
        total = len(rows)
        wins = sum(1 for r in rows if r[0] == "Vitória")
        wr = (wins/total)*100 if total > 0 else 0
        diff_counts = {"Normal": 0, "Advanced": 0, "Challenge": 0, "Ultimate": 0}
        for r in rows:
            v_str = r[2]
            if "(Ultimate)" in v_str: diff_counts["Ultimate"] += 1
            elif "(Challenge)" in v_str: diff_counts["Challenge"] += 1
            elif "(Advanced)" in v_str: diff_counts["Advanced"] += 1
            else: diff_counts["Normal"] += 1

        self.global_stat_labels["total"].configure(text=str(total))
        self.global_stat_labels["wins"].configure(text=str(wins))
        self.global_stat_labels["losses"].configure(text=str(total - wins))
        self.global_stat_labels["wr"].configure(text=f"{wr:.1f}%", text_color=COLORS["success"] if wr >= 50 else COLORS["danger"])
        self.global_stat_labels["diff_normal"].configure(text=str(diff_counts["Normal"]))
        self.global_stat_labels["diff_advanced"].configure(text=str(diff_counts["Advanced"]))
        self.global_stat_labels["diff_challenge"].configure(text=str(diff_counts["Challenge"]))
        self.global_stat_labels["diff_ultimate"].configure(text=str(diff_counts["Ultimate"]))

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
                ctk.CTkLabel(row, text=name, font=FONTS["dashboard_row"], width=180, anchor="w").pack(side="left")
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
            for k, val in l: 
                pct = val[0]/val[1]*100
                t+=f"{pct:>6.1f}%  ({val[0]:>2}/{val[1]:<2})  {k}\n"
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