#!/usr/bin/env python3
"""
NeuroConnect - Agenda inteligente para pessoas neurodivergentes
Instale as dependências com: pip install customtkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
import time
import uuid
import hashlib
from datetime import datetime

# ─── Configuração visual global ────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ─── Paleta de cores (baseada no design dos slides) ────────────────────────
LARANJA       = "#F5893C"
LARANJA_ESC   = "#D96E20"
LARANJA_CLR   = "#FBBF8A"
VERDE         = "#4CAF50"
VERDE_ESC     = "#388E3C"
ROXO          = "#5C5FA6"
ROXO_ESC      = "#44478A"
CIANO         = "#2BBFA0"
FUNDO         = "#F0F0F5"
BRANCO        = "#FFFFFF"
CINZA_CARD    = "#E8E8EE"
CINZA_BORDA   = "#CCCCDD"
TEXTO_ESC     = "#2D2D2D"
TEXTO_CLR     = "#FFFFFF"
VERMELHO      = "#E53935"

# ─── Arquivo de dados ──────────────────────────────────────────────────────
DADOS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")

DIAS_SEMANA = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]

# Cor padrão por nome de rotina
CORES_ROTINA = {
    "Rotina Pessoal":   LARANJA,
    "Rotina Acadêmica": VERDE,
}


# ─── Funções utilitárias ────────────────────────────────────────────────────
def carregar_dados() -> dict:
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuarios": {}}


def salvar_dados(dados: dict):
    with open(DADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def minutos_agora() -> int:
    n = datetime.now()
    return n.hour * 60 + n.minute


def str_para_minutos(hhmm: str) -> int:
    """Converte '15:45' para 945 minutos."""
    try:
        h, m = hhmm.strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return -1


def dia_hoje() -> str:
    return DIAS_SEMANA[datetime.now().weekday()]


def cor_rotina(nome: str) -> str:
    return CORES_ROTINA.get(nome, ROXO)


# ─── Canvas: símbolo ∞ estilizado ──────────────────────────────────────────
class LogoCanvas(tk.Canvas):
    """Desenha o símbolo infinito em duas cores (laranja + ciano)."""

    def __init__(self, master, tamanho: int = 90, fundo: str = BRANCO, **kw):
        super().__init__(master, width=tamanho, height=tamanho // 2 + 10,
                         bg=fundo, highlightthickness=0, **kw)
        self._desenhar(tamanho)

    def _desenhar(self, t):
        w = t
        h = t // 2 + 10
        r = h // 2 - 4
        cx1 = w // 2 - r + 2
        cx2 = w // 2 + r - 2
        cy = h // 2

        # Loop esquerdo – laranja
        self.create_oval(cx1 - r, cy - r, cx1 + r, cy + r,
                         outline=LARANJA, width=7, fill="")
        # Loop direito – ciano
        self.create_oval(cx2 - r, cy - r, cx2 + r, cy + r,
                         outline=CIANO, width=7, fill="")


# ─── Tela de Login ──────────────────────────────────────────────────────────
class TelaLogin(ctk.CTkFrame):
    def __init__(self, master: "NeuroConnect"):
        super().__init__(master, fg_color=BRANCO)
        self.app = master
        self._construir()

    def _construir(self):
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Logo
        logo_frame = tk.Frame(self, bg=BRANCO)
        logo_frame.grid(row=1, column=0, pady=(30, 4))
        LogoCanvas(logo_frame, tamanho=120, fundo=BRANCO).pack()

        # Título
        ctk.CTkLabel(self, text="NeuroConnect", font=("Helvetica", 26, "bold"),
                     text_color=TEXTO_ESC).grid(row=2, column=0, pady=(0, 2))
        ctk.CTkLabel(self, text="Organizador e otimizador de tarefas",
                     font=("Helvetica", 12), text_color="#777777").grid(row=3, column=0, pady=(0, 20))

        # Formulário
        form = ctk.CTkFrame(self, fg_color=CINZA_CARD, corner_radius=16)
        form.grid(row=4, column=0, padx=60, pady=10, sticky="ew")
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Usuário", font=("Helvetica", 12),
                     text_color=TEXTO_ESC).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 2))
        self.entry_usuario = ctk.CTkEntry(form, placeholder_text="Digite seu usuário",
                                          height=38, corner_radius=8)
        self.entry_usuario.grid(row=1, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(form, text="Senha", font=("Helvetica", 12),
                     text_color=TEXTO_ESC).grid(row=2, column=0, sticky="w", padx=20, pady=(12, 2))
        self.entry_senha = ctk.CTkEntry(form, placeholder_text="Digite sua senha",
                                        show="●", height=38, corner_radius=8)
        self.entry_senha.grid(row=3, column=0, padx=20, sticky="ew")
        self.entry_senha.bind("<Return>", lambda e: self._entrar())

        # Botão Entrar (laranja, preenchido)
        ctk.CTkButton(form, text="Entrar", height=40, corner_radius=20,
                      fg_color=LARANJA, hover_color=LARANJA_ESC,
                      font=("Helvetica", 14, "bold"),
                      command=self._entrar).grid(row=4, column=0, padx=20, pady=(16, 8), sticky="ew")

        # Botão Criar Conta (contorno)
        ctk.CTkButton(form, text="Criar Conta", height=40, corner_radius=20,
                      fg_color=BRANCO, hover_color=CINZA_CARD,
                      text_color=LARANJA, border_width=2, border_color=LARANJA,
                      font=("Helvetica", 13),
                      command=self._criar_conta).grid(row=5, column=0, padx=20, pady=(0, 16), sticky="ew")

        self.label_erro = ctk.CTkLabel(self, text="", text_color=VERMELHO,
                                       font=("Helvetica", 11))
        self.label_erro.grid(row=5, column=0, pady=4)

    def _entrar(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        if not usuario or not senha:
            self.label_erro.configure(text="Preencha usuário e senha.")
            return
        dados = carregar_dados()
        u = dados["usuarios"].get(usuario)
        if u and u["senha"] == hash_senha(senha):
            self.app.abrir_principal(usuario, dados)
        else:
            self.label_erro.configure(text="Usuário ou senha incorretos.")

    def _criar_conta(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Criar Conta")
        janela.geometry("340x300")
        janela.grab_set()
        janela.resizable(False, False)

        ctk.CTkLabel(janela, text="Criar nova conta",
                     font=("Helvetica", 16, "bold")).pack(pady=(20, 10))

        ctk.CTkLabel(janela, text="Usuário").pack(anchor="w", padx=30)
        e_user = ctk.CTkEntry(janela, width=280)
        e_user.pack(padx=30, pady=(0, 8))

        ctk.CTkLabel(janela, text="Senha").pack(anchor="w", padx=30)
        e_senha = ctk.CTkEntry(janela, show="●", width=280)
        e_senha.pack(padx=30, pady=(0, 8))

        ctk.CTkLabel(janela, text="Confirmar senha").pack(anchor="w", padx=30)
        e_conf = ctk.CTkEntry(janela, show="●", width=280)
        e_conf.pack(padx=30, pady=(0, 12))

        lbl_err = ctk.CTkLabel(janela, text="", text_color=VERMELHO)
        lbl_err.pack()

        def salvar():
            user = e_user.get().strip()
            s1 = e_senha.get()
            s2 = e_conf.get()
            if not user or not s1:
                lbl_err.configure(text="Preencha todos os campos.")
                return
            if s1 != s2:
                lbl_err.configure(text="Senhas não coincidem.")
                return
            dados = carregar_dados()
            if user in dados["usuarios"]:
                lbl_err.configure(text="Usuário já existe.")
                return
            dados["usuarios"][user] = {
                "senha": hash_senha(s1),
                "rotinas": {
                    "Rotina Pessoal": [],
                    "Rotina Acadêmica": []
                }
            }
            salvar_dados(dados)
            messagebox.showinfo("Conta criada", f"Conta '{user}' criada com sucesso!")
            janela.destroy()

        ctk.CTkButton(janela, text="Criar Conta", fg_color=LARANJA,
                      hover_color=LARANJA_ESC, command=salvar).pack(pady=8)


# ─── Diálogo: adicionar / editar tarefa ────────────────────────────────────
class DialogoTarefa(ctk.CTkToplevel):
    def __init__(self, master, cor: str, tarefa: dict | None = None):
        super().__init__(master)
        self.title("Nova Tarefa" if tarefa is None else "Editar Tarefa")
        self.geometry("420x560")
        self.resizable(False, False)
        self.grab_set()
        self.resultado: dict | None = None
        self._cor = cor
        self._tarefa = tarefa or {}
        self._construir()

    def _construir(self):
        # Cabeçalho colorido
        cab = tk.Frame(self, bg=self._cor, height=50)
        cab.pack(fill="x")
        titulo = "Nova Tarefa" if not self._tarefa else "Editar Tarefa"
        tk.Label(cab, text=titulo, bg=self._cor, fg=BRANCO,
                 font=("Helvetica", 15, "bold")).pack(pady=12)

        corpo = ctk.CTkScrollableFrame(self, fg_color=BRANCO)
        corpo.pack(fill="both", expand=True, padx=16, pady=12)
        corpo.grid_columnconfigure(0, weight=1)

        def label(pai, txt):
            ctk.CTkLabel(pai, text=txt, font=("Helvetica", 12, "bold"),
                         text_color=TEXTO_ESC).pack(anchor="w", pady=(8, 2))

        # Nome da tarefa
        label(corpo, "Nome da tarefa")
        self.e_nome = ctk.CTkEntry(corpo, placeholder_text="Ex: Ler Livro", height=36)
        self.e_nome.pack(fill="x")
        if self._tarefa.get("nome"):
            self.e_nome.insert(0, self._tarefa["nome"])

        # Dias da semana
        label(corpo, "Dias da semana")
        dias_frame = ctk.CTkFrame(corpo, fg_color=CINZA_CARD, corner_radius=8)
        dias_frame.pack(fill="x", pady=4)
        dias_row = tk.Frame(dias_frame, bg=CINZA_CARD)
        dias_row.pack(pady=6)
        self._vars_dias = {}
        dias_tarefa = self._tarefa.get("dias", [])
        for d in DIAS_SEMANA:
            var = tk.BooleanVar(value=d in dias_tarefa)
            self._vars_dias[d] = var
            cb = tk.Checkbutton(dias_row, text=d, variable=var,
                                bg=CINZA_CARD, fg=TEXTO_ESC,
                                selectcolor=self._cor,
                                font=("Helvetica", 10, "bold"),
                                activebackground=CINZA_CARD)
            cb.pack(side="left", padx=3)

        # Horários
        hora_frame = tk.Frame(corpo, bg=BRANCO)
        hora_frame.pack(fill="x", pady=4)

        col_ini = tk.Frame(hora_frame, bg=BRANCO)
        col_ini.pack(side="left", expand=True, fill="x", padx=(0, 8))
        label(col_ini, "Início (HH:MM)")
        self.e_inicio = ctk.CTkEntry(col_ini, placeholder_text="15:45", height=36)
        self.e_inicio.pack(fill="x")
        if self._tarefa.get("inicio"):
            self.e_inicio.insert(0, self._tarefa["inicio"])

        col_fim = tk.Frame(hora_frame, bg=BRANCO)
        col_fim.pack(side="left", expand=True, fill="x")
        label(col_fim, "Fim (HH:MM)")
        self.e_fim = ctk.CTkEntry(col_fim, placeholder_text="16:45", height=36)
        self.e_fim.pack(fill="x")
        if self._tarefa.get("fim"):
            self.e_fim.insert(0, self._tarefa["fim"])

        # Lembretes
        label(corpo, "Lembretes / Notas")
        self.e_lembretes = ctk.CTkTextbox(corpo, height=90, corner_radius=8)
        self.e_lembretes.pack(fill="x")
        if self._tarefa.get("lembretes"):
            self.e_lembretes.insert("0.0", "\n".join(self._tarefa["lembretes"]))

        # Botões
        btn_frame = tk.Frame(self, bg=BRANCO)
        btn_frame.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(btn_frame, text="Cancelar", width=120,
                      fg_color=CINZA_CARD, hover_color=CINZA_BORDA,
                      text_color=TEXTO_ESC,
                      command=self.destroy).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="Salvar", width=120,
                      fg_color=self._cor,
                      hover_color=LARANJA_ESC if self._cor == LARANJA else VERDE_ESC,
                      command=self._salvar).pack(side="right")

    def _salvar(self):
        nome = self.e_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome da tarefa.", parent=self)
            return
        dias = [d for d, v in self._vars_dias.items() if v.get()]
        if not dias:
            messagebox.showwarning("Atenção", "Selecione pelo menos um dia.", parent=self)
            return
        inicio = self.e_inicio.get().strip()
        fim = self.e_fim.get().strip()
        if str_para_minutos(inicio) < 0 or str_para_minutos(fim) < 0:
            messagebox.showwarning("Atenção", "Use o formato HH:MM nos horários.", parent=self)
            return
        texto_lem = self.e_lembretes.get("0.0", "end").strip()
        lembretes = [l.strip() for l in texto_lem.split("\n") if l.strip()]

        self.resultado = {
            "id": self._tarefa.get("id", str(uuid.uuid4())),
            "nome": nome,
            "dias": dias,
            "inicio": inicio,
            "fim": fim,
            "lembretes": lembretes,
        }
        self.destroy()


# ─── Widget: cartão de tarefa ───────────────────────────────────────────────
class CartaoTarefa(ctk.CTkFrame):
    def __init__(self, master, tarefa: dict, cor: str,
                 on_editar, on_deletar, **kw):
        super().__init__(master, fg_color=BRANCO, corner_radius=10,
                         border_width=1, border_color=CINZA_BORDA, **kw)
        self._construir(tarefa, cor, on_editar, on_deletar)

    def _construir(self, t, cor, on_edit, on_del):
        self.grid_columnconfigure(0, weight=1)

        # Faixa colorida lateral
        barra = tk.Frame(self, bg=cor, width=5)
        barra.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 8))
        barra.grid_propagate(False)

        # Linha principal
        linha_top = tk.Frame(self, bg=BRANCO)
        linha_top.grid(row=0, column=1, sticky="ew", pady=(6, 0))

        dias_str = " · ".join(t.get("dias", []))
        nome_label = tk.Label(linha_top, text=t["nome"],
                              bg=BRANCO, fg=TEXTO_ESC,
                              font=("Helvetica", 12, "bold"))
        nome_label.pack(side="left")

        tk.Label(linha_top, text=f"  {dias_str}",
                 bg=BRANCO, fg="#888888", font=("Helvetica", 10)).pack(side="left")

        horario = f"{t.get('inicio','?')} – {t.get('fim','?')}"
        tk.Label(linha_top, text=horario,
                 bg=BRANCO, fg=cor, font=("Helvetica", 11, "bold")).pack(side="right", padx=8)

        # Lembretes
        if t.get("lembretes"):
            lem_frame = tk.Frame(self, bg=BRANCO)
            lem_frame.grid(row=1, column=1, sticky="ew", pady=(2, 0))
            for lem in t["lembretes"]:
                tk.Label(lem_frame, text=f"• {lem}",
                         bg=BRANCO, fg="#666666", font=("Helvetica", 10),
                         wraplength=380, justify="left").pack(anchor="w")

        # Botões editar / deletar
        btn_frame = tk.Frame(self, bg=BRANCO)
        btn_frame.grid(row=2, column=1, sticky="e", pady=(4, 6), padx=4)

        ctk.CTkButton(btn_frame, text="✏️ Editar", width=80, height=26,
                      fg_color=CINZA_CARD, hover_color=CINZA_BORDA,
                      text_color=TEXTO_ESC, corner_radius=6,
                      command=on_edit).pack(side="left", padx=4)

        ctk.CTkButton(btn_frame, text="🗑️ Deletar", width=90, height=26,
                      fg_color="#FFECEC", hover_color="#FFDDDD",
                      text_color=VERMELHO, corner_radius=6,
                      command=on_del).pack(side="left")


# ─── Widget: seção de rotina (expansível) ──────────────────────────────────
class SecaoRotina(ctk.CTkFrame):
    def __init__(self, master, nome: str, tarefas: list,
                 on_salvar, **kw):
        super().__init__(master, fg_color=FUNDO, **kw)
        self._nome = nome
        self._tarefas = tarefas
        self._on_salvar = on_salvar
        self._cor = cor_rotina(nome)
        self._expandida = tk.BooleanVar(value=True)
        self._construir()

    def _construir(self):
        self.grid_columnconfigure(0, weight=1)

        # Cabeçalho clicável
        self._cab = tk.Frame(self, bg=self._cor, cursor="hand2")
        self._cab.grid(row=0, column=0, sticky="ew", padx=4, pady=(6, 0))
        self._cab.grid_columnconfigure(0, weight=1)

        tk.Label(self._cab, text=self._nome.upper(),
                 bg=self._cor, fg=BRANCO,
                 font=("Helvetica", 13, "bold")).grid(row=0, column=0,
                                                       sticky="w", padx=14, pady=10)
        self._seta = tk.Label(self._cab, text="▲", bg=self._cor, fg=BRANCO,
                              font=("Helvetica", 12))
        self._seta.grid(row=0, column=1, padx=14)

        self._cab.bind("<Button-1>", self._toggle)
        for w in self._cab.winfo_children():
            w.bind("<Button-1>", self._toggle)

        # Corpo
        self._corpo = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=0)
        self._corpo.grid(row=1, column=0, sticky="ew", padx=4)
        self._corpo.grid_columnconfigure(0, weight=1)

        self._renderizar_tarefas()

    def _toggle(self, _=None):
        if self._expandida.get():
            self._corpo.grid_remove()
            self._seta.configure(text="▼")
            self._expandida.set(False)
        else:
            self._corpo.grid()
            self._seta.configure(text="▲")
            self._expandida.set(True)

    def _renderizar_tarefas(self):
        for w in self._corpo.winfo_children():
            w.destroy()

        if not self._tarefas:
            tk.Label(self._corpo, text="Nenhuma tarefa. Clique em '+' para adicionar.",
                     fg="#AAAAAA", bg=BRANCO, font=("Helvetica", 10)).pack(pady=10)

        for i, tarefa in enumerate(self._tarefas):
            card = CartaoTarefa(self._corpo, tarefa, self._cor,
                                on_editar=lambda t=tarefa: self._editar(t),
                                on_deletar=lambda t=tarefa: self._deletar(t))
            card.pack(fill="x", padx=8, pady=4)

        # Botão adicionar
        btn_add = ctk.CTkButton(self._corpo, text="+ Adicionar Tarefa",
                                height=34, corner_radius=8,
                                fg_color=self._cor, hover_color=LARANJA_ESC if self._cor == LARANJA else VERDE_ESC,
                                font=("Helvetica", 12),
                                command=self._nova_tarefa)
        btn_add.pack(pady=(6, 10), padx=8, anchor="w")

    def _nova_tarefa(self):
        dlg = DialogoTarefa(self, self._cor)
        self.wait_window(dlg)
        if dlg.resultado:
            self._tarefas.append(dlg.resultado)
            self._on_salvar()
            self._renderizar_tarefas()

    def _editar(self, tarefa: dict):
        dlg = DialogoTarefa(self, self._cor, tarefa)
        self.wait_window(dlg)
        if dlg.resultado:
            idx = next((i for i, t in enumerate(self._tarefas) if t["id"] == tarefa["id"]), -1)
            if idx >= 0:
                self._tarefas[idx] = dlg.resultado
            self._on_salvar()
            self._renderizar_tarefas()

    def _deletar(self, tarefa: dict):
        if messagebox.askyesno("Confirmar", f"Deletar '{tarefa['nome']}'?"):
            self._tarefas[:] = [t for t in self._tarefas if t["id"] != tarefa["id"]]
            self._on_salvar()
            self._renderizar_tarefas()

    def adicionar_rotina_externa(self, nome: str):
        """Não usado aqui, mas mantido para extensibilidade."""
        pass


# ─── Tela Principal ─────────────────────────────────────────────────────────
class TelaPrincipal(ctk.CTkFrame):
    def __init__(self, master: "NeuroConnect", usuario: str, dados: dict):
        super().__init__(master, fg_color=FUNDO)
        self.app = master
        self._usuario = usuario
        self._dados = dados
        self._notif_ativas: set = set()
        self._construir()
        self._iniciar_monitor()

    # ── Construção ──────────────────────────────────────────────────────────
    def _construir(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._criar_barra_topo()
        self._criar_area_rolavel()
        self._criar_rodape()
        self._renderizar_rotinas()

    def _criar_barra_topo(self):
        barra = tk.Frame(self, bg=BRANCO, height=60)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_propagate(False)
        barra.grid_columnconfigure(1, weight=1)

        # Logo pequeno + título
        esq = tk.Frame(barra, bg=BRANCO)
        esq.grid(row=0, column=0, padx=16, pady=8)
        LogoCanvas(esq, tamanho=50, fundo=BRANCO).pack(side="left")
        tk.Label(esq, text="NeuroConnect", bg=BRANCO, fg=TEXTO_ESC,
                 font=("Helvetica", 14, "bold")).pack(side="left", padx=8)

        # Usuário e botões
        dir_ = tk.Frame(barra, bg=BRANCO)
        dir_.grid(row=0, column=2, padx=16)

        tk.Label(dir_, text=f"👤 {self._usuario}", bg=BRANCO, fg=TEXTO_ESC,
                 font=("Helvetica", 11)).pack(side="left", padx=8)

        ctk.CTkButton(dir_, text="+ Rotina", width=90, height=30,
                      fg_color=ROXO, hover_color=ROXO_ESC,
                      font=("Helvetica", 11),
                      command=self._nova_rotina).pack(side="left", padx=4)

        ctk.CTkButton(dir_, text="Sair", width=70, height=30,
                      fg_color=CINZA_CARD, hover_color=CINZA_BORDA,
                      text_color=TEXTO_ESC,
                      command=self.app.voltar_login).pack(side="left", padx=4)

    def _criar_area_rolavel(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=FUNDO,
                                               label_text="Minhas Rotinas",
                                               label_font=("Helvetica", 13, "bold"),
                                               label_fg_color=FUNDO,
                                               label_text_color=TEXTO_ESC)
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self._scroll.grid_columnconfigure(0, weight=1)

    def _criar_rodape(self):
        rod = tk.Frame(self, bg=BRANCO, height=36)
        rod.grid(row=2, column=0, sticky="ew")
        rod.grid_propagate(False)
        tk.Label(rod, text="∞  NeuroConnect — tecnologia inteligente que organiza, conecta e inclui.",
                 bg=BRANCO, fg="#AAAAAA", font=("Helvetica", 9)).pack(side="right", padx=12, pady=8)

    # ── Renderização das rotinas ─────────────────────────────────────────────
    def _renderizar_rotinas(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        rotinas = self._dados_usuario().get("rotinas", {})
        if not rotinas:
            tk.Label(self._scroll, text="Nenhuma rotina. Clique em '+ Rotina' para começar.",
                     fg="#AAAAAA", bg=FUNDO, font=("Helvetica", 11)).pack(pady=40)
            return

        for nome, tarefas in rotinas.items():
            sec = SecaoRotina(self._scroll, nome, tarefas,
                              on_salvar=self._salvar)
            sec.pack(fill="x", pady=6)

    def _dados_usuario(self) -> dict:
        return self._dados["usuarios"].get(self._usuario, {})

    def _salvar(self):
        salvar_dados(self._dados)

    # ── Nova rotina ──────────────────────────────────────────────────────────
    def _nova_rotina(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Nova Rotina")
        janela.geometry("320x180")
        janela.resizable(False, False)
        janela.grab_set()

        ctk.CTkLabel(janela, text="Nome da nova rotina:",
                     font=("Helvetica", 13)).pack(pady=(20, 6))
        e = ctk.CTkEntry(janela, width=260, placeholder_text="Ex: Rotina de Saúde")
        e.pack()
        e.focus()

        def confirmar():
            nome = e.get().strip()
            if not nome:
                return
            rotinas = self._dados_usuario().setdefault("rotinas", {})
            if nome in rotinas:
                messagebox.showwarning("Aviso", "Rotina já existe.", parent=janela)
                return
            rotinas[nome] = []
            self._salvar()
            self._renderizar_rotinas()
            janela.destroy()

        e.bind("<Return>", lambda _: confirmar())
        ctk.CTkButton(janela, text="Criar", fg_color=ROXO, hover_color=ROXO_ESC,
                      command=confirmar).pack(pady=16)

    # ── Monitor de notificações ──────────────────────────────────────────────
    def _iniciar_monitor(self):
        self._monitorando = True
        t = threading.Thread(target=self._loop_notificacoes, daemon=True)
        t.start()

    def _loop_notificacoes(self):
        while self._monitorando:
            self._verificar_tarefas()
            time.sleep(60)

    def _verificar_tarefas(self):
        agora = minutos_agora()
        hoje = dia_hoje()
        rotinas = self._dados_usuario().get("rotinas", {})
        for nome_rot, tarefas in rotinas.items():
            for t in tarefas:
                if hoje not in t.get("dias", []):
                    continue
                inicio_min = str_para_minutos(t.get("inicio", ""))
                if inicio_min < 0:
                    continue
                # Avisa 5 minutos antes
                diff = inicio_min - agora
                chave = t["id"] + str(inicio_min)
                if 0 < diff <= 5 and chave not in self._notif_ativas:
                    self._notif_ativas.add(chave)
                    self.after(0, lambda n=t["nome"], d=diff, i=t.get("inicio"):
                               self._mostrar_alerta(n, d, i))
                # Remove chave após passar do horário para poder alertar amanhã
                if diff < -2 and chave in self._notif_ativas:
                    self._notif_ativas.discard(chave)

    def _mostrar_alerta(self, nome: str, minutos: int, horario: str):
        janela = ctk.CTkToplevel(self)
        janela.title("⏰ Lembrete NeuroConnect")
        janela.geometry("360x200")
        janela.attributes("-topmost", True)
        janela.resizable(False, False)

        tk.Frame(janela, bg=LARANJA, height=8).pack(fill="x")

        ctk.CTkLabel(janela, text="⏰  Próxima atividade!",
                     font=("Helvetica", 15, "bold"),
                     text_color=LARANJA).pack(pady=(16, 4))

        ctk.CTkLabel(janela, text=f"{nome}",
                     font=("Helvetica", 14)).pack()

        ctk.CTkLabel(janela, text=f"Começa às {horario}  ({minutos} min)",
                     font=("Helvetica", 11), text_color="#666666").pack(pady=4)

        ctk.CTkButton(janela, text="OK, entendido!", fg_color=LARANJA,
                      hover_color=LARANJA_ESC,
                      command=janela.destroy).pack(pady=16)

    def destruir(self):
        self._monitorando = False


# ─── Janela principal ────────────────────────────────────────────────────────
class NeuroConnect(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NeuroConnect")
        self.geometry("720x580")
        self.minsize(620, 480)
        self.configure(fg_color=BRANCO)

        self._frame_atual: ctk.CTkFrame | None = None
        self.abrir_login()

    def _trocar_frame(self, novo: ctk.CTkFrame):
        if self._frame_atual:
            if hasattr(self._frame_atual, "destruir"):
                self._frame_atual.destruir()
            self._frame_atual.destroy()
        self._frame_atual = novo
        novo.pack(fill="both", expand=True)

    def abrir_login(self):
        self._trocar_frame(TelaLogin(self))

    def abrir_principal(self, usuario: str, dados: dict):
        self._trocar_frame(TelaPrincipal(self, usuario, dados))

    def voltar_login(self):
        self.abrir_login()


# ─── Entrada ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = NeuroConnect()
    app.mainloop()
