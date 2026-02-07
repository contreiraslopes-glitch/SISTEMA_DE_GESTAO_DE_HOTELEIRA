import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
                    
# Variáveis globais para armazenar os dados
livros = []
emprestimos = []

# Funções principais do sistema
def cadastrar_livro():
    """Cadastra um novo livro no sistema"""
    titulo = entry_titulo.get()
    autor = entry_autor.get()
    ano = entry_ano.get()
    
    if not titulo or not autor:
        messagebox.showerror("Erro", "Preencha título e autor do livro!")
        return
    
    # Gerar ID único para o livro
    livro_id = len(livros) + 1
    
    livro = {
        'id': livro_id,
        'titulo': titulo,
        'autor': autor,
        'ano': ano if ano else "Desconhecido",
        'disponivel': True
    }
    
    livros.append(livro)
    
    # Limpar campos de entrada
    entry_titulo.delete(0, tk.END)
    entry_autor.delete(0, tk.END)
    entry_ano.delete(0, tk.END)
    
    messagebox.showinfo("Sucesso", f"Livro '{titulo}' cadastrado com sucesso!")
    atualizar_lista_livros()

def emprestar_livro():
    """Realiza o empréstimo de um livro"""
    livro_id = combo_livros_emprestar.get().split(":")[0].strip()
    
    if not livro_id.isdigit():
        messagebox.showerror("Erro", "Selecione um livro válido!")
        return
    
    livro_id = int(livro_id)
    nome_pessoa = entry_pessoa.get()
    
    if not nome_pessoa:
        messagebox.showerror("Erro", "Digite o nome da pessoa!")
        return
    
    # Verificar se o livro existe e está disponível
    livro_encontrado = None
    for livro in livros:
        if livro['id'] == livro_id and livro['disponivel']:
            livro_encontrado = livro
            break
    
    if not livro_encontrado:
        messagebox.showerror("Erro", "Livro não disponível para empréstimo!")
        return
    
    # Marcar livro como indisponível
    livro_encontrado['disponivel'] = False
    
    # Registrar empréstimo
    emprestimo_id = len(emprestimos) + 1
    data_emprestimo = datetime.now()
    data_devolucao = data_emprestimo + timedelta(days=14)  # Prazo de 14 dias
    
    emprestimo = {
        'id': emprestimo_id,
        'livro_id': livro_id,
        'titulo': livro_encontrado['titulo'],
        'pessoa': nome_pessoa,
        'data_emprestimo': data_emprestimo.strftime("%d/%m/%Y"),
        'data_devolucao_prevista': data_devolucao.strftime("%d/%m/%Y"),
        'devolvido': False
    }
    
    emprestimos.append(emprestimo)
    
    # Limpar campos
    entry_pessoa.delete(0, tk.END)
    
    messagebox.showinfo("Sucesso", f"Livro '{livro_encontrado['titulo']}' emprestado para {nome_pessoa}!")
    atualizar_lista_livros()
    atualizar_livros_para_emprestar()
    atualizar_livros_para_devolver()

def devolver_livro():
    """Registra a devolução de um livro"""
    emprestimo_selecionado = combo_livros_devolver.get()
    
    if not emprestimo_selecionado:
        messagebox.showerror("Erro", "Selecione um empréstimo para devolver!")
        return
    
    # Extrair ID do empréstimo
    emprestimo_id = int(emprestimo_selecionado.split(":")[0].strip())
    
    # Encontrar empréstimo
    emprestimo_encontrado = None
    for emprestimo in emprestimos:
        if emprestimo['id'] == emprestimo_id and not emprestimo['devolvido']:
            emprestimo_encontrado = emprestimo
            break
    
    if not emprestimo_encontrado:
        messagebox.showerror("Erro", "Empréstimo não encontrado!")
        return
    
    # Marcar empréstimo como devolvido
    emprestimo_encontrado['devolvido'] = True
    emprestimo_encontrado['data_devolucao_real'] = datetime.now().strftime("%d/%m/%Y")
    
    # Marcar livro como disponível
    for livro in livros:
        if livro['id'] == emprestimo_encontrado['livro_id']:
            livro['disponivel'] = True
            break
    
    messagebox.showinfo("Sucesso", f"Livro '{emprestimo_encontrado['titulo']}' devolvido com sucesso!")
    atualizar_lista_livros()
    atualizar_livros_para_emprestar()
    atualizar_livros_para_devolver()

# Funções auxiliares para atualizar listas
def atualizar_lista_livros():
    """Atualiza a lista de livros na aba de visualização"""
    # Limpar a treeview
    for item in tree_livros.get_children():
        tree_livros.delete(item)
    
    # Adicionar livros à treeview
    for livro in livros:
        status = "Disponível" if livro['disponivel'] else "Emprestado"
        tree_livros.insert("", tk.END, values=(
            livro['id'], 
            livro['titulo'], 
            livro['autor'], 
            livro['ano'], 
            status
        ))

def atualizar_livros_para_emprestar():
    """Atualiza a lista de livros disponíveis para empréstimo"""
    combo_livros_emprestar['values'] = []
    
    livros_disponiveis = []
    for livro in livros:
        if livro['disponivel']:
            livros_disponiveis.append(f"{livro['id']}: {livro['titulo']} ({livro['autor']})")
    
    combo_livros_emprestar['values'] = livros_disponiveis
    if livros_disponiveis:
        combo_livros_emprestar.current(0)

def atualizar_livros_para_devolver():
    """Atualiza a lista de livros emprestados para devolução"""
    combo_livros_devolver['values'] = []
    
    emprestimos_ativos = []
    for emprestimo in emprestimos:
        if not emprestimo['devolvido']:
            emprestimos_ativos.append(f"{emprestimo['id']}: {emprestimo['titulo']} - {emprestimo['pessoa']}")
    
    combo_livros_devolver['values'] = emprestimos_ativos
    if emprestimos_ativos:
        combo_livros_devolver.current(0)

def atualizar_estatisticas():
    """Atualiza as estatísticas na tela principal"""
    total_livros = len(livros)
    livros_disponiveis = sum(1 for livro in livros if livro['disponivel'])
    livros_emprestados = total_livros - livros_disponiveis
    emprestimos_ativos = sum(1 for emprestimo in emprestimos if not emprestimo['devolvido'])
    
    label_total_livros.config(text=f"Total de Livros: {total_livros}")
    label_livros_disponiveis.config(text=f"Livros Disponíveis: {livros_disponiveis}")
    label_livros_emprestados.config(text=f"Livros Emprestados: {livros_emprestados}")
    label_emprestimos_ativos.config(text=f"Empréstimos Ativos: {emprestimos_ativos}")

def atualizar_tudo():
    """Atualiza todas as listas e estatísticas"""
    atualizar_lista_livros()
    atualizar_livros_para_emprestar()
    atualizar_livros_para_devolver()
    atualizar_estatisticas()

# Configuração da janela principal
root = tk.Tk()
root.title("Sistema de Gestão de Biblioteca")
root.geometry("800x600")
root.resizable(True, True)

# Configurar estilo
style = ttk.Style()
style.theme_use('clam')

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configurar expansão da grade
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Título do sistema
titulo = ttk.Label(main_frame, text="Sistema de Gestão de Biblioteca", font=("Arial", 16, "bold"))
titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))

# Criar notebook (abas)
notebook = ttk.Notebook(main_frame)
notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

# Aba 1: Cadastrar Livro
aba_cadastrar = ttk.Frame(notebook, padding="10")
notebook.add(aba_cadastrar, text="Cadastrar Livro")

# Campos para cadastro
label_titulo = ttk.Label(aba_cadastrar, text="Título do Livro:", font=("Arial", 10))
label_titulo.grid(row=0, column=0, sticky=tk.W, pady=5)
entry_titulo = ttk.Entry(aba_cadastrar, width=40)
entry_titulo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

label_autor = ttk.Label(aba_cadastrar, text="Autor:", font=("Arial", 10))
label_autor.grid(row=1, column=0, sticky=tk.W, pady=5)
entry_autor = ttk.Entry(aba_cadastrar, width=40)
entry_autor.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

label_ano = ttk.Label(aba_cadastrar, text="Ano de Publicação (opcional):", font=("Arial", 10))
label_ano.grid(row=2, column=0, sticky=tk.W, pady=5)
entry_ano = ttk.Entry(aba_cadastrar, width=40)
entry_ano.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

# Botão para cadastrar
btn_cadastrar = ttk.Button(aba_cadastrar, text="Cadastrar Livro", command=cadastrar_livro, width=20)
btn_cadastrar.grid(row=3, column=0, columnspan=2, pady=20)

# Aba 2: Emprestar Livro
aba_emprestar = ttk.Frame(notebook, padding="10")
notebook.add(aba_emprestar, text="Emprestar Livro")

# Lista de livros disponíveis
label_selecionar_livro = ttk.Label(aba_emprestar, text="Selecione o Livro:", font=("Arial", 10))
label_selecionar_livro.grid(row=0, column=0, sticky=tk.W, pady=5)

combo_livros_emprestar = ttk.Combobox(aba_emprestar, width=50, state="readonly")
combo_livros_emprestar.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

# Campo para nome da pessoa
label_pessoa = ttk.Label(aba_emprestar, text="Nome da Pessoa:", font=("Arial", 10))
label_pessoa.grid(row=1, column=0, sticky=tk.W, pady=5)
entry_pessoa = ttk.Entry(aba_emprestar, width=40)
entry_pessoa.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

# Botão para emprestar
btn_emprestar = ttk.Button(aba_emprestar, text="Realizar Empréstimo", command=emprestar_livro, width=20)
btn_emprestar.grid(row=2, column=0, columnspan=2, pady=20)

# Aba 3: Devolver Livro
aba_devolver = ttk.Frame(notebook, padding="10")
notebook.add(aba_devolver, text="Devolver Livro")

# Lista de livros emprestados
label_selecionar_devolucao = ttk.Label(aba_devolver, text="Selecione o Empréstimo:", font=("Arial", 10))
label_selecionar_devolucao.grid(row=0, column=0, sticky=tk.W, pady=5)

combo_livros_devolver = ttk.Combobox(aba_devolver, width=50, state="readonly")
combo_livros_devolver.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

# Botão para devolver
btn_devolver = ttk.Button(aba_devolver, text="Registrar Devolução", command=devolver_livro, width=20)
btn_devolver.grid(row=1, column=0, columnspan=2, pady=20)

# Aba 4: Ver Livros
aba_ver = ttk.Frame(notebook, padding="10")
notebook.add(aba_ver, text="Ver Livros")

# Treeview para listar livros
frame_tree = ttk.Frame(aba_ver)
frame_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configurar treeview com scrollbar
tree_scroll = ttk.Scrollbar(frame_tree)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree_livros = ttk.Treeview(frame_tree, yscrollcommand=tree_scroll.set, selectmode="browse", height=15)
tree_scroll.config(command=tree_livros.yview)

# Definir colunas
tree_livros['columns'] = ("ID", "Título", "Autor", "Ano", "Status")
tree_livros.column("#0", width=0, stretch=tk.NO)
tree_livros.column("ID", width=50, anchor=tk.CENTER)
tree_livros.column("Título", width=200, anchor=tk.W)
tree_livros.column("Autor", width=150, anchor=tk.W)
tree_livros.column("Ano", width=80, anchor=tk.CENTER)
tree_livros.column("Status", width=100, anchor=tk.CENTER)

# Criar cabeçalhos
tree_livros.heading("ID", text="ID", anchor=tk.CENTER)
tree_livros.heading("Título", text="Título", anchor=tk.CENTER)
tree_livros.heading("Autor", text="Autor", anchor=tk.CENTER)
tree_livros.heading("Ano", text="Ano", anchor=tk.CENTER)
tree_livros.heading("Status", text="Status", anchor=tk.CENTER)                                                  

tree_livros.pack(fill=tk.BOTH, expand=True)

# Frame de estatísticas
frame_stats = ttk.LabelFrame(main_frame, text="Estatísticas da Biblioteca", padding="10")
frame_stats.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 10))

label_total_livros = ttk.Label(frame_stats, text="Total de Livros: 0", font=("Arial", 10))
label_total_livros.grid(row=0, column=0, padx=20, pady=5)

label_livros_disponiveis = ttk.Label(frame_stats, text="Livros Disponíveis: 0", font=("Arial", 10))
label_livros_disponiveis.grid(row=0, column=1, padx=20, pady=5)

label_livros_emprestados = ttk.Label(frame_stats, text="Livros Emprestados: 0", font=("Arial", 10))
label_livros_emprestados.grid(row=0, column=2, padx=20, pady=5)

label_emprestimos_ativos = ttk.Label(frame_stats, text="Empréstimos Ativos: 0", font=("Arial", 10))
label_emprestimos_ativos.grid(row=0, column=3, padx=20, pady=5)

# Botão para atualizar dados
btn_atualizar = ttk.Button(main_frame, text="Atualizar Dados", command=atualizar_tudo, width=20)
btn_atualizar.grid(row=3, column=0, columnspan=2, pady=(10, 0))

# Adicionar alguns livros de exemplo ao iniciar o sistema
livros_exemplo = [
    {'id': 1, 'titulo': 'Dom Casmurro', 'autor': 'Machado de Assis', 'ano': '1899', 'disponivel': True},
    {'id': 2, 'titulo': 'O Senhor dos Anéis', 'autor': 'J.R.R. Tolkien', 'ano': '1954', 'disponivel': True},
    {'id': 3, 'titulo': '1984', 'autor': 'George Orwell', 'ano': '1949', 'disponivel': True},
    {'id': 4, 'titulo': 'A Revolução dos Bichos', 'autor': 'George Orwell', 'ano': '1945', 'disponivel': True},
    {'id': 5, 'titulo': 'Harry Potter e a Pedra Filosofal', 'autor': 'J.K. Rowling', 'ano': '1997', 'disponivel': True}
]

livros.extend(livros_exemplo)

# Atualizar dados iniciais
atualizar_tudo()

# Iniciar a aplicação
root.mainloop()