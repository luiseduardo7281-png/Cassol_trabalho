#!/usr/bin/env python3
"""
NeuroConnect - Agenda inteligente para pessoas neurodivergentes
Instale: pip install customtkinter pygame
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json, os, threading, time, uuid, hashlib, math, io, wave
from datetime import datetime, date, timedelta
import array as arr_mod

try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 1, 1024)
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  PALETAS DE CORES
# ══════════════════════════════════════════════════════════════════════════════
TEMAS = {
    "Bege Suave": {
        "fundo": "#F5EDD8", "card": "#EDE0C4", "borda": "#C8B89A",
        "texto": "#3D2B1F", "texto_sec": "#7A6050", "superficie": "#FBF6EE",
        "vermelho": "#B03020", "modo_ctk": "light",
    },
    "Azul Calmo": {
        "fundo": "#DDE8F2", "card": "#C8D8EC", "borda": "#9AB8D8",
        "texto": "#1A2F4A", "texto_sec": "#3A6A9A", "superficie": "#EEF4FA",
        "vermelho": "#B03020", "modo_ctk": "light",
    },
    "Verde Floresta": {
        "fundo": "#E0EEE0", "card": "#C8DEC8", "borda": "#9AC49A",
        "texto": "#1A3A1A", "texto_sec": "#3A7A3A", "superficie": "#F0F8F0",
        "vermelho": "#B03020", "modo_ctk": "light",
    },
    "Lavanda": {
        "fundo": "#EDE8F8", "card": "#DCD4F4", "borda": "#B8A8E8",
        "texto": "#2D1A4A", "texto_sec": "#6A4A9A", "superficie": "#F6F2FC",
        "vermelho": "#B03020", "modo_ctk": "light",
    },
    "Modo Escuro": {
        "fundo": "#1E1E2E", "card": "#313244", "borda": "#45475A",
        "texto": "#CDD6F4", "texto_sec": "#A6ADC8", "superficie": "#24243E",
        "vermelho": "#F38BA8", "modo_ctk": "dark",
    },
    "Roxo Noturno": {
        "fundo": "#1A1B2E", "card": "#252640", "borda": "#3D3F6E",
        "texto": "#E0DEFF", "texto_sec": "#9B9BC8", "superficie": "#20213A",
        "vermelho": "#FF7B9C", "modo_ctk": "dark",
    },
    "Verde Noturno": {
        "fundo": "#141F1A", "card": "#1E302A", "borda": "#2E5040",
        "texto": "#C4EDE4", "texto_sec": "#7ABBA8", "superficie": "#192620",
        "vermelho": "#FF7F7F", "modo_ctk": "dark",
    },
}

NOME_TEMA_PADRAO = "Bege Suave"
T = dict(TEMAS[NOME_TEMA_PADRAO])

LARANJA     = "#F5893C"
LARANJA_ESC = "#D96E20"
VERDE_COR   = "#4CAF50"
VERDE_ESC   = "#388E3C"
ROXO        = "#5C5FA6"
ROXO_ESC    = "#44478A"
CIANO       = "#2BBFA0"

CORES_ROTINA_PADRAO = {
    "Rotina Pessoal":   LARANJA,
    "Rotina Academica": VERDE_COR,
}
PALETA_CORES = [
    ("Laranja", "#F5893C"), ("Verde",    "#4CAF50"), ("Roxo",    "#5C5FA6"),
    ("Azul",    "#2196F3"), ("Rosa",     "#E91E63"), ("Vermelho","#E53935"),
    ("Ciano",   "#00BCD4"), ("Amarelo",  "#FF9800"), ("Marrom",  "#795548"),
]
DIAS_SEMANA = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
DADOS_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")

HUMOR_OPCOES = [
    ("😴", "Cansado",    "#9B9BC8", "Tudo bem, vá com calma hoje."),
    ("😐", "Normal",     CIANO,     "Bom dia! Sua rotina está pronta."),
    ("⚡", "Energético", LARANJA,   "Ótimo! Aproveite a energia!"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SONS
# ══════════════════════════════════════════════════════════════════════════════
SONS_BUILTIN = ["Suave", "Sino", "Duplo", "Neutro", "Silêncio"]
SOM_PADRAO   = "Suave"
RECEITAS_SOM = {
    "Suave":    [(440, 0.50)],
    "Sino":     [(880, 0.18), (0, 0.06), (660, 0.34)],
    "Duplo":    [(523, 0.14), (0, 0.10), (659, 0.14)],
    "Neutro":   [(330, 0.55)],
    "Silêncio": [],
}

def _gerar_pcm(freq, duracao, volume=0.45, sr=44100):
    n = int(sr * duracao)
    if freq == 0 or n == 0:
        return [0] * n
    fade = min(int(sr * 0.02), n // 4)
    s = []
    for i in range(n):
        v = math.sin(2 * math.pi * freq * i / sr) * volume
        if i < fade:      v *= i / fade
        elif i > n - fade: v *= (n - i) / fade
        s.append(int(v * 32767))
    return s

def _pcm_para_wav(samples, sr=44100):
    buf = io.BytesIO()
    a = arr_mod.array('h', samples)
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(a.tobytes())
    buf.seek(0)
    return buf

def tocar_som(nome_som, arquivo_custom=None):
    if not PYGAME_OK:
        return
    if arquivo_custom and os.path.exists(arquivo_custom):
        try:
            pygame.mixer.music.load(arquivo_custom)
            pygame.mixer.music.play()
        except Exception:
            pass
        return
    if nome_som == "Silêncio" or nome_som not in RECEITAS_SOM:
        return
    pcm = []
    for freq, dur in RECEITAS_SOM[nome_som]:
        pcm.extend(_gerar_pcm(freq, dur))
    pygame.mixer.Sound(_pcm_para_wav(pcm)).play()

# ══════════════════════════════════════════════════════════════════════════════
#  FUNÇÕES UTILITÁRIAS
# ══════════════════════════════════════════════════════════════════════════════
def aplicar_tema(nome: str):
    global T
    T = dict(TEMAS[nome])
    ctk.set_appearance_mode(T["modo_ctk"])

def carregar_dados():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuarios": {}}

def salvar_dados(dados):
    with open(DADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def minutos_agora():
    n = datetime.now()
    return n.hour * 60 + n.minute

def str_para_minutos(hhmm):
    try:
        h, m = hhmm.strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return -1

def dia_hoje():
    return DIAS_SEMANA[datetime.now().weekday()]

def cor_de_rotina(nome, dados_usuario):
    return dados_usuario.get("cores_rotinas", {}).get(
        nome, CORES_ROTINA_PADRAO.get(nome, ROXO))

def escurecer(hex_cor, fator=0.80):
    r = max(0, int(int(hex_cor[1:3], 16) * fator))
    g = max(0, int(int(hex_cor[3:5], 16) * fator))
    b = max(0, int(int(hex_cor[5:7], 16) * fator))
    return f"#{r:02x}{g:02x}{b:02x}"

def saudacao():
    h = datetime.now().hour
    if h < 12: return "Bom dia"
    if h < 18: return "Boa tarde"
    return "Boa noite"

# ══════════════════════════════════════════════════════════════════════════════
#  LOGO
# ══════════════════════════════════════════════════════════════════════════════
class LogoCanvas(tk.Canvas):
    def __init__(self, master, tamanho=90, fundo=None, **kw):
        bg = fundo or T["superficie"]
        super().__init__(master, width=tamanho, height=tamanho // 2 + 10,
                         bg=bg, highlightthickness=0, **kw)
        self._desenhar(tamanho)

    def _desenhar(self, t):
        h = t // 2 + 10; r = h // 2 - 4
        cx1 = t // 2 - r + 2; cx2 = t // 2 + r - 2; cy = h // 2
        self.create_oval(cx1-r, cy-r, cx1+r, cy+r, outline=LARANJA, width=7, fill="")
        self.create_oval(cx2-r, cy-r, cx2+r, cy+r, outline=CIANO,   width=7, fill="")

# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO DE HUMOR
# ══════════════════════════════════════════════════════════════════════════════
class DialogoHumor(ctk.CTkToplevel):
    def __init__(self, master, usuario, dados, on_salvar, on_concluir):
        super().__init__(master)
        self.title("Como você está hoje?")
        self.geometry("420x260")
        self.grab_set()
        self.resizable(False, False)
        self.configure(fg_color=T["fundo"])
        self._usuario   = usuario
        self._dados     = dados
        self._on_salvar = on_salvar
        self._on_conc   = on_concluir
        self._construir()

    def _du(self):
        return self._dados["usuarios"].get(self._usuario, {})

    def _construir(self):
        tk.Frame(self, bg=LARANJA, height=6).pack(fill="x")
        ctk.CTkLabel(self, text="Como você está hoje?",
                     font=("Helvetica", 17, "bold"),
                     text_color=T["texto"]).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Isso nos ajuda a adaptar seus lembretes.",
                     font=("Helvetica", 11),
                     text_color=T["texto_sec"]).pack()

        bf = tk.Frame(self, bg=T["fundo"])
        bf.pack(pady=20)
        for emoji, nome, cor, msg in HUMOR_OPCOES:
            f = tk.Frame(bf, bg=T["card"], cursor="hand2", bd=0)
            f.pack(side="left", padx=10, ipadx=16, ipady=10)
            tk.Label(f, text=emoji, bg=T["card"], font=("Helvetica", 30)).pack()
            tk.Label(f, text=nome, bg=T["card"], fg=cor,
                     font=("Helvetica", 10, "bold")).pack()

            def escolher(n=nome, c=cor, m=msg):
                self._du()["humor_hoje"] = {
                    "data": date.today().isoformat(),
                    "nivel": n, "cor": c, "mensagem": m,
                }
                self._on_salvar()
                self._on_conc()
                self.destroy()

            f.bind("<Button-1>", lambda e, fn=escolher: fn())
            for w in f.winfo_children():
                w.bind("<Button-1>", lambda e, fn=escolher: fn())

        ctk.CTkButton(self, text="Pular por hoje", width=140, height=28,
                      fg_color=T["card"], hover_color=T["borda"],
                      text_color=T["texto_sec"], font=("Helvetica", 10),
                      command=lambda: [self._on_conc(), self.destroy()]).pack()

# ══════════════════════════════════════════════════════════════════════════════
#  TELA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════
class TelaLogin(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=T["fundo"])
        self.app = master
        self._construir()

    def _construir(self):
        self.grid_rowconfigure(list(range(8)), weight=1)
        self.grid_columnconfigure(0, weight=1)

        lf = tk.Frame(self, bg=T["fundo"])
        lf.grid(row=1, column=0, pady=(20, 4))
        LogoCanvas(lf, tamanho=120, fundo=T["fundo"]).pack()

        ctk.CTkLabel(self, text="NeuroConnect", font=("Helvetica", 26, "bold"),
                     text_color=T["texto"]).grid(row=2, column=0, pady=(0, 2))
        ctk.CTkLabel(self, text="Organizador e otimizador de tarefas",
                     font=("Helvetica", 12),
                     text_color=T["texto_sec"]).grid(row=3, column=0, pady=(0, 16))

        form = ctk.CTkFrame(self, fg_color=T["card"], corner_radius=16)
        form.grid(row=4, column=0, padx=70, pady=8, sticky="ew")
        form.grid_columnconfigure(0, weight=1)

        def lbl(txt, rn):
            ctk.CTkLabel(form, text=txt, font=("Helvetica", 12),
                         text_color=T["texto"]).grid(
                         row=rn, column=0, sticky="w", padx=22, pady=(12, 2))

        lbl("Usuário", 0)
        self.e_user = ctk.CTkEntry(form, placeholder_text="Digite seu usuário",
                                   height=38, corner_radius=8)
        self.e_user.grid(row=1, column=0, padx=22, sticky="ew")

        lbl("Senha", 2)
        self.e_senha = ctk.CTkEntry(form, placeholder_text="Digite sua senha",
                                    show="*", height=38, corner_radius=8)
        self.e_senha.grid(row=3, column=0, padx=22, sticky="ew")
        self.e_senha.bind("<Return>", lambda e: self._entrar())

        ctk.CTkButton(form, text="Entrar", height=44, corner_radius=22,
                      fg_color=LARANJA, hover_color=LARANJA_ESC,
                      font=("Helvetica", 14, "bold"),
                      command=self._entrar).grid(
                      row=4, column=0, padx=22, pady=(16, 8), sticky="ew")

        ctk.CTkButton(form, text="Criar Conta", height=44, corner_radius=22,
                      fg_color=T["superficie"], hover_color=T["card"],
                      text_color=LARANJA, border_width=2, border_color=LARANJA,
                      font=("Helvetica", 13),
                      command=self._criar_conta).grid(
                      row=5, column=0, padx=22, pady=(0, 16), sticky="ew")

        self.lbl_erro = ctk.CTkLabel(self, text="", text_color=T["vermelho"],
                                     font=("Helvetica", 11))
        self.lbl_erro.grid(row=5, column=0, pady=4)

    def _entrar(self):
        usuario = self.e_user.get().strip()
        senha   = self.e_senha.get()
        if not usuario or not senha:
            self.lbl_erro.configure(text="Preencha usuário e senha.")
            return
        dados = carregar_dados()
        u = dados["usuarios"].get(usuario)
        if u and u["senha"] == hash_senha(senha):
            if u.get("tema", NOME_TEMA_PADRAO) in TEMAS:
                aplicar_tema(u["tema"])
            self.app.abrir_principal(usuario, dados)
        else:
            self.lbl_erro.configure(text="Usuário ou senha incorretos.")

    def _criar_conta(self):
        jan = ctk.CTkToplevel(self)
        jan.title("Criar Conta"); jan.geometry("420x420")
        jan.grab_set(); jan.resizable(False, False)
        jan.configure(fg_color=T["fundo"])

        cab = tk.Frame(jan, bg=LARANJA, height=54)
        cab.pack(fill="x")
        tk.Label(cab, text="Criar nova conta", bg=LARANJA, fg="#FFFFFF",
                 font=("Helvetica", 16, "bold")).pack(pady=14)

        corpo = tk.Frame(jan, bg=T["fundo"])
        corpo.pack(fill="both", expand=True, padx=36, pady=12)

        def campo(parent, label_txt, show=None):
            ctk.CTkLabel(parent, text=label_txt, font=("Helvetica", 12),
                         text_color=T["texto"]).pack(anchor="w", pady=(10, 2))
            e = ctk.CTkEntry(parent, height=40, show=show or "")
            e.pack(fill="x"); return e

        e_user  = campo(corpo, "Usuário")
        e_senha = campo(corpo, "Senha", show="*")
        e_conf  = campo(corpo, "Confirmar senha", show="*")

        lbl_err = ctk.CTkLabel(corpo, text="", text_color=T["vermelho"],
                               font=("Helvetica", 11))
        lbl_err.pack(pady=(8, 0))

        def salvar():
            user = e_user.get().strip()
            s1, s2 = e_senha.get(), e_conf.get()
            if not user or not s1:
                lbl_err.configure(text="Preencha todos os campos."); return
            if s1 != s2:
                lbl_err.configure(text="Senhas não coincidem."); return
            dados = carregar_dados()
            if user in dados["usuarios"]:
                lbl_err.configure(text="Usuário já existe."); return
            dados["usuarios"][user] = {
                "senha": hash_senha(s1), "tema": NOME_TEMA_PADRAO,
                "som_nome": SOM_PADRAO, "som_arquivo": None,
                "cores_rotinas": {}, "conclusoes": {},
                "rotinas": {"Rotina Pessoal": [], "Rotina Academica": []},
            }
            salvar_dados(dados)
            messagebox.showinfo("Conta criada",
                                f"Conta '{user}' criada com sucesso!", parent=jan)
            jan.destroy()

        rodape = tk.Frame(jan, bg=T["fundo"])
        rodape.pack(fill="x", padx=36, pady=(4, 16))
        ctk.CTkButton(rodape, text="Criar Conta", height=50, corner_radius=25,
                      fg_color=LARANJA, hover_color=LARANJA_ESC,
                      text_color="#FFFFFF", font=("Helvetica", 15, "bold"),
                      command=salvar).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(rodape, text="Cancelar", height=38, corner_radius=19,
                      fg_color=T["card"], hover_color=T["borda"],
                      text_color=T["texto"], font=("Helvetica", 12),
                      command=jan.destroy).pack(fill="x")

# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGO DE TAREFA
# ══════════════════════════════════════════════════════════════════════════════
class DialogoTarefa(ctk.CTkToplevel):
    def __init__(self, master, cor, tarefa=None):
        super().__init__(master)
        self.title("Nova Tarefa" if tarefa is None else "Editar Tarefa")
        self.geometry("440x580"); self.resizable(False, False)
        self.grab_set(); self.configure(fg_color=T["fundo"])
        self.resultado = None
        self._cor = cor; self._tarefa = tarefa or {}
        self._construir()

    def _construir(self):
        cab = tk.Frame(self, bg=self._cor, height=52); cab.pack(fill="x")
        tk.Label(cab, text="Nova Tarefa" if not self._tarefa else "Editar Tarefa",
                 bg=self._cor, fg="#FFFFFF",
                 font=("Helvetica", 15, "bold")).pack(pady=14)

        corpo = ctk.CTkScrollableFrame(self, fg_color=T["superficie"])
        corpo.pack(fill="both", expand=True, padx=16, pady=12)

        def lbl(pai, txt):
            ctk.CTkLabel(pai, text=txt, font=("Helvetica", 12, "bold"),
                         text_color=T["texto"]).pack(anchor="w", pady=(8, 2))

        lbl(corpo, "Nome da tarefa")
        self.e_nome = ctk.CTkEntry(corpo, placeholder_text="Ex: Ler Livro", height=36)
        self.e_nome.pack(fill="x")
        if self._tarefa.get("nome"): self.e_nome.insert(0, self._tarefa["nome"])

        lbl(corpo, "Dias da semana")
        df = ctk.CTkFrame(corpo, fg_color=T["card"], corner_radius=8); df.pack(fill="x", pady=4)
        dr = tk.Frame(df, bg=T["card"]); dr.pack(pady=6)
        self._vars_dias = {}
        for d in DIAS_SEMANA:
            var = tk.BooleanVar(value=d in self._tarefa.get("dias", []))
            self._vars_dias[d] = var
            tk.Checkbutton(dr, text=d, variable=var, bg=T["card"], fg=T["texto"],
                           selectcolor=self._cor, font=("Helvetica", 10, "bold"),
                           activebackground=T["card"],
                           activeforeground=T["texto"]).pack(side="left", padx=3)

        hf = tk.Frame(corpo, bg=T["superficie"]); hf.pack(fill="x", pady=4)
        ci = tk.Frame(hf, bg=T["superficie"]); ci.pack(side="left", expand=True, fill="x", padx=(0,8))
        lbl(ci, "Início (HH:MM)")
        self.e_inicio = ctk.CTkEntry(ci, placeholder_text="15:45", height=36); self.e_inicio.pack(fill="x")
        if self._tarefa.get("inicio"): self.e_inicio.insert(0, self._tarefa["inicio"])

        cf = tk.Frame(hf, bg=T["superficie"]); cf.pack(side="left", expand=True, fill="x")
        lbl(cf, "Fim (HH:MM)")
        self.e_fim = ctk.CTkEntry(cf, placeholder_text="16:45", height=36); self.e_fim.pack(fill="x")
        if self._tarefa.get("fim"): self.e_fim.insert(0, self._tarefa["fim"])

        lbl(corpo, "Lembretes / Notas")
        self.e_lem = ctk.CTkTextbox(corpo, height=90, corner_radius=8,
                                    fg_color=T["card"], text_color=T["texto"])
        self.e_lem.pack(fill="x")
        if self._tarefa.get("lembretes"):
            self.e_lem.insert("0.0", "\n".join(self._tarefa["lembretes"]))

        bf = tk.Frame(self, bg=T["fundo"]); bf.pack(fill="x", padx=16, pady=12)
        ctk.CTkButton(bf, text="Cancelar", width=120, fg_color=T["card"],
                      hover_color=T["borda"], text_color=T["texto"],
                      command=self.destroy).pack(side="left")
        ctk.CTkButton(bf, text="Salvar", width=120, fg_color=self._cor,
                      hover_color=escurecer(self._cor), text_color="#FFFFFF",
                      command=self._salvar).pack(side="right")

    def _salvar(self):
        nome = self.e_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome da tarefa.", parent=self); return
        dias = [d for d, v in self._vars_dias.items() if v.get()]
        if not dias:
            messagebox.showwarning("Atenção", "Selecione pelo menos um dia.", parent=self); return
        inicio = self.e_inicio.get().strip(); fim = self.e_fim.get().strip()
        if str_para_minutos(inicio) < 0 or str_para_minutos(fim) < 0:
            messagebox.showwarning("Atenção", "Use o formato HH:MM nos horários.", parent=self); return
        lem_txt   = self.e_lem.get("0.0", "end").strip()
        lembretes = [l.strip() for l in lem_txt.split("\n") if l.strip()]
        self.resultado = {
            "id": self._tarefa.get("id", str(uuid.uuid4())),
            "nome": nome, "dias": dias,
            "inicio": inicio, "fim": fim, "lembretes": lembretes,
        }
        self.destroy()

# ══════════════════════════════════════════════════════════════════════════════
#  CARTÃO DE TAREFA (rotinas)
# ══════════════════════════════════════════════════════════════════════════════
class CartaoTarefa(ctk.CTkFrame):
    def __init__(self, master, tarefa, cor, on_editar, on_deletar, **kw):
        super().__init__(master, fg_color=T["superficie"], corner_radius=10,
                         border_width=1, border_color=T["borda"], **kw)
        self._construir(tarefa, cor, on_editar, on_deletar)

    def _construir(self, t, cor, on_edit, on_del):
        self.grid_columnconfigure(1, weight=1)
        barra = tk.Frame(self, bg=cor, width=6)
        barra.grid(row=0, column=0, rowspan=3, sticky="ns"); barra.grid_propagate(False)
        linha = tk.Frame(self, bg=T["superficie"])
        linha.grid(row=0, column=1, sticky="ew", pady=(6,0), padx=10)
        tk.Label(linha, text=t["nome"], bg=T["superficie"], fg=T["texto"],
                 font=("Helvetica", 12, "bold")).pack(side="left")
        tk.Label(linha, text="  " + " · ".join(t.get("dias", [])),
                 bg=T["superficie"], fg=T["texto_sec"], font=("Helvetica", 10)).pack(side="left")
        tk.Label(linha, text=f"{t.get('inicio','?')} – {t.get('fim','?')}",
                 bg=T["superficie"], fg=cor, font=("Helvetica", 11, "bold")).pack(side="right")
        if t.get("lembretes"):
            lf = tk.Frame(self, bg=T["superficie"])
            lf.grid(row=1, column=1, sticky="ew", padx=10)
            for lem in t["lembretes"]:
                tk.Label(lf, text=f"• {lem}", bg=T["superficie"], fg=T["texto_sec"],
                         font=("Helvetica", 10), wraplength=380, justify="left").pack(anchor="w")
        bf = tk.Frame(self, bg=T["superficie"])
        bf.grid(row=2, column=1, sticky="e", pady=(4,6), padx=10)
        ctk.CTkButton(bf, text="Editar", width=80, height=26, fg_color=T["card"],
                      hover_color=T["borda"], text_color=T["texto"], corner_radius=6,
                      command=on_edit).pack(side="left", padx=(0,4))
        ctk.CTkButton(bf, text="Deletar", width=82, height=26, fg_color=T["card"],
                      hover_color="#FFCCCC", text_color=T["vermelho"], corner_radius=6,
                      command=on_del).pack(side="left")

# ══════════════════════════════════════════════════════════════════════════════
#  CARTÃO DE TAREFA (aba Hoje — com checkbox)
# ══════════════════════════════════════════════════════════════════════════════
class CartaoTarefaHoje(ctk.CTkFrame):
    def __init__(self, master, tarefa, cor, concluida, on_toggle, **kw):
        alpha = T["superficie"] if not concluida else T["card"]
        super().__init__(master, fg_color=alpha, corner_radius=10,
                         border_width=1, border_color=T["borda"], **kw)
        self._construir(tarefa, cor, concluida, on_toggle)

    def _construir(self, t, cor, concluida, on_toggle):
        self.grid_columnconfigure(1, weight=1)
        barra_cor = cor if not concluida else T["borda"]
        barra = tk.Frame(self, bg=barra_cor, width=6)
        barra.grid(row=0, column=0, rowspan=2, sticky="ns"); barra.grid_propagate(False)

        linha = tk.Frame(self, bg=self.cget("fg_color") if not concluida else T["card"])
        linha.grid(row=0, column=1, sticky="ew", pady=(8,4), padx=10)

        txt_cor = T["texto_sec"] if concluida else T["texto"]
        prefixo = "✓  " if concluida else ""
        tk.Label(linha, text=prefixo + t["nome"],
                 bg=linha.cget("bg"), fg=txt_cor,
                 font=("Helvetica", 12, "bold")).pack(side="left")
        tk.Label(linha, text=f"  {t.get('inicio','?')} – {t.get('fim','?')}",
                 bg=linha.cget("bg"), fg=cor if not concluida else T["texto_sec"],
                 font=("Helvetica", 11, "bold")).pack(side="right")

        bf = tk.Frame(self, bg=self.cget("fg_color") if not concluida else T["card"])
        bf.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 6))
        if t.get("lembretes"):
            for lem in t["lembretes"]:
                tk.Label(bf, text=f"• {lem}", bg=bf.cget("bg"), fg=T["texto_sec"],
                         font=("Helvetica", 10), wraplength=360, justify="left").pack(anchor="w")

        btn_txt = "Desmarcar" if concluida else "Concluir"
        btn_cor = T["card"] if concluida else VERDE_COR
        btn_hov = T["borda"] if concluida else VERDE_ESC
        ctk.CTkButton(bf, text=btn_txt, width=100, height=26,
                      fg_color=btn_cor, hover_color=btn_hov,
                      text_color="#FFFFFF" if not concluida else T["texto"],
                      corner_radius=6,
                      command=on_toggle).pack(side="right")

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO DE ROTINA
# ══════════════════════════════════════════════════════════════════════════════
class SecaoRotina(ctk.CTkFrame):
    def __init__(self, master, nome, tarefas, cor, on_salvar, **kw):
        super().__init__(master, fg_color=T["fundo"], **kw)
        self._nome = nome; self._tarefas = tarefas
        self._cor = cor; self._on_salvar = on_salvar
        self._expandida = tk.BooleanVar(value=True)
        self._construir()

    def _construir(self):
        self.grid_columnconfigure(0, weight=1)
        self._cab = tk.Frame(self, bg=self._cor, cursor="hand2")
        self._cab.grid(row=0, column=0, sticky="ew", padx=4, pady=(4,0))
        self._cab.grid_columnconfigure(0, weight=1)
        tk.Label(self._cab, text=self._nome.upper(), bg=self._cor, fg="#FFFFFF",
                 font=("Helvetica", 13, "bold")).grid(row=0, column=0, sticky="w", padx=14, pady=10)
        self._seta = tk.Label(self._cab, text="▲", bg=self._cor, fg="#FFFFFF",
                              font=("Helvetica", 12))
        self._seta.grid(row=0, column=1, padx=14)
        self._cab.bind("<Button-1>", self._toggle)
        for w in self._cab.winfo_children(): w.bind("<Button-1>", self._toggle)
        self._corpo = ctk.CTkFrame(self, fg_color=T["superficie"], corner_radius=0)
        self._corpo.grid(row=1, column=0, sticky="ew", padx=4)
        self._corpo.grid_columnconfigure(0, weight=1)
        self._renderizar()

    def _toggle(self, _=None):
        if self._expandida.get():
            self._corpo.grid_remove(); self._seta.configure(text="▼")
        else:
            self._corpo.grid(); self._seta.configure(text="▲")
        self._expandida.set(not self._expandida.get())

    def _renderizar(self):
        for w in self._corpo.winfo_children(): w.destroy()
        if not self._tarefas:
            tk.Label(self._corpo, text="Nenhuma tarefa. Clique em '+' para adicionar.",
                     fg=T["texto_sec"], bg=T["superficie"],
                     font=("Helvetica", 10)).pack(pady=10)
        for tarefa in self._tarefas:
            CartaoTarefa(self._corpo, tarefa, self._cor,
                         on_editar=lambda t=tarefa: self._editar(t),
                         on_deletar=lambda t=tarefa: self._deletar(t)
                         ).pack(fill="x", padx=8, pady=4)
        ctk.CTkButton(self._corpo, text="+ Adicionar Tarefa", height=34, corner_radius=8,
                      fg_color=self._cor, hover_color=escurecer(self._cor),
                      text_color="#FFFFFF", font=("Helvetica", 12),
                      command=self._nova_tarefa).pack(pady=(6,10), padx=8, anchor="w")

    def _nova_tarefa(self):
        dlg = DialogoTarefa(self, self._cor)
        self.wait_window(dlg)
        if dlg.resultado:
            self._tarefas.append(dlg.resultado); self._on_salvar(); self._renderizar()

    def _editar(self, tarefa):
        dlg = DialogoTarefa(self, self._cor, tarefa)
        self.wait_window(dlg)
        if dlg.resultado:
            idx = next((i for i, t in enumerate(self._tarefas) if t["id"] == tarefa["id"]), -1)
            if idx >= 0: self._tarefas[idx] = dlg.resultado
            self._on_salvar(); self._renderizar()

    def _deletar(self, tarefa):
        if messagebox.askyesno("Confirmar", f"Deletar '{tarefa['nome']}'?"):
            self._tarefas[:] = [t for t in self._tarefas if t["id"] != tarefa["id"]]
            self._on_salvar(); self._renderizar()

# ══════════════════════════════════════════════════════════════════════════════
#  JANELA POMODORO
# ══════════════════════════════════════════════════════════════════════════════
class JanelaPomodoro(ctk.CTkToplevel):
    FOCO_SEG  = 25 * 60
    PAUSA_SEG = 5  * 60

    def __init__(self, master, tocar_fn):
        super().__init__(master)
        self.title("Modo Foco — Pomodoro")
        self.geometry("300x340")
        self.resizable(False, False)
        self.configure(fg_color=T["fundo"])
        self._tocar   = tocar_fn
        self._rodando = False
        self._foco    = True
        self._restante = self.FOCO_SEG
        self._ciclos   = 0
        self._after_id = None
        self._construir()

    def _construir(self):
        tk.Frame(self, bg=LARANJA, height=6).pack(fill="x")
        self._lbl_estado = ctk.CTkLabel(self, text="FOCO",
                           font=("Helvetica", 13, "bold"), text_color=LARANJA)
        self._lbl_estado.pack(pady=(14, 2))
        self._lbl_timer = ctk.CTkLabel(self, text="25:00",
                          font=("Helvetica", 52, "bold"), text_color=T["texto"])
        self._lbl_timer.pack()
        self._barra = ctk.CTkProgressBar(self, width=220, height=12,
                      fg_color=T["card"], progress_color=LARANJA)
        self._barra.set(1.0); self._barra.pack(pady=10)
        self._lbl_ciclo = ctk.CTkLabel(self, text="Ciclo 1 de 4",
                          font=("Helvetica", 10), text_color=T["texto_sec"])
        self._lbl_ciclo.pack()

        bf = tk.Frame(self, bg=T["fundo"]); bf.pack(pady=16)
        self._btn = ctk.CTkButton(bf, text="▶ Iniciar", width=120, height=40,
                   fg_color=LARANJA, hover_color=LARANJA_ESC,
                   text_color="#FFFFFF", font=("Helvetica", 13, "bold"),
                   command=self._toggle)
        self._btn.pack(side="left", padx=4)
        ctk.CTkButton(bf, text="↺ Resetar", width=90, height=40,
                      fg_color=T["card"], hover_color=T["borda"],
                      text_color=T["texto"], font=("Helvetica", 11),
                      command=self._resetar).pack(side="left", padx=4)

        ctk.CTkLabel(self, text="25 min foco  •  5 min pausa",
                     font=("Helvetica", 9), text_color=T["texto_sec"]).pack()

    def _toggle(self):
        if self._rodando: self._pausar()
        else:             self._iniciar()

    def _iniciar(self):
        self._rodando = True
        self._btn.configure(text="⏸ Pausar")
        self._tick()

    def _pausar(self):
        self._rodando = False
        self._btn.configure(text="▶ Continuar")
        if self._after_id: self.after_cancel(self._after_id)

    def _resetar(self):
        self._pausar()
        self._foco = True; self._restante = self.FOCO_SEG; self._ciclos = 0
        self._btn.configure(text="▶ Iniciar")
        self._atualizar()

    def _tick(self):
        if not self._rodando: return
        self._restante -= 1
        self._atualizar()
        if self._restante <= 0:
            self._fase_concluida()
        else:
            self._after_id = self.after(1000, self._tick)

    def _fase_concluida(self):
        threading.Thread(target=self._tocar, daemon=True).start()
        if self._foco:
            self._ciclos += 1; self._foco = False; self._restante = self.PAUSA_SEG
        else:
            self._foco = True; self._restante = self.FOCO_SEG
        self._rodando = False
        self._btn.configure(text="▶ Iniciar")
        self._atualizar()

    def _atualizar(self):
        total = self.FOCO_SEG if self._foco else self.PAUSA_SEG
        m = self._restante // 60; s = self._restante % 60
        self._lbl_timer.configure(text=f"{m:02d}:{s:02d}")
        self._barra.set(self._restante / total)
        if self._foco:
            self._lbl_estado.configure(text="FOCO", text_color=LARANJA)
            self._barra.configure(progress_color=LARANJA)
        else:
            self._lbl_estado.configure(text="PAUSA", text_color=VERDE_COR)
            self._barra.configure(progress_color=VERDE_COR)
        self._lbl_ciclo.configure(text=f"Ciclo {min(self._ciclos + 1, 4)} de 4")

    def destruir(self):
        if self._after_id: self.after_cancel(self._after_id)
        try: self.destroy()
        except Exception: pass

# ══════════════════════════════════════════════════════════════════════════════
#  ABA: HOJE
# ══════════════════════════════════════════════════════════════════════════════
class AbaHoje(ctk.CTkFrame):
    def __init__(self, master, usuario, dados, on_salvar, tocar_fn, **kw):
        super().__init__(master, fg_color=T["fundo"], **kw)
        self._usuario   = usuario
        self._dados     = dados
        self._on_salvar = on_salvar
        self._tocar_fn  = tocar_fn
        self._pomodoro  = None
        self._construir()

    def _du(self):
        return self._dados["usuarios"].get(self._usuario, {})

    def _hoje_str(self):
        return date.today().isoformat()

    def _tarefas_hoje(self):
        du = self._du(); hoje = dia_hoje()
        tarefas = []
        for nome_rotina, lista in du.get("rotinas", {}).items():
            for t in lista:
                if hoje in t.get("dias", []):
                    tarefas.append((nome_rotina, t))
        tarefas.sort(key=lambda x: str_para_minutos(x[1].get("inicio", "99:99")))
        return tarefas

    def _concluidas(self):
        return set(self._du().get("conclusoes", {}).get(self._hoje_str(), []))

    def _toggle_conclusao(self, task_id):
        du    = self._du()
        hoje  = self._hoje_str()
        lista = du.setdefault("conclusoes", {}).setdefault(hoje, [])
        if task_id in lista: lista.remove(task_id)
        else:                lista.append(task_id)
        self._on_salvar()
        self.atualizar()

    def _abrir_pomodoro(self):
        if self._pomodoro and self._pomodoro.winfo_exists():
            self._pomodoro.lift(); return
        self._pomodoro = JanelaPomodoro(self, self._tocar_fn)

    def atualizar(self):
        for w in self.winfo_children(): w.destroy()
        self._construir()

    def _construir(self):
        du       = self._du()
        tarefas  = self._tarefas_hoje()
        concluidas = self._concluidas()
        humor    = du.get("humor_hoje", {})
        tem_humor = humor.get("data") == self._hoje_str()

        # ── Cabeçalho ──
        cab = tk.Frame(self, bg=T["superficie"]); cab.pack(fill="x", padx=0, pady=0)
        esq = tk.Frame(cab, bg=T["superficie"]); esq.pack(side="left", padx=16, pady=12)

        titulo = f"{saudacao()}, {self._usuario}!"
        if tem_humor:
            emoji = next((o[0] for o in HUMOR_OPCOES if o[1] == humor.get("nivel")), "")
            titulo = f"{emoji} {titulo}"
        ctk.CTkLabel(esq, text=titulo, font=("Helvetica", 15, "bold"),
                     text_color=T["texto"]).pack(anchor="w")

        if tem_humor:
            ctk.CTkLabel(esq, text=humor.get("mensagem", ""),
                         font=("Helvetica", 11), text_color=T["texto_sec"]).pack(anchor="w")

        n_hoje    = len(tarefas)
        n_feitas  = len([1 for _, t in tarefas if t["id"] in concluidas])
        ctk.CTkLabel(esq, text=f"{n_feitas} de {n_hoje} tarefas concluídas hoje",
                     font=("Helvetica", 10), text_color=T["texto_sec"]).pack(anchor="w")

        ctk.CTkButton(cab, text="⏱ Modo Foco", width=110, height=34,
                      fg_color=ROXO, hover_color=ROXO_ESC,
                      text_color="#FFFFFF", font=("Helvetica", 11),
                      command=self._abrir_pomodoro).pack(side="right", padx=16, pady=14)

        # Barra de progresso do dia
        if n_hoje > 0:
            prog_frame = tk.Frame(self, bg=T["fundo"]); prog_frame.pack(fill="x", padx=16, pady=(4,0))
            barra = ctk.CTkProgressBar(prog_frame, height=8, fg_color=T["card"],
                                       progress_color=VERDE_COR)
            barra.set(n_feitas / n_hoje)
            barra.pack(fill="x")

        # ── Lista de tarefas ──
        scroll = ctk.CTkScrollableFrame(self, fg_color=T["fundo"])
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        scroll.grid_columnconfigure(0, weight=1)

        if not tarefas:
            ctk.CTkLabel(scroll,
                         text="Você não tem tarefas agendadas para hoje.\nCrie rotinas na aba Rotinas!",
                         font=("Helvetica", 12), text_color=T["texto_sec"],
                         justify="center").pack(pady=40)
            return

        agora = minutos_agora()
        for nome_rotina, t in tarefas:
            cor    = cor_de_rotina(nome_rotina, du)
            feita  = t["id"] in concluidas
            ini    = str_para_minutos(t.get("inicio", ""))
            fim    = str_para_minutos(t.get("fim", ""))
            em_andamento = ini <= agora <= fim and not feita

            f = tk.Frame(scroll, bg=T["fundo"]); f.pack(fill="x", pady=2)
            if em_andamento:
                tk.Label(f, text="● EM ANDAMENTO", bg=T["fundo"], fg=VERDE_COR,
                         font=("Helvetica", 8, "bold")).pack(anchor="w", padx=4)
            CartaoTarefaHoje(f, t, cor, feita,
                             on_toggle=lambda tid=t["id"]: self._toggle_conclusao(tid)
                             ).pack(fill="x", padx=4, pady=2)

# ══════════════════════════════════════════════════════════════════════════════
#  ABA: PROGRESSO
# ══════════════════════════════════════════════════════════════════════════════
class AbaProgresso(ctk.CTkFrame):
    def __init__(self, master, usuario, dados, **kw):
        super().__init__(master, fg_color=T["fundo"], **kw)
        self._usuario = usuario
        self._dados   = dados
        self._construir()

    def _du(self):
        return self._dados["usuarios"].get(self._usuario, {})

    def _streak(self):
        conclusoes = self._du().get("conclusoes", {})
        streak = 0; d = date.today()
        while True:
            if conclusoes.get(d.isoformat()):
                streak += 1; d -= timedelta(days=1)
            else:
                break
        return streak

    def atualizar(self):
        for w in self.winfo_children(): w.destroy()
        self._construir()

    def _construir(self):
        du         = self._du()
        conclusoes = du.get("conclusoes", {})
        streak     = self._streak()
        total      = sum(len(v) for v in conclusoes.values())

        scroll = ctk.CTkScrollableFrame(self, fg_color=T["fundo"])
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        # ── Streak ──
        sf = ctk.CTkFrame(scroll, fg_color=T["card"], corner_radius=16)
        sf.pack(fill="x", pady=(8, 12))

        emoji_streak = "🔥" if streak >= 3 else ("⭐" if streak >= 1 else "💤")
        ctk.CTkLabel(sf, text=f"{emoji_streak}  {streak} dias seguidos",
                     font=("Helvetica", 24, "bold"), text_color=LARANJA).pack(pady=(18, 4))

        if streak == 0:   msg = "Complete uma tarefa hoje para começar sua sequência!"
        elif streak < 3:  msg = "Boa! Continue assim para manter a sequência."
        elif streak < 7:  msg = "Incrível! Você está criando um hábito."
        else:             msg = f"🏆 Fantástico! {streak} dias de dedicação!"
        ctk.CTkLabel(sf, text=msg, font=("Helvetica", 11),
                     text_color=T["texto_sec"]).pack(pady=(0, 18))

        # ── Calendário 35 dias ──
        ctk.CTkLabel(scroll, text="Últimas 5 semanas",
                     font=("Helvetica", 13, "bold"),
                     text_color=T["texto"]).pack(anchor="w", pady=(4, 6))

        grade = tk.Frame(scroll, bg=T["fundo"]); grade.pack(anchor="w")

        dias_abrev = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for i, d in enumerate(dias_abrev):
            tk.Label(grade, text=d, bg=T["fundo"], fg=T["texto_sec"],
                     font=("Helvetica", 9), width=4).grid(row=0, column=i, padx=2)

        hoje   = date.today()
        # Iniciar no domingo passado (ou mais), para alinhar colunas à semana
        inicio = hoje - timedelta(days=hoje.weekday()) - timedelta(weeks=4)

        for i in range(35):
            d = inicio + timedelta(days=i)
            s = d.isoformat()
            futuro   = d > hoje
            tem_conc = bool(conclusoes.get(s)) if not futuro else False
            eh_hoje  = d == hoje

            if futuro:     cor = T["borda"]
            elif tem_conc: cor = VERDE_COR
            else:          cor = T["card"]

            bd    = 2 if eh_hoje else 0
            linha = i // 7; col = i % 7
            quadrado = tk.Frame(grade, bg=cor, width=30, height=30,
                                relief="solid" if eh_hoje else "flat",
                                bd=bd, highlightbackground=LARANJA if eh_hoje else cor,
                                highlightthickness=bd)
            quadrado.grid(row=linha + 1, column=col, padx=2, pady=2)
            quadrado.grid_propagate(False)
            if tem_conc:
                n = len(conclusoes.get(s, []))
                tk.Label(quadrado, text=str(n), bg=cor, fg="#FFFFFF",
                         font=("Helvetica", 8, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Legenda
        leg = tk.Frame(scroll, bg=T["fundo"]); leg.pack(anchor="w", pady=(8, 4))
        for cor, txt in [(VERDE_COR, "Tarefas concluídas"), (T["card"], "Sem conclusões"), (LARANJA, "Hoje")]:
            tk.Frame(leg, bg=cor, width=14, height=14).pack(side="left", padx=(0,4))
            tk.Label(leg, text=txt, bg=T["fundo"], fg=T["texto_sec"],
                     font=("Helvetica", 9)).pack(side="left", padx=(0,12))

        # ── Estatísticas ──
        stat = ctk.CTkFrame(scroll, fg_color=T["card"], corner_radius=12)
        stat.pack(fill="x", pady=12)
        stat.grid_columnconfigure((0,1,2), weight=1)

        dias_ativos = len([d for d, v in conclusoes.items() if v])
        for col, (val, label) in enumerate([
            (total,       "tarefas\nconcluídas"),
            (dias_ativos, "dias\nativos"),
            (streak,      "sequência\natual"),
        ]):
            f = tk.Frame(stat, bg=T["card"]); f.grid(row=0, column=col, padx=8, pady=12)
            tk.Label(f, text=str(val), bg=T["card"], fg=LARANJA,
                     font=("Helvetica", 22, "bold")).pack()
            tk.Label(f, text=label, bg=T["card"], fg=T["texto_sec"],
                     font=("Helvetica", 9), justify="center").pack()

# ══════════════════════════════════════════════════════════════════════════════
#  TELA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class TelaPrincipal(ctk.CTkFrame):
    def __init__(self, master, usuario, dados):
        super().__init__(master, fg_color=T["fundo"])
        self.app       = master
        self._usuario  = usuario
        self._dados    = dados
        self._notif_ativas = set()
        self._aba_ativa    = "Hoje"
        self._construir()
        self._iniciar_monitor()

    def _du(self):
        return self._dados["usuarios"].get(self._usuario, {})

    def _salvar(self):
        salvar_dados(self._dados)

    def _tocar(self):
        du = self._du()
        tocar_som(du.get("som_nome", SOM_PADRAO), du.get("som_arquivo"))

    # ── Construção ────────────────────────────────────────────────────────────
    def _construir(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._criar_barra_topo()
        self._criar_tabs_bar()
        self._criar_conteudo()
        self._criar_rodape()
        self._mostrar_aba("Hoje")

    def _criar_barra_topo(self):
        barra = tk.Frame(self, bg=T["superficie"], height=60)
        barra.grid(row=0, column=0, sticky="ew"); barra.grid_propagate(False)
        barra.grid_columnconfigure(1, weight=1)

        esq = tk.Frame(barra, bg=T["superficie"]); esq.grid(row=0, column=0, padx=12, pady=10)
        LogoCanvas(esq, tamanho=44, fundo=T["superficie"]).pack(side="left")
        tk.Label(esq, text="NeuroConnect", bg=T["superficie"], fg=T["texto"],
                 font=("Helvetica", 14, "bold")).pack(side="left", padx=8)

        dir_ = tk.Frame(barra, bg=T["superficie"]); dir_.grid(row=0, column=2, padx=12)
        tk.Label(dir_, text=f"  {self._usuario}", bg=T["superficie"], fg=T["texto"],
                 font=("Helvetica", 11)).pack(side="left", padx=4)

        for txt, cmd, cor in [
            ("Tema",     self._escolher_tema,    T["card"]),
            ("Som",      self._escolher_som,     T["card"]),
            ("+ Rotina", self._nova_rotina,      ROXO),
            ("Sair",     self.app.voltar_login,  T["card"]),
        ]:
            ctk.CTkButton(dir_, text=txt, width=80, height=30,
                          fg_color=cor,
                          hover_color=escurecer(cor) if cor == ROXO else T["borda"],
                          text_color="#FFFFFF" if cor == ROXO else T["texto"],
                          font=("Helvetica", 11),
                          command=cmd).pack(side="left", padx=3)

    def _criar_tabs_bar(self):
        self._tab_bar = tk.Frame(self, bg=T["card"], height=42)
        self._tab_bar.grid(row=1, column=0, sticky="ew"); self._tab_bar.grid_propagate(False)
        self._tab_btns = {}
        for nome in ["Hoje", "Rotinas", "Progresso"]:
            btn = tk.Label(self._tab_bar, text=nome, bg=T["card"], fg=T["texto_sec"],
                           font=("Helvetica", 11), cursor="hand2", padx=20, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=nome: self._mostrar_aba(n))
            self._tab_btns[nome] = btn

    def _criar_conteudo(self):
        self._frame_conteudo = tk.Frame(self, bg=T["fundo"])
        self._frame_conteudo.grid(row=2, column=0, sticky="nsew")
        self._frame_conteudo.grid_rowconfigure(0, weight=1)
        self._frame_conteudo.grid_columnconfigure(0, weight=1)

        self._aba_hoje     = AbaHoje(self._frame_conteudo, self._usuario,
                                     self._dados, self._salvar, self._tocar)
        self._aba_rotinas  = self._criar_aba_rotinas()
        self._aba_progresso = AbaProgresso(self._frame_conteudo, self._usuario, self._dados)

        for aba in [self._aba_hoje, self._aba_rotinas, self._aba_progresso]:
            aba.grid(row=0, column=0, sticky="nsew")

    def _criar_aba_rotinas(self):
        frame = ctk.CTkFrame(self._frame_conteudo, fg_color=T["fundo"])
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(frame, fg_color=T["fundo"],
                                         label_text="Minhas Rotinas",
                                         label_font=("Helvetica", 13, "bold"),
                                         label_fg_color=T["fundo"],
                                         label_text_color=T["texto"])
        scroll.grid(row=0, column=0, sticky="nsew", padx=16, pady=8)
        scroll.grid_columnconfigure(0, weight=1)
        self._scroll_rotinas = scroll
        self._renderizar_rotinas()
        return frame

    def _renderizar_rotinas(self):
        for w in self._scroll_rotinas.winfo_children(): w.destroy()
        du = self._du(); rotinas = du.get("rotinas", {})
        if not rotinas:
            tk.Label(self._scroll_rotinas,
                     text="Nenhuma rotina. Clique em '+ Rotina' para começar.",
                     fg=T["texto_sec"], bg=T["fundo"], font=("Helvetica", 11)).pack(pady=40)
            return
        for nome, tarefas in rotinas.items():
            cor = cor_de_rotina(nome, du)
            SecaoRotina(self._scroll_rotinas, nome, tarefas, cor,
                        on_salvar=self._salvar).pack(fill="x", pady=5)

    def _criar_rodape(self):
        rod = tk.Frame(self, bg=T["superficie"], height=30)
        rod.grid(row=3, column=0, sticky="ew"); rod.grid_propagate(False)
        tk.Label(rod, text="NeuroConnect — tecnologia inteligente que organiza, conecta e inclui.",
                 bg=T["superficie"], fg=T["texto_sec"], font=("Helvetica", 9)).pack(side="right", padx=12, pady=6)

    def _mostrar_aba(self, nome):
        self._aba_ativa = nome
        mapa = {"Hoje": self._aba_hoje, "Rotinas": self._aba_rotinas, "Progresso": self._aba_progresso}
        for n, f in mapa.items():
            if n == nome: f.tkraise()
        for n, btn in self._tab_btns.items():
            if n == nome:
                btn.configure(bg=T["superficie"], fg=LARANJA, font=("Helvetica", 11, "bold"))
            else:
                btn.configure(bg=T["card"], fg=T["texto_sec"], font=("Helvetica", 11))
        if nome == "Hoje":
            self._aba_hoje.atualizar()
        elif nome == "Progresso":
            self._aba_progresso.atualizar()

    # ── Escolher tema ─────────────────────────────────────────────────────────
    def _escolher_tema(self):
        jan = ctk.CTkToplevel(self)
        jan.title("Escolher Tema"); jan.geometry("400x500")
        jan.grab_set(); jan.resizable(False, False); jan.configure(fg_color=T["fundo"])

        ctk.CTkLabel(jan, text="Escolha a paleta de cores",
                     font=("Helvetica", 15, "bold"), text_color=T["texto"]).pack(pady=(18,8))
        tema_atual = self._du().get("tema", NOME_TEMA_PADRAO)

        for nome_tema, cfg in TEMAS.items():
            sel = nome_tema == tema_atual
            linha = tk.Frame(jan, bg=cfg["superficie"],
                             relief="solid" if sel else "flat", bd=2 if sel else 0, cursor="hand2")
            linha.pack(fill="x", padx=24, pady=3)
            amos = tk.Frame(linha, bg=cfg["superficie"]); amos.pack(side="left", padx=8, pady=6)
            for hc in [cfg["fundo"], cfg["card"], cfg["borda"]]:
                tk.Frame(amos, bg=hc, width=18, height=18).pack(side="left", padx=2)
            tk.Label(linha, text=nome_tema, bg=cfg["superficie"], fg=cfg["texto"],
                     font=("Helvetica", 12, "bold"), padx=4).pack(side="left")
            if sel:
                tk.Label(linha, text="  Em uso", bg=cfg["superficie"], fg=VERDE_COR,
                         font=("Helvetica", 10, "bold")).pack(side="right", padx=10)
            def ao_clicar(n=nome_tema):
                aplicar_tema(n); self._du()["tema"] = n; self._salvar()
                jan.destroy(); self.app.abrir_principal(self._usuario, self._dados)
            linha.bind("<Button-1>", lambda e, f=ao_clicar: f())
            for w in linha.winfo_children(): w.bind("<Button-1>", lambda e, f=ao_clicar: f())

        ctk.CTkButton(jan, text="Fechar", width=200, height=36,
                      fg_color=T["card"], hover_color=T["borda"],
                      text_color=T["texto"], command=jan.destroy).pack(pady=12)

    # ── Escolher som ─────────────────────────────────────────────────────────
    def _escolher_som(self):
        jan = ctk.CTkToplevel(self)
        jan.title("Escolher Som de Alerta"); jan.geometry("420x420")
        jan.grab_set(); jan.resizable(False, False); jan.configure(fg_color=T["fundo"])

        ctk.CTkLabel(jan, text="Som do aviso de tarefa",
                     font=("Helvetica", 15, "bold"), text_color=T["texto"]).pack(pady=(18,4))

        du = self._du(); som_var = tk.StringVar(value=du.get("som_nome", SOM_PADRAO))
        arq_atual = du.get("som_arquivo"); arq_var = tk.StringVar(value=arq_atual or "")

        if not PYGAME_OK:
            ctk.CTkLabel(jan, text="⚠  pip install pygame  para ativar sons",
                         font=("Helvetica", 11), text_color=T["vermelho"]).pack(pady=4)

        fs = ctk.CTkFrame(jan, fg_color=T["card"], corner_radius=10)
        fs.pack(fill="x", padx=24, pady=8)
        ctk.CTkLabel(fs, text="Sons embutidos", font=("Helvetica", 11, "bold"),
                     text_color=T["texto_sec"]).pack(anchor="w", padx=12, pady=(8,4))
        for ns in SONS_BUILTIN:
            linha = tk.Frame(fs, bg=T["card"]); linha.pack(fill="x", padx=12, pady=2)
            tk.Radiobutton(linha, text=ns, variable=som_var, value=ns,
                           bg=T["card"], fg=T["texto"], selectcolor=LARANJA,
                           activebackground=T["card"], activeforeground=T["texto"],
                           font=("Helvetica", 11)).pack(side="left")
            ctk.CTkButton(linha, text="▶ Testar", width=80, height=26,
                          fg_color=T["superficie"], hover_color=T["borda"],
                          text_color=T["texto"], font=("Helvetica", 10),
                          command=lambda n=ns: tocar_som(n)).pack(side="right")

        fc = ctk.CTkFrame(jan, fg_color=T["card"], corner_radius=10)
        fc.pack(fill="x", padx=24, pady=4)
        ctk.CTkLabel(fc, text="Som personalizado (WAV / MP3 / OGG)",
                     font=("Helvetica", 11, "bold"), text_color=T["texto_sec"]).pack(anchor="w", padx=12, pady=(8,4))
        lbl_arq = ctk.CTkLabel(fc, text=os.path.basename(arq_atual) if arq_atual else "Nenhum arquivo",
                               font=("Helvetica", 10), text_color=T["texto_sec"])
        lbl_arq.pack(anchor="w", padx=12)

        def escolher_arq():
            p = filedialog.askopenfilename(parent=jan, title="Escolher som",
                filetypes=[("Áudio", "*.wav *.mp3 *.ogg"), ("Todos", "*.*")])
            if p:
                arq_var.set(p); lbl_arq.configure(text=os.path.basename(p))
                som_var.set("__custom__")

        bfc = tk.Frame(fc, bg=T["card"]); bfc.pack(fill="x", padx=12, pady=(4,10))
        ctk.CTkButton(bfc, text="Escolher arquivo...", width=160, height=30,
                      fg_color=ROXO, hover_color=ROXO_ESC, text_color="#FFFFFF",
                      font=("Helvetica", 11), command=escolher_arq).pack(side="left", padx=(0,6))
        ctk.CTkButton(bfc, text="▶ Testar", width=80, height=30,
                      fg_color=T["superficie"], hover_color=T["borda"],
                      text_color=T["texto"], font=("Helvetica", 10),
                      command=lambda: tocar_som("__custom__", arq_var.get())).pack(side="left")

        def salvar_som():
            nome_e = som_var.get()
            du["som_nome"]    = nome_e
            du["som_arquivo"] = arq_var.get() if nome_e == "__custom__" else None
            self._salvar(); jan.destroy()

        ctk.CTkButton(jan, text="Salvar preferência", width=300, height=42,
                      corner_radius=21, fg_color=LARANJA, hover_color=LARANJA_ESC,
                      text_color="#FFFFFF", font=("Helvetica", 13, "bold"),
                      command=salvar_som).pack(pady=12)

    # ── Nova rotina ───────────────────────────────────────────────────────────
    def _nova_rotina(self):
        jan = ctk.CTkToplevel(self)
        jan.title("Nova Rotina"); jan.geometry("400x340")
        jan.grab_set(); jan.resizable(False, False); jan.configure(fg_color=T["fundo"])

        ctk.CTkLabel(jan, text="Nome da nova rotina:",
                     font=("Helvetica", 13, "bold"), text_color=T["texto"]).pack(pady=(20,6))
        e = ctk.CTkEntry(jan, width=340, height=40, placeholder_text="Ex: Rotina de Saúde")
        e.pack(); e.focus()

        ctk.CTkLabel(jan, text="Cor da rotina:",
                     font=("Helvetica", 13, "bold"), text_color=T["texto"]).pack(pady=(14,6))
        cor_sel = tk.StringVar(value=ROXO)
        grade   = tk.Frame(jan, bg=T["fundo"]); grade.pack()
        preview = tk.Label(jan, text="  Roxo selecionado  ", bg=ROXO, fg="#FFFFFF",
                           font=("Helvetica", 11, "bold"), pady=7)
        preview.pack(padx=40, fill="x", pady=8)

        def sel_cor(h, n):
            cor_sel.set(h); preview.configure(bg=h, text=f"  {n} selecionado  ")

        for i, (nc, hc) in enumerate(PALETA_CORES):
            tk.Button(grade, bg=hc, width=3, height=1, relief="flat", cursor="hand2",
                      command=lambda h=hc, n=nc: sel_cor(h, n)
                      ).grid(row=i // 5, column=i % 5, padx=5, pady=4)

        def confirmar():
            nome = e.get().strip()
            if not nome: return
            du = self._du(); rotinas = du.setdefault("rotinas", {})
            if nome in rotinas:
                messagebox.showwarning("Aviso", "Rotina já existe.", parent=jan); return
            rotinas[nome] = []
            du.setdefault("cores_rotinas", {})[nome] = cor_sel.get()
            self._salvar(); self._renderizar_rotinas(); jan.destroy()
            if self._aba_ativa == "Hoje": self._aba_hoje.atualizar()

        e.bind("<Return>", lambda _: confirmar())
        ctk.CTkButton(jan, text="Criar Rotina", width=340, height=44, corner_radius=22,
                      fg_color=ROXO, hover_color=ROXO_ESC, text_color="#FFFFFF",
                      font=("Helvetica", 13, "bold"), command=confirmar).pack(pady=(2,12))

    # ── Monitor de notificações ───────────────────────────────────────────────
    def _iniciar_monitor(self):
        self._monitorando = True
        threading.Thread(target=self._loop_monitor, daemon=True).start()

    def _loop_monitor(self):
        while self._monitorando:
            self._checar_tarefas()
            time.sleep(60)

    def _checar_tarefas(self):
        agora = minutos_agora(); hoje = dia_hoje()
        for tarefas in self._du().get("rotinas", {}).values():
            for t in tarefas:
                if hoje not in t.get("dias", []): continue
                tid = t["id"]
                ini = str_para_minutos(t.get("inicio", ""))
                fim = str_para_minutos(t.get("fim", ""))

                # Alerta de início (5 min antes)
                if ini >= 0:
                    diff = ini - agora
                    chave = tid + "ini" + str(ini)
                    if 0 < diff <= 5 and chave not in self._notif_ativas:
                        self._notif_ativas.add(chave)
                        self.after(0, lambda n=t["nome"], d=diff, h=t.get("inicio"):
                                   self._alerta(n, d, h, tipo="inicio"))
                    if diff < -2: self._notif_ativas.discard(chave)

                # Alerta de fim (5 min antes de acabar)
                if fim >= 0:
                    diff_fim = fim - agora
                    chave_fim = tid + "fim" + str(fim)
                    if 0 < diff_fim <= 5 and chave_fim not in self._notif_ativas:
                        self._notif_ativas.add(chave_fim)
                        self.after(0, lambda n=t["nome"], d=diff_fim, h=t.get("fim"):
                                   self._alerta(n, d, h, tipo="fim"))
                    if diff_fim < -2: self._notif_ativas.discard(chave_fim)

    def _alerta(self, nome, minutos, horario, tipo="inicio"):
        threading.Thread(target=self._tocar, daemon=True).start()
        jan = ctk.CTkToplevel(self)
        jan.title("Lembrete NeuroConnect")
        jan.geometry("360x220"); jan.attributes("-topmost", True)
        jan.resizable(False, False); jan.configure(fg_color=T["fundo"])

        cor_topo = LARANJA if tipo == "inicio" else CIANO
        tk.Frame(jan, bg=cor_topo, height=8).pack(fill="x")

        if tipo == "inicio":
            ctk.CTkLabel(jan, text="Próxima atividade!",
                         font=("Helvetica", 15, "bold"), text_color=LARANJA).pack(pady=(14,4))
            ctk.CTkLabel(jan, text=nome,
                         font=("Helvetica", 14), text_color=T["texto"]).pack()
            ctk.CTkLabel(jan, text=f"Começa às {horario}  ({minutos} min)",
                         font=("Helvetica", 11), text_color=T["texto_sec"]).pack(pady=4)
        else:
            ctk.CTkLabel(jan, text="Atividade encerrando em breve",
                         font=("Helvetica", 15, "bold"), text_color=CIANO).pack(pady=(14,4))
            ctk.CTkLabel(jan, text=nome,
                         font=("Helvetica", 14), text_color=T["texto"]).pack()
            ctk.CTkLabel(jan, text=f"Termina às {horario}  ({minutos} min restantes)",
                         font=("Helvetica", 11), text_color=T["texto_sec"]).pack(pady=4)
            ctk.CTkLabel(jan, text="Vá preparando a transição para a próxima atividade.",
                         font=("Helvetica", 10), text_color=T["texto_sec"]).pack()

        ctk.CTkButton(jan, text="OK, entendido!", fg_color=cor_topo,
                      hover_color=escurecer(cor_topo), text_color="#FFFFFF",
                      command=jan.destroy).pack(pady=14)

    def destruir(self):
        self._monitorando = False

# ══════════════════════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class NeuroConnect(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NeuroConnect")
        self.geometry("820x640"); self.minsize(700, 520)
        aplicar_tema(NOME_TEMA_PADRAO)
        self.configure(fg_color=T["fundo"])
        self._frame_atual = None
        self.abrir_login()

    def _trocar_frame(self, novo):
        if self._frame_atual:
            if hasattr(self._frame_atual, "destruir"): self._frame_atual.destruir()
            self._frame_atual.destroy()
        self.configure(fg_color=T["fundo"])
        self._frame_atual = novo
        novo.pack(fill="both", expand=True)

    def abrir_login(self):
        self._trocar_frame(TelaLogin(self))

    def abrir_principal(self, usuario, dados):
        tela = TelaPrincipal(self, usuario, dados)
        self._trocar_frame(tela)
        # Mostrar diálogo de humor se ainda não preenchido hoje
        du = dados["usuarios"].get(usuario, {})
        humor = du.get("humor_hoje", {})
        if humor.get("data") != date.today().isoformat():
            def on_concluir():
                tela._aba_hoje.atualizar()
            self.after(300, lambda: DialogoHumor(
                tela, usuario, dados,
                on_salvar=lambda: salvar_dados(dados),
                on_concluir=on_concluir,
            ))

    def voltar_login(self):
        self.abrir_login()

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRADA
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = NeuroConnect()
    app.mainloop()
