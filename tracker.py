import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from collections import defaultdict

# --- Configuração Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- SEUS DADOS (Edite aqui) ---
HEROIS = [
    "Legacy", "Legacy (America's Greatest)",
    "Expatriette", "Expatriette (Dark Watch)",
    "Tachyon", "Ra", "Absolute Zero", "Wraith", "Bunker", "Haka", "Fanatic", "Visionary"
]
HEROIS.sort()

VILOES = [
    "Baron Blade", "Citizen Dawn", "Grand Warlord Voss", "Omnitron", 
    "Spite", "The Chairman", "Akash'Bhuta", "GloomWeaver"
]
VILOES.sort()

AMBIENTES = [
    "Megalopolis", "Insula Primalis", "Ruins of Atlantis", 
    "Wagner Mars Base", "Rook City", "Pike Industrial Complex"
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

        self.title("Sentinels Tracker - v2.0")
        self.geometry("1000x700")

        # Criação das Abas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_reg = self.tabview.add("Registrar Partida")
        self.tab_stats = self.tabview.add("Estatísticas Detalhadas")

        # === ABA 1: REGISTRO ===
        self.setup_register_tab()

        # === ABA 2: ESTATÍSTICAS ===
        self.setup_stats_tab()

    def setup_register_tab(self):
        # Frame de rolagem para o formulário
        scroll = ctk.CTkScrollableFrame(self.tab_reg, label_text="Dados da Partida")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Vilão
        ctk.CTkLabel(scroll, text="Vilão Enfrentado:").pack(pady=(10, 0))
        self.combo_vilao = ctk.CTkComboBox(scroll, values=VILOES, width=300)
        self.combo_vilao.pack(pady=5)

        # Ambiente
        ctk.CTkLabel(scroll, text="Ambiente:").pack(pady=(10, 0))
        self.combo_env = ctk.CTkComboBox(scroll, values=AMBIENTES, width=300)
        self.combo_env.pack(pady=5)

        # Resultado
        ctk.CTkLabel(scroll, text="Resultado:").pack(pady=(10, 0))
        self.seg_result = ctk.CTkSegmentedButton(scroll, values=["Vitória", "Derrota"])
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=5)

        # Heróis
        ctk.CTkLabel(scroll, text="Equipe de Heróis:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.hero_selectors = []
        for i in range(5):
            combo = ctk.CTkComboBox(scroll, values=["(Nenhum)"] + HEROIS, width=300)
            combo.pack(pady=2)
            self.hero_selectors.append(combo)

        # Botão Salvar
        btn = ctk.CTkButton(scroll, text="SALVAR PARTIDA", command=self.save_game, fg_color="green", height=40)
        btn.pack(pady=30)

    def setup_stats_tab(self):
        # Botão de atualizar no topo
        self.btn_refresh = ctk.CTkButton(self.tab_stats, text="Atualizar Dados Agora", command=self.calculate_stats)
        self.btn_refresh.pack(pady=10)

        # Cria 3 colunas para os dados (Vilões, Ambientes, Heróis)
        self.stats_frame = ctk.CTkFrame(self.tab_stats)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)

        # Coluna Vilões
        self.frame_v = ctk.CTkScrollableFrame(self.stats_frame, label_text="Win Rate vs Vilões")
        self.frame_v.grid(row=0, column=0, sticky="nsew", padx=5)
        self.lbl_stats_v = ctk.CTkLabel(self.frame_v, text="Sem dados.", justify="left")
        self.lbl_stats_v.pack(padx=5, pady=5, anchor="w")

        # Coluna Ambientes
        self.frame_e = ctk.CTkScrollableFrame(self.stats_frame, label_text="Win Rate em Ambientes")
        self.frame_e.grid(row=0, column=1, sticky="nsew", padx=5)
        self.lbl_stats_e = ctk.CTkLabel(self.frame_e, text="Sem dados.", justify="left")
        self.lbl_stats_e.pack(padx=5, pady=5, anchor="w")

        # Coluna Heróis
        self.frame_h = ctk.CTkScrollableFrame(self.stats_frame, label_text="Win Rate dos Heróis")
        self.frame_h.grid(row=0, column=2, sticky="nsew", padx=5)
        self.lbl_stats_h = ctk.CTkLabel(self.frame_h, text="Sem dados.", justify="left")
        self.lbl_stats_h.pack(padx=5, pady=5, anchor="w")
        
        # Carrega dados iniciais
        self.calculate_stats()

    def save_game(self):
        villain = self.combo_vilao.get()
        env = self.combo_env.get()
        result = self.seg_result.get()
        
        # Pega a lista de heróis selecionados (ignorando os vazios)
        selected_heroes = [s.get() for s in self.hero_selectors if s.get() != "(Nenhum)"]
        
        # 1. Validação de quantidade mínima
        if len(selected_heroes) < 3:
            messagebox.showwarning("Atenção", "Selecione pelo menos 3 heróis!")
            return

        # 2. Validação de "Personagem Único" (NOVA LÓGICA)
        personagens_na_mesa = set()
        
        for heroi_completo in selected_heroes:
            # Pega o nome base. Ex: "Legacy (Young)" vira apenas "Legacy"
            # O split(" (")[0] pega tudo antes do primeiro " ("
            nome_base = heroi_completo.split(" (")[0]
            
            if nome_base in personagens_na_mesa:
                messagebox.showerror("Erro de Regra", 
                    f"Conflito de Personagem!\n\n"
                    f"O personagem '{nome_base}' já está na equipe.\n"
                    "Você não pode usar o mesmo herói e sua variante juntos.")
                return
            
            personagens_na_mesa.add(nome_base)

        # 3. Se passou das validações, salva no banco
        heroes_str = ",".join(selected_heroes)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO games (date, villain, environment, result, heroes) VALUES (?, ?, ?, ?, ?)",
                  (date_str, villain, env, result, heroes_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Partida registrada com sucesso!")
        
        # Limpa seleção para o próximo jogo
        for s in self.hero_selectors: s.set("(Nenhum)")
        
        # Atualiza a aba de stats
        self.calculate_stats()

    def calculate_stats(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT villain, environment, result, heroes FROM games")
        rows = c.fetchall()
        conn.close()

        if not rows:
            return

        # Dicionários para contar: { "Nome": [vitorias, total_jogos] }
        stats_villain = defaultdict(lambda: [0, 0])
        stats_env = defaultdict(lambda: [0, 0])
        stats_hero = defaultdict(lambda: [0, 0])

        for v, e, res, h_str in rows:
            win = 1 if res == "Vitória" else 0
            
            # Vilão
            stats_villain[v][0] += win
            stats_villain[v][1] += 1
            
            # Ambiente
            stats_env[e][0] += win
            stats_env[e][1] += 1
            
            # Heróis (separa a string e conta cada um individualmente)
            heroes_list = h_str.split(",")
            for hero in heroes_list:
                stats_hero[hero][0] += win
                stats_hero[hero][1] += 1

        # Função auxiliar para formatar texto
        def format_text(stats_dict):
            # Ordena por quem tem mais jogos
            items = sorted(stats_dict.items(), key=lambda x: x[1][1], reverse=True)
            text = ""
            for nome, dados in items:
                wins, total = dados
                pct = (wins / total) * 100
                # Ex: Baron Blade: 66% (2/3)
                text += f"{nome}\n  WR: {pct:.1f}% ({wins}/{total})\n\n"
            return text

        self.lbl_stats_v.configure(text=format_text(stats_villain))
        self.lbl_stats_e.configure(text=format_text(stats_env))
        self.lbl_stats_h.configure(text=format_text(stats_hero))

if __name__ == "__main__":
    init_db()
    app = TrackerApp()
    app.mainloop()