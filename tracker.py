import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict

# --- Configuração Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- LISTA EXPANDIDA DE HERÓIS ---
# A lógica de "Personagem Único" pega tudo antes do primeiro " ("
HEROIS = [
    # Freedom Five & Core
    "Legacy", "Legacy (America's Greatest)", "Legacy (Young)", "Legacy (Freedom Five)",
    "Bunker", "Bunker (G.I.)", "Bunker (Freedom Five)", "Bunker (Termi-Nation)",
    "Wraith", "Wraith (Rook City)", "Wraith (Freedom Five)", "Wraith (Price of Freedom)",
    "Tachyon", "Tachyon (Super Scientific)", "Tachyon (Freedom Five)", "Tachyon (Team Leader)",
    "Absolute Zero", "Absolute Zero (Elemental)", "Absolute Zero (Freedom Five)", "Absolute Zero (Termi-Nation)",
    "Unity", "Unity (Termi-Nation)", "Unity (Golem)",
    
    # Prime Wardens
    "Haka", "Haka (Eternal)", "Haka (Prime Wardens)",
    "Fanatic", "Fanatic (Redeemer)", "Fanatic (Prime Wardens)", "Fanatic (Haunted)",
    "Tempest", "Tempest (Prime Wardens)", "Tempest (Freedom Six)",
    "Argent Adept", "Argent Adept (Dark Conductor)", "Argent Adept (Prime Wardens)",
    "Captain Cosmic", "Captain Cosmic (Prime Wardens)", "Captain Cosmic (Requiem)",

    # Dark Watch
    "Expatriette", "Expatriette (Dark Watch)",
    "Setback", "Setback (Dark Watch)",
    "NightMist", "NightMist (Dark Watch)",
    "Mr. Fixer", "Mr. Fixer (Dark Watch)",
    "The Harpy", "The Harpy (Dark Watch)", # (Se estiver jogando DE ou expansões novas)

    # Outros
    "Ra", "Ra (Setting Sun)", "Ra (Horus)",
    "Visionary", "Visionary (Dark)", "Visionary (Unleashed)",
    "Chrono-Ranger", "Chrono-Ranger (Best of Times)",
    "Omnitron-X", "Omnitron-U",
    "Sky-Scraper", "Sky-Scraper (Extremist)",
    "K.N.Y.F.E.", "K.N.Y.F.E. (Rogue Agent)",
    "Parse", "Parse (Fugue State)",
    "The Naturalist", "The Naturalist (Hunted)",
    "Sentinels", "Sentinels (Adamant)", # (O time conta como 1 herói na seleção)
    "Guise", "Guise (Santa)",
    "Stuntman", "Benchmark", "La Comodora", "Lifeline", "Akash'Thriya", "Luminary"
]
HEROIS.sort()

VILOES = [
    "Baron Blade", "Citizen Dawn", "Grand Warlord Voss", "Omnitron", 
    "Spite", "The Chairman", "Akash'Bhuta", "GloomWeaver", "The Matriarch", 
    "Plague Rat", "Ennead", "Apostate", "Iron Legacy", "Kismet", "La Capitan", 
    "Dreamer", "Kaargra Warfang", "Progeny", "Deadline", "Infinitor", "OblivAeon"
]
VILOES.sort()

AMBIENTES = [
    "Megalopolis", "Insula Primalis", "Ruins of Atlantis", 
    "Wagner Mars Base", "Rook City", "Pike Industrial Complex",
    "Tomb of Anubis", "Realm of Discord", "Nexus of the Void", "The Block",
    "Time Cataclysm", "Silver Gulch", "Final Wasteland", "Omnitron-IV",
    "Celestial Tribunal", "Magmaria", "Freedom Tower", "Mobile Defense Platform"
]
AMBIENTES.sort()

# --- Banco de Dados ---
def init_db():
    conn = sqlite3.connect('sentinels_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  villain TEXT,
                  environment TEXT,
                  result TEXT,
                  heroes TEXT)''')
    conn.commit()
    conn.close()

# --- App Principal ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sentinels Tracker - v3.0 (Team Size)")
        self.geometry("1100x700") # Aumentei um pouco a largura

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_reg = self.tabview.add("Registrar Partida")
        self.tab_stats = self.tabview.add("Estatísticas")

        self.setup_register_tab()
        self.setup_stats_tab()

    def setup_register_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_reg, label_text="Dados da Partida")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="Vilão:").pack(pady=(10, 0))
        self.combo_vilao = ctk.CTkComboBox(scroll, values=VILOES, width=300)
        self.combo_vilao.pack(pady=5)

        ctk.CTkLabel(scroll, text="Ambiente:").pack(pady=(10, 0))
        self.combo_env = ctk.CTkComboBox(scroll, values=AMBIENTES, width=300)
        self.combo_env.pack(pady=5)

        ctk.CTkLabel(scroll, text="Resultado:").pack(pady=(10, 0))
        self.seg_result = ctk.CTkSegmentedButton(scroll, values=["Vitória", "Derrota"])
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=5)

        ctk.CTkLabel(scroll, text="Equipe de Heróis:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.hero_selectors = []
        for i in range(5):
            combo = ctk.CTkComboBox(scroll, values=["(Nenhum)"] + HEROIS, width=300)
            combo.pack(pady=2)
            self.hero_selectors.append(combo)

        btn = ctk.CTkButton(scroll, text="SALVAR PARTIDA", command=self.save_game, fg_color="green", height=40)
        btn.pack(pady=30)

    def setup_stats_tab(self):
        self.btn_refresh = ctk.CTkButton(self.tab_stats, text="Atualizar Dados", command=self.calculate_stats)
        self.btn_refresh.pack(pady=10)

        # Agora com 4 colunas!
        self.stats_frame = ctk.CTkFrame(self.tab_stats)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1)
            self.stats_frame.grid_rowconfigure(0, weight=1)

        # 1. Vilões
        self.frame_v = ctk.CTkScrollableFrame(self.stats_frame, label_text="Vs Vilões")
        self.frame_v.grid(row=0, column=0, sticky="nsew", padx=2)
        self.lbl_stats_v = ctk.CTkLabel(self.frame_v, text="", justify="left")
        self.lbl_stats_v.pack(anchor="w", padx=5)

        # 2. Ambientes
        self.frame_e = ctk.CTkScrollableFrame(self.stats_frame, label_text="Em Ambientes")
        self.frame_e.grid(row=0, column=1, sticky="nsew", padx=2)
        self.lbl_stats_e = ctk.CTkLabel(self.frame_e, text="", justify="left")
        self.lbl_stats_e.pack(anchor="w", padx=5)

        # 3. Tamanho do Time (NOVO)
        self.frame_s = ctk.CTkScrollableFrame(self.stats_frame, label_text="Por Tamanho de Time")
        self.frame_s.grid(row=0, column=2, sticky="nsew", padx=2)
        self.lbl_stats_s = ctk.CTkLabel(self.frame_s, text="", justify="left")
        self.lbl_stats_s.pack(anchor="w", padx=5)

        # 4. Heróis
        self.frame_h = ctk.CTkScrollableFrame(self.stats_frame, label_text="Por Herói")
        self.frame_h.grid(row=0, column=3, sticky="nsew", padx=2)
        self.lbl_stats_h = ctk.CTkLabel(self.frame_h, text="", justify="left")
        self.lbl_stats_h.pack(anchor="w", padx=5)
        
        self.calculate_stats()

    def save_game(self):
        villain = self.combo_vilao.get()
        env = self.combo_env.get()
        result = self.seg_result.get()
        
        selected_heroes = [s.get() for s in self.hero_selectors if s.get() != "(Nenhum)"]
        
        if len(selected_heroes) < 3:
            messagebox.showwarning("Erro", "Selecione pelo menos 3 heróis!")
            return

        # Validação de Personagem Único
        personagens_base = set()
        for h in selected_heroes:
            base = h.split(" (")[0]
            if base in personagens_base:
                messagebox.showerror("Erro", f"Conflito: '{base}' já está no time!")
                return
            personagens_base.add(base)

        heroes_str = ",".join(selected_heroes)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO games (date, villain, environment, result, heroes) VALUES (?, ?, ?, ?, ?)",
                  (date_str, villain, env, result, heroes_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Partida salva!")
        for s in self.hero_selectors: s.set("(Nenhum)")
        self.calculate_stats()

    def calculate_stats(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes FROM games")
        rows = c.fetchall()
        conn.close()

        if not rows:
            return

        stats_villain = defaultdict(lambda: [0, 0])
        stats_env = defaultdict(lambda: [0, 0])
        stats_hero = defaultdict(lambda: [0, 0])
        stats_size = defaultdict(lambda: [0, 0]) # Novo dicionário para o tamanho do time

        for v, e, res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            
            # Vilão e Ambiente
            stats_villain[v][0] += win; stats_villain[v][1] += 1
            stats_env[e][0] += win; stats_env[e][1] += 1
            
            # Heróis
            heroes_list = h_str.split(",")
            for hero in heroes_list:
                stats_hero[hero][0] += win; stats_hero[hero][1] += 1
            
            # Tamanho do Time (Lógica Nova)
            team_size = len(heroes_list)
            stats_size[team_size][0] += win
            stats_size[team_size][1] += 1

        def format_text(stats_dict, sort_by_key=False):
            # sort_by_key=True ordena por nome/número (útil para tamanho do time: 3, 4, 5)
            # sort_by_key=False ordena por quem tem mais partidas
            if sort_by_key:
                items = sorted(stats_dict.items(), key=lambda x: x[0])
            else:
                items = sorted(stats_dict.items(), key=lambda x: x[1][1], reverse=True)
                
            text = ""
            for nome, dados in items:
                wins, total = dados
                pct = (wins / total) * 100
                # Ex: 3 Heróis: 66% (2/3)
                prefixo = f"{nome} Heróis" if isinstance(nome, int) else nome
                text += f"{prefixo}\n  WR: {pct:.1f}% ({wins}/{total})\n\n"
            return text

        self.lbl_stats_v.configure(text=format_text(stats_villain))
        self.lbl_stats_e.configure(text=format_text(stats_env))
        self.lbl_stats_h.configure(text=format_text(stats_hero))
        
        # Atualiza a coluna de tamanho de time (ordenando por número: 3, 4, 5)
        self.lbl_stats_s.configure(text=format_text(stats_size, sort_by_key=True))

if __name__ == "__main__":
    init_db()
    app = TrackerApp()
    app.mainloop()