import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
from datetime import datetime
from collections import defaultdict
import math
import re
import os

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
    
    # --- CORES DE ACHIEVEMENTS ---
    "rank_bronze": "#cd7f32",   
    "rank_silver": "#7C9B99",   
    "rank_gold": "#ffd700",     
    "rank_platinum": "#e5e4e2",
    "rank_diamond": "#b9f2ff",
    
    # Novos Ranks
    "rank_dark_watch": "#ff7675",
    "rank_prime": "#e1b12c",
    "rank_xtreme": "#e84118",
    "rank_freedom": "#00a8ff",
    "rank_sentinel": "#9c88ff",

    # Mastery
    "mastery_text": "#00e676",
    "mastery_bg": "#1b5e20",
    # Dificuldade
    "diff_challenge": "#e67e22", "diff_ultimate": "#8e44ad"
}

FONTS = {
    "h1": ("Roboto", 36, "bold"),       "h2": ("Roboto", 22, "bold"),
    "h3": ("Roboto Medium", 16),        "body": ("Roboto", 13),
    "body_bold": ("Roboto", 13, "bold"),"mono": ("Roboto Medium", 10),
    "card_label": ("Roboto", 11, "bold"), "card_value": ("Roboto", 18, "bold"),
    "stat_big": ("Roboto", 28, "bold"), "dashboard_row": ("Roboto Medium", 13),
    "xp_label": ("Roboto", 13),
    "xp_val": ("Consolas", 13, "bold"),
    "xp_total": ("Roboto", 20, "bold")
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

HERO_COMPLEXITY = {
    "Legacy": 1, "Bunker": 2, "Wraith": 1, "Tachyon": 2, "Absolute Zero": 3,
    "Unity": 2, "Haka": 1, "Fanatic": 2, "Tempest": 1, "Argent Adept": 3,
    "Captain Cosmic": 2, "Expatriette": 3, "Setback": 3, "Nightmist": 3,
    "Mr. Fixer": 2, "Harpy": 2, "Ra": 1, "Visionary": 2, "Chrono-Ranger": 1,
    "Omnitron-X": 2, "Sky-Scraper": 2, "K.N.Y.F.E.": 1, "Parse": 3,
    "Naturalist": 2, "Sentinels": 2, "Guise": 2, "Scholar": 2, "Stuntman": 3,
    "Benchmark": 3, "La Comodora": 2, "Lifeline": 2, "Akash'Thriya": 3,
    "Luminary": 2, "Doctor Medico": 2, "Idealist": 2, "Mainstay": 2,
    "Writhe": 3, "Bowman": 2, "Captain Thunder": 2, "Daedalus": 2,
    "Doctor Metropolis": 2, "Johnny Rocket": 2, "Lady Liberty": 2,
    "Pseudo": 1, "Raven": 2, "Siren": 2, "Star Knight": 3,
    "Eldritch": 2, "Lantern Jack": 2
}

SOLO_VILLAIN_DIFF = {
    "Baron Blade": 1, "Mad Bomber Blade": 2, "Citizen Dawn": 4, "Grand Warlord Voss": 3,
    "Omnitron": 1, "Cosmic Omnitron": 3, "Ambuscade": 1, "Spite": 2, "Agent of Gloom Spite": 3,
    "Chairman": 4, "Akash'Bhuta": 2, "GloomWeaver": 1, "Skinwalker GloomWeaver": 3,
    "Matriarch": 3, "Miss Information": 4, "Plague Rat": 2, "Ennead": 3, "Apostate": 2,
    "Iron Legacy": 5, "Kismet": 2, "Unstable Kismet": 3, "La Capitan": 2, "Dreamer": 3,
    "Kaargra Warfang": 5, "Progeny": 4, "Deadline": 2, "Wager Master": 3, "Infinitor": 3,
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

SOLO_VILLAINS_DATA = {k: ["Normal", "Advanced", "Challenge", "Ultimate"] for k in SOLO_VILLAIN_DIFF.keys()}
if "OblivAeon" in SOLO_VILLAINS_DATA:
    del SOLO_VILLAINS_DATA["OblivAeon"]

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
    except: pass
    conn.commit()
    conn.close()

# --- 4. COMPONENTES VISUAIS (SELETORES) ---
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
            btn_fg, btn_border, btn_text_color = COLORS["bg_card"], COLORS["border"], "white"
            icon, border_width = "", 1

            if item_stats and item_name in item_stats:
                stats = item_stats[item_name]
                if stats[1] > 0: 
                    display_text = f"{item_name}\n🎮 {stats[0]}  |  🏆 {stats[1]:.0f}%"
                else:
                    display_text = f"{item_name}\n🎮 {stats[0]}  |  🏆 0%"

            if mastery_map and item_name in mastery_map:
                m_level, _ = mastery_map[item_name]
                display_text += f"\n(MR {m_level})"

            if style_map and item_name in style_map:
                style = style_map[item_name]
                if style.get('text_color'): btn_text_color = style['text_color']
                if style.get('border_color'): btn_border = style['border_color']; border_width = 2
                if style.get('icon'): icon = style['icon']; display_text = f"{display_text} {icon}"

            btn = ctk.CTkButton(
                scroll, text=display_text, font=FONTS["body_bold"], fg_color=btn_fg,
                border_width=border_width, border_color=btn_border, text_color=btn_text_color,
                hover_color=COLORS["accent"], height=60,
                command=lambda x=item_name: self.on_select(x)
            )
            btn.grid(row=i//columns, column=i%columns, padx=5, pady=5, sticky="ew")
            
            if mastery_map and item_name in mastery_map:
                _, xp = mastery_map[item_name]
                prog = (xp % 1000) / 1000
                xp_bar = ctk.CTkProgressBar(btn, height=3, width=50, progress_color=COLORS["mastery_text"])
                xp_bar.set(prog)
                xp_bar.place(relx=0.5, rely=0.92, anchor="center", relwidth=0.8)

        ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color=COLORS["danger"]).pack(pady=10)

    def on_select(self, item_name):
        self.withdraw()
        self.destroy() 
        self.callback(item_name) 

class MultiSelectionModal(ctk.CTkToplevel):
    def __init__(self, parent, title, item_list, callback, max_selection=5):
        super().__init__(parent)
        self.callback = callback
        self.max_selection = max_selection
        self.selected_items = set()
        self.buttons = {}
        
        self.title(title)
        self.geometry("1100x700")
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_title = ctk.CTkLabel(top_frame, text=f"{title.upper()} (0/{max_selection})", font=FONTS["h2"])
        self.lbl_title.pack(side="left")
        
        ctk.CTkButton(top_frame, text="CONFIRMAR SELEÇÃO", command=self.confirm_selection, 
                      fg_color=COLORS["success"], font=FONTS["body_bold"]).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=15, pady=5)
        columns = 4
        for i in range(columns): scroll.grid_columnconfigure(i, weight=1)

        for i, item_name in enumerate(item_list):
            btn = ctk.CTkButton(
                scroll, text=item_name, font=FONTS["body_bold"], 
                fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"],
                hover_color=COLORS["accent"], height=60,
                command=lambda x=item_name: self.toggle_item(x)
            )
            btn.grid(row=i//columns, column=i%columns, padx=5, pady=5, sticky="ew")
            self.buttons[item_name] = btn

        ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color=COLORS["danger"]).pack(pady=10)

    def toggle_item(self, item_name):
        if item_name in self.selected_items:
            self.selected_items.remove(item_name)
            self.buttons[item_name].configure(fg_color=COLORS["bg_card"], border_color=COLORS["border"])
        else:
            if len(self.selected_items) >= self.max_selection:
                return
            self.selected_items.add(item_name)
            self.buttons[item_name].configure(fg_color=COLORS["accent"], border_color="white")
        
        self.lbl_title.configure(text=f"SELECIONADOS ({len(self.selected_items)}/{self.max_selection})")

    def confirm_selection(self):
        self.withdraw()
        self.destroy()
        self.callback(list(self.selected_items))

class VariantAssignmentModal(ctk.CTkToplevel):
    def __init__(self, parent, selected_heroes, callback):
        super().__init__(parent)
        self.callback = callback
        self.selected_heroes = selected_heroes
        self.variant_vars = {}
        
        self.title("Selecionar Variantes")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        ctk.CTkLabel(self, text="ESCOLHA AS VARIANTES", font=FONTS["h2"]).pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for hero in selected_heroes:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=hero, font=FONTS["body_bold"], width=150, anchor="w").pack(side="left")
            
            variants = HEROES_DATA.get(hero, ["Base"])
            combo = ctk.CTkComboBox(row, values=variants, font=FONTS["body"])
            combo.set("Base")
            combo.pack(side="left", fill="x", expand=True, padx=10)
            self.variant_vars[hero] = combo
            
        ctk.CTkButton(self, text="CONFIRMAR EQUIPE", command=self.confirm, 
                      fg_color=COLORS["success"], font=FONTS["body_bold"], height=40).pack(pady=20, fill="x", padx=20)

    def confirm(self):
        final_list = []
        for hero in self.selected_heroes:
            var = self.variant_vars[hero].get()
            final_name = hero if var == "Base" else f"{hero} ({var})"
            final_list.append((hero, var, final_name))
        
        self.withdraw()
        self.destroy()
        self.callback(final_list)

class LogConfirmationModal(ctk.CTkToplevel):
    def __init__(self, parent, log_data, confirm_callback):
        super().__init__(parent)
        self.confirm_callback = confirm_callback
        self.log_data = log_data
        
        self.title("Confirmar Importação de Log")
        self.geometry("600x750")
        self.transient(parent)
        self.grab_set()
        
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        res_color = COLORS["success"] if log_data["result"] == "Vitória" else COLORS["danger"]
        ctk.CTkLabel(container, text=log_data["result"].upper(), font=("Roboto", 30, "bold"), text_color=res_color).pack(pady=(10, 5))
        ctk.CTkLabel(container, text="Resumo da Partida (Solo)", font=FONTS["h3"], text_color="gray").pack(pady=(0, 15))

        self._build_info_row(container, "VILÃO", f"{log_data['villain']} ({log_data['difficulty']})")
        self._build_info_row(container, "AMBIENTE", log_data['environment'])
        
        ctk.CTkFrame(container, height=2, fg_color=COLORS["separator"]).pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(container, text="EQUIPE IDENTIFICADA", font=FONTS["h2"]).pack(pady=10)
        
        app = parent
        style_map = app.get_hero_achievement_styles() if hasattr(app, "get_hero_achievement_styles") else None
        mastery_map = app.get_hero_mastery_map() if hasattr(app, "get_hero_mastery_map") else None
        
        for h_data in log_data['heroes_data']:
            hero_base, variant, full_str = h_data
            btn_fg, btn_border, btn_text_color = COLORS["bg_card"], COLORS["border"], "white"
            icon, border_width = "", 1
            display_text = f"{hero_base}\n{variant}"
            
            if style_map and hero_base in style_map:
                style = style_map[hero_base]
                if style.get('text_color'): btn_text_color = style['text_color']
                if style.get('border_color'): btn_border = style['border_color']; border_width = 2
                if style.get('icon'): icon = style['icon']; display_text = f"{display_text} {icon}"
            
            if mastery_map and hero_base in mastery_map:
                m_level, _ = mastery_map[hero_base]
                display_text += f" (MR {m_level})"

            card = ctk.CTkFrame(container, fg_color=btn_fg, border_width=border_width, border_color=btn_border, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=display_text, font=FONTS["body_bold"], text_color=btn_text_color).pack(pady=10)

        ctk.CTkFrame(container, height=2, fg_color=COLORS["separator"]).pack(fill="x", pady=15)
        
        ctk.CTkButton(self, text="CONFIRMAR E SALVAR PARTIDA", command=self.on_confirm, 
                      fg_color=COLORS["success"], height=50, font=("Roboto", 14, "bold")).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color=COLORS["danger"]).pack(fill="x", padx=20, pady=(0, 20))

    def _build_info_row(self, parent, label, value):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=label, font=FONTS["card_label"], text_color="gray", width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(f, text=value, font=FONTS["body_bold"], anchor="w").pack(side="left")

    def on_confirm(self):
        self.withdraw()
        self.destroy()
        self.confirm_callback(self.log_data)

class VillainSelector(ctk.CTkFrame):
    def __init__(self, master, index, controller=None, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.controller = controller
        self.selected_villain = None
        lbl = ctk.CTkLabel(self, text=f"Vilão {index}", font=("Roboto", 12, "bold"), text_color=COLORS["text_muted"], width=60)
        lbl.pack(side="left", padx=10)
        self.btn_select = ctk.CTkButton(self, text="Selecionar...", command=self.open_grid, width=200, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select.pack(side="left", fill="x", expand=True, padx=10, pady=8)

    def open_grid(self):
        parent = self.controller if self.controller else self.winfo_toplevel()
        GridSelectionModal(parent, "Selecione o Vilão", TEAM_VILLAINS_LIST, self.update_selection)

    def update_selection(self, name):
        self.selected_villain = name
        self.btn_select.configure(text=name, fg_color=COLORS["accent"])
        self.configure(border_color=COLORS["accent"])

    def get_selection(self): return self.selected_villain
    def reset(self):
        self.selected_villain = None
        self.btn_select.configure(text="Selecionar...", fg_color="#333")
        self.configure(border_color=COLORS["border"])

class EnvironmentSelector(ctk.CTkFrame):
    def __init__(self, master, index, controller=None, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.controller = controller
        self.selected_env = None
        lbl = ctk.CTkLabel(self, text=f"Ambiente {index}", font=("Roboto", 12, "bold"), text_color=COLORS["text_muted"], width=80)
        lbl.pack(side="left", padx=10)
        self.btn_select = ctk.CTkButton(self, text="Selecionar...", command=self.open_grid, width=200, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select.pack(side="left", fill="x", expand=True, padx=10, pady=8)

    def open_grid(self):
        parent = self.controller if self.controller else self.winfo_toplevel()
        GridSelectionModal(parent, "Selecione o Ambiente", AMBIENTES, self.update_selection)

    def update_selection(self, name):
        self.selected_env = name
        self.btn_select.configure(text=name, fg_color=COLORS["accent"])
        self.configure(border_color=COLORS["accent"])

    def get_selection(self): return self.selected_env
    def reset(self):
        self.selected_env = None
        self.btn_select.configure(text="Selecionar...", fg_color="#333")
        self.configure(border_color=COLORS["border"])

class HeroSelector(ctk.CTkFrame):
    def __init__(self, master, index, controller=None, **kwargs):
        super().__init__(master, corner_radius=12, border_width=1, border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kwargs)
        self.controller = controller
        self.selected_hero_name = None 
        self.selected_variant = None
        self.lbl_idx = ctk.CTkLabel(self, text=f"{index}", font=("Arial", 20, "bold"), text_color=COLORS["text_muted"], width=30)
        self.lbl_idx.pack(side="left", padx=(10, 5))
        self.combo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.combo_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.btn_select_hero = ctk.CTkButton(self.combo_frame, text="Selecionar Herói...", command=self.open_hero_grid, width=200, 
            font=FONTS["body_bold"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_hero.pack(pady=(0, 2), fill="x")
        self.lbl_variant = ctk.CTkLabel(self.combo_frame, text="-", font=("Roboto", 12), text_color="gray")
        self.lbl_variant.pack(pady=(2, 0))

    def open_hero_grid(self):
        app = self.controller if self.controller else self.winfo_toplevel()
        style_map = app.get_hero_achievement_styles() if hasattr(app, "get_hero_achievement_styles") else None
        mastery_map = app.get_hero_mastery_map() if hasattr(app, "get_hero_mastery_map") else None
        hero_names = sorted(list(HEROES_DATA.keys()))
        GridSelectionModal(app, "Selecione um Herói", hero_names, self.update_hero_selection, style_map=style_map, mastery_map=mastery_map)

    def update_hero_selection(self, hero_name):
        self.selected_hero_name = hero_name
        app = self.controller if self.controller else self.winfo_toplevel()
        text_color = "white"
        display_text = hero_name
        
        if hasattr(app, "get_hero_achievement_styles"):
            styles = app.get_hero_achievement_styles()
            if hero_name in styles and styles[hero_name].get('text_color'): text_color = styles[hero_name]['text_color']
        
        if hasattr(app, "get_hero_mastery_map"):
            m_map = app.get_hero_mastery_map()
            if hero_name in m_map: display_text = f"{hero_name} (MR {m_map[hero_name][0]})"

        self.btn_select_hero.configure(text=display_text, fg_color=COLORS["accent"], text_color=text_color)
        self.configure(border_color=COLORS["accent"])
        self.open_variant_grid()

    def open_variant_grid(self):
        if not self.selected_hero_name: return
        variants = HEROES_DATA.get(self.selected_hero_name, ["Base"])
        parent = self.controller if self.controller else self.winfo_toplevel()
        self.after(200, lambda: GridSelectionModal(parent, f"Variante de {self.selected_hero_name}", variants, self.update_variant_selection))

    def update_variant_selection(self, variant):
        self.selected_variant = variant
        display_text = "Base" if variant == "Base" else variant
        self.lbl_variant.configure(text=f"Var: {display_text}", text_color=COLORS["highlight"])

    def set_hero_data(self, hero_name, variant):
        self.selected_hero_name = hero_name
        self.selected_variant = variant
        
        app = self.controller if self.controller else self.winfo_toplevel()
        text_color = "white"
        display_text = hero_name
        
        if hasattr(app, "get_hero_achievement_styles"):
            styles = app.get_hero_achievement_styles()
            if hero_name in styles and styles[hero_name].get('text_color'): text_color = styles[hero_name]['text_color']
        
        if hasattr(app, "get_hero_mastery_map"):
            m_map = app.get_hero_mastery_map()
            if hero_name in m_map: display_text = f"{hero_name} (MR {m_map[hero_name][0]})"
            
        self.btn_select_hero.configure(text=display_text, fg_color=COLORS["accent"], text_color=text_color)
        self.configure(border_color=COLORS["accent"])
        display_v = "Base" if variant == "Base" else variant
        self.lbl_variant.configure(text=f"Var: {display_v}", text_color=COLORS["highlight"])

    def get_selection(self):
        if not self.selected_hero_name: return None
        v = self.selected_variant if self.selected_variant else "Base"
        return self.selected_hero_name if v == "Base" else f"{self.selected_hero_name} ({v})"
    
    def reset(self):
        self.selected_hero_name = None
        self.selected_variant = None
        self.btn_select_hero.configure(text="Selecionar Herói...", fg_color="#333", text_color="white")
        self.configure(border_color=COLORS["border"])
        self.lbl_variant.configure(text="-", text_color="gray")

# --- APLICAÇÃO PRINCIPAL ---
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentinels Tracker v1.4.1")
        self.geometry("1300x850")
        
        self.selected_villain = None
        self.selected_env = None
        self.selected_analysis_hero = None
        self.selected_villain_diff = None 
        self.insight_labels, self.insight_titles = [], []
        self.seg_stats_mode = None
        self.combo_variant_analysis, self.combo_diff_filter, self.combo_solo_mode = None, None, None
        self.dash_cards_frames, self.global_stat_labels, self.agg_lists_frames = {}, {}, {}
        self.achievements_frame, self.mastery_labels, self.mastery_history_frame = None, {}, None
        self.lbl_mastery_name, self.lbl_agg_name, self.lbl_achieve_name = None, None, None
        
        self.combo_oblivaeon_diff = None 

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
        self.seg_gamemode = ctk.CTkSegmentedButton(self.card_mode, values=["Solo", "Time de Vilões", "OblivAeon"], command=self.toggle_villain_mode, font=FONTS["body_bold"], height=32)
        self.seg_gamemode.set("Solo"); self.seg_gamemode.pack(pady=(0, 15), padx=20, fill="x")

        self.card_setup = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_setup.pack(fill="x", pady=(0, 15), ipady=10)
        self.container_villain = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_villain.pack(fill="x", padx=0, pady=0)

        self.frame_solo = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_solo, text="VILÃO", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_villain = ctk.CTkButton(self.frame_solo, text="Selecionar Vilão...", command=self.open_villain_grid, width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_villain.pack(padx=20, pady=(5, 5), fill="x")
        self.combo_solo_mode = ctk.CTkComboBox(self.frame_solo, values=["Normal"], width=250, font=FONTS["body"])
        
        self.lbl_villain_diff = ctk.CTkLabel(self.frame_solo, text="Modo: Normal", font=FONTS["body"], text_color="gray")
        self.lbl_villain_diff.pack(padx=20, pady=(0, 10))
        
        self.frame_team = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_team, text="TIME DE VILÕES (3-5)", font=FONTS["h3"]).pack(anchor="w", padx=20)
        
        self.btn_multi_villain = ctk.CTkButton(self.frame_team, text="SELEÇÃO RÁPIDA (TIME)", command=self.open_multi_villain_select,
                                               fg_color=COLORS["warning"], hover_color="#c98314", font=("Roboto", 12, "bold"))
        self.btn_multi_villain.pack(padx=20, pady=5, fill="x")

        self.team_selectors = []
        for i in range(5):
            sel = VillainSelector(self.frame_team, index=i+1, controller=self)
            sel.pack(padx=20, pady=4, fill="x")
            self.team_selectors.append(sel)
            
        self.frame_oblivaeon_villain = ctk.CTkFrame(self.container_villain, fg_color="transparent")
        ctk.CTkLabel(self.frame_oblivaeon_villain, text="VILÃO: OBLIVAEON", font=FONTS["h3"]).pack(anchor="w", padx=20)
        ctk.CTkLabel(self.frame_oblivaeon_villain, text="Selecione a Dificuldade", font=FONTS["body"], text_color="gray").pack(anchor="w", padx=20, pady=(5,0))
        self.combo_oblivaeon_diff = ctk.CTkComboBox(self.frame_oblivaeon_villain, values=["Normal", "Advanced", "Challenge", "Ultimate"], width=250, font=FONTS["body"])
        self.combo_oblivaeon_diff.pack(padx=20, pady=10, fill="x")
            
        self.frame_solo.pack(fill="x")

        ctk.CTkFrame(self.card_setup, height=1, fg_color=COLORS["separator"]).pack(fill="x", padx=20, pady=15)
        self.container_env = ctk.CTkFrame(self.card_setup, fg_color="transparent")
        self.container_env.pack(fill="x")
        
        self.frame_env_single = ctk.CTkFrame(self.container_env, fg_color="transparent")
        ctk.CTkLabel(self.frame_env_single, text="AMBIENTE", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.btn_select_env = ctk.CTkButton(self.frame_env_single, text="Selecionar Ambiente...", command=self.open_env_grid, width=250, font=FONTS["body"], fg_color="#333", border_width=1, border_color="#555")
        self.btn_select_env.pack(padx=20, pady=5, fill="x")
        self.frame_env_single.pack(fill="x")
        
        self.frame_env_multi = ctk.CTkFrame(self.container_env, fg_color="transparent")
        ctk.CTkLabel(self.frame_env_multi, text="ZONAS DE BATALHA (AMBIENTES)", font=FONTS["h3"]).pack(anchor="w", padx=20)
        self.obliv_env_selectors = []
        for i in range(5):
            sel = EnvironmentSelector(self.frame_env_multi, index=i+1, controller=self)
            sel.pack(padx=20, pady=4, fill="x")
            self.obliv_env_selectors.append(sel)

        self.card_result = ctk.CTkFrame(self.left_panel, corner_radius=12, fg_color=COLORS["bg_card"])
        self.card_result.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.card_result, text="RESULTADO DA BATALHA", font=FONTS["card_label"], text_color=COLORS["text_muted"]).pack(pady=(12, 5))
        self.seg_result = ctk.CTkSegmentedButton(self.card_result, values=["Vitória", "Derrota"], selected_color=COLORS["success"], selected_hover_color="#209662", font=FONTS["body_bold"], height=40)
        self.seg_result.set("Vitória"); self.seg_result.pack(pady=(0, 20), padx=20, fill="x")

        self.btn_import_log = ctk.CTkButton(self.left_panel, text="IMPORTAR LOG (BETA)", command=self.import_log, 
                                            fg_color=COLORS["warning"], hover_color="#c98314", font=("Roboto", 12, "bold"))
        self.btn_import_log.pack(side="top", fill="x", pady=(5, 15))

        self.btn_save = ctk.CTkButton(self.left_panel, text="SALVAR DADOS DA PARTIDA", command=self.save_game, fg_color=COLORS["accent"], hover_color="#144870", height=55, font=("Roboto", 15, "bold"), corner_radius=12)
        self.btn_save.pack(side="bottom", fill="x", pady=10)

        self.right_panel = ctk.CTkFrame(self.tab_reg, corner_radius=12, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_panel, text="EQUIPE DE HERÓIS", font=FONTS["h2"]).pack(pady=(0, 5), anchor="w")
        
        self.btn_multi_hero = ctk.CTkButton(self.right_panel, text="SELEÇÃO RÁPIDA (TIME)", command=self.open_multi_hero_select,
                                            fg_color=COLORS["highlight"], hover_color="#2980b9", font=("Roboto", 12, "bold"))
        self.btn_multi_hero.pack(pady=(0, 15), anchor="w", fill="x")

        self.hero_selectors = []
        for i in range(5):
            sel = HeroSelector(self.right_panel, index=i+1, controller=self)
            sel.pack(padx=0, pady=6, fill="x")
            self.hero_selectors.append(sel)

    def import_log(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path: return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            data = self.parse_log(content)
            if data:
                LogConfirmationModal(self, data, self.save_imported_game)
            else:
                messagebox.showerror("Erro de Leitura", "Não foi possível identificar os dados da partida.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler o arquivo: {str(e)}")

    def parse_log(self, content):
        result = "Vitória" if "Congratulations!" in content else "Derrota"
        
        difficulty = "Normal"
        if "Base_DefeatClassicUltimate" in content: difficulty = "Ultimate"
        elif "Base_DefeatClassicChallenge" in content: difficulty = "Challenge"
        elif "Base_DefeatClassicAdvanced" in content: difficulty = "Advanced"

        turn_takers = set(re.findall(r"Went from (.+?)'s", content))
        
        found_villain = None
        found_env = None
        
        # Mapeamentos para identificação
        solo_v_keys = SOLO_VILLAIN_DIFF.keys()
        env_keys = ENV_DIFF.keys()
        
        # 1. ORDENAR POR TAMANHO PARA EVITAR FALSO POSITIVO (ex: achar Ra em Chrono-Ranger)
        # Importante: Chaves maiores primeiro!
        hero_keys = sorted(HEROES_DATA.keys(), key=len, reverse=True)
        
        # Identificação de Vilão e Ambiente via Turnos
        for name in turn_takers:
            clean_name = name
            if name.startswith("The "): clean_name = name[4:]

            if name in solo_v_keys: found_villain = name; continue
            elif clean_name in solo_v_keys: found_villain = clean_name; continue
            
            if name in env_keys: found_env = name; continue
            elif clean_name in env_keys: found_env = clean_name; continue

        # Identificação de Heróis (Com Prioridade de Tamanho e Regex Boundary)
        detected_heroes = []
        for name in turn_takers:
            # Pula se for vilão ou ambiente
            if name == found_villain or name == found_env: continue
            if found_villain and name in found_villain: continue
            if found_env and name in found_env: continue

            matched_this_turn = False
            for h_key in hero_keys:
                # Regex procura a palavra exata do herói (evita "Ra" em "Terra")
                # (?i) ignora case, \b é boundary
                
                # CORRECAO: K.N.Y.F.E. termina em ponto, entao \b falha logo apos ele
                suffix_boundary = r"\b" if h_key[-1].isalnum() else ""
                
                pattern = r"(?i)\b" + re.escape(h_key) + suffix_boundary
                
                if re.search(pattern, name):
                    if h_key not in detected_heroes:
                        detected_heroes.append(h_key)
                    matched_this_turn = True
                    break # Parar de procurar nessa string específica para não achar "Ra" se já achou "Chrono-Ranger"
        
        # Detectar Variantes (Varrendo o texto inteiro do log)
        final_heroes_data = []
        for h in detected_heroes:
            variant = "Base"
            possible_vars = HEROES_DATA.get(h, ["Base"])
            
            for v in possible_vars:
                if v == "Base": continue
                
                # Prepara termo de busca (remove parenteses ex: "Freedom Six" de "Team Leader (Freedom Six)")
                search_term = v
                if "(" in v:
                    search_term = v.split("(")[1].replace(")", "")
                
                # Busca no LOG INTEIRO se essa variante foi mencionada
                if search_term in content:
                    variant = v
                    break # Prioridade para a primeira variante encontrada na lista (assumindo exclusividade)
            
            full_str = f"{h} ({variant})" if variant != "Base" else h
            final_heroes_data.append((h, variant, full_str))

        if not found_villain or not found_env or not final_heroes_data:
            return None

        return {
            "result": result,
            "difficulty": difficulty,
            "villain": found_villain,
            "environment": found_env,
            "heroes_data": final_heroes_data
        }

    def save_imported_game(self, data):
        try:
            conn = sqlite3.connect('sentinels_history.db')
            c = conn.cursor()
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            v_str = data["villain"]
            if data["difficulty"] != "Normal":
                v_str = f"{data['villain']} ({data['difficulty']})"
            
            h_list = [x[2] for x in data["heroes_data"]]
            
            c.execute("INSERT INTO games (date, villain, environment, result, heroes, game_type) VALUES (?, ?, ?, ?, ?, ?)", 
                      (dt, v_str, data["environment"], data["result"], ",".join(h_list), "SOLO"))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Partida importada e salva com sucesso!")
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e))

    def open_multi_hero_select(self):
        hero_names = sorted(list(HEROES_DATA.keys()))
        MultiSelectionModal(self, "Selecione o Time de Heróis", hero_names, self.on_multi_hero_selected, max_selection=5)

    def on_multi_hero_selected(self, selected_list):
        if not selected_list: return
        VariantAssignmentModal(self, selected_list, self.on_variant_confirmed)

    def on_variant_confirmed(self, hero_data_list):
        for sel in self.hero_selectors: sel.reset()
        for i, (h, v, _) in enumerate(hero_data_list):
            if i < len(self.hero_selectors):
                self.hero_selectors[i].set_hero_data(h, v)

    def open_multi_villain_select(self):
        MultiSelectionModal(self, "Selecione o Time de Vilões", TEAM_VILLAINS_LIST, self.on_multi_villain_selected, max_selection=5)

    def on_multi_villain_selected(self, selected_list):
        if not selected_list: return
        for sel in self.team_selectors: sel.reset()
        for i, v_name in enumerate(selected_list):
            if i < len(self.team_selectors):
                self.team_selectors[i].update_selection(v_name)

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

    def setup_hero_tab_structure(self):
        self.tab_hero_internal = ctk.CTkTabview(self.tab_heroes)
        self.tab_hero_internal.pack(fill="both", expand=True, padx=10, pady=10)
        self.subtab_analysis = self.tab_hero_internal.add(" Análise Específica ")
        self.subtab_summary = self.tab_hero_internal.add(" Resumo do Herói ")
        self.subtab_achievements = self.tab_hero_internal.add(" Conquistas ")
        self.subtab_mastery = self.tab_hero_internal.add(" Maestria & XP ") 
        self.subtab_global = self.tab_hero_internal.add(" Estatísticas Globais ")
        self.setup_subtab_analysis(); self.setup_subtab_summary(); self.setup_subtab_achievements(); self.setup_subtab_mastery(); self.setup_subtab_global()

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

    def setup_subtab_achievements(self):
        self.frame_achieve_header = ctk.CTkFrame(self.subtab_achievements, corner_radius=12, fg_color=COLORS["bg_card"])
        self.frame_achieve_header.pack(fill="x", padx=20, pady=20)
        top = ctk.CTkFrame(self.frame_achieve_header, fg_color="transparent"); top.pack(fill="x", padx=20, pady=(20, 20))
        self.lbl_achieve_name = ctk.CTkLabel(top, text="SELECIONE UM HERÓI", font=FONTS["h1"]); self.lbl_achieve_name.pack(side="left")
        self.btn_achieve_change = ctk.CTkButton(top, text="Trocar Herói", command=self.open_analysis_hero_grid, width=120, fg_color="#333", border_width=1, border_color="#555"); self.btn_achieve_change.pack(side="right")
        self.scroll_achieve = ctk.CTkScrollableFrame(self.subtab_achievements, corner_radius=12, fg_color="transparent"); self.scroll_achieve.pack(fill="both", expand=True, padx=20, pady=10)
    
    def setup_subtab_mastery(self):
        self.frame_mastery_header = ctk.CTkFrame(self.subtab_mastery, corner_radius=12, fg_color=COLORS["bg_card"])
        self.frame_mastery_header.pack(fill="x", padx=20, pady=20)
        top = ctk.CTkFrame(self.frame_mastery_header, fg_color="transparent"); top.pack(fill="x", padx=20, pady=(20, 0))
        self.lbl_mastery_name = ctk.CTkLabel(top, text="SELECIONE UM HERÓI", font=FONTS["h1"]); self.lbl_mastery_name.pack(side="left")
        self.btn_mastery_change = ctk.CTkButton(top, text="Trocar Herói", command=self.open_analysis_hero_grid, width=120, fg_color="#333", border_width=1, border_color="#555"); self.btn_mastery_change.pack(side="right")
        self.mastery_labels["bar_level"] = ctk.CTkLabel(self.frame_mastery_header, text="NÍVEL DE MAESTRIA: 0", font=("Roboto", 20, "bold"), text_color=COLORS["mastery_text"]); self.mastery_labels["bar_level"].pack(pady=(0, 5))
        self.mastery_xp_bar = ctk.CTkProgressBar(self.frame_mastery_header, height=25, corner_radius=12, progress_color=COLORS["mastery_text"]); self.mastery_xp_bar.pack(fill="x", padx=40, pady=5); self.mastery_xp_bar.set(0)
        self.mastery_labels["bar_text"] = ctk.CTkLabel(self.frame_mastery_header, text="0 / 1000 XP", font=FONTS["body_bold"], text_color="gray"); self.mastery_labels["bar_text"].pack(pady=(0, 20))
        self.mastery_history_frame = ctk.CTkScrollableFrame(self.subtab_mastery, corner_radius=12, fg_color="transparent", label_text="HISTÓRICO DE BATALHA & XP", label_font=FONTS["h3"]); self.mastery_history_frame.pack(fill="both", expand=True, padx=20, pady=10)

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

    def toggle_villain_mode(self, mode):
        self.frame_solo.pack_forget()
        self.frame_team.pack_forget()
        self.frame_oblivaeon_villain.pack_forget()
        self.frame_env_single.pack_forget()
        self.frame_env_multi.pack_forget()
        
        if mode == "Solo": 
            self.frame_solo.pack(fill="x")
            self.frame_env_single.pack(fill="x")
        elif mode == "Time de Vilões":
            self.frame_team.pack(fill="x")
            self.frame_env_single.pack(fill="x")
        elif mode == "OblivAeon":
            self.frame_oblivaeon_villain.pack(fill="x")
            self.frame_env_multi.pack(fill="x")

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
        if self.combo_solo_mode: self.combo_solo_mode.set(diff)

    def open_env_grid(self): GridSelectionModal(self, "Selecionar Ambiente", AMBIENTES, self.on_env_selected)
    def on_env_selected(self, env): self.selected_env = env; self.btn_select_env.configure(text=env, fg_color=COLORS["accent"])

    def open_analysis_hero_grid(self):
        hero_stats_map = self.get_all_heroes_stats_map()
        style_map = self.get_hero_achievement_styles()
        mastery_map = self.get_hero_mastery_map()
        sorted_heroes = sorted(list(HEROES_DATA.keys()), key=lambda x: (mastery_map.get(x, (0,0))[0], hero_stats_map.get(x, (0,0))[0], hero_stats_map.get(x, (0,0))[1]), reverse=True)
        GridSelectionModal(self, "Analisar Herói", sorted_heroes, self.on_analysis_hero_selected, item_stats=hero_stats_map, style_map=style_map, mastery_map=mastery_map)

    def on_analysis_hero_selected(self, hero_name):
        self.selected_analysis_hero = hero_name
        self.btn_select_analysis_hero.configure(text=hero_name, fg_color=COLORS["accent"])
        self.update_hero_variants_analysis(hero_name)
        self.calculate_aggregate_hero_stats(hero_name)
        self.lbl_agg_name.configure(text=hero_name.upper())
        self.lbl_achieve_name.configure(text=hero_name.upper())
        self.lbl_mastery_name.configure(text=hero_name.upper())

    def update_hero_variants_analysis(self, hero_name):
        variants = HEROES_DATA.get(hero_name, ["Base"])
        self.combo_variant_analysis.configure(values=variants, state="normal"); self.combo_variant_analysis.set("Base")
        self.display_hero_insights()

    # --- XP HELPERS ---
    def get_match_xp_breakdown(self, villain_str, env, result, game_type, heroes_str):
        if result != "Vitória": return None
        
        details = {
            "v_name": villain_str,
            "v_diff_mode": "Normal",
            "v_base_xp": 500,
            "team_bonus": 0,
            "v_mult_val": 1.0,
            "e_name": env,
            "e_base_xp": 75,
            "e_mult_val": 1.0,
            "salt_val": 0,
            "total_xp": 0,
            "heroes_list": [],
            "villains_list": []
        }

        if "(Ultimate)" in villain_str:
            details["v_diff_mode"] = "Ultimate"
            details["v_base_xp"] = 1000
            details["e_base_xp"] = 125
        elif "(Challenge)" in villain_str:
            details["v_diff_mode"] = "Challenge"
            details["v_base_xp"] = 750
            details["e_base_xp"] = 100
        elif "(Advanced)" in villain_str:
            details["v_diff_mode"] = "Advanced"
            details["v_base_xp"] = 750
            details["e_base_xp"] = 100
        
        h_list = heroes_str.split(",")
        details["heroes_list"] = h_list
        size = len(h_list)
        if size == 3: details["team_bonus"] = 500
        elif size == 4: details["team_bonus"] = 200

        v_diff_sum_for_salt = 0
        total_env_xp_val = 0 
        
        if game_type == "SOLO":
            v_name_clean = villain_str.split(" (")[0]
            details["v_mult_val"] = SOLO_VILLAIN_DIFF.get(v_name_clean, 1)
            v_diff_sum_for_salt = details["v_mult_val"]
            details["villains_list"] = [villain_str]
            details["e_mult_val"] = ENV_DIFF.get(env, 1)
            total_env_xp_val = (details["e_base_xp"] * details["e_mult_val"])
            
        elif game_type == "OBLIVAEON":
            details["v_mult_val"] = 20 
            v_diff_sum_for_salt = 20
            details["villains_list"] = [villain_str]
            
            envs = env.split(",")
            sum_env_mult = 0
            current_env_total = 0
            for e_item in envs:
                e_mult = ENV_DIFF.get(e_item, 1)
                sum_env_mult += e_mult
                current_env_total += (details["e_base_xp"] * e_mult)
            
            total_env_xp_val = current_env_total
            details["e_mult_val"] = sum_env_mult 
            details["e_name"] = "Zona de Batalha (5 Ambientes)" 

        else: 
            team_members = villain_str.split(",")
            details["villains_list"] = team_members
            total_diff = sum([TEAM_VILLAIN_DIFF.get(tm, 1) for tm in team_members])
            v_diff_sum_for_salt = total_diff
            if len(team_members) > 0:
                details["v_mult_val"] = total_diff / len(team_members)
            
            details["e_mult_val"] = ENV_DIFF.get(env, 1)
            total_env_xp_val = (details["e_base_xp"] * details["e_mult_val"])

        xp_pre_mult = details["v_base_xp"] + details["team_bonus"]
        main_xp = (xp_pre_mult * details["v_mult_val"]) + total_env_xp_val

        sum_complexity = 0
        for h in h_list:
            base = h.split(" (")[0]
            sum_complexity += HERO_COMPLEXITY.get(base, 1) * 11
        
        details["salt_val"] = sum_complexity + details["e_mult_val"] + v_diff_sum_for_salt
        details["total_xp"] = int(math.ceil(main_xp + details["salt_val"]))
        
        return details

    def calculate_match_xp(self, villain_str, env, result, game_type, heroes_str):
        data = self.get_match_xp_breakdown(villain_str, env, result, game_type, heroes_str)
        return data["total_xp"] if data else 0

    def get_hero_mastery_map(self):
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT heroes, villain, environment, result, game_type FROM games")
        rows = c.fetchall()
        conn.close()
        hero_xp = defaultdict(int)
        for h_str, v_str, env, res, g_type in rows:
            xp = self.calculate_match_xp(v_str, env, res, g_type, h_str)
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
                data = self.get_match_xp_breakdown(v_str, env, res, g_type, h_str)
                if data:
                    total_xp += data["total_xp"]
                    match_log.append(data)

        m_level = total_xp // 1000
        m_curr = total_xp % 1000
        self.mastery_labels["bar_level"].configure(text=f"NÍVEL DE MAESTRIA: {m_level}")
        self.mastery_labels["bar_text"].configure(text=f"{m_curr} / 1000 XP (Total: {total_xp:,})")
        self.mastery_xp_bar.set(m_curr / 1000)

        for data in reversed(match_log):
            self.create_history_row(data)

        if not match_log:
            ctk.CTkLabel(self.mastery_history_frame, text="Nenhuma partida vitoriosa registrada.", text_color="gray").pack(pady=20)

    def create_history_row(self, data):
        container = ctk.CTkFrame(self.mastery_history_frame, fg_color=COLORS["bg_card"], corner_radius=6)
        container.pack(fill="x", pady=2, padx=5)

        header = ctk.CTkFrame(container, fg_color="transparent", height=35)
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(header, text=data["v_name"], font=FONTS["body_bold"], anchor="w").place(relx=0.02, rely=0.5, anchor="w", relwidth=0.45)
        ctk.CTkLabel(header, text=data["e_name"], font=FONTS["body"], text_color="gray", anchor="center").place(relx=0.5, rely=0.5, anchor="center", relwidth=0.3)
        ctk.CTkLabel(header, text=f"+{data['total_xp']} XP", font=FONTS["body_bold"], text_color=COLORS["mastery_text"], anchor="e").place(relx=0.98, rely=0.5, anchor="e", relwidth=0.2)

        detail = ctk.CTkFrame(container, fg_color="#1a1a1a", corner_radius=6)
        
        self._add_detail_row(detail, f"Vilão Base ({data['v_diff_mode']})", f"{data['v_base_xp']} XP")
        if data['team_bonus'] > 0:
            self._add_detail_row(detail, "Bônus de Time", f"+{data['team_bonus']} XP", COLORS["highlight"])
        
        mult_text = f"x{data['v_mult_val']:.2f}"
        self._add_detail_row(detail, "Multiplicador de Dificuldade", mult_text)
        
        if data.get("e_name") == "Zona de Batalha (5 Ambientes)":
             self._add_detail_row(detail, "Soma de Ambientes", "Calculado", COLORS["highlight"])
        else:
             env_math = f"{data['e_base_xp']} x {data['e_mult_val']} = {data['e_base_xp']*data['e_mult_val']}"
             self._add_detail_row(detail, f"Ambiente", f"+{env_math} XP")
        
        self._add_detail_row(detail, "Adicional de Composição", f"+{data['salt_val']} XP", COLORS["warning"])
        
        ctk.CTkFrame(detail, height=1, fg_color="#333").pack(fill="x", padx=10, pady=5)
        self._add_detail_row(detail, "TOTAL", f"{data['total_xp']} XP", COLORS["mastery_text"], FONTS["xp_total"])

        ctk.CTkFrame(detail, height=1, fg_color="#333").pack(fill="x", padx=10, pady=5)
        
        part_frame = ctk.CTkFrame(detail, fg_color="transparent")
        part_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(part_frame, text="HERÓIS:", font=FONTS["card_label"], text_color="gray").pack(anchor="w")
        ctk.CTkLabel(part_frame, text=", ".join(data['heroes_list']), font=FONTS["body"], text_color="white", wraplength=700, justify="left").pack(anchor="w", pady=(0, 5))
        
        if len(data['villains_list']) > 1:
            ctk.CTkLabel(part_frame, text="VILÕES:", font=FONTS["card_label"], text_color="gray").pack(anchor="w")
            ctk.CTkLabel(part_frame, text=", ".join(data['villains_list']), font=FONTS["body"], text_color="white", wraplength=700, justify="left").pack(anchor="w")

        def toggle(event=None):
            if detail.winfo_ismapped(): detail.pack_forget()
            else: detail.pack(fill="x", padx=5, pady=5)

        header.bind("<Button-1>", toggle)
        for child in header.winfo_children(): child.bind("<Button-1>", toggle)

    def _add_detail_row(self, parent, label, value, val_color="white", val_font=FONTS["xp_val"]):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        row.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(row, text=label, font=FONTS["xp_label"], text_color="gray", anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=value, font=val_font, text_color=val_color, anchor="e").pack(side="right")

    def get_hero_achievement_styles(self):
        mastery_map = self.get_hero_mastery_map()
        conn = sqlite3.connect('sentinels_history.db')
        c = conn.cursor()
        c.execute("SELECT heroes, villain, result, game_type FROM games")
        rows = c.fetchall()
        conn.close()
        hero_villains_normal, hero_villains_ultimate, hero_variants_wins = defaultdict(set), defaultdict(set), defaultdict(int)
        all_villains = set(SOLO_VILLAINS_DATA.keys()) 

        for h_str, v_str, res, g_type in rows:
            is_win = (res == "Vitória")
            if not is_win: continue
            h_list = h_str.split(",")
            villain_base, is_ultimate, is_normal = None, False, False
            if g_type == "SOLO" or g_type == "OBLIVAEON":
                if "(" in v_str:
                    villain_base = v_str.split(" (")[0]
                    if "(Ultimate)" in v_str: is_ultimate = True
                    if not any(x in v_str for x in ["(Ultimate)", "(Challenge)", "(Advanced)"]): is_normal = True
                else: villain_base = v_str; is_normal = True
            for h_full in h_list:
                h_base = h_full.split(" (")[0]
                hero_variants_wins[h_full] += 1
                if villain_base and villain_base in all_villains:
                    if is_normal: hero_villains_normal[h_base].add(villain_base)
                    if is_ultimate: hero_villains_ultimate[h_base].add(villain_base)

        style_map = {}
        for hero in HEROES_DATA.keys():
            style = {}
            level = mastery_map.get(hero, (0, 0))[0]
            
            icon_badge = ""
            
            if level >= 25000:
                style['text_color'] = COLORS["rank_sentinel"]
                icon_badge = "🛡" 
            elif level >= 10000:
                style['text_color'] = COLORS["rank_freedom"]
                icon_badge = "🦅" 
            elif level >= 7500:
                style['text_color'] = COLORS["rank_xtreme"]
                icon_badge = "⚡" 
            elif level >= 5000:
                style['text_color'] = COLORS["rank_prime"]
                icon_badge = "☀" 
            elif level >= 2500: 
                style['text_color'] = COLORS["rank_dark_watch"]
                icon_badge = "🎲" 
            elif level >= 1000: style['text_color'] = COLORS["rank_diamond"]
            elif level >= 500: style['text_color'] = COLORS["rank_platinum"]
            elif level >= 100: style['text_color'] = COLORS["rank_gold"]
            elif level >= 25: style['text_color'] = COLORS["rank_silver"]
            elif level >= 10: style['text_color'] = COLORS["rank_bronze"]
            else: style['text_color'] = "white"

            defeated_norm = len(hero_villains_normal[hero])
            defeated_ult = len(hero_villains_ultimate[hero])
            total_unique = len(all_villains)
            if total_unique > 0:
                if defeated_ult >= total_unique: style['border_color'] = COLORS["rank_gold"]
                elif defeated_norm >= total_unique: style['border_color'] = COLORS["rank_silver"]
            
            variants = HEROES_DATA.get(hero, [])
            star_count = 0
            if variants:
                for v in variants:
                    v_full = hero if v == "Base" else f"{hero} ({v})"
                    if hero_variants_wins[v_full] >= 100: star_count += 1
            
            final_icon = ""
            if icon_badge: final_icon += f"{icon_badge} "
            if star_count > 0: final_icon += ("★" * star_count)
            
            if final_icon: style['icon'] = final_icon

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
                if g_type == "SOLO" or g_type == "OBLIVAEON":
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

        total_xp_for_mr = 0

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
                
                xp = self.calculate_match_xp(v_str, env, res, g_type, h_str)
                total_xp_for_mr += xp

                v_list = v_str.split(",") if g_type == "TEAM" else [v_str]
                current_diff = "Normal"
                
                for v_full in v_list:
                    v_clean = v_full
                    is_ult = False; is_norm = False
                    
                    if g_type == "SOLO" or g_type == "OBLIVAEON":
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

        mr = total_xp_for_mr // 1000
        self.build_achievements_view(base_name, mr, unique_villains_norm, unique_villains_ult, var_stats)
        self.update_mastery_history_list(base_name)

        def update_list(label_key, data_map):
            txt = ""
            sorted_items = sorted(data_map.items(), key=lambda x: x[1][1], reverse=True)
            for name, stats in sorted_items:
                v_wr = (stats[0]/stats[1])*100 if stats[1] > 0 else 0
                txt += f"{v_wr:>5.0f}% WR | {stats[1]:>3} J | {name}\n"
                txt += "─"*45 + "\n"
            if not txt: txt = "Sem dados."
            self.agg_lists_frames[label_key].configure(text=txt)

        update_list("VARIANTES", var_stats)
        update_list("VILÕES ENFRENTADOS", villain_stats)
        update_list("AMBIENTES JOGADOS", env_stats)

    def build_achievements_view(self, hero_name, mastery_level, villains_norm, villains_ult, var_stats):
        for widget in self.scroll_achieve.winfo_children(): widget.destroy()

        ranks = [
            (10, "Bronze", COLORS["rank_bronze"]), 
            (25, "Prata", COLORS["rank_silver"]), 
            (100, "Ouro", COLORS["rank_gold"]), 
            (500, "Platina", COLORS["rank_platinum"]), 
            (1000, "Diamante", COLORS["rank_diamond"]), 
            (2500, "Dark Watch (🎲)", COLORS["rank_dark_watch"]),
            (5000, "Prime Wardens (☀)", COLORS["rank_prime"]),
            (7500, "XTREME PW (⚡)", COLORS["rank_xtreme"]),
            (10000, "Freedom Five (🦅)", COLORS["rank_freedom"]),
            (25000, "SENTINEL (🛡)", COLORS["rank_sentinel"])
        ]
        
        curr_rank, curr_color, next_goal, next_rank_name = "Sem Ranque", "gray", 10, "Bronze"
        for w, n, c in ranks:
            if mastery_level >= w: curr_rank, curr_color = n, c
            else: next_goal, next_rank_name = w, n; break
        
        prog = 1.0 if mastery_level >= 25000 else mastery_level / next_goal
        disp_next = "MÁXIMO ALCANÇADO" if mastery_level >= 25000 else f"Próximo: {next_rank_name} ({next_goal} MR)"

        self.create_achievement_card("RANQUE DE HERÓI (MR)", f"Atual: {curr_rank}", mastery_level, next_goal, prog, curr_color, disp_next)

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
    
    def create_achievement_card(self, title, status, val, max_val, prog_val, color, desc, missing_list=None):
        card = ctk.CTkFrame(self.scroll_achieve, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=10)
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(top, text=title, font=FONTS["h3"], text_color=color).pack(side="left")
        ctk.CTkLabel(top, text=status, font=FONTS["body_bold"], text_color="white").pack(side="right")
        
        bar = ctk.CTkProgressBar(card, height=10, progress_color=color)
        bar.pack(fill="x", padx=15, pady=5)
        bar.set(prog_val)
        
        ctk.CTkLabel(card, text=desc, font=FONTS["body"], text_color="gray").pack(anchor="w", padx=15, pady=(0, 15))

        if missing_list:
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            def show_missing():
                top = ctk.CTkToplevel(self)
                top.title(f"Faltam: {title}")
                top.geometry("400x500")
                top.transient(self)
                scroll = ctk.CTkScrollableFrame(top)
                scroll.pack(fill="both", expand=True)
                for m in missing_list:
                    ctk.CTkLabel(scroll, text=f"• {m}", font=FONTS["body"], anchor="w").pack(fill="x", padx=10, pady=2)

            if len(missing_list) > 0:
                ctk.CTkButton(btn_frame, text=f"Ver Faltantes ({len(missing_list)})", command=show_missing, height=24, 
                              fg_color="#333", font=FONTS["body"]).pack(side="right")

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
        res = self.seg_result.get()
        
        env = None
        g_type = "SOLO"
        v_str = ""
        
        if mode == "Solo":
            g_type = "SOLO"
            env = self.selected_env
            if not env: return messagebox.showwarning("Atenção", "Selecione um Ambiente.")
            
            v = self.selected_villain
            if not v: return messagebox.showwarning("Atenção", "Selecione um Vilão.")
            m = self.selected_villain_diff if self.selected_villain_diff else "Normal"
            v_str = v if m == "Normal" else f"{v} ({m})"
            
        elif mode == "Time de Vilões":
            g_type = "TEAM"
            env = self.selected_env
            if not env: return messagebox.showwarning("Atenção", "Selecione um Ambiente.")
            
            lst = []
            for sel in self.team_selectors:
                val = sel.get_selection()
                if val: lst.append(val)
            if len(lst) < 3: return messagebox.showwarning("Atenção", "Selecione 3+ vilões.")
            if len(lst) != len(set(lst)): return messagebox.showwarning("Atenção", "Vilões duplicados.")
            v_str = ",".join(lst)
            
        elif mode == "OblivAeon":
            g_type = "OBLIVAEON"
            
            env_lst = []
            for sel in self.obliv_env_selectors:
                val = sel.get_selection()
                if val: env_lst.append(val)
            
            if len(env_lst) < 5: return messagebox.showwarning("Atenção", "Selecione TODOS os 5 ambientes para o modo OblivAeon.")
            env = ",".join(env_lst)
            
            diff = self.combo_oblivaeon_diff.get()
            v_str = f"OblivAeon ({diff})" if diff != "Normal" else "OblivAeon"

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
            if self.combo_solo_mode: self.combo_solo_mode.set("Normal")
            
            for s in self.team_selectors: s.reset()
            for s in self.obliv_env_selectors: s.reset()
            self.combo_oblivaeon_diff.set("Normal")
            
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
            
            if g_t == "OBLIVAEON":
                e_list = e.split(",")
                for ev in e_list:
                    e_stats[ev][0]+=w; e_stats[ev][1]+=1
            else:
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
        raw_mode = self.seg_stats_mode.get() if self.seg_stats_mode else "Stats Solo"
        mode_map = {"Stats Solo": "SOLO", "Stats Time": "TEAM"} 
        
        mode = mode_map.get(raw_mode, "SOLO")
        
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