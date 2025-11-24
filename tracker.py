import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# --- Configuração Visual ---
ctk.set_appearance_mode("Dark")  # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

# --- Listas de Dados (VOCÊ PODE ADICIONAR MAIS AQUI) ---
# A chave é ter o nome exato para diferenciar as variantes
HEROIS = [
    "Legacy", "Legacy (America's Greatest)", "Legacy (Young)",
    "Expatriette", "Expatriette (Dark Watch)",
    "Tachyon", "Tachyon (Super Scientific)",
    "Ra", "Ra (Setting Sun)",
    "Absolute Zero", "Wraith", "Bunker", "Haka", "Fanatic", "Visionary"
]
HEROIS.sort() # Deixa em ordem alfabética

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
    # Tabela simples para guardar o jogo
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  villain TEXT,
                  environment TEXT,
                  result TEXT,
                  heroes TEXT)''')
    conn.commit()
    conn.close()

# --- Interface Gráfica ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sentinels of the Multiverse Tracker")
        self.geometry("900x600")

        # Layout de Grid (2 colunas)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === Menu Lateral (Estatísticas Rápidas) ===
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DADOS DO\nMULTIVERSO", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.stats_label = ctk.CTkLabel(self.sidebar_frame, text="Carregando...", justify="left")
        self.stats_label.grid(row=1, column=0, padx=20, pady=10)

        self.refresh_btn = ctk.CTkButton(self.sidebar_frame, text="Atualizar Dados", command=self.update_stats)
        self.refresh_btn.grid(row=2, column=0, padx=20, pady=10)

        # === Área Principal (Registro) ===
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Registrar Nova Partida")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Seleção de Vilão
        self.label_vilao = ctk.CTkLabel(self.main_frame, text="Vilão Enfrentado:")
        self.label_vilao.pack(pady=(10, 0), anchor="w")
        self.combo_vilao = ctk.CTkComboBox(self.main_frame, values=VILOES, width=300)
        self.combo_vilao.pack(pady=(5, 10), anchor="w")

        # Seleção de Ambiente
        self.label_env = ctk.CTkLabel(self.main_frame, text="Ambiente:")
        self.label_env.pack(pady=(10, 0), anchor="w")
        self.combo_env = ctk.CTkComboBox(self.main_frame, values=AMBIENTES, width=300)
        self.combo_env.pack(pady=(5, 10), anchor="w")

        # Resultado
        self.label_res = ctk.CTkLabel(self.main_frame, text="Resultado:")
        self.label_res.pack(pady=(10, 0), anchor="w")
        self.seg_result = ctk.CTkSegmentedButton(self.main_frame, values=["Vitória", "Derrota"])
        self.seg_result.set("Vitória")
        self.seg_result.pack(pady=(5, 10), anchor="w")

        # Seleção de Heróis (Vamos colocar 5 slots)
        self.label_heroes = ctk.CTkLabel(self.main_frame, text="Heróis (3 a 5):", font=ctk.CTkFont(weight="bold"))
        self.label_heroes.pack(pady=(20, 5), anchor="w")
        
        self.hero_selectors = []
        for i in range(5):
            lbl = ctk.CTkLabel(self.main_frame, text=f"Herói {i+1}:")
            lbl.pack(anchor="w")
            # Adiciona uma opção vazia para casos de menos de 5 heróis
            combo = ctk.CTkComboBox(self.main_frame, values=["(Nenhum)"] + HEROIS, width=300)
            combo.pack(pady=(0, 5), anchor="w")
            self.hero_selectors.append(combo)

        # Botão Salvar
        self.save_btn = ctk.CTkButton(self.main_frame, text="SALVAR PARTIDA", command=self.save_game, fg_color="green", hover_color="darkgreen")
        self.save_btn.pack(pady=30)

        # Inicializa stats
        self.update_stats()

    def save_game(self):
        villain = self.combo_vilao.get()
        env = self.combo_env.get()
        result = self.seg_result.get()
        
        # Coletar heróis (ignorando os vazios)
        selected_heroes = []
        for selector in self.hero_selectors:
            h = selector.get()
            if h != "(Nenhum)":
                selected_heroes.append(h)
        
        if len(selected_heroes) < 3:
            messagebox.showwarning("Atenção", "Selecione pelo menos 3 heróis!")
            return

        # Formatar heróis como string para o banco simples (Ex: "Legacy,Ra,Wraith")
        heroes_str = ",".join(selected_heroes)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Salvar no SQLite
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO games (date, villain, environment, result, heroes) VALUES (?, ?, ?, ?, ?)",
                  (date_str, villain, env, result, heroes_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Partida registrada com sucesso!")
        self.update_stats()

    def update_stats(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        
        # Puxar dados gerais
        c.execute("SELECT result FROM games")
        results = c.fetchall()
        conn.close()

        total_games = len(results)
        if total_games == 0:
            self.stats_label.configure(text="Nenhuma partida\nregistrada ainda.")
            return

        wins = sum(1 for r in results if r[0] == "Vitória")
        losses = total_games - wins
        winrate = (wins / total_games) * 100

        stats_text = (
            f"Total de Jogos: {total_games}\n\n"
            f"Vitórias: {wins}\n"
            f"Derrotas: {losses}\n\n"
            f"Win Rate Geral:\n{winrate:.1f}%"
        )
        self.stats_label.configure(text=stats_text)

if __name__ == "__main__":
    init_db()
    app = TrackerApp()
    app.mainloop()