import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict

# --- Configuração Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- DADOS DOS HERÓIS (COM VARIANTES) ---
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

# --- DADOS DOS VILÕES SOLO ---
MODOS_VILAO = ["Normal", "Advanced", "Challenge", "Ultimate"]
SOLO_VILLAINS_DATA = {
    "Baron Blade": MODOS_VILAO,
    "Citizen Dawn": MODOS_VILAO,
    "Grand Warlord Voss": MODOS_VILAO,
    "Omnitron": MODOS_VILAO,
    "Spite": MODOS_VILAO,
    "The Chairman": MODOS_VILAO,
    "Akash'Bhuta": MODOS_VILAO,
    "GloomWeaver": MODOS_VILAO + ["Skinwalker"],
    "The Matriarch": MODOS_VILAO,
    "Plague Rat": MODOS_VILAO,
    "Ennead": MODOS_VILAO,
    "Apostate": MODOS_VILAO,
    "Iron Legacy": MODOS_VILAO,
    "Kismet": MODOS_VILAO,
    "La Capitan": MODOS_VILAO,
    "Dreamer": MODOS_VILAO,
    "Kaargra Warfang": MODOS_VILAO,
    "Progeny": MODOS_VILAO,
    "Deadline": MODOS_VILAO,
    "Infinitor": MODOS_VILAO,
    "OblivAeon": ["Normal", "Advanced"]
}

# --- DADOS DOS VILÕES DE TIME (Vengeance / Villains of the Multiverse) ---
# Estes são contabilizados separadamente
TEAM_VILLAINS_LIST = [
    "Baron Blade", "Friction", "Fright Train", "Proletariat", "Ermine", # Vengeful Five
    "Vander", "Dr. Tremata", "Marcato", "Honored Maidens", "Pariah", # Vengeance Others
    "Ambuscade", "Biomancer", "Bugbear", "Citizen Hammer", "Greazer", 
    "La Capitan", "Miss Information", "Plague Rat", "Sergeant Steel", "The Operative" # Villains of Multiverse
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

# --- BANCO DE DADOS COM MIGRAÇÃO ---
def init_db():
    conn = sqlite3.connect('sentinels_history.db')
    c = conn.cursor()
    
    # Cria a tabela base se não existir
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  villain TEXT,
                  environment TEXT,
                  result TEXT,
                  heroes TEXT,
                  game_type TEXT DEFAULT 'SOLO')''')
    
    # Migração: Verifica se a coluna game_type existe (para quem já rodou o código antigo)
    c.execute("PRAGMA table_info(games)")
    columns = [info[1] for info in c.fetchall()]
    if 'game_type' not in columns:
        try:
            c.execute("ALTER TABLE games ADD COLUMN game_type TEXT DEFAULT 'SOLO'")
            print("Banco de dados atualizado: Coluna game_type adicionada.")
        except Exception as e:
            print(f"Erro na migração: {e}")

    conn.commit()
    conn.close()

# --- WIDGET SELETOR DE HERÓI (Reutilizável) ---
class HeroSelector(ctk.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(self, text=label_text, width=60, anchor="w")
        self.label.grid(row=0, column=0, padx=5)
        
        names = ["(Nenhum)"] + sorted(list(HEROES_DATA.keys()))
        self.hero_combo = ctk.CTkComboBox(self, values=names, command=self.update_variants, width=200)
        self.hero_combo.grid(row=0, column=1, padx=5)
        
        self.variant_combo = ctk.CTkComboBox(self, values=["-"], width=150, state="disabled")
        self.variant_combo.grid(row=0, column=2, padx=5)

    def update_variants(self, choice):
        if choice == "(Nenhum)":
            self.variant_combo.configure(values=["-"], state="disabled")
            self.variant_combo.set("-")
        else:
            variants = HEROES_DATA.get(choice, ["Base"])
            self.variant_combo.configure(values=variants, state="normal")
            self.variant_combo.set("Base")

    def get_selection(self):
        h = self.hero_combo.get()
        v = self.variant_combo.get()
        if h == "(Nenhum)": return None
        return h if v == "Base" else f"{h} ({v})"
    
    def reset(self):
        self.hero_combo.set("(Nenhum)")
        self.update_variants("(Nenhum)")

# --- APP PRINCIPAL ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Tracker - v5.0 (Villain Teams)")
        self.geometry("1100x800")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tab_reg = self.tabview.add("Registrar Partida")
        self.tab_stats = self.tabview.add("Estatísticas")

        self.setup_register_tab()
        self.setup_stats_tab()

    # ================= ABA REGISTRO =================
    def setup_register_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_reg, label_text="Nova Partida")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Escolha do Modo de Jogo
        ctk.CTkLabel(scroll, text="Tipo de Jogo:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.seg_gamemode = ctk.CTkSegmentedButton(scroll, values=["Solo", "Time de Vilões"], command=self.toggle_villain_mode)
        self.seg_gamemode.set("Solo")
        self.seg_gamemode.pack(pady=5)

        # 2. Frames dos Vilões (Um para Solo, Um para Time)
        
        # --- FRAME SOLO ---
        self.frame_solo = ctk.CTkFrame(scroll, fg_color="transparent")
        ctk.CTkLabel(self.frame_solo, text="Vilão:", width=60, anchor="w").grid(row=0, column=0, padx=5)
        self.combo_solo_name = ctk.CTkComboBox(self.frame_solo, values=sorted(list(SOLO_VILLAINS_DATA.keys())), 
                                               command=self.update_solo_modes, width=200)
        self.combo_solo_name.grid(row=0, column=1, padx=5)
        self.combo_solo_mode = ctk.CTkComboBox(self.frame_solo, values=["Normal"], width=150)
        self.combo_solo_mode.grid(row=0, column=2, padx=5)
        self.update_solo_modes(self.combo_solo_name.get())
        
        # --- FRAME TIME ---
        self.frame_team = ctk.CTkFrame(scroll, fg_color="transparent")
        ctk.CTkLabel(self.frame_team, text="Membros do Time de Vilões (3 a 5):", font=ctk.CTkFont(weight="bold")).pack(pady=(0,5))
        self.team_villain_combos = []
        for i in range(5):
            lbl = ctk.CTkLabel(self.frame_team, text=f"Vilão {i+1}:")
            lbl.pack(anchor="w", padx=20)
            combo = ctk.CTkComboBox(self.frame_team, values=["(Nenhum)"] + TEAM_VILLAINS_LIST, width=300)
            combo.pack(anchor="w", padx=20, pady=2)
            self.team_villain_combos.append(combo)

        # Inicializa mostrando o Solo
        self.frame_solo.pack(pady=10, anchor="center")

        # 3. Ambiente
        ctk.CTkLabel(scroll, text="Ambiente:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.combo_env = ctk.CTkComboBox(scroll, values=AMBIENTES, width=300)
        self.combo_env.pack(pady=5)

        # 4. Resultado
        ctk.CTkLabel(scroll, text="Resultado:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.seg_result = ctk.CTkSegmentedButton(scroll, values=["Vitória", "Derrota"])
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=5)

        # 5. Heróis
        ctk.CTkLabel(scroll, text="Equipe de Heróis:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        self.hero_selectors = []
        for i in range(5):
            sel = HeroSelector(scroll, f"Herói {i+1}:")
            sel.pack(pady=2)
            self.hero_selectors.append(sel)

        # Botão Salvar
        ctk.CTkButton(scroll, text="SALVAR PARTIDA", command=self.save_game, fg_color="green", height=40).pack(pady=30)

    def toggle_villain_mode(self, mode):
        # Esconde ambos e mostra só o selecionado
        self.frame_solo.pack_forget()
        self.frame_team.pack_forget()
        
        if mode == "Solo":
            self.frame_solo.pack(pady=10)
        else:
            self.frame_team.pack(pady=10)

    def update_solo_modes(self, choice):
        modes = SOLO_VILLAINS_DATA.get(choice, ["Normal"])
        self.combo_solo_mode.configure(values=modes)
        self.combo_solo_mode.set("Normal")

    # ================= ABA STATS =================
    def setup_stats_tab(self):
        # Filtro de Stats
        top_frame = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(top_frame, text="Atualizar", command=self.calculate_stats, width=100).pack(side="right", padx=10)
        
        self.seg_stats_mode = ctk.CTkSegmentedButton(top_frame, values=["Stats Solo", "Stats Time"], command=lambda x: self.calculate_stats())
        self.seg_stats_mode.set("Stats Solo")
        self.seg_stats_mode.pack(side="left", padx=10)

        # Grid de Colunas
        self.stats_frame = ctk.CTkFrame(self.tab_stats)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1)
            self.stats_frame.grid_rowconfigure(0, weight=1)

        self.frame_v = ctk.CTkScrollableFrame(self.stats_frame, label_text="Vs Vilões")
        self.frame_v.grid(row=0, column=0, sticky="nsew", padx=2)
        self.lbl_stats_v = ctk.CTkLabel(self.frame_v, text="", justify="left")
        self.lbl_stats_v.pack(anchor="w", padx=5)

        self.frame_e = ctk.CTkScrollableFrame(self.stats_frame, label_text="Em Ambientes")
        self.frame_e.grid(row=0, column=1, sticky="nsew", padx=2)
        self.lbl_stats_e = ctk.CTkLabel(self.frame_e, text="", justify="left")
        self.lbl_stats_e.pack(anchor="w", padx=5)

        self.frame_s = ctk.CTkScrollableFrame(self.stats_frame, label_text="Por Tamanho de Time")
        self.frame_s.grid(row=0, column=2, sticky="nsew", padx=2)
        self.lbl_stats_s = ctk.CTkLabel(self.frame_s, text="", justify="left")
        self.lbl_stats_s.pack(anchor="w", padx=5)

        self.frame_h = ctk.CTkScrollableFrame(self.stats_frame, label_text="Por Herói")
        self.frame_h.grid(row=0, column=3, sticky="nsew", padx=2)
        self.lbl_stats_h = ctk.CTkLabel(self.frame_h, text="", justify="left")
        self.lbl_stats_h.pack(anchor="w", padx=5)
        
        self.calculate_stats()

    # ================= LÓGICA DE SALVAMENTO =================
    def save_game(self):
        mode_label = self.seg_gamemode.get()
        game_type = "SOLO" if mode_label == "Solo" else "TEAM"
        env = self.combo_env.get()
        result = self.seg_result.get()

        # 1. Captura Vilão(ões)
        villain_str = ""
        if game_type == "SOLO":
            v_name = self.combo_solo_name.get()
            v_mode = self.combo_solo_mode.get()
            villain_str = v_name if v_mode == "Normal" else f"{v_name} ({v_mode})"
        else:
            # Time de Vilões: Pega todos os selecionados
            team_list = [c.get() for c in self.team_villain_combos if c.get() != "(Nenhum)"]
            if len(team_list) < 3:
                messagebox.showwarning("Erro", "Times de vilões precisam de pelo menos 3 vilões!")
                return
            
            # Checa duplicatas no time de vilões (ex: 2 Baron Blades)
            if len(team_list) != len(set(team_list)):
                messagebox.showwarning("Erro", "Você selecionou o mesmo vilão duas vezes!")
                return
            villain_str = ",".join(team_list)

        # 2. Captura Heróis
        hero_list = []
        for sel in self.hero_selectors:
            val = sel.get_selection()
            if val: hero_list.append(val)
        
        if len(hero_list) < 3:
            messagebox.showwarning("Erro", "Selecione pelo menos 3 heróis!")
            return

        # 3. Validação Regra do Multiverso (Heróis)
        bases = set()
        for h in hero_list:
            b = h.split(" (")[0]
            if b in bases:
                messagebox.showerror("Conflito", f"O herói '{b}' já está no time!")
                return
            bases.add(b)

        # 4. Salvar no Banco
        try:
            conn = sqlite3.connect('sentinels_history.db')
            c = conn.cursor()
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("""
                INSERT INTO games (date, villain, environment, result, heroes, game_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, villain_str, env, result, ",".join(hero_list), game_type))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", f"Partida {game_type} salva com sucesso!")
            
            # Limpa formulário
            for sel in self.hero_selectors: sel.reset()
            for c in self.team_villain_combos: c.set("(Nenhum)")
            self.calculate_stats()
            
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e))

    # ================= LÓGICA DE ESTATÍSTICAS =================
    def calculate_stats(self):
        current_mode_label = self.seg_stats_mode.get() # "Stats Solo" ou "Stats Time"
        db_type = "SOLO" if current_mode_label == "Stats Solo" else "TEAM"

        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        # Filtra pelo game_type!
        c.execute("SELECT villain, environment, result, heroes FROM games WHERE game_type=?", (db_type,))
        rows = c.fetchall()
        conn.close()

        # Reseta labels se não tiver dados
        if not rows:
            msg = "Sem dados."
            self.lbl_stats_v.configure(text=msg); self.lbl_stats_e.configure(text=msg)
            self.lbl_stats_s.configure(text=msg); self.lbl_stats_h.configure(text=msg)
            return

        stats_v = defaultdict(lambda: [0, 0])
        stats_e = defaultdict(lambda: [0, 0])
        stats_h = defaultdict(lambda: [0, 0])
        stats_s = defaultdict(lambda: [0, 0])

        for v_str, env, res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            
            # Estatística de Vilão
            if db_type == "SOLO":
                # No Solo, v_str é o nome único (ex: "Baron Blade")
                stats_v[v_str][0] += win
                stats_v[v_str][1] += 1
            else:
                # No Time, v_str é uma lista (ex: "Baron Blade,Friction,Proletariat")
                # Vamos contar winrate INDIVIDUAL contra cada membro do time
                members = v_str.split(",")
                for m in members:
                    stats_v[m][0] += win
                    stats_v[m][1] += 1

            # Ambiente
            stats_e[env][0] += win; stats_e[env][1] += 1
            
            # Heróis
            h_list = h_str.split(",")
            for h in h_list:
                stats_h[h][0] += win; stats_h[h][1] += 1
            
            # Tamanho do Time
            stats_s[len(h_list)][0] += win; stats_s[len(h_list)][1] += 1

        # Formatação
        def fmt(d, sort_key=False):
            items = sorted(d.items(), key=lambda x: x[0] if sort_key else x[1][1], reverse=not sort_key)
            txt = ""
            for k, v in items:
                prefix = f"{k} Heróis" if isinstance(k, int) else k
                pct = (v[0]/v[1])*100
                txt += f"{prefix}\n  {pct:.0f}% ({v[0]}/{v[1]})\n\n"
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