import tkinter as tk
from tkinter import ttk, messagebox

# Variáveis globais
tarefas = []  # Lista para armazenar as tarefas
tarefa_selecionada = None  # Índice da tarefa atualmente selecionada

# ============================================================================
# FUNÇÕES DE CRUD (CREATE, READ, UPDATE, DELETE)
# ============================================================================

def criar_tarefa():
    """Cria uma nova tarefa vazia"""
    global tarefa_selecionada
    
    nova_tarefa = {
        "id": len(tarefas) + 1,
        "titulo": "Nova Tarefa",
        "descricao": "",
        "concluida": False
    }
    
    tarefas.append(nova_tarefa)
    tarefa_selecionada = len(tarefas) - 1
    
    # Atualizar interface
    atualizar_lista_tarefas()
    carregar_tarefa_editor()
    habilitar_editor()
    
    # Focar no título para edição imediata
    entry_titulo.focus()
    entry_titulo.select_range(0, tk.END)

def ler_tarefas():
    """Retorna a lista completa de tarefas"""
    return tarefas

def atualizar_tarefa():
    """Atualiza a tarefa atualmente selecionada"""
    global tarefa_selecionada
    
    if tarefa_selecionada is None:
        messagebox.showwarning("Aviso", "Nenhuma tarefa selecionada para atualizar!")
        return
    
    # Validar dados
    titulo = entry_titulo.get().strip()
    if not titulo:
        messagebox.showwarning("Aviso", "O título da tarefa não pode estar vazio!")
        entry_titulo.focus()
        return
    
    descricao = text_descricao.get("1.0", tk.END).strip()
    
    # Atualizar tarefa
    tarefas[tarefa_selecionada]["titulo"] = titulo
    tarefas[tarefa_selecionada]["descricao"] = descricao
    
    # Atualizar lista
    atualizar_lista_tarefas()
    
    # Feedback
    mostrar_status(f"Tarefa '{titulo}' atualizada!")

def deletar_tarefa():
    """Remove a tarefa atualmente selecionada"""
    global tarefa_selecionada
    
    if tarefa_selecionada is None:
        messagebox.showwarning("Aviso", "Nenhuma tarefa selecionada para deletar!")
        return
    
    # Obter título da tarefa para mensagem de confirmação
    titulo_tarefa = tarefas[tarefa_selecionada]["titulo"]
    
    # Confirmar exclusão
    confirmacao = messagebox.askyesno(
        "Confirmar Exclusão",
        f"Tem certeza que deseja excluir a tarefa '{titulo_tarefa}'?\nEsta ação não pode ser desfeita."
    )
    
    if not confirmacao:
        return
    
    # Remover tarefa
    tarefas.pop(tarefa_selecionada)
    
    # Reindexar IDs
    for i, tarefa in enumerate(tarefas):
        tarefa["id"] = i + 1
    
    # Resetar seleção
    tarefa_selecionada = None
    
    # Atualizar interface
    atualizar_lista_tarefas()
    limpar_editor()
    desabilitar_editor()
    
    # Feedback
    mostrar_status(f"Tarefa '{titulo_tarefa}' excluída!")

def marcar_concluida():
    """Marca/desmarca a tarefa como concluída"""
    global tarefa_selecionada
    
    if tarefa_selecionada is None:
        messagebox.showwarning("Aviso", "Nenhuma tarefa selecionada!")
        return
    
    # Alternar status
    tarefas[tarefa_selecionada]["concluida"] = not tarefas[tarefa_selecionada]["concluida"]
    
    # Atualizar interface
    atualizar_lista_tarefas()
    carregar_tarefa_editor()
    
    # Feedback
    status = "concluída" if tarefas[tarefa_selecionada]["concluida"] else "pendente"
    mostrar_status(f"Tarefa marcada como {status}!")

# ============================================================================
# FUNÇÕES DE INTERFACE
# ============================================================================

def atualizar_lista_tarefas():
    """Atualiza a lista de tarefas na barra lateral"""
    # Limpar lista atual
    lista_tarefas.delete(0, tk.END)
    
    # Adicionar todas as tarefas
    for tarefa in tarefas:
        titulo = tarefa["titulo"]
        
        # Adicionar ícone de status
        if tarefa["concluida"]:
            prefixo = "✓ "
            cor = "#34c759"  # Verde
        else:
            prefixo = "○ "
            cor = "#000000"  # Preto
        
        # Limitar tamanho do título para exibição
        if len(titulo) > 30:
            titulo = titulo[:27] + "..."
        
        lista_tarefas.insert(tk.END, prefixo + titulo)
        
        # Configurar cor baseada no status
        index = tarefas.index(tarefa)
        lista_tarefas.itemconfig(index, {'fg': cor})
    
    # Atualizar contador
    atualizar_contador()

def atualizar_contador():
    """Atualiza o contador de tarefas"""
    total = len(tarefas)
    concluidas = sum(1 for tarefa in tarefas if tarefa["concluida"])
    pendentes = total - concluidas
    
    texto_contador = f"Total: {total} | Concluídas: {concluidas} | Pendentes: {pendentes}"
    label_contador.config(text=texto_contador)

def selecionar_tarefa(event):
    """Gerencia a seleção de uma tarefa na lista"""
    global tarefa_selecionada
    
    # Obter índice selecionado
    selecao = lista_tarefas.curselection()
    if not selecao:
        return
    
    indice = selecao[0]
    tarefa_selecionada = indice
    
    # Carregar tarefa no editor
    carregar_tarefa_editor()
    habilitar_editor()

def carregar_tarefa_editor():
    """Carrega a tarefa selecionada no editor"""
    if tarefa_selecionada is None:
        return
    
    tarefa = tarefas[tarefa_selecionada]
    
    # Atualizar campos
    entry_titulo.delete(0, tk.END)
    entry_titulo.insert(0, tarefa["titulo"])
    
    text_descricao.delete("1.0", tk.END)
    text_descricao.insert("1.0", tarefa["descricao"])
    
    # Atualizar botão de conclusão
    if tarefa["concluida"]:
        btn_concluir.config(text="✓ Concluída", bg="#34c759", fg="white")
    else:
        btn_concluir.config(text="Marcar como Concluída", bg="#007aff", fg="white")
    
    # Focar no título
    entry_titulo.focus()

def limpar_editor():
    """Limpa os campos do editor"""
    entry_titulo.delete(0, tk.END)
    text_descricao.delete("1.0", tk.END)
    
    # Configurar placeholders
    entry_titulo.insert(0, "Título da tarefa")
    text_descricao.insert("1.0", "Descrição da tarefa...")
    configurar_placeholders()
    
    # Resetar botão de conclusão
    btn_concluir.config(text="Marcar como Concluída", bg="#007aff", fg="white")

def habilitar_editor():
    """Habilita os campos de edição"""
    entry_titulo.config(state=tk.NORMAL, fg="#000000")
    text_descricao.config(state=tk.NORMAL, fg="#000000")
    btn_guardar.config(state=tk.NORMAL)
    btn_apagar.config(state=tk.NORMAL)
    btn_concluir.config(state=tk.NORMAL)

def desabilitar_editor():
    """Desabilita os campos de edição"""
    btn_guardar.config(state=tk.DISABLED)
    btn_apagar.config(state=tk.DISABLED)
    btn_concluir.config(state=tk.DISABLED)

def configurar_placeholders():
    """Configura os textos placeholder nos campos"""
    if entry_titulo.get().strip() == "":
        entry_titulo.delete(0, tk.END)
        entry_titulo.insert(0, "Título da tarefa")
        entry_titulo.config(fg="#999999")
    
    descricao = text_descricao.get("1.0", tk.END).strip()
    if descricao == "":
        text_descricao.delete("1.0", tk.END)
        text_descricao.insert("1.0", "Descrição da tarefa...")
        text_descricao.config(fg="#999999")

def remover_placeholder_titulo(event):
    """Remove placeholder do campo título"""
    if entry_titulo.get() == "Título da tarefa":
        entry_titulo.delete(0, tk.END)
        entry_titulo.config(fg="#000000")

def remover_placeholder_descricao(event):
    """Remove placeholder do campo descrição"""
    if text_descricao.get("1.0", tk.END).strip() == "Descrição da tarefa...":
        text_descricao.delete("1.0", tk.END)
        text_descricao.config(fg="#000000")

def restaurar_placeholder_titulo(event):
    """Restaura placeholder se campo título estiver vazio"""
    if entry_titulo.get().strip() == "":
        entry_titulo.insert(0, "Título da tarefa")
        entry_titulo.config(fg="#999999")

def restaurar_placeholder_descricao(event):
    """Restaura placeholder se campo descrição estiver vazio"""
    if text_descricao.get("1.0", tk.END).strip() == "":
        text_descricao.insert("1.0", "Descrição da tarefa...")
        text_descricao.config(fg="#999999")

def mostrar_status(mensagem):
    """Exibe uma mensagem de status temporária"""
    label_status.config(text=mensagem)
    # Limpar mensagem após 3 segundos
    root.after(3000, lambda: label_status.config(text="Pronto"))

def validar_titulo(event):
    """Valida o título durante a digitação"""
    titulo = entry_titulo.get()
    if len(titulo) > 100:
        entry_titulo.delete(100, tk.END)
        mostrar_status("Título limitado a 100 caracteres")

# ============================================================================
# CONFIGURAÇÃO DA JANELA PRINCIPAL
# ============================================================================

# Criar janela principal
root = tk.Tk()
root.title("Gestor de Tarefas")
root.geometry("900x600")
root.minsize(700, 500)

# Configurar tema claro
root.configure(bg="#f5f5f5")

# ============================================================================
# BARRA SUPERIOR
# ============================================================================

frame_superior = tk.Frame(root, bg="#ffffff", height=50)
frame_superior.pack(fill=tk.X)
frame_superior.pack_propagate(False)

# Título da aplicação
label_titulo_app = tk.Label(
    frame_superior,
    text="📋 Gestor de Tarefas",
    font=("Arial", 16, "bold"),
    bg="#ffffff",
    fg="#333333"
)
label_titulo_app.pack(side=tk.LEFT, padx=20)

# Botão Nova Tarefa
btn_nova_tarefa = tk.Button(
    frame_superior,
    text="+ Nova Tarefa",
    command=criar_tarefa,
    bg="#007aff",
    fg="#ffffff",
    font=("Arial", 10, "bold"),
    padx=15,
    pady=5,
    cursor="hand2",
    relief=tk.FLAT
)
btn_nova_tarefa.pack(side=tk.RIGHT, padx=20)

# ============================================================================
# ÁREA PRINCIPAL (LISTA + EDITOR)
# ============================================================================

frame_principal = tk.Frame(root, bg="#f5f5f5")
frame_principal.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

# ============================================================================
# PAINEL ESQUERDO - LISTA DE TAREFAS
# ============================================================================

frame_lista = tk.Frame(frame_principal, bg="#ffffff", width=250)
frame_lista.pack(side=tk.LEFT, fill=tk.Y)
frame_lista.pack_propagate(False)

# Cabeçalho da lista
frame_cabecalho_lista = tk.Frame(frame_lista, bg="#ffffff")
frame_cabecalho_lista.pack(fill=tk.X, padx=15, pady=(15, 10))

label_lista_titulo = tk.Label(
    frame_cabecalho_lista,
    text="TAREFAS",
    font=("Arial", 11, "bold"),
    bg="#ffffff",
    fg="#666666"
)
label_lista_titulo.pack(side=tk.LEFT)

label_contador = tk.Label(
    frame_cabecalho_lista,
    text="Total: 0 | Concluídas: 0 | Pendentes: 0",
    font=("Arial", 9),
    bg="#ffffff",
    fg="#999999"
)
label_contador.pack(side=tk.RIGHT)

# Lista de tarefas
frame_lista_tarefas = tk.Frame(frame_lista, bg="#ffffff")
frame_lista_tarefas.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 10))

# Scrollbar para lista
scrollbar_lista = tk.Scrollbar(frame_lista_tarefas)
scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y)

# Listbox para exibir tarefas
lista_tarefas = tk.Listbox(
    frame_lista_tarefas,
    yscrollcommand=scrollbar_lista.set,
    bg="#ffffff",
    fg="#333333",
    font=("Arial", 11),
    selectbackground="#e3f2fd",
    selectforeground="#333333",
    relief=tk.FLAT,
    highlightthickness=0,
    activestyle="none"
)
lista_tarefas.pack(fill=tk.BOTH, expand=True)

scrollbar_lista.config(command=lista_tarefas.yview)

# Vincular evento de seleção
lista_tarefas.bind('<<ListboxSelect>>', selecionar_tarefa)

# ============================================================================
# SEPARADOR VERTICAL
# ============================================================================

separador_vertical = tk.Frame(frame_principal, bg="#e0e0e0", width=1)
separador_vertical.pack(side=tk.LEFT, fill=tk.Y)

# ============================================================================
# PAINEL DIREITO - EDITOR DE TAREFAS
# ============================================================================

frame_editor = tk.Frame(frame_principal, bg="#ffffff")
frame_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ============================================================================
# BARRA DE FERRAMENTAS DO EDITOR
# ============================================================================

frame_ferramentas = tk.Frame(frame_editor, bg="#ffffff", height=50)
frame_ferramentas.pack(fill=tk.X, padx=20, pady=10)
frame_ferramentas.pack_propagate(False)

# Botão Concluir
btn_concluir = tk.Button(
    frame_ferramentas,
    text="Marcar como Concluída",
    command=marcar_concluida,
    bg="#007aff",
    fg="#ffffff",
    font=("Arial", 10, "bold"),
    padx=15,
    pady=6,
    cursor="hand2",
    state=tk.DISABLED,
    relief=tk.FLAT
)
btn_concluir.pack(side=tk.LEFT)

# Espaçador
frame_espacador_esquerda = tk.Frame(frame_ferramentas, bg="#ffffff")
frame_espacador_esquerda.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Botão Guardar
btn_guardar = tk.Button(
    frame_ferramentas,
    text="💾 Guardar",
    command=atualizar_tarefa,
    bg="#4CAF50",
    fg="#ffffff",
    font=("Arial", 10, "bold"),
    padx=15,
    pady=6,
    cursor="hand2",
    state=tk.DISABLED,
    relief=tk.FLAT
)
btn_guardar.pack(side=tk.RIGHT)

# Botão Apagar
btn_apagar = tk.Button(
    frame_ferramentas,
    text="🗑️ Apagar",
    command=deletar_tarefa,
    bg="#f44336",
    fg="#ffffff",
    font=("Arial", 10, "bold"),
    padx=15,
    pady=6,
    cursor="hand2",
    state=tk.DISABLED,
    relief=tk.FLAT
)
btn_apagar.pack(side=tk.RIGHT, padx=10)

# ============================================================================
# ÁREA DE EDIÇÃO
# ============================================================================

frame_edicao = tk.Frame(frame_editor, bg="#ffffff")
frame_edicao.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Campo Título
frame_titulo = tk.Frame(frame_edicao, bg="#ffffff")
frame_titulo.pack(fill=tk.X, pady=(0, 15))

label_titulo = tk.Label(
    frame_titulo,
    text="Título:",
    font=("Arial", 11, "bold"),
    bg="#ffffff",
    fg="#333333"
)
label_titulo.pack(anchor=tk.W)

entry_titulo = tk.Entry(
    frame_titulo,
    font=("Arial", 14),
    bg="#ffffff",
    fg="#999999",
    relief=tk.FLAT,
    highlightthickness=1,
    highlightcolor="#007aff",
    highlightbackground="#cccccc"
)
entry_titulo.pack(fill=tk.X, pady=(5, 0))
entry_titulo.insert(0, "Título da tarefa")

# Vincular eventos de placeholder
entry_titulo.bind("<FocusIn>", remover_placeholder_titulo)
entry_titulo.bind("<FocusOut>", restaurar_placeholder_titulo)
entry_titulo.bind("<KeyRelease>", validar_titulo)

# Separador
separador_horizontal = tk.Frame(frame_edicao, bg="#e0e0e0", height=1)
separador_horizontal.pack(fill=tk.X, pady=(0, 15))

# Campo Descrição
frame_descricao = tk.Frame(frame_edicao, bg="#ffffff")
frame_descricao.pack(fill=tk.BOTH, expand=True)

label_descricao = tk.Label(
    frame_descricao,
    text="Descrição:",
    font=("Arial", 11, "bold"),
    bg="#ffffff",
    fg="#333333"
)
label_descricao.pack(anchor=tk.W)

# Área de texto com scroll
frame_texto = tk.Frame(frame_descricao, bg="#ffffff")
frame_texto.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

# Scrollbars
scrollbar_vertical = tk.Scrollbar(frame_texto)
scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

scrollbar_horizontal = tk.Scrollbar(frame_texto, orient=tk.HORIZONTAL)
scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

# Widget Text para descrição
text_descricao = tk.Text(
    frame_texto,
    font=("Arial", 12),
    bg="#ffffff",
    fg="#999999",
    wrap=tk.WORD,
    relief=tk.FLAT,
    highlightthickness=1,
    highlightcolor="#007aff",
    highlightbackground="#cccccc",
    yscrollcommand=scrollbar_vertical.set,
    xscrollcommand=scrollbar_horizontal.set,
    padx=10,
    pady=10
)
text_descricao.pack(fill=tk.BOTH, expand=True)
text_descricao.insert("1.0", "Descrição da tarefa...")

# Configurar scrollbars
scrollbar_vertical.config(command=text_descricao.yview)
scrollbar_horizontal.config(command=text_descricao.xview)

# Vincular eventos de placeholder
text_descricao.bind("<FocusIn>", remover_placeholder_descricao)
text_descricao.bind("<FocusOut>", restaurar_placeholder_descricao)

# ============================================================================
# BARRA INFERIOR (STATUS)
# ============================================================================

frame_inferior = tk.Frame(root, bg="#ffffff", height=30)
frame_inferior.pack(fill=tk.X, side=tk.BOTTOM)
frame_inferior.pack_propagate(False)

# Barra de separação
barra_separacao = tk.Frame(frame_inferior, bg="#e0e0e0", height=1)
barra_separacao.pack(fill=tk.X)

# Label de status
label_status = tk.Label(
    frame_inferior,
    text="Pronto",
    font=("Arial", 9),
    bg="#ffffff",
    fg="#666666",
    anchor=tk.W
)
label_status.pack(fill=tk.X, padx=20, pady=5)

# ============================================================================
# ATALHOS DE TECLADO
# ============================================================================

def configurar_atalhos():
    """Configura atalhos de teclado"""
    # Ctrl+N: Nova tarefa
    root.bind("<Control-n>", lambda e: criar_tarefa())
    # Ctrl+S: Guardar tarefa
    root.bind("<Control-s>", lambda e: atualizar_tarefa())
    # Delete: Apagar tarefa
    root.bind("<Delete>", lambda e: deletar_tarefa())
    # Escape: Limpar seleção
    root.bind("<Escape>", lambda e: limpar_selecao())
    # Ctrl+Enter: Marcar como concluída
    root.bind("<Control-Return>", lambda e: marcar_concluida())

def limpar_selecao():
    """Limpa a seleção atual"""
    global tarefa_selecionada
    tarefa_selecionada = None
    lista_tarefas.selection_clear(0, tk.END)
    limpar_editor()
    desabilitar_editor()

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

def inicializar():
    """Inicializa a aplicação"""
    # Configurar placeholders iniciais
    configurar_placeholders()
    
    # Configurar atalhos
    configurar_atalhos()
    
    # Desabilitar editor inicialmente
    desabilitar_editor()
    
    # Atualizar lista vazia
    atualizar_lista_tarefas()
    
    # Focar na janela
    root.focus_force()

# Executar inicialização
inicializar()

# Iniciar loop principal
root.mainloop()