import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict

# --- CONFIGURAÇÃO VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- FONTES ---
FONT_BIG_NUMBER = ("Roboto", 40, "bold")
FONT_HEADER = ("Roboto Medium", 16)
FONT_CARD_TITLE = ("Roboto", 12, "bold")
FONT_NORMAL = ("Roboto", 12)
FONT_MONO = ("Consolas", 12)

# --- DADOS (Mantidos) ---
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
        self.title("Sentinels Multiverse Tracker v7.0")
        self.geometry("1280x800")
        
        self.main_container = ctk.CTkTabview(self, corner_radius=15)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_reg = self.main_container.add("  REGISTRAR  ")
        self.tab_overview = self.main_container.add("  VISÃO GERAL  ") # NOVA ABA
        self.tab_stats = self.main_container.add("  DETALHES  ")

        self.setup_register_tab()
        self.setup_overview_tab()
        self.setup_stats_tab()

    # ================= 1. ABA REGISTRAR =================
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

    # ================= 2. ABA VISÃO GERAL (NOVA) =================
    def setup_overview_tab(self):
        # Topo: Total de Jogos
        self.frame_total = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.frame_total.pack(fill="x", pady=20)
        
        ctk.CTkLabel(self.frame_total, text="TOTAL DE PARTIDAS", font=("Roboto", 16, "bold"), text_color="gray").pack()
        self.lbl_total_games = ctk.CTkLabel(self.frame_total, text="0", font=FONT_BIG_NUMBER, text_color="#2CC985")
        self.lbl_total_games.pack()
        
        ctk.CTkButton(self.frame_total, text="Atualizar Dados", command=self.refresh_all_data, 
                      height=25, width=100, fg_color="#333").pack(pady=5)

        # Grid para os Top 5
        self.grid_overview = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        self.grid_overview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 3 colunas, 2 linhas
        for i in range(3): self.grid_overview.grid_columnconfigure(i, weight=1)
        for i in range(2): self.grid_overview.grid_rowconfigure(i, weight=1)

        # Criação dos Cards
        self.card_hero_played = self.create_stat_card(0, 0, "Heróis Mais Jogados")
        self.card_hero_best = self.create_stat_card(0, 1, "Melhores Heróis (Winrate)", color="#1a4d1a") # Verde escuro
        self.card_hero_worst = self.create_stat_card(0, 2, "Piores Heróis (Winrate)", color="#4d1a1a") # Vermelho escuro
        
        self.card_villain_played = self.create_stat_card(1, 0, "Vilões Favoritos")
        self.card_villain_hardest = self.create_stat_card(1, 1, "Vilões Mais Difíceis", color="#4d1a1a")
        self.card_env_played = self.create_stat_card(1, 2, "Ambientes Mais Jogados")

        #self.refresh_all_data()

    def create_stat_card(self, row, col, title, color="#2b2b2b"):
        frame = ctk.CTkFrame(self.grid_overview, fg_color=color, corner_radius=10, border_width=1, border_color="#3a3a3a")
        frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        
        ctk.CTkLabel(frame, text=title, font=("Roboto", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkFrame(frame, height=2, fg_color="#555").pack(fill="x", padx=10, pady=(0,5))
        
        lbl_content = ctk.CTkLabel(frame, text="...", font=FONT_MONO, justify="left")
        lbl_content.pack(expand=True, padx=10, pady=5)
        return lbl_content

    # ================= 3. ABA DETALHES =================
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

    # ================= LOGICA =================
    def toggle_villain_mode(self, mode):
        self.frame_solo.pack_forget()
        self.frame_team.pack_forget()
        if mode == "Solo": self.frame_solo.pack(fill="x")
        else: self.frame_team.pack(fill="x")

    def update_solo_modes(self, choice):
        modes = SOLO_VILLAINS_DATA.get(choice, ["Normal"])
        self.combo_solo_mode.configure(values=modes)
        self.combo_solo_mode.set("Normal")

    def save_game(self):
        mode_label = self.seg_gamemode.get()
        game_type = "SOLO" if mode_label == "Solo" else "TEAM"
        env = self.combo_env.get()
        result = self.seg_result.get()

        villain_str = ""
        if game_type == "SOLO":
            v_name = self.combo_solo_name.get()
            v_mode = self.combo_solo_mode.get()
            villain_str = v_name if v_mode == "Normal" else f"{v_name} ({v_mode})"
        else:
            team_list = [c.get() for c in self.team_villain_combos if c.get() != "(Nenhum)"]
            if len(team_list) < 3:
                messagebox.showwarning("Erro", "Times de vilões precisam de pelo menos 3 vilões!")
                return
            if len(team_list) != len(set(team_list)):
                messagebox.showwarning("Erro", "Vilão duplicado no time!")
                return
            villain_str = ",".join(team_list)

        hero_list = []
        for sel in self.hero_selectors:
            val = sel.get_selection()
            if val: hero_list.append(val)
        
        if len(hero_list) < 3:
            messagebox.showwarning("Erro", "Selecione pelo menos 3 heróis!")
            return

        bases = set()
        for h in hero_list:
            b = h.split(" (")[0]
            if b in bases:
                messagebox.showerror("Regra do Multiverso", f"O herói '{b}' já está na mesa!")
                return
            bases.add(b)

        try:
            conn = sqlite3.connect('sentinels_history.db')
            c = conn.cursor()
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO games (date, villain, environment, result, heroes, game_type) VALUES (?, ?, ?, ?, ?, ?)",
                      (date_str, villain_str, env, result, ",".join(hero_list), game_type))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Partida registrada!")
            
            for sel in self.hero_selectors: sel.reset()
            for c in self.team_villain_combos: c.set("(Nenhum)")
            
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def refresh_all_data(self):
        self.calculate_overview()
        self.calculate_details()

    def calculate_overview(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes, game_type FROM games")
        rows = c.fetchall()
        conn.close()

        self.lbl_total_games.configure(text=str(len(rows)))

        if not rows: return

        # Contadores Gerais
        hero_stats = defaultdict(lambda: [0, 0]) # [Wins, Total]
        villain_stats = defaultdict(lambda: [0, 0])
        env_stats = defaultdict(lambda: [0, 0])

        for v_str, env, res, h_str, g_type in rows:
            win = 1 if res == "Vitória" else 0
            
            # Heróis
            for h in h_str.split(","):
                hero_stats[h][0] += win
                hero_stats[h][1] += 1
            
            # Ambiente
            env_stats[env][0] += win
            env_stats[env][1] += 1
            
            # Vilões (Separa se for time, mantem junto se for solo)
            if g_type == "TEAM":
                for v in v_str.split(","):
                    villain_stats[v][0] += win
                    villain_stats[v][1] += 1
            else:
                villain_stats[v_str][0] += win
                villain_stats[v_str][1] += 1

        # Funções de Ordenação
        def get_top_played(stats, limit=5):
            # Ordena por Total de Jogos (desc)
            sorted_items = sorted(stats.items(), key=lambda x: x[1][1], reverse=True)[:limit]
            return sorted_items

        def get_winrate(stats, reverse=True, limit=5, min_games=3):
            # Filtra min_games, Calcula %, Ordena por % e depois por Total Jogos
            valid_items = [x for x in stats.items() if x[1][1] >= min_games]
            sorted_items = sorted(valid_items, key=lambda x: ((x[1][0]/x[1][1]), x[1][1]), reverse=reverse)[:limit]
            return sorted_items

        def fmt_list(items, show_wr=False):
            txt = ""
            for idx, (name, val) in enumerate(items):
                if show_wr:
                    pct = (val[0]/val[1])*100
                    txt += f"{idx+1}. {name}\n   {pct:.1f}% ({val[0]}/{val[1]})\n"
                else:
                    txt += f"{idx+1}. {name} ({val[1]})\n"
            return txt if txt else "(Poucos dados)"

        # Preenche os cards
        self.card_hero_played.configure(text=fmt_list(get_top_played(hero_stats)))
        self.card_hero_best.configure(text=fmt_list(get_winrate(hero_stats, reverse=True), show_wr=True))
        self.card_hero_worst.configure(text=fmt_list(get_winrate(hero_stats, reverse=False), show_wr=True))
        
        self.card_villain_played.configure(text=fmt_list(get_top_played(villain_stats)))
        self.card_villain_hardest.configure(text=fmt_list(get_winrate(villain_stats, reverse=False), show_wr=True)) # Menor winrate = Mais difícil
        
        self.card_env_played.configure(text=fmt_list(get_top_played(env_stats)))


    def calculate_details(self):
        current_mode_label = self.seg_stats_mode.get()
        db_type = "SOLO" if current_mode_label == "Stats Solo" else "TEAM"

        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes FROM games WHERE game_type=?", (db_type,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            for lbl in [self.lbl_stats_v, self.lbl_stats_e, self.lbl_stats_s, self.lbl_stats_h]:
                lbl.configure(text="Sem registros.")
            return

        stats_v = defaultdict(lambda: [0, 0])
        stats_e = defaultdict(lambda: [0, 0])
        stats_h = defaultdict(lambda: [0, 0])
        stats_s = defaultdict(lambda: [0, 0])

        for v_str, env, res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            
            if db_type == "SOLO":
                stats_v[v_str][0] += win; stats_v[v_str][1] += 1
            else:
                for m in v_str.split(","):
                    stats_v[m][0] += win; stats_v[m][1] += 1

            stats_e[env][0] += win; stats_e[env][1] += 1
            h_list = h_str.split(",")
            for h in h_list:
                stats_h[h][0] += win; stats_h[h][1] += 1
            stats_s[len(h_list)][0] += win; stats_s[len(h_list)][1] += 1

        def fmt(d, sort_key=False):
            items = sorted(d.items(), key=lambda x: x[0] if sort_key else x[1][1], reverse=not sort_key)
            txt = ""
            for k, v in items:
                prefix = f"{k} Heróis" if isinstance(k, int) else k
                pct = (v[0]/v[1])*100
                txt += f"{pct:5.1f}%  ({v[0]}/{v[1]})  {prefix}\n" + "─"*30 + "\n"
            return txt

        self.lbl_stats_v.configure(text=fmt(stats_v))
        self.lbl_stats_e.configure(text=fmt(stats_e))
        self.lbl_stats_h.configure(text=fmt(stats_h))
        self.lbl_stats_s.configure(text=fmt(stats_s, True))

if __name__ == "__main__":
    try:
        init_db()
        app = TrackerApp()
        app.mainloop()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Erro Fatal", str(e))