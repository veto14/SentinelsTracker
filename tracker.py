import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict
import math

# --- CONFIGURAÇÃO VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- FONTES ---
FONT_BIG_NUMBER = ("Roboto", 40, "bold")
FONT_MED_NUMBER = ("Roboto", 24, "bold") 
FONT_HEADER = ("Roboto Medium", 16)
FONT_CARD_TITLE = ("Roboto", 12, "bold")
FONT_NORMAL = ("Roboto", 12)
FONT_MONO = ("Consolas", 12)
# NOVAS FONTES PARA OS INSIGHTS
FONT_INSIGHT_TITLE = ("Roboto", 16, "bold")
FONT_INSIGHT_CONTENT = ("Roboto", 14)


# --- DADOS (HEROES_DATA, VILLAINS, ETC - MANTIDOS IGUAIS) ---
HEROES_DATA = {
    "Legacy": ["Base", "America's Greatest", "Young", "Freedom Five"],
    "Bunker": ["Base", "G.I.", "Freedom Five", "Termi-Nation"],
    "Wraith": ["Base", "Rook City", "Freedom Five", "Price of Freedom"],
    "Tachyon": ["Base", "Super Scientific", "Freedom Five", "Team Leader"],
    "Absolute Zero": ["Base", "Elemental", "Freedom Five", "Termi-Nation"],
    "Unity": ["Base", "Termi-Nation", "Golem"],
    "Haka": ["Base", "Eternal", "Prime Wardens"],
    "Fanatic": ["Base", "Redeemer", "Prime Wardens", "Haunted"],
    "Tempest": ["Base", "Prime Wardens", "Freedom Six"],
    "Argent Adept": ["Base", "Dark Conductor", "Prime Wardens"],
    "Captain Cosmic": ["Base", "Prime Wardens", "Requiem"],
    "Expatriette": ["Base", "Dark Watch"],
    "Setback": ["Base", "Dark Watch"],
    "NightMist": ["Base", "Dark Watch"],
    "Mr. Fixer": ["Base", "Dark Watch"],
    "The Harpy": ["Base", "Dark Watch"],
    "Ra": ["Base", "Setting Sun", "Horus"],
    "Visionary": ["Base", "Dark", "Unleashed"],
    "Chrono-Ranger": ["Base", "Best of Times"],
    "Omnitron-X": ["Base", "Omnitron-U"],
    "Sky-Scraper": ["Base", "Extremist"],
    "K.N.Y.F.E.": ["Base", "Rogue Agent"],
    "Parse": ["Base", "Fugue State"],
    "The Naturalist": ["Base", "Hunted"],
    "Sentinels": ["Base", "Adamant"],
    "Guise": ["Base", "Santa"],
    "Stuntman": ["Base", "Action Hero"],
    "Benchmark": ["Base"],
    "La Comodora": ["Base"],
    "Lifeline": ["Base"],
    "Akash'Thriya": ["Base"],
    "Luminary": ["Base"]
}

SOLO_VILLAINS_DATA = {
    "Baron Blade": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Citizen Dawn": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Grand Warlord Voss": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Omnitron": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Spite": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "The Chairman": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Akash'Bhuta": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "GloomWeaver": ["Normal", "Advanced", "Challenge", "Ultimate", "Skinwalker"],
    "The Matriarch": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Plague Rat": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Ennead": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Apostate": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Iron Legacy": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Kismet": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "La Capitan": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Dreamer": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Kaargra Warfang": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Progeny": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Deadline": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "Infinitor": ["Normal", "Advanced", "Challenge", "Ultimate"],
    "OblivAeon": ["Normal", "Advanced"]
}

TEAM_VILLAINS_LIST = [
    "Baron Blade", "Friction", "Fright Train", "Proletariat", "Ermine",
    "Vander", "Dr. Tremata", "Marcato", "Honored Maidens", "Pariah",
    "Ambuscade", "Biomancer", "Bugbear", "Citizen Hammer", "Greazer", 
    "La Capitan", "Miss Information", "Plague Rat", "Sergeant Steel", "The Operative"
]
TEAM_VILLAINS_LIST.sort()

AMBIENTES = [
    "Megalopolis", "Insula Primalis", "Ruins of Atlantis", 
    "Wagner Mars Base", "Rook City", "Pike Industrial Complex",
    "Tomb of Anubis", "Realm of Discord", "Nexus of the Void", "The Block",
    "Time Cataclysm", "Silver Gulch", "Final Wasteland", "Omnitron-IV",
    "Celestial Tribunal", "Magmaria", "Freedom Tower", "Mobile Defense Platform"
]
AMBIENTES.sort()

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

class HeroSelector(ctk.CTkFrame):
    def __init__(self, master, index, **kwargs):
        super().__init__(master, corner_radius=10, border_width=1, border_color="#3a3a3a", fg_color="#2b2b2b", **kwargs)
        self.lbl_idx = ctk.CTkLabel(self, text=f"{index}", font=("Arial", 20, "bold"), text_color="#555555", width=30)
        self.lbl_idx.pack(side="left", padx=(10, 5))
        self.combo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.combo_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        names = ["(Nenhum)"] + sorted(list(HEROES_DATA.keys()))
        self.hero_combo = ctk.CTkComboBox(self.combo_frame, values=names, command=self.update_variants, width=180, font=FONT_NORMAL)
        self.hero_combo.pack(pady=(0, 2))
        self.variant_combo = ctk.CTkComboBox(self.combo_frame, values=["-"], width=180, state="disabled", font=("Arial", 12))
        self.variant_combo.pack(pady=(2, 0))

    def update_variants(self, choice):
        if choice == "(Nenhum)":
            self.variant_combo.configure(values=["-"], state="disabled")
            self.variant_combo.set("-")
            self.configure(border_color="#3a3a3a")
        else:
            variants = HEROES_DATA.get(choice, ["Base"])
            self.variant_combo.configure(values=variants, state="normal")
            self.variant_combo.set("Base")
            self.configure(border_color="#1f6aa5")

    def get_selection(self):
        h = self.hero_combo.get()
        v = self.variant_combo.get()
        if h == "(Nenhum)": return None
        return h if v == "Base" else f"{h} ({v})"
    
    def reset(self):
        self.hero_combo.set("(Nenhum)")
        self.update_variants("(Nenhum)")

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Multiverse Tracker v10.0")
        self.geometry("1280x800")
        
        # INICIALIZA VARIÁVEIS SEGURAS
        self.insight_labels = [] 
        self.seg_stats_mode = None
        self.combo_hero_analysis = None
        self.combo_variant_analysis = None
        self.combo_diff_filter = None

        self.main_container = ctk.CTkTabview(self, corner_radius=15)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_reg = self.main_container.add("  REGISTRAR  ")
        self.tab_overview = self.main_container.add("  VISÃO GERAL  ")
        self.tab_heroes = self.main_container.add("  HERÓIS  ")
        self.tab_stats = self.main_container.add("  DETALHES  ")

        self.setup_register_tab()
        self.setup_overview_tab()
        self.setup_stats_tab()
        self.setup_hero_tab()
        
        # Garante que roda só depois de tudo pronto
        self.after(500, self.refresh_all_data) 

    # --- SETUP TABS ---
    def setup_register_tab(self):
        self.tab_reg.grid_columnconfigure(0, weight=1, uniform="g1")
        self.tab_reg.grid_columnconfigure(1, weight=1, uniform="g1")
        self.tab_reg.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.tab_reg, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.card_mode = ctk.CTkFrame(self.left_panel, corner_radius=10)
        self.card_mode.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_mode, text="MODO DE JOGO", font=("Roboto", 14, "bold"), text_color="gray").pack(pady=(10, 5))
        self.seg_gamemode = ctk.CTkSegmentedButton(self.card_mode, values=["Solo", "Time de Vilões"], 
                                                   command=self.toggle_villain_mode, font=("Roboto", 14, "bold"), height=35)
        self.seg_gamemode.set("Solo")
        self.seg_gamemode.pack(pady=(0, 15), padx=20, fill="x")

        self.card_setup = ctk.CTkFrame(self.left_panel, corner_radius=10)
        self.card_setup.pack(fill="x", pady=(0, 15), ipady=10)
        
        self.frame_solo = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        ctk.CTkLabel(self.frame_solo, text="VILÃO", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15)
        self.combo_solo_name = ctk.CTkComboBox(self.frame_solo, values=sorted(list(SOLO_VILLAINS_DATA.keys())), 
                                               command=self.update_solo_modes, width=250, font=FONT_NORMAL)
        self.combo_solo_name.pack(padx=15, pady=(5, 5), fill="x")
        self.combo_solo_mode = ctk.CTkComboBox(self.frame_solo, values=["Normal"], width=250, font=FONT_NORMAL)
        self.combo_solo_mode.pack(padx=15, pady=(0, 10), fill="x")
        
        self.frame_team = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        ctk.CTkLabel(self.frame_team, text="TIME DE VILÕES", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15)
        self.team_villain_combos = []
        for i in range(5):
            c = ctk.CTkComboBox(self.frame_team, values=["(Nenhum)"] + TEAM_VILLAINS_LIST, height=28)
            c.pack(padx=15, pady=2, fill="x")
            self.team_villain_combos.append(c)
        self.frame_solo.pack(fill="x")
        self.update_solo_modes(self.combo_solo_name.get())

        ctk.CTkFrame(self.card_setup, height=2, fg_color="#3a3a3a").pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(self.card_setup, text="AMBIENTE", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15)
        self.combo_env = ctk.CTkComboBox(self.card_setup, values=AMBIENTES, font=FONT_NORMAL)
        self.combo_env.pack(padx=15, pady=5, fill="x")

        self.card_result = ctk.CTkFrame(self.left_panel, corner_radius=10)
        self.card_result.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_result, text="RESULTADO", font=("Roboto", 14, "bold"), text_color="gray").pack(pady=(10, 5))
        self.seg_result = ctk.CTkSegmentedButton(self.card_result, values=["Vitória", "Derrota"], 
                                                 selected_color="#2CC985", selected_hover_color="#209662",
                                                 font=("Roboto", 14, "bold"), height=40)
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=(0, 20), padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.left_panel, text="REGISTRAR PARTIDA", command=self.save_game, 
                                      fg_color="#1f6aa5", hover_color="#144870", height=60, font=("Roboto", 18, "bold"), corner_radius=10)
        self.btn_save.pack(side="bottom", fill="x", pady=10)

        self.right_panel = ctk.CTkFrame(self.tab_reg, corner_radius=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_panel, text="EQUIPE DE HERÓIS", font=FONT_HEADER).pack(pady=15)
        self.hero_selectors = []
        for i in range(5):
            sel = HeroSelector(self.right_panel, index=i+1)
            sel.pack(padx=15, pady=6, fill="x")
            self.hero_selectors.append(sel)

    def setup_overview_tab(self):
        self.frame_total = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.frame_total.pack(fill="x", pady=20)
        ctk.CTkLabel(self.frame_total, text="TOTAL DE PARTIDAS", font=("Roboto", 16, "bold"), text_color="gray").pack()
        self.lbl_total_games = ctk.CTkLabel(self.frame_total, text="0", font=FONT_BIG_NUMBER, text_color="#2CC985")
        self.lbl_total_games.pack()
        ctk.CTkButton(self.frame_total, text="Atualizar Dados", command=self.refresh_all_data, 
                      height=25, width=100, fg_color="#333").pack(pady=5)

        self.grid_overview = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.grid_overview.pack(fill="both", expand=True, padx=10, pady=10)
        for i in range(3): self.grid_overview.grid_columnconfigure(i, weight=1)
        for i in range(2): self.grid_overview.grid_rowconfigure(i, weight=1)

        self.card_hero_played = self.create_stat_card(0, 0, "Heróis Mais Jogados")
        self.card_hero_best = self.create_stat_card(0, 1, "Melhores Heróis (Winrate)", color="#1a4d1a")
        self.card_hero_worst = self.create_stat_card(0, 2, "Piores Heróis (Winrate)", color="#4d1a1a")
        self.card_villain_played = self.create_stat_card(1, 0, "Vilões Favoritos")
        self.card_villain_hardest = self.create_stat_card(1, 1, "Vilões Mais Difíceis", color="#4d1a1a")
        self.card_env_played = self.create_stat_card(1, 2, "Ambientes Mais Jogados")

    def create_stat_card(self, row, col, title, color="#2b2b2b"):
        frame = ctk.CTkFrame(self.grid_overview, fg_color=color, corner_radius=10, border_width=1, border_color="#3a3a3a")
        frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(frame, text=title, font=("Roboto", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkFrame(frame, height=2, fg_color="#555").pack(fill="x", padx=10, pady=(0,5))
        lbl_content = ctk.CTkLabel(frame, text="...", font=FONT_MONO, justify="left")
        lbl_content.pack(expand=True, padx=10, pady=5)
        return lbl_content

    # ================= 3. ABA HERÓIS (ATUALIZADA) =================
    def setup_hero_tab(self):
        self.tab_heroes.grid_columnconfigure(0, weight=1)
        self.tab_heroes.grid_columnconfigure(1, weight=3)
        self.tab_heroes.grid_rowconfigure(0, weight=1)

        # --- LADO ESQUERDO: SELEÇÃO E FILTROS ---
        self.hero_selection_frame = ctk.CTkFrame(self.tab_heroes, corner_radius=10, width=250)
        self.hero_selection_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.hero_selection_frame, text="Selecione o Herói", font=FONT_HEADER).pack(pady=(15, 5))
        
        hero_names = sorted(list(HEROES_DATA.keys()))
        if not hero_names: hero_names = ["(Vazio)"]

        self.combo_hero_analysis = ctk.CTkComboBox(self.hero_selection_frame, 
                                                   values=hero_names, 
                                                   command=self.update_hero_variants_analysis, 
                                                   width=200, font=FONT_NORMAL)
        self.combo_hero_analysis.pack(pady=5)
        self.combo_variant_analysis = ctk.CTkComboBox(self.hero_selection_frame, 
                                                      values=["Base"], 
                                                      command=lambda x: self.display_hero_insights(), 
                                                      width=200, font=FONT_NORMAL)
        self.combo_variant_analysis.pack(pady=(0, 20))
        
        # DIVISOR
        ctk.CTkFrame(self.hero_selection_frame, height=2, fg_color="#444").pack(fill="x", padx=20, pady=10)
        
        # FILTRO DE DIFICULDADE
        ctk.CTkLabel(self.hero_selection_frame, text="Filtro de Dificuldade", font=FONT_HEADER).pack(pady=(10, 5))
        self.combo_diff_filter = ctk.CTkComboBox(self.hero_selection_frame, 
                                                 values=["Todos", "Normal", "Advanced", "Challenge", "Ultimate"],
                                                 command=lambda x: self.display_hero_insights(),
                                                 width=200, font=FONT_NORMAL)
        self.combo_diff_filter.set("Todos")
        self.combo_diff_filter.pack(pady=5)
        
        if hero_names and hero_names[0] != "(Vazio)":
            self.combo_hero_analysis.set(hero_names[0])
            self.update_hero_variants_analysis(hero_names[0])

        # --- LADO DIREITO: RESUMO E INSIGHTS ---
        right_panel_container = ctk.CTkFrame(self.tab_heroes, fg_color="transparent")
        right_panel_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # HEADLINE STATS (Winrate e Jogos)
        self.stats_header_frame = ctk.CTkFrame(right_panel_container, corner_radius=10, fg_color="#222")
        self.stats_header_frame.pack(fill="x", pady=(0, 10))
        
        self.lbl_hero_wr = ctk.CTkLabel(self.stats_header_frame, text="WR: --%", font=FONT_BIG_NUMBER, text_color="#2CC985")
        self.lbl_hero_wr.pack(side="left", padx=30, pady=20)
        
        self.lbl_hero_games = ctk.CTkLabel(self.stats_header_frame, text="0 Partidas", font=FONT_MED_NUMBER, text_color="gray")
        self.lbl_hero_games.pack(side="right", padx=30, pady=20)

        # INSIGHTS SCROLL
        self.insights_scroll_frame = ctk.CTkScrollableFrame(right_panel_container, corner_radius=10, label_text="Análise Estratégica", label_font=("Roboto", 18, "bold"))
        self.insights_scroll_frame.pack(fill="both", expand=True)
        
        self.insight_labels = []
        for i in range(5):
            # Alteração principal aqui: definindo a fonte para os insights
            lbl = ctk.CTkLabel(self.insights_scroll_frame, text="Aguardando...", 
                               justify="left", wraplength=500, font=FONT_INSIGHT_CONTENT, 
                               fg_color="#3a3a3a", corner_radius=8, padx=10, pady=10)
            lbl.pack(fill="x", pady=10)
            self.insight_labels.append(lbl)

    def setup_stats_tab(self):
        top_bar = ctk.CTkFrame(self.tab_stats, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=10, pady=10)
        self.seg_stats_mode = ctk.CTkSegmentedButton(top_bar, values=["Stats Solo", "Stats Time"], 
                                                     command=lambda x: self.calculate_details(), width=300)
        self.seg_stats_mode.set("Stats Solo")
        self.seg_stats_mode.pack(side="left")

        self.stats_grid = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.stats_grid.pack(fill="both", expand=True, padx=5, pady=5)
        for i in range(4):
            self.stats_grid.grid_columnconfigure(i, weight=1)
            self.stats_grid.grid_rowconfigure(0, weight=1)

        def create_col(title, col_idx):
            frame = ctk.CTkFrame(self.stats_grid, corner_radius=10)
            frame.grid(row=0, column=col_idx, sticky="nsew", padx=5)
            header = ctk.CTkFrame(frame, height=40, corner_radius=10, fg_color="#202020")
            header.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(header, text=title, font=("Roboto", 14, "bold")).pack(pady=8)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=5, pady=5)
            lbl = ctk.CTkLabel(scroll, text="...", justify="left", font=FONT_MONO)
            lbl.pack(anchor="w")
            return lbl

        self.lbl_stats_v = create_col("VILÕES", 0)
        self.lbl_stats_e = create_col("AMBIENTES", 1)
        self.lbl_stats_s = create_col("TAMANHO TIME", 2)
        self.lbl_stats_h = create_col("HERÓIS", 3)

    # --- LÓGICA ---
    def toggle_villain_mode(self, mode):
        self.frame_solo.pack_forget()
        self.frame_team.pack_forget()
        if mode == "Solo": self.frame_solo.pack(fill="x")
        else: self.frame_team.pack(fill="x")

    def update_solo_modes(self, choice):
        modes = SOLO_VILLAINS_DATA.get(choice, ["Normal"])
        self.combo_solo_mode.configure(values=modes)
        self.combo_solo_mode.set("Normal")

    def update_hero_variants_analysis(self, hero_name):
        variants = HEROES_DATA.get(hero_name, ["Base"])
        self.combo_variant_analysis.configure(values=variants)
        self.combo_variant_analysis.set("Base")
        self.display_hero_insights()

    def display_hero_insights(self):
        hero_base = self.combo_hero_analysis.get()
        variant = self.combo_variant_analysis.get()
        diff_filter = self.combo_diff_filter.get() 

        if not hero_base or hero_base == "(Vazio)" or not self.insight_labels: return
        hero_full = hero_base if variant == "Base" else f"{hero_base} ({variant})"
        
        stats_data = self.calculate_hero_insights(hero_full, diff_filter)
        
        total_games = stats_data[0]
        win_rate = stats_data[1]
        insights = stats_data[2:]

        self.lbl_hero_games.configure(text=f"{total_games} Partidas")
        self.lbl_hero_wr.configure(text=f"{win_rate:.1f}%", text_color="#2CC985" if win_rate >= 50 else "#d63031")

        titles = ["Vilão Mais Fácil", "Vilão Mais Difícil", "Parceiro Frequente", "Ambiente Frequente", "Consistência (DP)"]
        for i, (title, content) in enumerate(zip(titles, insights)):
            # Alteração para formatar o texto usando as novas fontes
            full_text = f"{title}\n\n{content}" # Coloca o conteúdo em negrito
            self.insight_labels[i].configure(text=full_text, font=FONT_INSIGHT_TITLE) # Usa a fonte maior
            # A cor já é definida pelo widget pai (fg_color="#3a3a3a")

    def calculate_hero_insights(self, target_hero, difficulty="Todos"):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        try:
            c.execute("SELECT villain, environment, result, heroes, game_type FROM games WHERE heroes LIKE ?", (f'%{target_hero}%',))
            rows = c.fetchall()
        except:
            return [0, 0.0, "Erro ao ler BD. Apague o arquivo .db e reinicie."] * 5
        finally:
            conn.close()

        # --- FILTRAGEM POR DIFICULDADE (Python-side) ---
        filtered_rows = []
        for r in rows:
            v_str, env, res, h_str, g_type = r
            
            if difficulty == "Todos":
                filtered_rows.append(r)
            elif g_type == "SOLO":
                if difficulty == "Normal":
                    if not any(x in v_str for x in ["(Advanced)", "(Challenge)", "(Ultimate)"]):
                        filtered_rows.append(r)
                else:
                    if f"({difficulty})" in v_str:
                        filtered_rows.append(r)
            else:
                if difficulty == "Todos":
                    filtered_rows.append(r)
        
        rows = filtered_rows
        
        total_games = len(rows)
        if total_games == 0:
            return [0, 0.0, "Sem partidas com esse filtro.", "Sem partidas.", "-", "-", "-"]

        total_wins = sum(1 for r in rows if r[2] == "Vitória")
        win_rate_perc = (total_wins / total_games) * 100

        villain_stats = defaultdict(lambda: [0, 0])
        teammate_stats = defaultdict(lambda: 0)
        env_counts = defaultdict(lambda: 0)
        all_winrates = []

        for v_str, env, res, h_str, g_type in rows:
            win = 1 if res == "Vitória" else 0
            v_list = v_str.split(",") if g_type == "TEAM" else [v_str]
            for v in v_list: villain_stats[v][0] += win; villain_stats[v][1] += 1
            for h in h_str.split(","):
                if h != target_hero: teammate_stats[h] += 1
            env_counts[env] += 1
            all_winrates.append(win)

        valid_vs = [x for x in villain_stats.items() if x[1][1] >= 1] 
        if valid_vs:
            sorted_vs = sorted(valid_vs, key=lambda x: (x[1][0]/x[1][1], x[1][1]), reverse=True)
            i1 = f"{sorted_vs[0][0]} ({(sorted_vs[0][1][0]/sorted_vs[0][1][1])*100:.0f}%)"
            i2 = f"{sorted_vs[-1][0]} ({(sorted_vs[-1][1][0]/sorted_vs[-1][1][1])*100:.0f}%)"
        else: i1 = i2 = "Dados insuficientes."

        i3 = f"{max(teammate_stats.items(), key=lambda x: x[1])[0]}" if teammate_stats else "-"
        i4 = f"{max(env_counts.items(), key=lambda x: x[1])[0]}" if env_counts else "-"
        
        if len(all_winrates) >= 2: 
            mean = sum(all_winrates)/len(all_winrates)
            std_dev = math.sqrt(sum([(x-mean)**2 for x in all_winrates])/len(all_winrates))
            i5 = f"DP: {std_dev:.3f}"
        else: i5 = "Min 2 jogos."

        return [total_games, win_rate_perc, i1, i2, i3, i4, i5]

    def save_game(self):
        mode = self.seg_gamemode.get()
        g_type = "SOLO" if mode == "Solo" else "TEAM"
        env = self.combo_env.get()
        res = self.seg_result.get()
        
        if g_type == "SOLO":
            v = self.combo_solo_name.get()
            m = self.combo_solo_mode.get()
            v_str = v if m == "Normal" else f"{v} ({m})"
        else:
            lst = [c.get() for c in self.team_villain_combos if c.get() != "(Nenhum)"]
            if len(lst) < 3: return messagebox.showwarning("Erro", "Min 3 vilões.")
            if len(lst) != len(set(lst)): return messagebox.showwarning("Erro", "Vilão duplicado.")
            v_str = ",".join(lst)

        h_list = []
        for s in self.hero_selectors:
            x = s.get_selection()
            if x: h_list.append(x)
        if len(h_list) < 3: return messagebox.showwarning("Erro", "Min 3 heróis.")
        
        if len(set([h.split(" (")[0] for h in h_list])) != len(h_list):
            return messagebox.showerror("Erro", "Herói duplicado.")

        try:
            conn = sqlite3.connect('sentinels_history.db')
            c = conn.cursor()
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO games (date, villain, environment, result, heroes, game_type) VALUES (?, ?, ?, ?, ?, ?)",
                      (dt, v_str, env, res, ",".join(h_list), g_type))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Salvo!")
            for s in self.hero_selectors: s.reset()
            for c in self.team_villain_combos: c.set("(Nenhum)")
            self.refresh_all_data()
        except Exception as e: messagebox.showerror("Erro", str(e))

    def refresh_all_data(self):
        self.calculate_overview()
        self.calculate_details()
        self.display_hero_insights()

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
        
        h_stats = defaultdict(lambda: [0, 0])
        v_stats = defaultdict(lambda: [0, 0])
        e_stats = defaultdict(lambda: [0, 0])

        for v_s, e, r, h_s, g_t in rows:
            w = 1 if r == "Vitória" else 0
            for h in h_s.split(","): h_stats[h][0]+=w; h_stats[h][1]+=1
            e_stats[e][0]+=w; e_stats[e][1]+=1
            v_lst = v_s.split(",") if g_t == "TEAM" else [v_s]
            for v in v_lst: v_stats[v][0]+=w; v_stats[v][1]+=1

        def fmt(lst, wr=False):
            txt = ""
            for i, (n, d) in enumerate(lst):
                if wr: txt += f"{i+1}. {n} ({d[0]/d[1]*100:.0f}%)\n"
                else: txt += f"{i+1}. {n} ({d[1]})\n"
            return txt

        top_h = sorted(h_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        self.card_hero_played.configure(text=fmt(top_h))
        
        valid_h = [x for x in h_stats.items() if x[1][1]>=3]
        best_h = sorted(valid_h, key=lambda x: (x[1][0]/x[1][1], x[1][1]), reverse=True)[:5]
        worst_h = sorted(valid_h, key=lambda x: (x[1][0]/x[1][1], x[1][1]))[:5]
        
        self.card_hero_best.configure(text=fmt(best_h, True))
        self.card_hero_worst.configure(text=fmt(worst_h, True))

        top_v = sorted(v_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        self.card_villain_played.configure(text=fmt(top_v))

        valid_v = [x for x in v_stats.items() if x[1][1]>=3]
        hard_v = sorted(valid_v, key=lambda x: (x[1][0]/x[1][1], x[1][1]))[:5]
        self.card_villain_hardest.configure(text=fmt(hard_v, True))

        top_e = sorted(e_stats.items(), key=lambda x: x[1][1], reverse=True)[:5]
        self.card_env_played.configure(text=fmt(top_e))

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
            for k, val in l: t+=f"{val[0]/val[1]*100:5.0f}% ({val[0]}/{val[1]}) {k}\n"
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