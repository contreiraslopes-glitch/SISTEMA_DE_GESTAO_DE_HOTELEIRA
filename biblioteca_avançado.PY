import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Variáveis globais para armazenar os dados
livros = []
emprestimos = []

# ================== CORES E ESTILO ==================
COR_PRIMARIA = "#2c3e50"       # Azul escuro
COR_SECUNDARIA = "#3498db"     # Azul claro
COR_SUCESSO = "#27ae60"        # Verde
COR_AVISO = "#f39c12"          # Laranja
COR_FUNDO = "#ecf0f1"          # Cinza claro
COR_TEXTO_ESCURO = "#2c3e50"   # Texto escuro
COR_TEXTO_CLARO = "#ffffff"    # Texto branco

# ================== FUNÇÕES DO SISTEMA ==================
def cadastrar_livro():
    """Abre a janela para cadastrar um novo livro"""
    janela_cadastrar = tk.Toplevel(root)
    janela_cadastrar.title("📚 Cadastrar Novo Livro")
    janela_cadastrar.geometry("500x400")
    janela_cadastrar.configure(bg=COR_FUNDO)
    janela_cadastrar.resizable(False, False)
    
    # Centralizar janela
    janela_cadastrar.update_idletasks()
    x = (janela_cadastrar.winfo_screenwidth() // 2) - (500 // 2)
    y = (janela_cadastrar.winfo_screenheight() // 2) - (400 // 2)
    janela_cadastrar.geometry(f'500x400+{x}+{y}')
    
    # Frame principal
    frame_principal = tk.Frame(janela_cadastrar, bg=COR_FUNDO, padx=30, pady=30)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    # Título
    tk.Label(frame_principal, text="📚 CADASTRAR NOVO LIVRO", 
             font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_PRIMARIA).pack(pady=(0, 20))
    
    # Frame do formulário
    frame_form = tk.Frame(frame_principal, bg=COR_FUNDO)
    frame_form.pack(fill=tk.BOTH, expand=True)
    
    # Formulário
    tk.Label(frame_form, text="Título do Livro:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    entry_titulo = tk.Entry(frame_form, font=("Arial", 11), width=40)
    entry_titulo.pack(pady=5)
    
    tk.Label(frame_form, text="Autor:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    entry_autor = tk.Entry(frame_form, font=("Arial", 11), width=40)
    entry_autor.pack(pady=5)
    
    tk.Label(frame_form, text="Ano de Publicação:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    entry_ano = tk.Entry(frame_form, font=("Arial", 11), width=40)
    entry_ano.pack(pady=5)
    
    # Função para cadastrar
    def salvar_livro():
        titulo = entry_titulo.get().strip()
        autor = entry_autor.get().strip()
        ano = entry_ano.get().strip()
        
        if not titulo or not autor:
            messagebox.showerror("Erro", "Título e autor são obrigatórios!", parent=janela_cadastrar)
            return
        
        livro_id = len(livros) + 1
        livro = {
            'id': livro_id,
            'titulo': titulo,
            'autor': autor,
            'ano': ano if ano else "Desconhecido",
            'disponivel': True
        }
        
        livros.append(livro)
        messagebox.showinfo("Sucesso", f"Livro '{titulo}' cadastrado com sucesso!", parent=janela_cadastrar)
        janela_cadastrar.destroy()
        atualizar_lista_livros()
        atualizar_estatisticas()
    
    # Frame para botões
    frame_botoes = tk.Frame(frame_principal, bg=COR_FUNDO)
    frame_botoes.pack(pady=20)
    
    # Botões lado a lado
    btn_salvar = tk.Button(frame_botoes, text="Cadastrar", font=("Arial", 11, "bold"),
                          bg=COR_SUCESSO, fg=COR_TEXTO_CLARO, padx=30, pady=10,
                          command=salvar_livro, cursor="hand2")
    btn_salvar.pack(side=tk.LEFT, padx=5)
    
    btn_cancelar = tk.Button(frame_botoes, text="Cancelar", font=("Arial", 11),
                            bg=COR_AVISO, fg=COR_TEXTO_CLARO, padx=30, pady=10,
                            command=janela_cadastrar.destroy, cursor="hand2")
    btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    entry_titulo.focus_set()

def emprestar_livro():
    """Abre a janela para emprestar um livro"""
    # Verificar se há livros disponíveis
    livros_disponiveis = [l for l in livros if l['disponivel']]
    if not livros_disponiveis:
        messagebox.showinfo("Informação", "Não há livros disponíveis para empréstimo!", parent=root)
        return
    
    janela_emprestar = tk.Toplevel(root)
    janela_emprestar.title("📤 Emprestar Livro")
    janela_emprestar.geometry("500x350")
    janela_emprestar.configure(bg=COR_FUNDO)
    janela_emprestar.resizable(False, False)
    
    # Centralizar janela
    janela_emprestar.update_idletasks()
    x = (janela_emprestar.winfo_screenwidth() // 2) - (500 // 2)
    y = (janela_emprestar.winfo_screenheight() // 2) - (350 // 2)
    janela_emprestar.geometry(f'500x350+{x}+{y}')
    
    # Frame principal
    frame_principal = tk.Frame(janela_emprestar, bg=COR_FUNDO, padx=30, pady=30)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    # Título
    tk.Label(frame_principal, text="📤 EMPRESTAR LIVRO", 
             font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_PRIMARIA).pack(pady=(0, 20))
    
    # Formulário
    tk.Label(frame_principal, text="Selecione o Livro:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    
    # Lista de livros disponíveis
    livros_opcoes = [f"{l['id']}: {l['titulo']} ({l['autor']})" for l in livros_disponiveis]
    combo_livro = ttk.Combobox(frame_principal, values=livros_opcoes, 
                               state="readonly", font=("Arial", 11), width=40)
    combo_livro.pack(pady=5)
    if livros_opcoes:
        combo_livro.current(0)
    
    tk.Label(frame_principal, text="Nome da Pessoa:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    entry_pessoa = tk.Entry(frame_principal, font=("Arial", 11), width=40)
    entry_pessoa.pack(pady=5)
    
    # Função para realizar empréstimo
    def realizar_emprestimo():
        selecao = combo_livro.get()
        if not selecao:
            messagebox.showerror("Erro", "Selecione um livro!", parent=janela_emprestar)
            return
        
        nome_pessoa = entry_pessoa.get().strip()
        if not nome_pessoa:
            messagebox.showerror("Erro", "Digite o nome da pessoa!", parent=janela_emprestar)
            return
        
        livro_id = int(selecao.split(":")[0].strip())
        
        # Encontrar livro
        for livro in livros:
            if livro['id'] == livro_id and livro['disponivel']:
                livro['disponivel'] = False
                
                # Registrar empréstimo
                emprestimo_id = len(emprestimos) + 1
                data_emprestimo = datetime.now()
                data_devolucao = data_emprestimo + timedelta(days=14)
                
                emprestimo = {
                    'id': emprestimo_id,
                    'livro_id': livro_id,
                    'titulo': livro['titulo'],
                    'pessoa': nome_pessoa,
                    'data_emprestimo': data_emprestimo.strftime("%d/%m/%Y"),
                    'data_devolucao_prevista': data_devolucao.strftime("%d/%m/%Y"),
                    'devolvido': False
                }
                
                emprestimos.append(emprestimo)
                messagebox.showinfo("Sucesso", 
                    f"Livro '{livro['titulo']}' emprestado para {nome_pessoa}!\nData para devolução: {data_devolucao.strftime('%d/%m/%Y')}",
                    parent=janela_emprestar)
                
                janela_emprestar.destroy()
                atualizar_lista_livros()
                atualizar_estatisticas()
                return
        
        messagebox.showerror("Erro", "Livro não está mais disponível!", parent=janela_emprestar)
    
    # Botões
    frame_botoes = tk.Frame(frame_principal, bg=COR_FUNDO)
    frame_botoes.pack(pady=30)
    
    tk.Button(frame_botoes, text="Emprestar", font=("Arial", 11, "bold"),
              bg=COR_AVISO, fg=COR_TEXTO_CLARO, padx=30, pady=10,
              command=realizar_emprestimo, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    tk.Button(frame_botoes, text="Cancelar", font=("Arial", 11),
              bg="#95a5a6", fg=COR_TEXTO_CLARO, padx=30, pady=10,
              command=janela_emprestar.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    entry_pessoa.focus_set()

def devolver_livro():
    """Abre a janela para devolver um livro"""
    # Verificar se há empréstimos ativos
    emprestimos_ativos = [e for e in emprestimos if not e['devolvido']]
    if not emprestimos_ativos:
        messagebox.showinfo("Informação", "Não há empréstimos ativos para devolução!", parent=root)
        return
    
    janela_devolver = tk.Toplevel(root)
    janela_devolver.title("📥 Devolver Livro")
    janela_devolver.geometry("500x300")
    janela_devolver.configure(bg=COR_FUNDO)
    janela_devolver.resizable(False, False)
    
    # Centralizar janela
    janela_devolver.update_idletasks()
    x = (janela_devolver.winfo_screenwidth() // 2) - (500 // 2)
    y = (janela_devolver.winfo_screenheight() // 2) - (300 // 2)
    janela_devolver.geometry(f'500x300+{x}+{y}')
    
    # Frame principal
    frame_principal = tk.Frame(janela_devolver, bg=COR_FUNDO, padx=30, pady=30)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    # Título
    tk.Label(frame_principal, text="📥 DEVOLVER LIVRO", 
             font=("Arial", 18, "bold"), bg=COR_FUNDO, fg=COR_PRIMARIA).pack(pady=(0, 20))
    
    # Formulário
    tk.Label(frame_principal, text="Selecione o Empréstimo:", 
             font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(anchor=tk.W, pady=(10, 5))
    
    # Lista de empréstimos ativos
    emprestimos_opcoes = [f"{e['id']}: {e['titulo']} - {e['pessoa']}" for e in emprestimos_ativos]
    combo_emprestimo = ttk.Combobox(frame_principal, values=emprestimos_opcoes, 
                                    state="readonly", font=("Arial", 11), width=40)
    combo_emprestimo.pack(pady=5)
    if emprestimos_opcoes:
        combo_emprestimo.current(0)
    
    # Função para realizar devolução
    def realizar_devolucao():
        selecao = combo_emprestimo.get()
        if not selecao:
            messagebox.showerror("Erro", "Selecione um empréstimo!", parent=janela_devolver)
            return
        
        emprestimo_id = int(selecao.split(":")[0].strip())
        
        # Encontrar empréstimo
        for emprestimo in emprestimos:
            if emprestimo['id'] == emprestimo_id and not emprestimo['devolvido']:
                emprestimo['devolvido'] = True
                emprestimo['data_devolucao_real'] = datetime.now().strftime("%d/%m/%Y")
                
                # Marcar livro como disponível
                for livro in livros:
                    if livro['id'] == emprestimo['livro_id']:
                        livro['disponivel'] = True
                        break
                
                messagebox.showinfo("Sucesso", 
                    f"Livro '{emprestimo['titulo']}' devolvido com sucesso!",
                    parent=janela_devolver)
                
                janela_devolver.destroy()
                atualizar_lista_livros()
                atualizar_estatisticas()
                return
        
        messagebox.showerror("Erro", "Empréstimo não encontrado!", parent=janela_devolver)
    
    # Botões
    frame_botoes = tk.Frame(frame_principal, bg=COR_FUNDO)
    frame_botoes.pack(pady=30)
    
    tk.Button(frame_botoes, text="Devolver", font=("Arial", 11, "bold"),
              bg="#e74c3c", fg=COR_TEXTO_CLARO, padx=30, pady=10,
              command=realizar_devolucao, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    tk.Button(frame_botoes, text="Cancelar", font=("Arial", 11),
              bg="#95a5a6", fg=COR_TEXTO_CLARO, padx=30, pady=10,
              command=janela_devolver.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)

def atualizar_lista_livros():
    """Atualiza a lista de livros na interface"""
    # Limpar a treeview
    for item in tree_livros.get_children():
        tree_livros.delete(item)
    
    # Adicionar livros à treeview
    for livro in livros:
        status = "✅ Disponível" if livro['disponivel'] else "⏳ Emprestado"
        tree_livros.insert("", tk.END, values=(
            livro['id'], 
            livro['titulo'], 
            livro['autor'], 
            livro['ano'], 
            status
        ))
    
    # Atualizar contador
    label_contador.config(text=f"Total de Livros: {len(livros)}")

def atualizar_estatisticas():
    """Atualiza as estatísticas na interface"""
    total = len(livros)
    disponiveis = sum(1 for livro in livros if livro['disponivel'])
    emprestados = total - disponiveis
    
    label_disponiveis.config(text=f"Disponíveis: {disponiveis}")
    label_emprestados.config(text=f"Emprestados: {emprestados}")
    
    # Atualizar cores
    label_disponiveis.config(fg="#27ae60" if disponiveis > 0 else "#7f8c8d")
    label_emprestados.config(fg="#e74c3c" if emprestados > 0 else "#7f8c8d")

def pesquisar_livros():
    """Pesquisa livros por título ou autor"""
    termo = entry_pesquisa.get().strip().lower()
    
    # Limpar a treeview
    for item in tree_livros.get_children():
        tree_livros.delete(item)
    
    # Filtrar livros
    if termo:
        livros_filtrados = [l for l in livros 
                          if termo in l['titulo'].lower() 
                          or termo in l['autor'].lower()]
    else:
        livros_filtrados = livros
    
    # Adicionar à treeview
    for livro in livros_filtrados:
        status = "✅ Disponível" if livro['disponivel'] else "⏳ Emprestado"
        tree_livros.insert("", tk.END, values=(
            livro['id'], 
            livro['titulo'], 
            livro['autor'], 
            livro['ano'], 
            status
        ))
    
    label_contador.config(text=f"Livros encontrados: {len(livros_filtrados)}")

# ================== INTERFACE PRINCIPAL ==================
root = tk.Tk()
root.title("📚 Sistema de Gestão de Biblioteca")
root.geometry("1000x700")
root.configure(bg=COR_FUNDO)

# Centralizar janela
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (1000 // 2)
y = (root.winfo_screenheight() // 2) - (700 // 2)
root.geometry(f'1000x700+{x}+{y}')

# ================== CABEÇALHO ==================
header_frame = tk.Frame(root, bg=COR_PRIMARIA, height=80)
header_frame.pack(fill=tk.X)

tk.Label(header_frame, text="📚 BIBLIOTECA DIGITAL", 
         font=("Arial", 24, "bold"), bg=COR_PRIMARIA, fg=COR_TEXTO_CLARO).pack(pady=20)

# ================== BARRA DE BOTÕES PRINCIPAIS ==================
botoes_frame = tk.Frame(root, bg=COR_FUNDO, pady=15)
botoes_frame.pack(fill=tk.X)

# Configurar grid para os botões
botoes_frame.columnconfigure(0, weight=1)
botoes_frame.columnconfigure(1, weight=1)
botoes_frame.columnconfigure(2, weight=1)

# Botão Cadastrar Livro
btn_cadastrar = tk.Button(botoes_frame, text="📚 Cadastrar Livro", 
                          font=("Arial", 12, "bold"), bg=COR_SUCESSO, fg=COR_TEXTO_CLARO,
                          padx=20, pady=15, command=cadastrar_livro, cursor="hand2")
btn_cadastrar.grid(row=0, column=0, padx=10, sticky="ew")

# Botão Emprestar Livro
btn_emprestar = tk.Button(botoes_frame, text="📤 Emprestar Livro", 
                          font=("Arial", 12, "bold"), bg=COR_SECUNDARIA, fg=COR_TEXTO_CLARO,
                          padx=20, pady=15, command=emprestar_livro, cursor="hand2")
btn_emprestar.grid(row=0, column=1, padx=10, sticky="ew")

# Botão Devolver Livro
btn_devolver = tk.Button(botoes_frame, text="📥 Devolver Livro", 
                         font=("Arial", 12, "bold"), bg=COR_AVISO, fg=COR_TEXTO_CLARO,
                         padx=20, pady=15, command=devolver_livro, cursor="hand2")
btn_devolver.grid(row=0, column=2, padx=10, sticky="ew")

# ================== BARRA DE PESQUISA ==================
pesquisa_frame = tk.Frame(root, bg=COR_FUNDO, pady=15)
pesquisa_frame.pack(fill=tk.X, padx=20)

tk.Label(pesquisa_frame, text="🔍 Pesquisar:", 
         font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO_ESCURO).pack(side=tk.LEFT, padx=(0, 10))

entry_pesquisa = tk.Entry(pesquisa_frame, font=("Arial", 11), width=40)
entry_pesquisa.pack(side=tk.LEFT, padx=5)
entry_pesquisa.bind("<Return>", lambda e: pesquisar_livros())

tk.Button(pesquisa_frame, text="Buscar", font=("Arial", 10, "bold"),
          bg=COR_SECUNDARIA, fg=COR_TEXTO_CLARO, padx=20, pady=8,
          command=pesquisar_livros, cursor="hand2").pack(side=tk.LEFT, padx=5)

tk.Button(pesquisa_frame, text="Limpar", font=("Arial", 10),
          bg="#95a5a6", fg=COR_TEXTO_CLARO, padx=20, pady=8,
          command=lambda: [entry_pesquisa.delete(0, tk.END), pesquisar_livros()], 
          cursor="hand2").pack(side=tk.LEFT, padx=5)

# ================== ESTATÍSTICAS ==================
stats_frame = tk.Frame(root, bg=COR_FUNDO, pady=10)
stats_frame.pack(fill=tk.X, padx=20)

label_contador = tk.Label(stats_frame, text="Total de Livros: 0", 
                         font=("Arial", 11, "bold"), bg=COR_FUNDO, fg=COR_PRIMARIA)
label_contador.pack(side=tk.LEFT)

label_disponiveis = tk.Label(stats_frame, text="Disponíveis: 0", 
                            font=("Arial", 11), bg=COR_FUNDO, fg="#7f8c8d")
label_disponiveis.pack(side=tk.LEFT, padx=30)

label_emprestados = tk.Label(stats_frame, text="Emprestados: 0", 
                            font=("Arial", 11), bg=COR_FUNDO, fg="#7f8c8d")
label_emprestados.pack(side=tk.LEFT)

# ================== LISTA DE LIVROS ==================
lista_frame = tk.Frame(root, bg=COR_FUNDO)
lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Container para treeview com scrollbars
tree_container = tk.Frame(lista_frame, bg=COR_FUNDO)
tree_container.pack(fill=tk.BOTH, expand=True)

# Scrollbars
scroll_y = tk.Scrollbar(tree_container)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = tk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Treeview
tree_livros = ttk.Treeview(tree_container,
                          yscrollcommand=scroll_y.set,
                          xscrollcommand=scroll_x.set,
                          selectmode="browse",
                          height=15)

scroll_y.config(command=tree_livros.yview)
scroll_x.config(command=tree_livros.xview)

# Definir colunas
tree_livros['columns'] = ("ID", "Título", "Autor", "Ano", "Status")
tree_livros.column("#0", width=0, stretch=tk.NO)
tree_livros.column("ID", width=50, anchor=tk.CENTER)
tree_livros.column("Título", width=300, anchor=tk.W)
tree_livros.column("Autor", width=200, anchor=tk.W)
tree_livros.column("Ano", width=80, anchor=tk.CENTER)
tree_livros.column("Status", width=120, anchor=tk.CENTER)

# Cabeçalhos
tree_livros.heading("ID", text="ID", anchor=tk.CENTER)
tree_livros.heading("Título", text="Título", anchor=tk.CENTER)
tree_livros.heading("Autor", text="Autor", anchor=tk.CENTER)
tree_livros.heading("Ano", text="Ano", anchor=tk.CENTER)
tree_livros.heading("Status", text="Status", anchor=tk.CENTER)

tree_livros.pack(fill=tk.BOTH, expand=True)

# Configurar estilo da treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", 
                background="white",
                foreground=COR_TEXTO_ESCURO,
                rowheight=30,
                fieldbackground="white",
                font=("Arial", 10))

style.configure("Treeview.Heading", 
                background=COR_PRIMARIA,
                foreground=COR_TEXTO_CLARO,
                font=("Arial", 11, "bold"))

style.map("Treeview", background=[("selected", COR_SECUNDARIA)])

# ================== RODAPÉ ==================
footer_frame = tk.Frame(root, bg=COR_PRIMARIA, height=50)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

tk.Label(footer_frame, 
         text="Sistema de Gestão de Biblioteca | Projeto Escolar | Todos os direitos reservados",
         font=("Arial", 9), bg=COR_PRIMARIA, fg=COR_TEXTO_CLARO).pack(pady=15)

# ================== BOTÃO ATUALIZAR ==================
btn_atualizar_frame = tk.Frame(root, bg=COR_FUNDO)
btn_atualizar_frame.pack(pady=10)

tk.Button(btn_atualizar_frame, text="🔄 Atualizar Lista", font=("Arial", 10, "bold"),
          bg="#34495e", fg=COR_TEXTO_CLARO, padx=20, pady=8,
          command=lambda: [pesquisar_livros(), atualizar_estatisticas()], 
          cursor="hand2").pack()

# ================== INICIALIZAR ==================
# Atualizar interface inicial
pesquisar_livros()
atualizar_estatisticas()

# Iniciar aplicação
root.mainloop()