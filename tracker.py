import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict

# --- Configuração Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- ESTRUTURA DE DADOS INTELIGENTE ---
# Dicionário: "Nome do Herói": ["Lista de Variantes"]
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
    "Stuntman": ["Base", "Action Hero"], # Exemplo
    "Benchmark": ["Base"],
    "La Comodora": ["Base"],
    "Lifeline": ["Base"],
    "Akash'Thriya": ["Base"],
    "Luminary": ["Base"]
}

# Modos/Variantes Genéricos de Vilão
MODOS_VILAO = ["Normal", "Advanced", "Challenge", "Ultimate"]
# Se tiver vilões com variantes específicas (ex: Skinwalker Gloomweaver), adicione aqui
VILLAINS_DATA = {
    "Baron Blade": MODOS_VILAO,
    "Citizen Dawn": MODOS_VILAO,
    "Grand Warlord Voss": MODOS_VILAO,
    "Omnitron": MODOS_VILAO,
    "Spite": MODOS_VILAO,
    "The Chairman": MODOS_VILAO,
    "Akash'Bhuta": MODOS_VILAO,
    "GloomWeaver": MODOS_VILAO + ["Skinwalker"], # Exemplo de variante específica
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
    "OblivAeon": ["Normal", "Advanced"] # OblivAeon tem regras próprias
}

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
                  heroes TEXT)''')
    conn.commit()
    conn.close()

# --- COMPONENTE CUSTOMIZADO PARA SELEÇÃO DE HERÓI ---
class HeroSelector(ctk.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(self, text=label_text, width=60, anchor="w")
        self.label.grid(row=0, column=0, padx=5)

        # Combo de Personagem
        hero_names = ["(Nenhum)"] + sorted(list(HEROES_DATA.keys()))
        self.hero_combo = ctk.CTkComboBox(self, values=hero_names, command=self.update_variants, width=200)
        self.hero_combo.grid(row=0, column=1, padx=5)

        # Combo de Variante
        self.variant_combo = ctk.CTkComboBox(self, values=["-"], width=150)
        self.variant_combo.grid(row=0, column=2, padx=5)
        self.variant_combo.configure(state="disabled") # Começa desativado

    def update_variants(self, choice):
        if choice == "(Nenhum)":
            self.variant_combo.configure(values=["-"], state="disabled")
            self.variant_combo.set("-")
        else:
            variants = HEROES_DATA.get(choice, ["Base"])
            self.variant_combo.configure(values=variants, state="normal")
            self.variant_combo.set("Base") # Padrão é Base

    def get_selection(self):
        hero = self.hero_combo.get()
        variant = self.variant_combo.get()
        
        if hero == "(Nenhum)":
            return None
        
        # Formata para salvar: "Legacy" (se Base) ou "Legacy (Young)"
        if variant == "Base":
            return hero
        else:
            return f"{hero} ({variant})"

# --- APP PRINCIPAL ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Tracker - v4.0 (Smart Select)")
        self.geometry("1100x750")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tab_reg = self.tabview.add("Registrar Partida")
        self.tab_stats = self.tabview.add("Estatísticas")

        self.setup_register_tab()
        self.setup_stats_tab()

    def setup_register_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_reg, label_text="Nova Partida")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- SEÇÃO DO VILÃO ---
        frame_vilao = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_vilao.pack(pady=10, anchor="w")
        
        ctk.CTkLabel(frame_vilao, text="Vilão:", width=60, anchor="w").grid(row=0, column=0, padx=5)
        self.combo_vilao_nome = ctk.CTkComboBox(frame_vilao, values=sorted(list(VILLAINS_DATA.keys())), 
                                                command=self.update_villain_modes, width=200)
        self.combo_vilao_nome.grid(row=0, column=1, padx=5)
        
        self.combo_vilao_modo = ctk.CTkComboBox(frame_vilao, values=["Normal"], width=150)
        self.combo_vilao_modo.grid(row=0, column=2, padx=5)
        self.update_villain_modes(self.combo_vilao_nome.get()) # Inicializa

        # --- AMBIENTE ---
        frame_env = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_env.pack(pady=5, anchor="w")
        ctk.CTkLabel(frame_env, text="Ambiente:", width=60, anchor="w").grid(row=0, column=0, padx=5)
        self.combo_env = ctk.CTkComboBox(frame_env, values=AMBIENTES, width=360)
        self.combo_env.grid(row=0, column=1, padx=5)

        # --- RESULTADO ---
        ctk.CTkLabel(scroll, text="Resultado:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.seg_result = ctk.CTkSegmentedButton(scroll, values=["Vitória", "Derrota"])
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=5)

        # --- SELEÇÃO DE HERÓIS ---
        ctk.CTkLabel(scroll, text="Equipe (Selecione Herói e Variante):", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        
        self.hero_selectors = []
        for i in range(5):
            # Instancia nossa classe customizada
            selector = HeroSelector(scroll, label_text=f"Herói {i+1}:")
            selector.pack(pady=2, anchor="w")
            self.hero_selectors.append(selector)

        # Botão Salvar
        btn = ctk.CTkButton(scroll, text="SALVAR PARTIDA", command=self.save_game, fg_color="green", height=40)
        btn.pack(pady=30)

    def update_villain_modes(self, choice):
        modes = VILLAINS_DATA.get(choice, ["Normal"])
        self.combo_vilao_modo.configure(values=modes)
        self.combo_vilao_modo.set("Normal")

    def setup_stats_tab(self):
        # A aba de stats permanece a mesma lógica, pois salvamos os dados no formato antigo
        self.btn_refresh = ctk.CTkButton(self.tab_stats, text="Atualizar Dados", command=self.calculate_stats)
        self.btn_refresh.pack(pady=10)

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

    def save_game(self):
        # 1. Pega Vilão + Modo
        v_name = self.combo_vilao_nome.get()
        v_mode = self.combo_vilao_modo.get()
        
        # Formata: "Baron Blade" (se Normal) ou "Baron Blade (Advanced)"
        if v_mode == "Normal":
            villain_final = v_name
        else:
            villain_final = f"{v_name} ({v_mode})"
            
        env = self.combo_env.get()
        result = self.seg_result.get()
        
        # 2. Pega Heróis usando a nova classe
        selected_heroes = []
        for selector in self.hero_selectors:
            h_str = selector.get_selection() # Retorna "Nome (Variante)" ou None
            if h_str:
                selected_heroes.append(h_str)
        
        if len(selected_heroes) < 3:
            messagebox.showwarning("Erro", "Selecione pelo menos 3 heróis!")
            return

        # 3. Validação de Personagem Único (Rule of the Multiverse)
        personagens_base = set()
        for h in selected_heroes:
            # Pega o nome base antes do parênteses
            base = h.split(" (")[0]
            if base in personagens_base:
                messagebox.showerror("Conflito", f"O herói '{base}' já está na equipe!\nVocê não pode selecionar duas variantes do mesmo herói.")
                return
            personagens_base.add(base)

        # 4. Salvar
        heroes_str = ",".join(selected_heroes)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO games (date, villain, environment, result, heroes) VALUES (?, ?, ?, ?, ?)",
                  (date_str, villain_final, env, result, heroes_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Partida salva!")
        
        # Reset visual
        for selector in self.hero_selectors:
            selector.hero_combo.set("(Nenhum)")
            selector.update_variants("(Nenhum)")
            
        self.calculate_stats()

    def calculate_stats(self):
        # Lógica idêntica ao anterior, pois o formato do texto salvo é compatível
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes FROM games")
        rows = c.fetchall()
        conn.close()

        if not rows: return

        stats_villain = defaultdict(lambda: [0, 0])
        stats_env = defaultdict(lambda: [0, 0])
        stats_hero = defaultdict(lambda: [0, 0])
        stats_size = defaultdict(lambda: [0, 0])

        for v, e, res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            stats_villain[v][0] += win; stats_villain[v][1] += 1
            stats_env[e][0] += win; stats_env[e][1] += 1
            heroes_list = h_str.split(",")
            for hero in heroes_list:
                stats_hero[hero][0] += win; stats_hero[hero][1] += 1
            stats_size[len(heroes_list)][0] += win; stats_size[len(heroes_list)][1] += 1

        def format_text(stats_dict, sort_key=False):
            items = sorted(stats_dict.items(), key=lambda x: x[0] if sort_key else x[1][1], reverse=not sort_key)
            text = ""
            for nome, dados in items:
                prefixo = f"{nome} Heróis" if isinstance(nome, int) else nome
                text += f"{prefixo}\n  WR: {(dados[0]/dados[1])*100:.1f}% ({dados[0]}/{dados[1]})\n\n"
            return text

        self.lbl_stats_v.configure(text=format_text(stats_villain))
        self.lbl_stats_e.configure(text=format_text(stats_env))
        self.lbl_stats_h.configure(text=format_text(stats_hero))
        self.lbl_stats_s.configure(text=format_text(stats_size, True))

if __name__ == "__main__":
    try:
        init_db()
        app = TrackerApp()
        app.mainloop()
    except Exception as e:
        import traceback
        import tkinter as tk
        from tkinter import messagebox
        
        # Cria uma janelinha nativa só para mostrar o erro
        root = tk.Tk()
        root.withdraw() # Esconde a janela principal do tk
        error_msg = traceback.format_exc()
        print(error_msg) # Imprime no terminal também
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro ao iniciar:\n\n{e}\n\nDetalhes:\n{error_msg}")