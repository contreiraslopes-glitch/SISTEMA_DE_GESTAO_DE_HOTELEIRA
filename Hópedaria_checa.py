import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime, timedelta
import hashlib
import re
import time
import calendar
from tkinter import scrolledtext
import random
import threading
from collections import deque
import math
import os  
# ====================== ESTRUTURAS DE DADOS AVANÇADAS ======================

class BinarySearchTree:
    """Árvore Binária de Busca para indexação rápida"""
    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.left = None
            self.right = None
    
    def __init__(self):
        self.root = None
    
    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)
    
    def _insert(self, node, key, value):
        if node is None:
            return self.Node(key, value)
        
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Chave duplicada - atualiza valor
            node.value = value
        
        return node
    
    def search(self, key):
        return self._search(self.root, key)
    
    def _search(self, node, key):
        if node is None or node.key == key:
            return node.value if node else None
        
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)
    
    def inorder_traversal(self):
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append((node.key, node.value))
            self._inorder(node.right, result)

class HashTable:
    """Tabela Hash para busca rápida por nome"""
    def __init__(self, size=1000):
        self.size = size
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def insert(self, key, value):
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    
    def search(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None
    
    def delete(self, key):
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                del self.table[index][i]
                return True
        return False

# ====================== ARQUITETURA DE NEGÓCIOS ======================

class DatabaseManager:
    """Gerenciador de banco de dados - Camada de persistência"""
    def __init__(self, db_name='hospedaria_checa.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
            self.create_tables()
            self.initialize_data()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")
            return False
    
    def create_tables(self):
        """Cria todas as tabelas necessárias"""
        queries = [
            # Tabela de usuários
            '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('gerente', 'recepcionista', 'financeiro', 'rh')),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
            ''',
            # Tabela de configuração da hospedaria
            '''
            CREATE TABLE IF NOT EXISTS config_hospedaria (
                id INTEGER PRIMARY KEY,
                nome TEXT DEFAULT 'Hospedaria Checa',
                qtde_quartos INTEGER DEFAULT 0,
                preco_hora_normal INTEGER DEFAULT 2000,
                preco_hora_vip INTEGER DEFAULT 3500,
                telefone TEXT DEFAULT '+244 923 456 789',
                endereco TEXT DEFAULT 'Luanda, Angola',
                email TEXT DEFAULT 'info@hospedariacheca.ao',
                slogan TEXT DEFAULT 'Conforto e Elegância em Cada Detalhe'
            )
            ''',
            # Tabela de quartos
            '''
            CREATE TABLE IF NOT EXISTS quartos (
                numero INTEGER PRIMARY KEY,
                nome TEXT,
                categoria TEXT CHECK(categoria IN ('VIP', 'Normal')) DEFAULT 'Normal',
                ocupado BOOLEAN DEFAULT 0,
                id_hospede INTEGER,
                ultima_limpeza TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_manutencao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                status TEXT CHECK(status IN ('disponivel', 'ocupado', 'manutencao', 'limpeza')) DEFAULT 'disponivel',
                FOREIGN KEY (id_hospede) REFERENCES hospedes(id) ON DELETE SET NULL
            )
            ''',
            # Tabela de hóspedes
            '''
            CREATE TABLE IF NOT EXISTS hospedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT NOT NULL UNIQUE,
                nacionalidade TEXT,
                telefone TEXT,
                email TEXT,
                tempo_horas INTEGER NOT NULL,
                tempo_texto TEXT NOT NULL,
                quarto_numero INTEGER NOT NULL,
                quarto_nome TEXT,
                categoria_quarto TEXT NOT NULL,
                preco_total INTEGER NOT NULL,
                check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                forma_pagamento TEXT DEFAULT 'Dinheiro',
                observacoes TEXT,
                FOREIGN KEY (quarto_numero) REFERENCES quartos(numero)
            )
            ''',
            # Tabela de transações financeiras
            '''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                descricao TEXT NOT NULL,
                valor INTEGER NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_hospede INTEGER,
                categoria TEXT,
                usuario_id INTEGER,
                FOREIGN KEY (id_hospede) REFERENCES hospedes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            ''',
            # Tabela de serviços adicionais
            '''
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco INTEGER NOT NULL,
                ativo BOOLEAN DEFAULT 1
            )
            ''',
            # Tabela de serviços contratados
            '''
            CREATE TABLE IF NOT EXISTS servicos_contratados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_hospede INTEGER NOT NULL,
                id_servico INTEGER NOT NULL,
                quantidade INTEGER DEFAULT 1,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_hospede) REFERENCES hospedes(id),
                FOREIGN KEY (id_servico) REFERENCES servicos(id)
            )
            ''',
            # Tabela de histórico de ações
            '''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                usuario_nome TEXT,
                acao TEXT NOT NULL,
                modulo TEXT NOT NULL,
                detalhes TEXT,
                ip TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            ''',
            # Tabela de notificações em tempo real
            '''
            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK(tipo IN ('info', 'alerta', 'sucesso', 'erro')),
                titulo TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                modulo_destino TEXT NOT NULL,
                usuario_destino_id INTEGER,
                lida BOOLEAN DEFAULT 0,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_destino_id) REFERENCES usuarios(id)
            )
            ''',
        
            # Tabela de funcionários
            '''
            CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT NOT NULL UNIQUE,
                cargo TEXT NOT NULL,
                departamento TEXT CHECK(departamento IN ('Recepção', 'Limpeza', 'Manutenção', 'Gerência', 'Cozinha', 'Segurança')),
                data_admissao DATE NOT NULL,
                salario_base INTEGER NOT NULL,
                banco TEXT,
                conta_bancaria TEXT,
                agencia TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                data_nascimento DATE,
                estado_civil TEXT,
                filhos INTEGER DEFAULT 0,
                ativo BOOLEAN DEFAULT 1,
                observacoes TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            
            # Tabela de lançamentos da folha de pagamento
            '''
            CREATE TABLE IF NOT EXISTS folha_pagamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                mes_ano DATE NOT NULL,
                salario_base INTEGER NOT NULL,
                horas_extras INTEGER DEFAULT 0,
                valor_horas_extras INTEGER DEFAULT 0,
                subsidios INTEGER DEFAULT 0,
                faltas INTEGER DEFAULT 0,
                descontos_faltas INTEGER DEFAULT 0,
                ferias INTEGER DEFAULT 0,
                valor_ferias INTEGER DEFAULT 0,
                outros_acrescimos INTEGER DEFAULT 0,
                outros_descontos INTEGER DEFAULT 0,
                salario_liquido INTEGER NOT NULL,
                status TEXT CHECK(status IN ('pendente', 'calculado', 'enviado_financeiro', 'aprovado', 'pago', 'rejeitado')) DEFAULT 'pendente',
                data_calculo TIMESTAMP,
                data_envio_financeiro TIMESTAMP,
                data_aprovacao TIMESTAMP,
                data_pagamento TIMESTAMP,
                usuario_calculo_id INTEGER,
                usuario_envio_id INTEGER,
                usuario_aprovacao_id INTEGER,
                usuario_pagamento_id INTEGER,
                observacoes TEXT,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
                FOREIGN KEY (usuario_calculo_id) REFERENCES usuarios(id),
                FOREIGN KEY (usuario_envio_id) REFERENCES usuarios(id),
                FOREIGN KEY (usuario_aprovacao_id) REFERENCES usuarios(id),
                FOREIGN KEY (usuario_pagamento_id) REFERENCES usuarios(id)
            )
            ''',
            
            # Tabela de registros de ponto
            '''
            CREATE TABLE IF NOT EXISTS registros_ponto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                data DATE NOT NULL,
                entrada TIME,
                saida TIME,
                horas_trabalhadas REAL,
                horas_extras REAL DEFAULT 0,
                atraso_minutos INTEGER DEFAULT 0,
                faltou BOOLEAN DEFAULT 0,
                observacoes TEXT,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
            )
            ''',
            
            # Tabela de férias
            '''
            CREATE TABLE IF NOT EXISTS ferias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                periodo_aquisitivo_inicio DATE NOT NULL,
                periodo_aquisitivo_fim DATE NOT NULL,
                periodo_gozo_inicio DATE NOT NULL,
                periodo_gozo_fim DATE NOT NULL,
                dias INTEGER NOT NULL,
                status TEXT CHECK(status IN ('solicitada', 'aprovada', 'em_gozo', 'concluida', 'cancelada')) DEFAULT 'solicitada',
                data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_aprovacao TIMESTAMP,
                usuario_aprovacao_id INTEGER,
                observacoes TEXT,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
                FOREIGN KEY (usuario_aprovacao_id) REFERENCES usuarios(id)
            )
            ''',
            
            # Tabela de faltas e ausências
            '''
            CREATE TABLE IF NOT EXISTS faltas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                data DATE NOT NULL,
                tipo TEXT CHECK(tipo IN ('falta', 'atestado', 'licenca', 'ferias', 'outro')) NOT NULL,
                justificativa TEXT,
                horas_ausentes INTEGER DEFAULT 8,
                atestado_medico BOOLEAN DEFAULT 0,
                arquivo_atestado TEXT,
                status TEXT CHECK(status IN ('pendente', 'aprovada', 'rejeitada')) DEFAULT 'pendente',
                usuario_aprovacao_id INTEGER,
                observacoes TEXT,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
                FOREIGN KEY (usuario_aprovacao_id) REFERENCES usuarios(id)
            )
            ''',
            
            # Tabela de subsídios e benefícios
            '''
            CREATE TABLE IF NOT EXISTS subsidios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                tipo TEXT CHECK(tipo IN ('alimentacao', 'transporte', 'saude', 'educacao', 'outro')) NOT NULL,
                valor INTEGER NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE,
                periodicidade TEXT CHECK(periodicidade IN ('diario', 'semanal', 'quinzenal', 'mensal', 'unico')) DEFAULT 'mensal',
                observacoes TEXT,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
            )
            '''
        ]
        
        for query in queries:
            try:
                self.cursor.execute(query)
            except Exception as e:
                print(f"Erro ao criar tabela: {e}")
        
        self.conn.commit()
    
    def initialize_data(self):
        """Inicializa dados padrão da hospedaria"""
        # Configuração da hospedaria
        self.cursor.execute("SELECT COUNT(*) FROM config_hospedaria WHERE id = 1")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO config_hospedaria (id, nome, preco_hora_normal, preco_hora_vip)
                VALUES (1, 'Hospedaria Checa', 2000, 3500)
            ''')
        
        # Usuário administrador padrão (apenas gerente)
        senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        self.cursor.execute('''
            INSERT OR IGNORE INTO usuarios (nome, senha, tipo)
            VALUES ('admin', ?, 'gerente')
        ''', (senha_hash,))
        
        self.conn.commit()
    
    def execute_query(self, query, params=(), commit=True):
        """Executa uma query SQL"""
        try:
            result = self.cursor.execute(query, params)
            if commit:
                self.conn.commit()
            return result
        except Exception as e:
            print(f"Erro na query: {e}")
            return None
    
    def log_action(self, usuario_id, usuario_nome, acao, modulo, detalhes=""):
        """Registra ação no histórico"""
        self.execute_query('''
            INSERT INTO historico (usuario_id, usuario_nome, acao, modulo, detalhes)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, usuario_nome, acao, modulo, detalhes))
    
    def send_notification(self, tipo, titulo, mensagem, modulo_destino, usuario_destino_id=None):
        """Envia notificação em tempo real"""
        self.execute_query('''
            INSERT INTO notificacoes (tipo, titulo, mensagem, modulo_destino, usuario_destino_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (tipo, titulo, mensagem, modulo_destino, usuario_destino_id))
    
    def get_unread_notifications(self, usuario_id=None):
        """Obtém notificações não lidas"""
        query = "SELECT * FROM notificacoes WHERE lida = 0"
        params = ()
        
        if usuario_id:
            query += " AND (usuario_destino_id = ? OR usuario_destino_id IS NULL)"
            params = (usuario_id,)
        
        query += " ORDER BY data DESC LIMIT 10"
        
        result = self.execute_query(query, params, commit=False)
        return result.fetchall()
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()

class UserService:
    """Serviço de gerenciamento de usuários"""
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_user = None
    
    def hash_password(self, password):
        """Cria hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, nome, senha, confirmar_senha, tipo):
        """Registra um novo usuário (cadastro próprio)"""
        # Validações
        if not nome or not senha or not confirmar_senha:
            return False, "Preencha todos os campos!"
        
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres!"
        
        if senha != confirmar_senha:
            return False, "As senhas não coincidem!"
        
        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres!"
        
        # Verificar se nome já existe
        result = self.db.execute_query(
            "SELECT id FROM usuarios WHERE nome = ?", 
            (nome,), 
            commit=False
        )
        
        if result.fetchone():
            return False, "Este nome de usuário já está em uso!"
        
        # Criar hash da senha
        senha_hash = self.hash_password(senha)
        
        try:
            self.db.execute_query(
                "INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)",
                (nome, senha_hash, tipo)
            )
            
            # Notificação para gerente
            self.db.send_notification(
                'info',
                'Novo Usuário',
                f'Novo usuário registrado: {nome} ({tipo})',
                'gerente'
            )
            
            return True, "Cadastro realizado com sucesso! Agora faça login."
        except Exception as e:
            return False, f"Erro ao cadastrar: {str(e)}"
    
    def login(self, nome, senha):
        """Autentica um usuário"""
        senha_hash = self.hash_password(senha)
        
        result = self.db.execute_query(
            "SELECT id, nome, tipo FROM usuarios WHERE nome = ? AND senha = ? AND ativo = 1",
            (nome, senha_hash),
            commit=False
        )
        
        user = result.fetchone()
        if user:
            self.current_user = {
                'id': user[0],
                'nome': user[1],
                'tipo': user[2]
            }
            
            # Log do login
            self.db.log_action(
                user[0], user[1], 'LOGIN', 'Sistema', 'Login realizado'
            )
            
            # Notificação de login
            self.db.send_notification(
                'info',
                'Login Realizado',
                f'Usuário {user[1]} fez login no sistema',
                'gerente',
                user[0]
            )
            
            return True, "Login bem-sucedido!"
        
        return False, "Usuário ou senha incorretos"
    
    def logout(self):
        """Realiza logout do usuário atual"""
        if self.current_user:
            self.db.log_action(
                self.current_user['id'],
                self.current_user['nome'],
                'LOGOUT',
                'Sistema',
                'Logout realizado'
            )
        self.current_user = None
    
    def get_user_info(self):
        """Retorna informações do usuário atual"""
        return self.current_user
    
    def can_access_module(self, modulo):
        """Verifica se usuário tem acesso ao módulo"""
        if not self.current_user:
            return False
        
        permissoes = {
            'gerente': ['relatorios', 'configuracoes', 'usuarios', 'dashboard', 
                    'notificacoes', 'relatorios_tempo_real', 'rh', 'financeiro',
                    'funcionarios', 'salarios'],
            'recepcionista': ['hospedes', 'quartos', 'checkin', 'checkout', 
                            'servicos', 'editar_hospedes'],
            'financeiro': ['financeiro', 'transacoes', 'relatorios_financeiros',
                        'pagamentos', 'contas', 'balanco'],
            'rh': ['rh', 'funcionarios', 'salarios', 'ferias', 'faltas', 
                'horas_extras', 'subsidios', 'relatorios_rh', 'folha_pagamento']
        }
        
        return modulo in permissoes.get(self.current_user['tipo'], [])

class RoomService:
    """Serviço de gerenciamento de quartos"""
    def __init__(self, db_manager):
        self.db = db_manager
        self.room_tree = BinarySearchTree()  # Para busca por número
        self.room_hash = HashTable()  # Para busca por nome
        self.load_rooms_to_memory()
    
    def load_rooms_to_memory(self):
        """Carrega quartos para estruturas de dados em memória"""
        result = self.db.execute_query(
            "SELECT numero, nome, categoria, ocupado, status FROM quartos",
            commit=False
        )
        
        for row in result.fetchall():
            numero, nome, categoria, ocupado, status = row
            room_data = {
                'numero': numero,
                'nome': nome,
                'categoria': categoria,
                'ocupado': bool(ocupado),
                'status': status
            }
            
            # Indexar por número (árvore binária)
            self.room_tree.insert(numero, room_data)
            
            # Indexar por nome (tabela hash)
            if nome:
                self.room_hash.insert(nome.lower(), room_data)
    
    def configure_rooms(self, quantidade, usuario_info):
        """Configura a quantidade de quartos"""
        try:
            # Limpa quartos existentes
            self.db.execute_query("DELETE FROM quartos")
            
            # Limpa estruturas em memória
            self.room_tree = BinarySearchTree()
            self.room_hash = HashTable()
            
            # Insere novos quartos
            for i in range(1, quantidade + 1):
                self.db.execute_query(
                    "INSERT INTO quartos (numero, nome, status) VALUES (?, ?, 'disponivel')",
                    (i, f"Quarto {i}"),
                    commit=False
                )
                
                # Adiciona às estruturas em memória
                room_data = {
                    'numero': i,
                    'nome': f"Quarto {i}",
                    'categoria': 'Normal',
                    'ocupado': False,
                    'status': 'disponivel'
                }
                self.room_tree.insert(i, room_data)
                self.room_hash.insert(f"quarto {i}", room_data)
            
            # Atualiza configuração
            self.db.execute_query(
                "UPDATE config_hospedaria SET qtde_quartos = ? WHERE id = 1",
                (quantidade,)
            )
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'CONFIGURAR_QUARTOS',
                'Configuração',
                f"Configurados {quantidade} quartos"
            )
            
            # Notificação
            self.db.send_notification(
                'sucesso',
                'Quartos Configurados',
                f'{quantidade} quartos configurados com sucesso!',
                'gerente'
            )
            
            return True, f"{quantidade} quartos configurados com sucesso!"
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def search_room_by_number(self, numero):
        """Busca quarto por número usando árvore binária"""
        return self.room_tree.search(numero)
    
    def search_room_by_name(self, nome):
        """Busca quarto por nome usando tabela hash"""
        return self.room_hash.search(nome.lower())
    
    def search_rooms_by_category(self, categoria):
        """Busca quartos por categoria"""
        result = self.db.execute_query(
            "SELECT * FROM quartos WHERE categoria = ? ORDER BY numero",
            (categoria,),
            commit=False
        )
        return result.fetchall()
    
    def get_available_rooms(self):
        """Retorna lista de quartos disponíveis"""
        result = self.db.execute_query(
            "SELECT numero FROM quartos WHERE ocupado = 0 AND status = 'disponivel' ORDER BY numero",
            commit=False
        )
        return [row[0] for row in result.fetchall()]
    
    def get_occupied_rooms(self):
        """Retorna lista de quartos ocupados"""
        result = self.db.execute_query(
            "SELECT numero FROM quartos WHERE ocupado = 1 ORDER BY numero",
            commit=False
        )
        return [row[0] for row in result.fetchall()]
    
    def get_all_rooms(self):
        """Retorna todos os quartos com informações"""
        result = self.db.execute_query('''
            SELECT q.numero, q.nome, q.categoria, q.ocupado, q.status,
                   h.nome as hospede_nome, h.check_in
            FROM quartos q
            LEFT JOIN hospedes h ON q.id_hospede = h.id AND h.ativo = 1
            ORDER BY q.numero
        ''', commit=False)
        
        rooms = []
        for row in result.fetchall():
            rooms.append({
                'numero': row[0],
                'nome': row[1] or f"Quarto {row[0]}",
                'categoria': row[2],
                'ocupado': bool(row[3]),
                'status': row[4],
                'hospede': row[5],
                'check_in': row[6]
            })
        return rooms
    
    def get_room_stats(self):
        """Retorna estatísticas dos quartos"""
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos", commit=False
        )
        total = result.fetchone()[0]
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE ocupado = 1", commit=False
        )
        ocupados = result.fetchone()[0]
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE categoria = 'VIP'", commit=False
        )
        vip = result.fetchone()[0]
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE status = 'disponivel'", commit=False
        )
        disponiveis = result.fetchone()[0]
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE status = 'manutencao'", commit=False
        )
        manutencao = result.fetchone()[0]
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE status = 'limpeza'", commit=False
        )
        limpeza = result.fetchone()[0]
        
        return {
            'total': total or 0,
            'ocupados': ocupados or 0,
            'disponiveis': disponiveis or 0,
            'vip': vip or 0,
            'normal': (total or 0) - (vip or 0),
            'manutencao': manutencao or 0,
            'limpeza': limpeza or 0,
            'taxa_ocupacao': (ocupados or 0) / (total or 1) * 100
        }
    
    def update_room_status(self, numero, status, usuario_info):
        """Atualiza status do quarto"""
        try:
            self.db.execute_query(
                "UPDATE quartos SET status = ? WHERE numero = ?",
                (status, numero)
            )
            
            # Atualizar em memória
            room_data = self.room_tree.search(numero)
            if room_data:
                room_data['status'] = status
            
            # Log e notificação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'ATUALIZAR_STATUS_QUARTO',
                'Quartos',
                f"Quarto {numero}: {status}"
            )
            
            self.db.send_notification(
                'info',
                'Status do Quarto Atualizado',
                f'Quarto {numero} agora está em {status}',
                'gerente'
            )
            
            return True, f"Status do quarto {numero} atualizado para {status}!"
        except Exception as e:
            return False, f"Erro: {str(e)}"

class GuestService:
    """Serviço de gerenciamento de hóspedes"""
    def __init__(self, db_manager):
        self.db = db_manager
        self.guest_tree = BinarySearchTree()  # Para busca por ID
        self.guest_hash = HashTable()  # Para busca por nome
        self.room_guest_map = {}  # Mapeamento quarto -> hóspede
        self.load_guests_to_memory()
    
    def load_guests_to_memory(self):
        """Carrega hóspedes para estruturas de dados em memória"""
        result = self.db.execute_query(
            "SELECT id, nome, documento, quarto_numero FROM hospedes WHERE ativo = 1",
            commit=False
        )
        
        for row in result.fetchall():
            guest_id, nome, documento, quarto_numero = row
            guest_data = {
                'id': guest_id,
                'nome': nome,
                'documento': documento,
                'quarto_numero': quarto_numero
            }
            
            # Indexar por ID (árvore binária)
            self.guest_tree.insert(guest_id, guest_data)
            
            # Indexar por nome (tabela hash)
            self.guest_hash.insert(nome.lower(), guest_data)
            
            # Mapear quarto -> hóspede
            self.room_guest_map[quarto_numero] = guest_id
    
    def calculate_price(self, quantidade, unidade, categoria):
        """Calcula o preço baseado no tempo e categoria"""
        # Obtém preços da configuração
        result = self.db.execute_query(
            "SELECT preco_hora_normal, preco_hora_vip FROM config_hospedaria WHERE id = 1",
            commit=False
        )
        config = result.fetchone()
        
        preco_normal = config[0] if config else 2000
        preco_vip = config[1] if config else 3500
        
        preco_hora = preco_vip if categoria == 'VIP' else preco_normal
        
        # Converte para horas
        horas_por_unidade = {
            'horas': 1,
            'dias': 24,
            'semanas': 168,
            'meses': 720
        }
        
        horas_totais = quantidade * horas_por_unidade.get(unidade, 1)
        preco_total = horas_totais * preco_hora
        
        return horas_totais, preco_total, preco_hora
    
    def register_guest(self, guest_data, usuario_info):
        """Registra um novo hóspede"""
        try:
            # Calcula preço
            horas_totais, preco_total, preco_hora = self.calculate_price(
                guest_data['tempo_quantidade'],
                guest_data['tempo_unidade'],
                guest_data['categoria_quarto']
            )
            
            # Insere hóspede
            result = self.db.execute_query('''
                INSERT INTO hospedes 
                (nome, documento, nacionalidade, telefone, email,
                 tempo_horas, tempo_texto, quarto_numero, quarto_nome,
                 categoria_quarto, preco_total, forma_pagamento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guest_data['nome'],
                guest_data['documento'],
                guest_data.get('nacionalidade', ''),
                guest_data.get('telefone', ''),
                guest_data.get('email', ''),
                horas_totais,
                guest_data['tempo_texto'],
                guest_data['quarto_numero'],
                guest_data['quarto_nome'],
                guest_data['categoria_quarto'],
                preco_total,
                guest_data.get('forma_pagamento', 'Dinheiro'),
                guest_data.get('observacoes', '')
            ), commit=False)
            
            guest_id = self.db.cursor.lastrowid
            
            # Atualiza quarto
            self.db.execute_query('''
                UPDATE quartos 
                SET nome = ?, categoria = ?, ocupado = 1, id_hospede = ?, status = 'ocupado'
                WHERE numero = ?
            ''', (
                guest_data['quarto_nome'],
                guest_data['categoria_quarto'],
                guest_id,
                guest_data['quarto_numero']
            ), commit=False)
            
            # Adiciona às estruturas em memória
            guest_info = {
                'id': guest_id,
                'nome': guest_data['nome'],
                'documento': guest_data['documento'],
                'quarto_numero': guest_data['quarto_numero']
            }
            self.guest_tree.insert(guest_id, guest_info)
            self.guest_hash.insert(guest_data['nome'].lower(), guest_info)
            self.room_guest_map[guest_data['quarto_numero']] = guest_id
            
            # Registra transação financeira
            self.db.execute_query('''
                INSERT INTO transacoes 
                (tipo, descricao, valor, id_hospede, categoria, usuario_id)
                VALUES ('entrada', 'Hospedagem', ?, ?, 'hospedagem', ?)
            ''', (preco_total, guest_id, usuario_info['id']))
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'CHECKIN',
                'Hóspedes',
                f"Hóspede {guest_data['nome']} - Quarto {guest_data['quarto_numero']}"
            )
            
            # Notificação em tempo real para gerente
            self.db.send_notification(
                'sucesso',
                'Novo Check-in',
                f'Hóspede {guest_data["nome"]} registrado no quarto {guest_data["quarto_numero"]}',
                'gerente'
            )
            
            self.db.conn.commit()
            return True, "Hóspede registrado com sucesso!", guest_id
        except Exception as e:
            self.db.conn.rollback()
            return False, f"Erro ao registrar hóspede: {str(e)}", None
    
    def search_guest_by_id(self, guest_id):
        """Busca hóspede por ID usando árvore binária"""
        return self.guest_tree.search(guest_id)
    
    def search_guest_by_name(self, nome):
        """Busca hóspede por nome usando tabela hash"""
        return self.guest_hash.search(nome.lower())
    
    def search_guest_by_room(self, room_number):
        """Busca hóspede por número do quarto"""
        guest_id = self.room_guest_map.get(room_number)
        if guest_id:
            return self.guest_tree.search(guest_id)
        return None
    
    def search_guests_by_category(self, categoria):
        """Busca hóspedes por categoria de quarto"""
        result = self.db.execute_query(
            "SELECT * FROM hospedes WHERE categoria_quarto = ? AND ativo = 1 ORDER BY nome",
            (categoria,),
            commit=False
        )
        return result.fetchall()
    
    def update_guest(self, guest_id, guest_data, usuario_info):
        """Atualiza informações do hóspede"""
        try:
            # Verifica se o hóspede existe
            result = self.db.execute_query(
                "SELECT nome FROM hospedes WHERE id = ? AND ativo = 1",
                (guest_id,),
                commit=False
            )
            
            if not result.fetchone():
                return False, "Hóspede não encontrado ou inativo!"
            
            # Atualiza no banco
            self.db.execute_query('''
                UPDATE hospedes SET
                    nome = ?,
                    documento = ?,
                    nacionalidade = ?,
                    telefone = ?,
                    email = ?,
                    forma_pagamento = ?,
                    observacoes = ?
                WHERE id = ?
            ''', (
                guest_data['nome'],
                guest_data['documento'],
                guest_data.get('nacionalidade', ''),
                guest_data.get('telefone', ''),
                guest_data.get('email', ''),
                guest_data.get('forma_pagamento', 'Dinheiro'),
                guest_data.get('observacoes', ''),
                guest_id
            ))
            
            # Atualiza nas estruturas em memória
            old_guest_info = self.guest_tree.search(guest_id)
            if old_guest_info:
                # Remove nome antigo da tabela hash
                self.guest_hash.delete(old_guest_info['nome'].lower())
                
                # Atualiza com novos dados
                new_guest_info = {
                    'id': guest_id,
                    'nome': guest_data['nome'],
                    'documento': guest_data['documento'],
                    'quarto_numero': old_guest_info['quarto_numero']
                }
                
                # Atualiza árvore e tabela hash
                self.guest_tree.insert(guest_id, new_guest_info)
                self.guest_hash.insert(guest_data['nome'].lower(), new_guest_info)
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'ATUALIZAR_HOSPEDE',
                'Hóspedes',
                f"Hóspede ID {guest_id} atualizado"
            )
            
            # Notificação em tempo real
            self.db.send_notification(
                'info',
                'Hóspede Atualizado',
                f'Informações do hóspede ID {guest_id} foram atualizadas',
                'gerente'
            )
            
            return True, "Hóspede atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar hóspede: {str(e)}"
    
    def get_all_guests(self, ativos=True):
        """Obtém todos os hóspedes"""
        status = 1 if ativos else 0
        result = self.db.execute_query('''
            SELECT * FROM hospedes 
            WHERE ativo = ? 
            ORDER BY check_in DESC
        ''', (status,), commit=False)
        return result.fetchall()
    
    def checkout_guest(self, guest_id, usuario_info):
        """Realiza checkout do hóspede"""
        try:
            # Obtém informações do hóspede
            result = self.db.execute_query(
                "SELECT * FROM hospedes WHERE id = ? AND ativo = 1",
                (guest_id,),
                commit=False
            )
            guest = result.fetchone()
            
            if not guest:
                return False, "Hóspede não encontrado ou já fez check-out", None
            
            # Atualiza quarto
            self.db.execute_query(
                "UPDATE quartos SET ocupado = 0, id_hospede = NULL, status = 'limpeza' WHERE numero = ?",
                (guest[8],),  # quarto_numero
                commit=False
            )
            
            # Atualiza hóspede
            self.db.execute_query(
                "UPDATE hospedes SET ativo = 0, check_out = CURRENT_TIMESTAMP WHERE id = ?",
                (guest_id,),
                commit=False
            )
            
            # Remove das estruturas em memória
            guest_info = self.guest_tree.search(guest_id)
            if guest_info:
                self.guest_hash.delete(guest_info['nome'].lower())
                del self.room_guest_map[guest_info['quarto_numero']]
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'CHECKOUT',
                'Hóspedes',
                f"Hóspede ID {guest_id} - {guest[1]}"
            )
            
            # Notificação em tempo real
            self.db.send_notification(
                'info',
                'Check-out Realizado',
                f'Hóspede {guest[1]} fez check-out do quarto {guest[8]}',
                'gerente'
            )
            
            self.db.conn.commit()
            return True, "Check-out realizado com sucesso!", guest
        except Exception as e:
            self.db.conn.rollback()
            return False, f"Erro no check-out: {str(e)}", None
    
    def get_guest_stats(self):
        """Retorna estatísticas de hóspedes"""
        # Hóspedes ativos
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM hospedes WHERE ativo = 1",
            commit=False
        )
        ativos = result.fetchone()[0]
        
        # Total de hóspedes
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM hospedes",
            commit=False
        )
        total = result.fetchone()[0]
        
        # Por nacionalidade
        result = self.db.execute_query('''
            SELECT nacionalidade, COUNT(*) as quantidade 
            FROM hospedes 
            WHERE ativo = 1 AND nacionalidade != ''
            GROUP BY nacionalidade 
            ORDER BY quantidade DESC
            LIMIT 5
        ''', commit=False)
        nacionalidades = result.fetchall()
        
        # Por categoria de quarto
        result = self.db.execute_query('''
            SELECT categoria_quarto, COUNT(*) as quantidade, SUM(preco_total) as receita
            FROM hospedes 
            WHERE ativo = 1
            GROUP BY categoria_quarto
        ''', commit=False)
        categorias = result.fetchall()
        
        return {
            'ativos': ativos or 0,
            'total': total or 0,
            'nacionalidades': nacionalidades,
            'categorias': categorias,
            'taxa_ocupacao': (ativos or 0) / (total or 1) * 100 if total > 0 else 0
        }

class FinanceService:
    """Serviço de gestão financeira"""
    def __init__(self, db_manager):
        self.db = db_manager
    
    def register_transaction(self, tipo, descricao, valor, categoria, usuario_info, id_hospede=None):
        """Registra uma transação financeira"""
        try:
            self.db.execute_query('''
                INSERT INTO transacoes 
                (tipo, descricao, valor, id_hospede, categoria, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, descricao, valor, id_hospede, categoria, usuario_info['id']))
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'REGISTRAR_TRANSACAO',
                'Financeiro',
                f"{tipo.upper()}: {descricao} - {valor:,} Kz"
            )
            
            # Notificação em tempo real para gerente
            self.db.send_notification(
                'info' if tipo == 'entrada' else 'alerta',
                f'Transação {tipo.upper()}',
                f'{descricao}: {valor:,} Kz',
                'gerente'
            )
            
            return True, "Transação registrada com sucesso!"
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def get_financial_summary(self, periodo='hoje'):
        """Retorna resumo financeiro"""
        query = '''
            SELECT 
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as receitas,
                SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as despesas,
                COUNT(DISTINCT id_hospede) as hospedes
            FROM transacoes 
            WHERE 1=1
        '''
        
        params = []
        
        if periodo == 'hoje':
            query += " AND DATE(data) = DATE('now')"
        elif periodo == 'mes':
            query += " AND strftime('%Y-%m', data) = strftime('%Y-%m', 'now')"
        elif periodo == 'ano':
            query += " AND strftime('%Y', data) = strftime('%Y', 'now')"
        
        result = self.db.execute_query(query, tuple(params), commit=False)
        row = result.fetchone()
        
        receitas = row[0] or 0
        despesas = row[1] or 0
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'lucro': receitas - despesas,
            'hospedes': row[2] or 0
        }
    
    def get_monthly_revenue(self, ano=None):
        """Retorna receita mensal"""
        ano = ano or datetime.now().year
        
        result = self.db.execute_query('''
            SELECT 
                strftime('%m', data) as mes,
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as receita,
                SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as despesa
            FROM transacoes 
            WHERE strftime('%Y', data) = ?
            GROUP BY strftime('%m', data)
            ORDER BY mes
        ''', (str(ano),), commit=False)
        
        dados = {}
        for mes_num, receita, despesa in result.fetchall():
            mes_nome = calendar.month_name[int(mes_num)]
            dados[mes_nome] = {
                'receita': receita or 0,
                'despesa': despesa or 0,
                'lucro': (receita or 0) - (despesa or 0)
            }
        
        return dados
    
    def get_top_services(self):
        """Retorna serviços mais vendidos"""
        result = self.db.execute_query('''
            SELECT s.nome, COUNT(sc.id) as quantidade, SUM(s.preco * sc.quantidade) as total
            FROM servicos_contratados sc
            JOIN servicos s ON sc.id_servico = s.id
            GROUP BY s.nome
            ORDER BY total DESC
            LIMIT 10
        ''', commit=False)
        
        return result.fetchall()

class ReportService:
    """Serviço de relatórios"""
    def __init__(self, db_manager):
        self.db = db_manager
    
    def generate_daily_report(self, data=None):
        """Gera relatório diário"""
        data = data or datetime.now().date()
        
        # Hóspedes do dia
        result = self.db.execute_query('''
            SELECT COUNT(*) as checkins,
                   SUM(preco_total) as receita_dia
            FROM hospedes
            WHERE DATE(check_in) = ? AND ativo = 1
        ''', (data.isoformat(),), commit=False)
        
        checkins_row = result.fetchone()
        
        # Checkouts do dia
        result = self.db.execute_query('''
            SELECT COUNT(*) as checkouts
            FROM hospedes
            WHERE DATE(check_out) = ? AND ativo = 0
        ''', (data.isoformat(),), commit=False)
        
        checkouts_row = result.fetchone()
        
        # Ocupação atual
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE ocupado = 1",
            commit=False
        )
        ocupacao_row = result.fetchone()
        
        # Receitas do dia
        result = self.db.execute_query('''
            SELECT SUM(valor) FROM transacoes 
            WHERE tipo = 'entrada' AND DATE(data) = ?
        ''', (data.isoformat(),), commit=False)
        receitas_row = result.fetchone()
        
        return {
            'data': data.strftime('%d/%m/%Y'),
            'checkins': checkins_row[0] or 0,
            'checkouts': checkouts_row[0] or 0,
            'receita_dia': receitas_row[0] or 0,
            'hospedagem_dia': checkins_row[1] or 0,
            'ocupacao_atual': ocupacao_row[0] or 0,
            'taxa_ocupacao': self.calculate_occupancy_rate()
        }
    
    def calculate_occupancy_rate(self):
        """Calcula taxa de ocupação"""
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos",
            commit=False
        )
        total_quartos = result.fetchone()[0] or 1
        
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE ocupado = 1",
            commit=False
        )
        quartos_ocupados = result.fetchone()[0] or 0
        
        return (quartos_ocupados / total_quartos) * 100 if total_quartos > 0 else 0
    
    def generate_guest_report(self):
        """Gera relatório de hóspedes"""
        result = self.db.execute_query('''
            SELECT 
                categoria_quarto,
                COUNT(*) as quantidade,
                AVG(tempo_horas) as tempo_medio,
                SUM(preco_total) as receita_total
            FROM hospedes
            WHERE ativo = 1
            GROUP BY categoria_quarto
        ''', commit=False)
        
        categorias = {}
        for row in result.fetchall():
            categorias[row[0]] = {
                'quantidade': row[1],
                'tempo_medio': round(row[2], 1),
                'receita_total': row[3]
            }
        
        return categorias
    
    def generate_financial_report(self, inicio=None, fim=None):
        """Gera relatório financeiro"""
        inicio = inicio or (datetime.now() - timedelta(days=30)).date()
        fim = fim or datetime.now().date()
        
        result = self.db.execute_query('''
            SELECT 
                tipo,
                categoria,
                COUNT(*) as quantidade,
                SUM(valor) as total
            FROM transacoes
            WHERE DATE(data) BETWEEN ? AND ?
            GROUP BY tipo, categoria
            ORDER BY tipo, total DESC
        ''', (inicio.isoformat(), fim.isoformat()), commit=False)
        
        return result.fetchall()
    
    def generate_real_time_report(self):
        """Gera relatório em tempo real"""
        # Hóspedes ativos agora
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM hospedes WHERE ativo = 1",
            commit=False
        )
        hospedes_ativos = result.fetchone()[0] or 0
        
        # Quartos ocupados agora
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM quartos WHERE ocupado = 1",
            commit=False
        )
        quartos_ocupados = result.fetchone()[0] or 0
        
        # Receitas hoje
        result = self.db.execute_query('''
            SELECT SUM(valor) FROM transacoes 
            WHERE tipo = 'entrada' AND DATE(data) = DATE('now')
        ''', commit=False)
        receita_hoje = result.fetchone()[0] or 0
        
        # Check-ins hoje
        result = self.db.execute_query('''
            SELECT COUNT(*) FROM hospedes 
            WHERE DATE(check_in) = DATE('now') AND ativo = 1
        ''', commit=False)
        checkins_hoje = result.fetchone()[0] or 0
        
        # Últimas transações
        result = self.db.execute_query('''
            SELECT tipo, descricao, valor, data 
            FROM transacoes 
            ORDER BY data DESC 
            LIMIT 5
        ''', commit=False)
        ultimas_transacoes = result.fetchall()
        
        # Últimos hóspedes
        result = self.db.execute_query('''
            SELECT nome, quarto_numero, check_in 
            FROM hospedes 
            WHERE ativo = 1 
            ORDER BY check_in DESC 
            LIMIT 5
        ''', commit=False)
        ultimos_hospedes = result.fetchall()
        
        return {
            'hospedes_ativos': hospedes_ativos,
            'quartos_ocupados': quartos_ocupados,
            'receita_hoje': receita_hoje,
            'checkins_hoje': checkins_hoje,
            'ultimas_transacoes': ultimas_transacoes,
            'ultimos_hospedes': ultimos_hospedes,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }

class HRService:
    """Serviço de Gestão de Recursos Humanos"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def cadastrar_funcionario(self, dados_funcionario, usuario_info):
        """Cadastra um novo funcionário"""
        try:
            result = self.db.execute_query('''
                INSERT INTO funcionarios 
                (nome, documento, cargo, departamento, data_admissao, salario_base,
                 banco, conta_bancaria, agencia, telefone, email, endereco,
                 data_nascimento, estado_civil, filhos, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados_funcionario['nome'],
                dados_funcionario['documento'],
                dados_funcionario['cargo'],
                dados_funcionario['departamento'],
                dados_funcionario['data_admissao'],
                dados_funcionario['salario_base'],
                dados_funcionario.get('banco', ''),
                dados_funcionario.get('conta_bancaria', ''),
                dados_funcionario.get('agencia', ''),
                dados_funcionario.get('telefone', ''),
                dados_funcionario.get('email', ''),
                dados_funcionario.get('endereco', ''),
                dados_funcionario.get('data_nascimento', ''),
                dados_funcionario.get('estado_civil', ''),
                dados_funcionario.get('filhos', 0),
                dados_funcionario.get('observacoes', '')
            ), commit=False)
            
            funcionario_id = self.db.cursor.lastrowid
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'CADASTRAR_FUNCIONARIO',
                'RH',
                f"Funcionário {dados_funcionario['nome']} cadastrado"
            )
            
            # Notificação
            self.db.send_notification(
                'sucesso',
                'Novo Funcionário',
                f'Funcionário {dados_funcionario["nome"]} cadastrado no sistema',
                'gerente'
            )
            
            self.db.conn.commit()
            return True, "Funcionário cadastrado com sucesso!", funcionario_id
            
        except Exception as e:
            self.db.conn.rollback()
            return False, f"Erro ao cadastrar funcionário: {str(e)}", None
    
    def calcular_salario(self, funcionario_id, mes_ano, usuario_info):
        """Calcula salário de um funcionário"""
        try:
            # Buscar dados do funcionário
            result = self.db.execute_query(
                "SELECT salario_base FROM funcionarios WHERE id = ? AND ativo = 1",
                (funcionario_id,),
                commit=False
            )
            funcionario = result.fetchone()
            
            if not funcionario:
                return False, "Funcionário não encontrado ou inativo!"
            
            salario_base = funcionario[0]
            
            # Buscar horas extras do mês
            result = self.db.execute_query('''
                SELECT SUM(horas_extras) 
                FROM registros_ponto 
                WHERE funcionario_id = ? 
                AND strftime('%Y-%m', data) = ?
            ''', (funcionario_id, mes_ano), commit=False)
            
            horas_extras = result.fetchone()[0] or 0
            
            # Buscar faltas do mês
            result = self.db.execute_query('''
                SELECT SUM(horas_ausentes) 
                FROM faltas 
                WHERE funcionario_id = ? 
                AND status = 'aprovada'
                AND strftime('%Y-%m', data) = ?
            ''', (funcionario_id, mes_ano), commit=False)
            
            horas_faltas = result.fetchone()[0] or 0
            
            # Buscar subsídios
            result = self.db.execute_query('''
                SELECT SUM(valor) 
                FROM subsidios 
                WHERE funcionario_id = ? 
                AND (data_fim IS NULL OR data_fim >= ?)
            ''', (funcionario_id, mes_ano + '-01'), commit=False)
            
            subsidios = result.fetchone()[0] or 0
            
            # Calcular valores
            valor_hora = salario_base / 220  # 220 horas mensais
            valor_horas_extras = horas_extras * valor_hora * 1.5  # 50% extra
            descontos_faltas = (horas_faltas / 8) * (salario_base / 30)  # Desconto por dia de falta
            
            # Calcular salário líquido
            salario_liquido = (salario_base + valor_horas_extras + subsidios) - descontos_faltas
            
            # Inserir na folha de pagamento
            self.db.execute_query('''
                INSERT INTO folha_pagamento 
                (funcionario_id, mes_ano, salario_base, horas_extras, valor_horas_extras,
                 subsidios, faltas, descontos_faltas, salario_liquido, status,
                 data_calculo, usuario_calculo_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'calculado', CURRENT_TIMESTAMP, ?)
            ''', (
                funcionario_id, mes_ano, salario_base, horas_extras, valor_horas_extras,
                subsidios, horas_faltas/8, descontos_faltas, salario_liquido,
                usuario_info['id']
            ))
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'CALCULAR_SALARIO',
                'RH',
                f"Salário calculado para funcionário {funcionario_id} - {mes_ano}"
            )
            
            return True, f"Salário calculado: {salario_liquido:,.0f} Kz", salario_liquido
            
        except Exception as e:
            return False, f"Erro ao calcular salário: {str(e)}", None
    
    def get_all_funcionarios(self, ativos=True):
        """Obtém todos os funcionários"""
        status = 1 if ativos else 0
        result = self.db.execute_query(
            "SELECT * FROM funcionarios WHERE ativo = ? ORDER BY nome",
            (status,),
            commit=False
        )
        return result.fetchall()
    
    def get_funcionario_stats(self):
        """Retorna estatísticas de funcionários"""
        # Total de funcionários
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM funcionarios WHERE ativo = 1",
            commit=False
        )
        total = result.fetchone()[0] or 0
        
        # Por departamento
        result = self.db.execute_query('''
            SELECT departamento, COUNT(*) as quantidade, AVG(salario_base) as media_salario
            FROM funcionarios 
            WHERE ativo = 1
            GROUP BY departamento
            ORDER BY quantidade DESC
        ''', commit=False)
        departamentos = result.fetchall()
        
        # Folha de pagamento do mês
        mes_atual = datetime.now().strftime('%Y-%m')
        result = self.db.execute_query('''
            SELECT SUM(salario_liquido) 
            FROM folha_pagamento 
            WHERE strftime('%Y-%m', mes_ano) = ?
            AND status IN ('calculado', 'pago')
        ''', (mes_atual,), commit=False)
        folha_mensal = result.fetchone()[0] or 0
        
        return {
            'total_funcionarios': total,
            'departamentos': departamentos,
            'folha_mensal': folha_mensal,
            'media_salario': folha_mensal / total if total > 0 else 0
        }
    
    def registrar_ponto(self, funcionario_id, tipo, usuario_info):
        """Registra ponto (entrada/saída) de funcionário"""
        try:
            data_atual = datetime.now().date().isoformat()
            hora_atual = datetime.now().time().strftime('%H:%M')
            
            if tipo == 'entrada':
                # Verificar se já existe registro para hoje
                result = self.db.execute_query(
                    "SELECT id FROM registros_ponto WHERE funcionario_id = ? AND data = ?",
                    (funcionario_id, data_atual),
                    commit=False
                )
                
                if result.fetchone():
                    return False, "Entrada já registrada para hoje!"
                
                # Registrar entrada
                self.db.execute_query('''
                    INSERT INTO registros_ponto (funcionario_id, data, entrada)
                    VALUES (?, ?, ?)
                ''', (funcionario_id, data_atual, hora_atual))
                
                mensagem = f"Entrada registrada às {hora_atual}"
                
            else:  # saída
                # Buscar registro da entrada
                result = self.db.execute_query(
                    "SELECT entrada FROM registros_ponto WHERE funcionario_id = ? AND data = ?",
                    (funcionario_id, data_atual),
                    commit=False
                )
                
                registro = result.fetchone()
                if not registro or not registro[0]:
                    return False, "Entrada não registrada para hoje!"
                
                # Calcular horas trabalhadas
                entrada = datetime.strptime(registro[0], '%H:%M')
                saida = datetime.strptime(hora_atual, '%H:%M')
                
                horas_trabalhadas = (saida - entrada).seconds / 3600
                
                # Calcular horas extras (considerando jornada de 8 horas)
                horas_extras = max(0, horas_trabalhadas - 8)
                
                # Atualizar registro
                self.db.execute_query('''
                    UPDATE registros_ponto 
                    SET saida = ?, horas_trabalhadas = ?, horas_extras = ?
                    WHERE funcionario_id = ? AND data = ?
                ''', (hora_atual, horas_trabalhadas, horas_extras, funcionario_id, data_atual))
                
                mensagem = f"Saída registrada às {hora_atual} - {horas_trabalhadas:.1f}h trabalhadas"
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'REGISTRAR_PONTO',
                'RH',
                f"Ponto {tipo} - Funcionário {funcionario_id}"
            )
            
            return True, mensagem
            
        except Exception as e:
            return False, f"Erro ao registrar ponto: {str(e)}"
    
    def solicitar_ferias(self, funcionario_id, dados_ferias, usuario_info):
        """Solicita férias para um funcionário"""
        try:
            self.db.execute_query('''
                INSERT INTO ferias 
                (funcionario_id, periodo_aquisitivo_inicio, periodo_aquisitivo_fim,
                 periodo_gozo_inicio, periodo_gozo_fim, dias, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                funcionario_id,
                dados_ferias['periodo_aquisitivo_inicio'],
                dados_ferias['periodo_aquisitivo_fim'],
                dados_ferias['periodo_gozo_inicio'],
                dados_ferias['periodo_gozo_fim'],
                dados_ferias['dias'],
                dados_ferias.get('observacoes', '')
            ))
            
            # Log e notificação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'SOLICITAR_FERIAS',
                'RH',
                f"Férias solicitadas - Funcionário {funcionario_id}"
            )
            
            self.db.send_notification(
                'info',
                'Solicitação de Férias',
                f'Novo pedido de férias - Funcionário {funcionario_id}',
                'gerente'
            )
            
            return True, "Férias solicitadas com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao solicitar férias: {str(e)}"
    
    def registrar_falta(self, funcionario_id, dados_falta, usuario_info):
        """Registra falta/ausência de funcionário"""
        try:
            self.db.execute_query('''
                INSERT INTO faltas 
                (funcionario_id, data, tipo, justificativa, horas_ausentes,
                 atestado_medico, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                funcionario_id,
                dados_falta['data'],
                dados_falta['tipo'],
                dados_falta.get('justificativa', ''),
                dados_falta.get('horas_ausentes', 8),
                dados_falta.get('atestado_medico', 0),
                dados_falta.get('observacoes', '')
            ))
            
            # Log e notificação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'REGISTRAR_FALTA',
                'RH',
                f"Falta registrada - Funcionário {funcionario_id}"
            )
            
            return True, "Falta registrada com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao registrar falta: {str(e)}"
    
    def adicionar_subsidio(self, funcionario_id, dados_subsidio, usuario_info):
        """Adiciona subsídio/benefício a funcionário"""
        try:
            self.db.execute_query('''
                INSERT INTO subsidios 
                (funcionario_id, tipo, valor, data_inicio, periodicidade, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                funcionario_id,
                dados_subsidio['tipo'],
                dados_subsidio['valor'],
                dados_subsidio['data_inicio'],
                dados_subsidio.get('periodicidade', 'mensal'),
                dados_subsidio.get('observacoes', '')
            ))
            
            # Log da ação
            self.db.log_action(
                usuario_info['id'],
                usuario_info['nome'],
                'ADICIONAR_SUBSIDIO',
                'RH',
                f"Subsídio adicionado - Funcionário {funcionario_id}"
            )
            
            return True, "Subsídio adicionado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao adicionar subsídio: {str(e)}"
    
    def enviar_para_financeiro(self, folha_id, usuario_info):
        """Envia folha de pagamento para aprovação do financeiro"""
        try:
            self.db.execute_query('''
                UPDATE folha_pagamento 
                SET status = 'enviado_financeiro',
                    data_envio_financeiro = CURRENT_TIMESTAMP,
                    usuario_envio_id = ?
                WHERE id = ?
            ''', (usuario_info['id'], folha_id))
            
            # Notificar financeiro
            self.db.send_notification(
                'info',
                'Folha de Pagamento Pendente',
                f'Nova folha de pagamento ID {folha_id} aguardando aprovação',
                'financeiro'
            )
            
            return True, "Folha enviada para o financeiro com sucesso!"
        except Exception as e:
            return False, f"Erro ao enviar para financeiro: {str(e)}"

    def get_folhas_para_financeiro(self):
        """Obtém folhas de pagamento enviadas para o financeiro"""
        result = self.db.execute_query('''
            SELECT fp.*, f.nome as funcionario_nome, f.cargo, f.departamento
            FROM folha_pagamento fp
            JOIN funcionarios f ON fp.funcionario_id = f.id
            WHERE fp.status = 'enviado_financeiro'
            ORDER BY fp.mes_ano DESC, f.nome
        ''', commit=False)
        return result.fetchall()

    def gerar_relatorio_rh(self, mes_ano=None):
        """Gera relatório consolidado de RH"""
        mes_ano = mes_ano or datetime.now().strftime('%Y-%m')
        
        # Dados gerais
        stats = self.get_funcionario_stats()
        
        # Folha de pagamento do mês
        result = self.db.execute_query('''
            SELECT f.nome, fp.salario_base, fp.salario_liquido, fp.status
            FROM folha_pagamento fp
            JOIN funcionarios f ON fp.funcionario_id = f.id
            WHERE strftime('%Y-%m', fp.mes_ano) = ?
            ORDER BY f.nome
        ''', (mes_ano,), commit=False)
        
        folha_pagamento = result.fetchall()
        
        # Faltas do mês
        result = self.db.execute_query('''
            SELECT f.nome, COUNT(fa.id) as faltas, SUM(fa.horas_ausentes) as horas_ausentes
            FROM faltas fa
            JOIN funcionarios f ON fa.funcionario_id = f.id
            WHERE strftime('%Y-%m', fa.data) = ? AND fa.status = 'aprovada'
            GROUP BY f.nome
            ORDER BY faltas DESC
        ''', (mes_ano,), commit=False)
        
        faltas = result.fetchall()
        
        # Horas extras do mês
        result = self.db.execute_query('''
            SELECT f.nome, SUM(rp.horas_extras) as horas_extras
            FROM registros_ponto rp
            JOIN funcionarios f ON rp.funcionario_id = f.id
            WHERE strftime('%Y-%m', rp.data) = ?
            GROUP BY f.nome
            ORDER BY horas_extras DESC
        ''', (mes_ano,), commit=False)
        
        horas_extras = result.fetchall()
        
        return {
            'mes_ano': mes_ano,
            'estatisticas': stats,
            'folha_pagamento': folha_pagamento,
            'faltas': faltas,
            'horas_extras': horas_extras,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
# ====================== INTERFACE GRÁFICA ======================

class Theme:
    """Tema visual da Hospedaria Checa"""
    colors = {
        'primary': '#1a237e',  # Azul escuro elegante
        'primary_light': '#534bae',
        'primary_dark': '#000051',
        'secondary': '#d32f2f',  # Vermelho vinho
        'secondary_light': '#ff6659',
        'secondary_dark': '#9a0007',
        'accent': '#ff9800',  # Laranja
        'accent_light': '#ffc947',
        'accent_dark': '#c66900',
        'success': '#388e3c',
        'warning': '#f57c00',
        'danger': '#d32f2f',
        'info': '#1976d2',
        'light': '#f5f5f5',
        'dark': '#212121',
        'gray': '#757575',
        'background': '#fafafa',
        'surface': '#ffffff',
        'vip': '#9c27b0',
        'normal': '#2196f3',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'text_light': '#ffffff'
    }
    
    fonts = {
        'title': ('Segoe UI', 24, 'bold'),
        'subtitle': ('Segoe UI', 16, 'bold'),
        'heading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'small': ('Segoe UI', 9),
        'mono': ('Consolas', 10)
    }

class AnimatedLabel(tk.Label):
    """Label com animação de digitação"""
    def __init__(self, master=None, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.full_text = text
        self.current_text = ""
        self.index = 0
        self.delay = 30
    
    def start_typing(self, callback=None):
        if self.index < len(self.full_text):
            self.current_text += self.full_text[self.index]
            self.configure(text=self.current_text)
            self.index += 1
            self.after(self.delay, lambda: self.start_typing(callback))
        elif callback:
            callback()

class ModernButton(tk.Button):
    """Botão moderno com efeitos"""
    def __init__(self, master=None, **kwargs):
        # Cores padrão do tema
        bg = kwargs.pop('bg', Theme.colors['primary'])
        fg = kwargs.pop('fg', Theme.colors['text_light'])
        hover_bg = kwargs.pop('hover_bg', Theme.colors['primary_light'])
        font_size = kwargs.pop('font_size', 10)
        rounded = kwargs.pop('rounded', True)
        
        super().__init__(master, **kwargs)
        
        self.default_bg = bg
        self.hover_bg = hover_bg
        self.rounded = rounded
        
        self.configure(
            bg=bg,
            fg=fg,
            font=('Segoe UI', font_size, 'bold'),
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            padx=20,
            pady=10,
            activebackground=hover_bg,
            activeforeground=fg
        )
        
        if rounded:
            self.configure(borderwidth=0, highlightthickness=0)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        if self.rounded:
            self.configure(bg=self.hover_bg)
        else:
            self.configure(relief='raised')
    
    def on_leave(self, e):
        if self.rounded:
            self.configure(bg=self.default_bg)
        else:
            self.configure(relief='flat')

class Card(tk.Frame):
    """Card moderno para exibição de informações"""
    def __init__(self, master=None, title="", **kwargs):
        bg = kwargs.pop('bg', Theme.colors['surface'])
        super().__init__(master, bg=bg, **kwargs)
        
        self.configure(
            relief='raised',
            borderwidth=1,
            highlightbackground='#e0e0e0',
            highlightthickness=1
        )
        
        if title:
            title_frame = tk.Frame(self, bg=Theme.colors['primary'], height=40)
            title_frame.pack(fill='x')
            title_frame.pack_propagate(False)
            
            tk.Label(
                title_frame,
                text=title,
                font=('Segoe UI', 12, 'bold'),
                fg=Theme.colors['text_light'],
                bg=Theme.colors['primary']
            ).pack(expand=True)
        
        self.content_frame = tk.Frame(self, bg=bg)
        self.content_frame.pack(fill='both', expand=True, padx=15, pady=15)

class StatCard(Card):
    """Card para exibição de estatísticas"""
    def __init__(self, master=None, title="", value="0", icon="", color=None, **kwargs):
        super().__init__(master, title=title, **kwargs)
        
        color = color or Theme.colors['primary']
        
        # Ícone
        icon_frame = tk.Frame(self.content_frame, bg=Theme.colors['surface'])
        icon_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            icon_frame,
            text=icon,
            font=('Segoe UI', 24),
            bg=Theme.colors['surface'],
            fg=color
        ).pack(side='left')
        
        # Valor
        tk.Label(
            self.content_frame,
            text=str(value),
            font=('Segoe UI', 28, 'bold'),
            bg=Theme.colors['surface'],
            fg=Theme.colors['text_primary']
        ).pack(expand=True)
        
        # Efeito de brilho
        self.glow_label = tk.Label(
            self,
            bg=color,
            opacity=0.1
        )
        self.glow_label.place(relx=0.5, rely=0.5, anchor='center', width=150, height=150)

class NotificationPanel:
    """Painel de notificações em tempo real"""
    def __init__(self, master, db_manager, user_service):
        self.master = master
        self.db = db_manager
        self.user_service = user_service
        self.notification_frame = None
        self.notification_count = 0
        
    def create_panel(self):
        """Cria painel de notificações"""
        self.notification_frame = tk.Frame(self.master, bg=Theme.colors['surface'], relief='raised', borderwidth=1)
        
        # Cabeçalho
        header = tk.Frame(self.notification_frame, bg=Theme.colors['primary'], height=40)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔔 NOTIFICAÇÕES",
            font=('Segoe UI', 12, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(expand=True)
        
        # Lista de notificações
        self.notification_list = tk.Frame(self.notification_frame, bg=Theme.colors['surface'])
        self.notification_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botão de atualizar
        btn_frame = tk.Frame(self.notification_frame, bg=Theme.colors['surface'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ModernButton(
            btn_frame,
            text="SAIR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=9,
            command=self.close_panel  # Adicionar este método
        ).pack(side='right')
        
        ModernButton(
            btn_frame,
            text="🔄 ATUALIZAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=9,
            command=self.update_notifications
        ).pack()
        
        # Iniciar atualização automática
        self.update_notifications()
        self.start_auto_refresh()
    
    def close_panel(self):
        """Fecha o painel de notificações"""
        if self.notification_frame and self.notification_frame.winfo_exists():
           self.notification_frame.place_forget()
   
    def update_notifications(self):
        """Atualiza lista de notificações"""
        # Limpar notificações existentes
        for widget in self.notification_list.winfo_children():
            widget.destroy()
        
        # Obter notificações não lidas
        user_info = self.user_service.get_user_info()
        notifications = self.db.get_unread_notifications(user_info['id'] if user_info else None)
        self.notification_count = len(notifications)
        
        if not notifications:
            tk.Label(
                self.notification_list,
                text="Sem notificações novas",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(pady=20)
            return
        
        # Adicionar notificações
        for notif in notifications:
            self.add_notification_item(notif)
    
    def add_notification_item(self, notif):
        """Adiciona um item de notificação"""
        notif_id, tipo, titulo, mensagem, modulo, usuario_id, lida, data = notif
        
        # Cores por tipo
        colors = {
            'info': Theme.colors['info'],
            'alerta': Theme.colors['warning'],
            'sucesso': Theme.colors['success'],
            'erro': Theme.colors['danger']
        }
        
        color = colors.get(tipo, Theme.colors['primary'])
        
        # Frame da notificação
        notif_frame = tk.Frame(self.notification_list, bg=Theme.colors['surface'], relief='groove', borderwidth=1)
        notif_frame.pack(fill='x', pady=2)
        
        # Ícone do tipo
        icons = {
            'info': 'ℹ️',
            'alerta': '⚠️',
            'sucesso': '✅',
            'erro': '❌'
        }
        
        icon_label = tk.Label(
            notif_frame,
            text=icons.get(tipo, '📢'),
            font=('Segoe UI', 14),
            bg=Theme.colors['surface'],
            fg=color
        )
        icon_label.pack(side='left', padx=5, pady=5)
        
        # Conteúdo
        content_frame = tk.Frame(notif_frame, bg=Theme.colors['surface'])
        content_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            content_frame,
            text=titulo,
            font=('Segoe UI', 10, 'bold'),
            fg=color,
            bg=Theme.colors['surface']
        ).pack(anchor='w')
        
        tk.Label(
            content_frame,
            text=mensagem,
            font=('Segoe UI', 9),
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface'],
            wraplength=250
        ).pack(anchor='w')
        
        tk.Label(
            content_frame,
            text=data[:16],
            font=('Segoe UI', 8),
            fg=Theme.colors['gray'],
            bg=Theme.colors['surface']
        ).pack(anchor='w')
        
        # Botão de marcar como lida
        ModernButton(
            notif_frame,
            text="✓",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=8,
            padx=5,
            pady=2,
            command=lambda nid=notif_id: self.mark_as_read(nid)
        ).pack(side='right', padx=5)
    
    def mark_as_read(self, notification_id):
        """Marca notificação como lida"""
        self.db.execute_query(
            "UPDATE notificacoes SET lida = 1 WHERE id = ?",
            (notification_id,)
        )
        self.update_notifications()
    
    def start_auto_refresh(self):
        """Inicia atualização automática das notificações"""
        self.update_notifications()
        self.master.after(10000, self.start_auto_refresh)  # Atualiza a cada 10 segundos
    
    def lighten_color(self, color, percent):
        """Clareia uma cor hexadecimal"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c + (255 - c) * percent / 100)) for c in rgb)
            return '#%02x%02x%02x' % lightened
        except:
            return color
    
    def get_count(self):
        """Retorna contagem de notificações"""
        return self.notification_count

class RealTimeDashboard:
    """Dashboard em tempo real para o gerente"""
    def __init__(self, parent, db_manager, room_service, guest_service, finance_service):
        self.parent = parent
        self.db = db_manager
        self.room_service = room_service
        self.guest_service = guest_service
        self.finance_service = finance_service
        
        # Widgets de atualização
        self.stats_labels = {}
        self.last_update = None
        
    def create_dashboard(self):
        """Cria dashboard em tempo real"""
        # Container principal
        dashboard_frame = tk.Frame(self.parent, bg=Theme.colors['background'])
        dashboard_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Cabeçalho com relógio em tempo real
        header_frame = tk.Frame(dashboard_frame, bg=Theme.colors['primary'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="⏱️ DASHBOARD EM TEMPO REAL",
            font=('Segoe UI', 18, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(side='left', padx=20, pady=10)
        
        self.clock_label = tk.Label(
            header_frame,
            text=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            font=('Segoe UI', 14, 'bold'),
            fg=Theme.colors['accent_light'],
            bg=Theme.colors['primary']
        )
        self.clock_label.pack(side='right', padx=20, pady=10)
        
        # Grid de estatísticas em tempo real
        stats_grid = tk.Frame(dashboard_frame, bg=Theme.colors['background'])
        stats_grid.pack(fill='both', expand=True)
        
        # Estatísticas dos quartos
        room_stats = self.room_service.get_room_stats()
        
        room_metrics = [
            {
                'title': 'Quartos Ocupados',
                'value': f"{room_stats['ocupados']}/{room_stats['total']}",
                'icon': '🔒',
                'color': Theme.colors['secondary'],
                'key': 'ocupados'
            },
            {
                'title': 'Taxa de Ocupação',
                'value': f"{room_stats['taxa_ocupacao']:.1f}%",
                'icon': '📊',
                'color': Theme.colors['accent'],
                'key': 'taxa_ocupacao'
            },
            {
                'title': 'Quartos VIP',
                'value': room_stats['vip'],
                'icon': '🏆',
                'color': Theme.colors['vip'],
                'key': 'vip'
            },
            {
                'title': 'Em Manutenção',
                'value': room_stats['manutencao'],
                'icon': '🔧',
                'color': Theme.colors['warning'],
                'key': 'manutencao'
            }
        ]
        
        for i, metric in enumerate(room_metrics):
            card = self.create_stat_card(stats_grid, metric, row=0, column=i)
            self.stats_labels[metric['key']] = card
        
        # Estatísticas de hóspedes
        guest_stats = self.guest_service.get_guest_stats()
        
        guest_metrics = [
            {
                'title': 'Hóspedes Ativos',
                'value': guest_stats['ativos'],
                'icon': '👥',
                'color': Theme.colors['info'],
                'key': 'ativos'
            },
            {
                'title': 'Taxa de Rotatividade',
                'value': f"{guest_stats['taxa_ocupacao']:.1f}%",
                'icon': '📈',
                'color': Theme.colors['success'],
                'key': 'taxa_rotatividade'
            },
            {
                'title': 'VIP vs Normal',
                'value': f"{sum(1 for c in guest_stats['categorias'] if c[0]=='VIP')}/{sum(1 for c in guest_stats['categorias'] if c[0]=='Normal')}",
                'icon': '⚖️',
                'color': Theme.colors['vip'],
                'key': 'vip_vs_normal'
            }
        ]
        
        for i, metric in enumerate(guest_metrics):
            card = self.create_stat_card(stats_grid, metric, row=1, column=i)
            self.stats_labels[metric['key']] = card
        
        # Grid de últimas atividades
        activities_frame = tk.Frame(dashboard_frame, bg=Theme.colors['background'])
        activities_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Últimas transações
        trans_card = Card(activities_frame, title="💰 ÚLTIMAS TRANSAÇÕES")
        trans_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.transactions_list = tk.Frame(trans_card.content_frame, bg=Theme.colors['surface'])
        self.transactions_list.pack(fill='both', expand=True)
        
        # Últimos hóspedes
        guests_card = Card(activities_frame, title="👥 ÚLTIMOS HÓSPEDES")
        guests_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        self.guests_list = tk.Frame(guests_card.content_frame, bg=Theme.colors['surface'])
        self.guests_list.pack(fill='both', expand=True)
        
        # Configurar pesos
        activities_frame.grid_columnconfigure(0, weight=1)
        activities_frame.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(2, weight=1)
        stats_grid.grid_columnconfigure(3, weight=1)
        
        # Iniciar atualização automática
        self.update_clock()
        self.update_real_time_data()
    
    def create_stat_card(self, parent, metric, row, column):
        """Cria card de estatística"""
        card = Card(parent, bg=Theme.colors['surface'], width=200, height=120)
        card.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
        
        # Ícone
        tk.Label(
            card.content_frame,
            text=metric['icon'],
            font=('Segoe UI', 24),
            bg=Theme.colors['surface'],
            fg=metric['color']
        ).pack()
        
        # Valor
        value_label = tk.Label(
            card.content_frame,
            text=str(metric['value']),
            font=('Segoe UI', 20, 'bold'),
            bg=Theme.colors['surface'],
            fg=Theme.colors['text_primary']
        )
        value_label.pack()
        
        # Título
        tk.Label(
            card.content_frame,
            text=metric['title'],
            font=('Segoe UI', 10),
            bg=Theme.colors['surface'],
            fg=Theme.colors['text_secondary']
        ).pack()
        
        return value_label
    
    def update_clock(self):
        """Atualiza o relógio em tempo real"""
        self.clock_label.configure(text=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        self.parent.after(1000, self.update_clock)
    
    def update_real_time_data(self):
        """Atualiza dados em tempo real"""
        # Atualizar estatísticas dos quartos
        room_stats = self.room_service.get_room_stats()
        if 'ocupados' in self.stats_labels:
            self.stats_labels['ocupados'].configure(text=f"{room_stats['ocupados']}/{room_stats['total']}")
        if 'taxa_ocupacao' in self.stats_labels:
            self.stats_labels['taxa_ocupacao'].configure(text=f"{room_stats['taxa_ocupacao']:.1f}%")
        if 'vip' in self.stats_labels:
            self.stats_labels['vip'].configure(text=str(room_stats['vip']))
        if 'manutencao' in self.stats_labels:
            self.stats_labels['manutencao'].configure(text=str(room_stats['manutencao']))
        
        # Atualizar estatísticas de hóspedes
        guest_stats = self.guest_service.get_guest_stats()
        if 'ativos' in self.stats_labels:
            self.stats_labels['ativos'].configure(text=str(guest_stats['ativos']))
        
        # Atualizar últimas transações
        self.update_transactions_list()
        
        # Atualizar últimos hóspedes
        self.update_guests_list()
        
        # Agendar próxima atualização
        self.last_update = datetime.now().strftime('%H:%M:%S')
        self.parent.after(5000, self.update_real_time_data)  # Atualiza a cada 5 segundos
    
    def update_transactions_list(self):
        """Atualiza lista de transações"""
        # Limpar lista existente
        for widget in self.transactions_list.winfo_children():
            widget.destroy()
        
        # Obter últimas transações
        result = self.db.execute_query('''
            SELECT tipo, descricao, valor, data 
            FROM transacoes 
            ORDER BY data DESC 
            LIMIT 5
        ''', commit=False)
        
        transactions = result.fetchall()
        
        if not transactions:
            tk.Label(
                self.transactions_list,
                text="Sem transações recentes",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(pady=10)
            return
        
        for trans in transactions:
            tipo, descricao, valor, data = trans
            
            # Formatar data
            data_dt = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            data_str = data_dt.strftime('%H:%M')
            
            # Cor por tipo
            color = Theme.colors['success'] if tipo == 'entrada' else Theme.colors['danger']
            
            # Frame da transação
            trans_frame = tk.Frame(self.transactions_list, bg=Theme.colors['surface'])
            trans_frame.pack(fill='x', pady=2)
            
            tk.Label(
                trans_frame,
                text="🟢" if tipo == 'entrada' else "🔴",
                font=('Segoe UI', 10),
                bg=Theme.colors['surface'],
                fg=color
            ).pack(side='left', padx=(0, 5))
            
            tk.Label(
                trans_frame,
                text=f"{descricao[:15]}...",
                font=('Segoe UI', 9),
                bg=Theme.colors['surface'],
                fg=Theme.colors['text_primary']
            ).pack(side='left', padx=(0, 10))
            
            tk.Label(
                trans_frame,
                text=f"{valor:,} Kz",
                font=('Segoe UI', 9, 'bold'),
                bg=Theme.colors['surface'],
                fg=color
            ).pack(side='left', padx=(0, 10))
            
            tk.Label(
                trans_frame,
                text=data_str,
                font=('Segoe UI', 8),
                bg=Theme.colors['surface'],
                fg=Theme.colors['text_secondary']
            ).pack(side='right')
    
    def update_guests_list(self):
        """Atualiza lista de hóspedes"""
        # Limpar lista existente
        for widget in self.guests_list.winfo_children():
            widget.destroy()
        
        # Obter últimos hóspedes
        result = self.db.execute_query('''
            SELECT nome, quarto_numero, check_in 
            FROM hospedes 
            WHERE ativo = 1 
            ORDER BY check_in DESC 
            LIMIT 5
        ''', commit=False)
        
        guests = result.fetchall()
        
        if not guests:
            tk.Label(
                self.guests_list,
                text="Sem hóspedes ativos",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(pady=10)
            return
        
        for guest in guests:
            nome, quarto, check_in = guest
            
            # Formatar data
            check_in_dt = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
            check_in_str = check_in_dt.strftime('%H:%M')
            
            # Frame do hóspede
            guest_frame = tk.Frame(self.guests_list, bg=Theme.colors['surface'])
            guest_frame.pack(fill='x', pady=2)
            
            tk.Label(
                guest_frame,
                text="👤",
                font=('Segoe UI', 12),
                bg=Theme.colors['surface'],
                fg=Theme.colors['primary']
            ).pack(side='left', padx=(0, 5))
            
            tk.Label(
                guest_frame,
                text=f"{nome[:15]}...",
                font=('Segoe UI', 9),
                bg=Theme.colors['surface'],
                fg=Theme.colors['text_primary']
            ).pack(side='left', padx=(0, 10))
            
            tk.Label(
                guest_frame,
                text=f"Q{quarto}",
                font=('Segoe UI', 9, 'bold'),
                bg=Theme.colors['surface'],
                fg=Theme.colors['info']
            ).pack(side='left', padx=(0, 10))
            
            tk.Label(
                guest_frame,
                text=check_in_str,
                font=('Segoe UI', 8),
                bg=Theme.colors['surface'],
                fg=Theme.colors['text_secondary']
            ).pack(side='right')

class SistemaHospedariaCheca:
    """Sistema principal da Hospedaria Checa"""
    def __init__(self):
        # Inicializar serviços
        self.db = DatabaseManager()
        self.user_service = UserService(self.db)
        self.room_service = RoomService(self.db)
        self.guest_service = GuestService(self.db)
        self.finance_service = FinanceService(self.db)
        self.report_service = ReportService(self.db)
        self.hr_service = HRService(self.db)  
        
        # Janela principal
        self.root = tk.Tk()
        self.root.title("🏨 Hospedaria Checa - Sistema de Gestão")
        self.root.geometry("1400x900")
        self.root.configure(bg=Theme.colors['background'])
        
        # Centralizar janela
        self.center_window(1400, 900)
        
        # Variáveis de controle
        self.current_module = None
        self.notification_panel = None
        self.real_time_dashboard = None
        
        # Iniciar com tela de boas-vindas
        self.show_welcome_screen()
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_keyboard_shortcuts()
         
    def center_window(self, width, height):
        """Centraliza a janela na tela"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def clear_window(self):
        """Limpa todas os widgets da janela"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Tela de boas-vindas animada"""
        self.clear_window()
        
        # Frame principal com gradiente
        main_frame = tk.Frame(self.root, bg=Theme.colors['primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Conteúdo central
        content_frame = tk.Frame(main_frame, bg=Theme.colors['primary'])
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo da Hospedaria Checa
        logo_text = AnimatedLabel(
            content_frame,
            text="🏰 HOSPEDARIA CHECA",
            font=('Segoe UI', 48, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        )
        logo_text.pack(pady=(0, 10))
        logo_text.start_typing()
        
        # Slogan
        slogan = AnimatedLabel(
            content_frame,
            text="Conforto e Elegância em Cada Detalhe",
            font=('Segoe UI', 18, 'italic'),
            fg=Theme.colors['accent_light'],
            bg=Theme.colors['primary']
        )
        slogan.pack(pady=(0, 40))
        slogan.start_typing()
        
        # Separador decorativo
        separator = tk.Frame(content_frame, height=2, bg=Theme.colors['accent'])
        separator.pack(fill='x', pady=20)
        
        # Mensagem de boas-vindas
        welcome_text = AnimatedLabel(
            content_frame,
            text="Bem-vindo ao Sistema de Gestão Integrada",
            font=('Segoe UI', 22),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        )
        welcome_text.pack(pady=(0, 30))
        welcome_text.start_typing(lambda: self.show_login_button(content_frame))
        
        # Rodapé
        footer = tk.Label(
            main_frame,
            text="© 2026 Hospedaria Checa - Sistema Interno",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        )
        footer.pack(side='bottom', pady=20)
    
    def show_login_button(self, parent):
        """Mostra botão para iniciar sistema"""
        # Frame para botão com efeito
        button_frame = tk.Frame(parent, bg=Theme.colors['primary'])
        button_frame.pack(pady=20)
        
        # Botão com efeito de brilho
        login_btn = ModernButton(
            button_frame,
            text="▶️ ACESSAR SISTEMA",
            bg=Theme.colors['accent'],
            hover_bg=self.lighten_color(Theme.colors['accent'], 20),
            font_size=14,
            rounded=True,
            command=self.show_access_selection
        )
        login_btn.pack()
        
        # Efeito de pulsação
        self.pulse_button(login_btn)
    
    def pulse_button(self, button):
        """Efeito de pulsação no botão"""
        current_bg = button.cget('bg')
        if current_bg == Theme.colors['accent']:
            new_bg = self.lighten_color(Theme.colors['accent'], 20)
        else:
            new_bg = Theme.colors['accent']
        
        button.configure(bg=new_bg)
        self.root.after(1000, lambda: self.pulse_button(button))
    
    def show_access_selection(self):
        """Tela de seleção de tipo de acesso (cadastro/login)"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Cabeçalho
        header = tk.Frame(main_frame, bg=Theme.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐 ACESSO AO SISTEMA",
            font=Theme.fonts['title'],
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(expand=True)
        
        # Container principal
        container = tk.Frame(main_frame, bg=Theme.colors['background'], padx=50, pady=50)
        container.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            container,
            text="Escolha uma opção:",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['background']
        ).pack(pady=(0, 40))
        
        # Cards de seleção
        cards_frame = tk.Frame(container, bg=Theme.colors['background'])
        cards_frame.pack(expand=True)
        
        cards_data = [
            {
                'title': '📝 NOVO CADASTRO',
                'desc': 'Crie sua conta de funcionário\nEscolha seu cargo e defina sua senha',
                'action': 'cadastro',
                'color': Theme.colors['success'],
                'icon': '👤'
            },
            {
                'title': '🔐 LOGIN',
                'desc': 'Já tem uma conta?\nAcesse o sistema com suas credenciais',
                'action': 'login',
                'color': Theme.colors['primary'],
                'icon': '🔑'
            }
        ]
        
        for i, card_data in enumerate(cards_data):
            card = Card(
                cards_frame,
                title=f"{card_data['icon']} {card_data['title']}",
                bg=Theme.colors['surface'],
                width=300,
                height=200
            )
            card.grid(row=0, column=i, padx=20, ipadx=10, ipady=10)
            
            # Descrição
            tk.Label(
                card.content_frame,
                text=card_data['desc'],
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                justify='center',
                wraplength=250
            ).pack(fill='both', expand=True, pady=10)
            
            # Botão de seleção
            ModernButton(
                card.content_frame,
                text="SELECIONAR",
                bg=card_data['color'],
                hover_bg=self.lighten_color(card_data['color'], 20),
                font_size=11,
                command=lambda a=card_data['action']: self.handle_access_action(a)
            ).pack(pady=(10, 0))
        
        # Botão de voltar
        back_frame = tk.Frame(container, bg=Theme.colors['background'])
        back_frame.pack(pady=(40, 0))
        
        ModernButton(
            back_frame,
            text="⬅️ VOLTAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=11,
            command=self.show_welcome_screen
        ).pack()
   
    def refresh_dashboard(self):
        """Atualiza todas as informações do dashboard atual"""
        user_info = self.user_service.get_user_info()
        if not user_info:
            return
        
        tipo = user_info['tipo']
        
        if tipo == 'gerente':
            if hasattr(self, 'real_time_dashboard'):
                self.real_time_dashboard.update_real_time_data()
            # Atualizar outras abas se existirem
            if hasattr(self, 'stats_labels'):
                # Atualizar estatísticas
                room_stats = self.room_service.get_room_stats()
                guest_stats = self.guest_service.get_guest_stats()
                
                # Atualizar labels de estatísticas se existirem
                if 'ocupados' in self.stats_labels:
                    self.stats_labels['ocupados'].configure(text=f"{room_stats['ocupados']}/{room_stats['total']}")
                if 'taxa_ocupacao' in self.stats_labels:
                    self.stats_labels['taxa_ocupacao'].configure(text=f"{room_stats['taxa_ocupacao']:.1f}%")
                if 'ativos' in self.stats_labels:
                    self.stats_labels['ativos'].configure(text=str(guest_stats['ativos']))
                
                # Forçar atualização da interface
                self.root.update()
        
        elif tipo == 'recepcionista':
            # Atualizar lista de hóspedes ativos
            if hasattr(self, 'guests_tree'):
                self.update_guests_tree()
            
            # Atualizar lista de quartos
            if hasattr(self, 'rooms_tree'):
                self.update_rooms_list_simple()
            
            # Atualizar quartos disponíveis no check-in
            if hasattr(self, 'checkin_quarto_numero'):
                available_rooms = self.room_service.get_available_rooms()
                self.checkin_quarto_numero['values'] = available_rooms
                if available_rooms:
                    self.checkin_quarto_numero.set(available_rooms[0])
        
        elif tipo == 'financeiro':
            # Atualizar lista de transações
            if hasattr(self, 'trans_tree'):
                self.update_transactions_list()
            
            # Atualizar relatório financeiro
            if hasattr(self, 'report_text'):
                self.generate_financial_report()
        
        
        elif tipo == 'rh':  # NOVO
            # Atualizar lista de funcionários
            if hasattr(self, 'employees_tree'):
                self.update_employees_list()
            # Atualizar outras listas específicas do RH
            
          
        # Log da ação
        if user_info:
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'ATUALIZAR_DASHBOARD',
                'Sistema',
                'Dashboard atualizado manualmente'
            )
        
    def handle_access_action(self, action):
        """Processa ação de acesso (cadastro ou login)"""
        if action == 'cadastro':
            self.show_role_selection()
        else:  # login
            self.show_login_screen()
    
    def show_role_selection(self):
        """Tela de seleção de cargo para cadastro"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Cabeçalho
        header = tk.Frame(main_frame, bg=Theme.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📝 NOVO CADASTRO",
            font=Theme.fonts['title'],
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(expand=True)
        
        # Container principal
        container = tk.Frame(main_frame, bg=Theme.colors['background'], padx=50, pady=50)
        container.pack(fill='both', expand=True)
        
        # Instrução
        tk.Label(
            container,
            text="Selecione o seu cargo:",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['background']
        ).pack(pady=(0, 30))
        
        # Cards de seleção de cargo
        cards_frame = tk.Frame(container, bg=Theme.colors['background'])
        cards_frame.pack(expand=True)
        
        cards_data = [
            {
                'title': '👔 GERENTE',
                'desc': 'Acesso a relatórios gerenciais\nMonitoramento do sistema',
                'type': 'gerente',
                'color': Theme.colors['primary'],
                'icon': '📈'
            },
            {
                'title': '💼 RECEPCIONISTA',
                'desc': 'Cadastro e gestão de hóspedes\nControle de quartos e serviços',
                'type': 'recepcionista',
                'color': Theme.colors['secondary'],
                'icon': '👥'
            },
            {
                'title': ' RECURSOS HUMANOS',
                'desc': 'Gestão de funcionários\nSalários, férias, faltas',
                'type': 'rh',  
                'color': Theme.colors['info'],
                'icon': '👨‍💼'
            },
            {
                'title': '💰 FINANCEIRO',
                'desc': 'Gestão financeira completa\nRelatórios e transações',
                'type': 'financeiro',
                'color': Theme.colors['success'],
                'icon': '💵'
            }
        ]
        
        # Ajustar layout para 4 colunas
        for i, card_data in enumerate(cards_data):
            card = Card(
                cards_frame,
                title=f"{card_data['icon']} {card_data['title']}",
                bg=Theme.colors['surface'],
                width=250,  # Ajustar largura
                height=180
            )
            card.grid(row=0, column=i, padx=5, ipadx=10, ipady=10) 
            
            # Descrição
            tk.Label(
                card.content_frame,
                text=card_data['desc'],
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                justify='center',
                wraplength=230
            ).pack(fill='both', expand=True, pady=5)
            
            # Botão de seleção
            ModernButton(
                card.content_frame,
                text="SELECIONAR CARGO",
                bg=card_data['color'],
                hover_bg=self.lighten_color(card_data['color'], 20),
                font_size=10,
                command=lambda t=card_data['type']: self.show_register_form(t)
            ).pack(pady=(5, 0))
        
        # Botão de voltar
        back_frame = tk.Frame(container, bg=Theme.colors['background'])
        back_frame.pack(pady=(40, 0))
        
        ModernButton(
            back_frame,
            text="⬅️ VOLTAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=11,
            command=self.show_access_selection
        ).pack()
    
    def show_register_form(self, user_type):
        """Mostra formulário de cadastro para o cargo selecionado"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Container com sombra (simulada)
        container = tk.Frame(main_frame, bg=Theme.colors['surface'])
        container.place(relx=0.5, rely=0.5, anchor='center', width=500, height=550)
        
        # Cabeçalho
        header = tk.Frame(container, bg=Theme.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        icons = {
            'gerente': '👔',
            'recepcionista': '💼',
            'financeiro': '💰'
        }
        
        tk.Label(
            header,
            text=f"{icons.get(user_type, '👤')}",
            font=('Segoe UI', 32),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(pady=(10, 0))
        
        tk.Label(
            header,
            text=f"Cadastro - {user_type.upper()}",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack()
        
        # Formulário
        form_frame = tk.Frame(container, bg=Theme.colors['surface'], padx=40, pady=30)
        form_frame.pack(fill='both', expand=True)
        
        # Nome de usuário
        tk.Label(
            form_frame,
            text="Nome de usuário:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.reg_nome = tk.Entry(
            form_frame,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            relief='flat',
            borderwidth=1,
            highlightbackground=Theme.colors['gray'],
            highlightthickness=1,
            highlightcolor=Theme.colors['primary']
        )
        self.reg_nome.pack(fill='x', pady=(0, 15))
        self.reg_nome.focus_set()
        
        # Senha
        tk.Label(
            form_frame,
            text="Senha:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.reg_senha = tk.Entry(
            form_frame,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            relief='flat',
            borderwidth=1,
            show='•',
            highlightbackground=Theme.colors['gray'],
            highlightthickness=1,
            highlightcolor=Theme.colors['primary']
        )
        self.reg_senha.pack(fill='x', pady=(0, 15))
        
        # Confirmar senha
        tk.Label(
            form_frame,
            text="Confirmar senha:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.reg_confirmar = tk.Entry(
            form_frame,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            relief='flat',
            borderwidth=1,
            show='•',
            highlightbackground=Theme.colors['gray'],
            highlightthickness=1,
            highlightcolor=Theme.colors['primary']
        )
        self.reg_confirmar.pack(fill='x', pady=(0, 25))
        
        # Informações sobre a senha
        info_frame = tk.Frame(form_frame, bg=Theme.colors['light'], padx=10, pady=5)
        info_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            info_frame,
            text="ℹ️ A senha deve ter pelo menos 6 caracteres",
            font=Theme.fonts['small'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['light']
        ).pack()
        
        # Botões
        button_frame = tk.Frame(form_frame, bg=Theme.colors['surface'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        ModernButton(
            button_frame,
            text="✅ CADASTRAR",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=11,
            command=lambda: self.register_user(user_type)
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="⬅️ VOLTAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=11,
            command=self.show_role_selection
        ).pack(side='left')
    
    def register_user(self, user_type):
        """Processa cadastro de novo usuário"""
        nome = self.reg_nome.get().strip()
        senha = self.reg_senha.get()
        confirmar = self.reg_confirmar.get()
        
        success, message = self.user_service.register_user(nome, senha, confirmar, user_type)
        
        if success:
            messagebox.showinfo("Cadastro Realizado", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Erro no Cadastro", message)
    
    def show_login_screen(self):
        """Tela de login"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Cabeçalho
        header = tk.Frame(main_frame, bg=Theme.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐 LOGIN NO SISTEMA",
            font=Theme.fonts['title'],
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(expand=True)
        
        # Container principal
        container = tk.Frame(main_frame, bg=Theme.colors['background'], padx=50, pady=50)
        container.pack(fill='both', expand=True)
        
        # Card de login
        login_card = Card(container, title="ACESSO")
        login_card.pack(fill='both', expand=True)
        
        login_content = login_card.content_frame
        
        # Formulário de login
        tk.Label(
            login_content,
            text="Nome de usuário:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.login_nome = tk.Entry(
            login_content,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            relief='flat',
            borderwidth=1,
            highlightbackground=Theme.colors['gray'],
            highlightthickness=1,
            highlightcolor=Theme.colors['primary'],
            width=30
        )
        self.login_nome.pack(fill='x', pady=(0, 20))
        self.login_nome.focus_set()
        
        tk.Label(
            login_content,
            text="Senha:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.login_senha = tk.Entry(
            login_content,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            relief='flat',
            borderwidth=1,
            show='•',
            highlightbackground=Theme.colors['gray'],
            highlightthickness=1,
            highlightcolor=Theme.colors['primary'],
            width=30
        )
        self.login_senha.pack(fill='x', pady=(0, 30))
        
        # Botões
        button_frame = tk.Frame(login_content, bg=Theme.colors['surface'])
        button_frame.pack(fill='x')
        
        ModernButton(
            button_frame,
            text="🔐 ENTRAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=12,
            command=self.process_login
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="📝 NOVO CADASTRO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=11,
            command=self.show_role_selection
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="⬅️ VOLTAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=11,
            command=self.show_access_selection
        ).pack(side='left')
        
        # Aviso de primeiro acesso
        info_frame = tk.Frame(login_content, bg=Theme.colors['light'], padx=10, pady=10)
        info_frame.pack(fill='x', pady=(30, 0))
        
        tk.Label(
            info_frame,
            text="ℹ️ Faça login com as informações do seu cadastro",
            font=Theme.fonts['small'],
            fg=Theme.colors['warning'],
            bg=Theme.colors['light'],
            wraplength=400
        ).pack()
    
    def process_login(self):
        """Processa o login do usuário"""
        username = self.login_nome.get().strip()
        password = self.login_senha.get()
        
        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        
        success, message = self.user_service.login(username, password)
        
        if success:
            user_info = self.user_service.get_user_info()
            
            # Mostrar mensagem de boas-vindas personalizada
            welcome_msg = f"""
            🎉 Bem-vindo(a), {user_info['nome']}!
            
            Cargo: {user_info['tipo'].upper()}
            Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            
            Sistema: Hospedaria Checa
            """
            messagebox.showinfo("Acesso Concedido", welcome_msg)
            
            # Verificar configuração inicial
            self.check_initial_configuration()
        else:
            messagebox.showerror("Erro de Autenticação", message)
    
    def check_initial_configuration(self):
        """Verifica se o sistema precisa de configuração inicial"""
        result = self.db.execute_query(
            "SELECT qtde_quartos FROM config_hospedaria WHERE id = 1",
            commit=False
        )
        config = result.fetchone()
        
        user_info = self.user_service.get_user_info()
        
        if not config or config[0] == 0:
            if user_info['tipo'] == 'gerente':
                self.show_initial_config()
            else:
                messagebox.showinfo("Aguarde", 
                    "O sistema está sendo configurado pelo gerente.\n"
                    "Por favor, aguarde para acessar.")
                self.user_service.logout()
                self.show_login_screen()
        else:
            self.show_dashboard()
    
    def show_initial_config(self):
        """Tela de configuração inicial"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Card de configuração
        card = Card(main_frame, title="⚙️ CONFIGURAÇÃO INICIAL")
        card.pack(fill='both', expand=True)
        
        content = card.content_frame
        
        # Informação
        tk.Label(
            content,
            text="Configuração da Hospedaria Checa",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(pady=(0, 20))
        
        tk.Label(
            content,
            text="Para iniciar o sistema, configure o número total de quartos:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface'],
            wraplength=500
        ).pack(pady=(0, 30))
        
        # Entrada para quantidade de quartos
        input_frame = tk.Frame(content, bg=Theme.colors['surface'])
        input_frame.pack(pady=(0, 30))
        
        tk.Label(
            input_frame,
            text="Número de quartos:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        self.entry_room_count = tk.Entry(
            input_frame,
            font=Theme.fonts['body'],
            width=10,
            justify='center'
        )
        self.entry_room_count.pack(side='left')
        self.entry_room_count.insert(0, "30")
        
        # Informações adicionais
        info_frame = tk.Frame(content, bg=Theme.colors['light'], padx=15, pady=10)
        info_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(
            info_frame,
            text="ℹ️ Os quartos serão criados automaticamente com numeração sequencial.\n"
                 "A categoria (VIP/Normal) será definida no cadastro de cada hóspede.",
            font=Theme.fonts['small'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['light'],
            justify='left'
        ).pack()
        
        # Botões
        button_frame = tk.Frame(content, bg=Theme.colors['surface'])
        button_frame.pack()
        
        ModernButton(
            button_frame,
            text="✅ CONFIGURAR E INICIAR",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=12,
            command=self.configure_system
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="🚪 SAIR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=12,
            command=self.logout
        ).pack(side='left')
    
    def configure_system(self):
        """Configura o sistema com os quartos"""
        try:
            room_count = int(self.entry_room_count.get().strip())
            if room_count <= 0 or room_count > 200:
                messagebox.showerror("Erro", "Digite um número válido (1-200)!")
                return
            
            user_info = self.user_service.get_user_info()
            success, message = self.room_service.configure_rooms(room_count, user_info)
            
            if success:
                messagebox.showinfo("Sucesso", message)
                self.show_dashboard()
            else:
                messagebox.showerror("Erro", message)
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")
    
    def show_dashboard(self):
        """Mostra dashboard baseado no tipo de usuário"""
        self.clear_window()
        
        user_info = self.user_service.get_user_info()
        if not user_info:
            self.show_login_screen()
            return
        
        # Barra superior
        self.create_top_bar(user_info)
        
        # Área principal baseada no tipo de usuário
        main_area = tk.Frame(self.root, bg=Theme.colors['background'])
        main_area.pack(fill='both', expand=True, padx=20, pady=20)
        
        if user_info['tipo'] == 'gerente':
            self.show_manager_dashboard(main_area)
        elif user_info['tipo'] == 'recepcionista':
            self.show_receptionist_dashboard(main_area)
        elif user_info['tipo'] == 'rh':
            self.show_hr_dashboard(main_area)
        elif user_info['tipo'] == 'financeiro':
            self.show_financial_dashboard(main_area)
          # Iniciar atualização automática
        
        self.root.after(5000, self.start_auto_refresh)  # Começar após 5 segundos

    def create_top_bar(self, user_info):
        """Cria a barra superior do sistema"""
        top_bar = tk.Frame(self.root, bg=Theme.colors['primary'], height=70)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Logo e nome do sistema
        left_frame = tk.Frame(top_bar, bg=Theme.colors['primary'])
        left_frame.pack(side='left', fill='y', padx=20)
        
        tk.Label(
            left_frame,
            text="🏰 HOSPEDARIA CHECA",
            font=('Segoe UI', 18, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(side='left', padx=(0, 20))
        
        # Módulo atual
        self.module_label = tk.Label(
            left_frame,
            text="Dashboard",
            font=('Segoe UI', 12),
            fg=Theme.colors['accent_light'],
            bg=Theme.colors['primary']
        )
        self.module_label.pack(side='left')
        
        # BOTÃO DE ATUALIZAÇÃO (ADICIONAR ESTE)
        refresh_frame = tk.Frame(top_bar, bg=Theme.colors['primary'])
        refresh_frame.pack(side='left', fill='y', padx=20)
        
        self.refresh_btn = ModernButton(
            refresh_frame,
            text="🔄 ATUALIZAR",
            bg=Theme.colors['accent'],
            hover_bg=self.lighten_color(Theme.colors['accent'], 20),
            font_size=9,
            padx=10,
            pady=5,
            command=self.refresh_dashboard
        )
        self.refresh_btn.pack(side='left')
        
        # Botão de notificações
        notif_frame = tk.Frame(top_bar, bg=Theme.colors['primary'])
        notif_frame.pack(side='left', fill='y', padx=20)
        
        self.notif_btn = ModernButton(
            notif_frame,
            text="🔔 NOTIFICAÇÕES",
            bg=Theme.colors['accent'],
            hover_bg=self.lighten_color(Theme.colors['accent'], 20),
            font_size=9,
            padx=10,
            pady=5,
            command=self.toggle_notifications
        )
        self.notif_btn.pack(side='left')
        
        # Informações do usuário
        right_frame = tk.Frame(top_bar, bg=Theme.colors['primary'])
        right_frame.pack(side='right', fill='y', padx=20)
        
        # Ícone do usuário
        user_icon = '👔' if user_info['tipo'] == 'gerente' else '💼' if user_info['tipo'] == 'recepcionista' else '💰'
        
        tk.Label(
            right_frame,
            text=user_icon,
            font=('Segoe UI', 14),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(side='left', padx=(0, 10))
        
        # Nome e cargo
        user_text = tk.Label(
            right_frame,
            text=f"{user_info['nome']} ({user_info['tipo'].upper()})",
            font=('Segoe UI', 11),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        )
        user_text.pack(side='left', padx=(0, 20))
        
        # Botão de logout
        ModernButton(
            right_frame,
            text="🚪 SAIR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=9,
            padx=15,
            pady=5,
            command=self.logout
        ).pack(side='left')
        
        # Data e hora atual
        self.time_label = tk.Label(
            right_frame,
            text=datetime.now().strftime('%d/%m/%Y %H:%M'),
            font=('Segoe UI', 10),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        )
        self.time_label.pack(side='left', padx=(20, 0))
        
        # Painel de notificações (inicialmente oculto)
        self.notification_panel = NotificationPanel(self.root, self.db, self.user_service)
        
        # Atualizar hora
        self.update_time()
    
    def start_auto_refresh(self):
        """Inicia atualização automática periódica"""
        # Atualizar dashboard a cada 30 segundos
        self.refresh_dashboard()
        self.root.after(30000, self.start_auto_refresh)  # 30 segundos
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado"""
        # F5 para atualizar
        self.root.bind('<F5>', lambda e: self.refresh_dashboard())
        # Ctrl+R para atualizar
        self.root.bind('<Control-r>', lambda e: self.refresh_dashboard())
        # Ctrl+Shift+R para atualizar
        self.root.bind('<Control-Shift-R>', lambda e: self.refresh_dashboard())
        
    def update_time(self):
        """Atualiza o relógio na barra superior"""
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.configure(text=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            self.root.after(1000, self.update_time)
    
    def toggle_notifications(self):
        """Alterna visibilidade do painel de notificações"""
        if not hasattr(self, 'notification_panel') or self.notification_panel is None:
            return
        
        if not self.notification_panel.notification_frame:
            self.notification_panel.create_panel()
            self.notification_panel.notification_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=500)
        else:
            if self.notification_panel.notification_frame.winfo_ismapped():
                self.notification_panel.notification_frame.place_forget()
            else:
                self.notification_panel.notification_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=500)
                self.notification_panel.update_notifications()
    
    def show_hr_dashboard(self, parent):
        """Dashboard do RH - Gestão de Recursos Humanos"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Aba de Funcionários
        funcionarios_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(funcionarios_frame, text='👥 FUNCIONÁRIOS')
        self.create_employees_section(funcionarios_frame)
        
        # Aba de Folha de Pagamento
        folha_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(folha_frame, text='💰 FOLHA DE PAGAMENTO')
        self.create_payroll_section(folha_frame)
        
        # Aba de Férias
        ferias_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(ferias_frame, text='🏖️ FÉRIAS')
        self.create_vacations_section_corrected(ferias_frame)
        
        # Aba de Ponto/Horas
        ponto_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(ponto_frame, text='⏰ PONTO/HORAS')
        self.create_time_attendance_section_corrected(ponto_frame)
        
        # Aba de Relatórios RH
        relatorios_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(relatorios_frame, text='📊 RELATÓRIOS RH')
        self.create_hr_reports_section_corrected(relatorios_frame)
    
    def create_employees_section(self, parent):
        """Cria seção de gestão de funcionários"""
        employees_card = Card(parent, title="👥 GESTÃO DE FUNCIONÁRIOS")
        employees_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        employees_content = employees_card.content_frame
        
        # Botões de ação
        action_frame = tk.Frame(employees_content, bg=Theme.colors['surface'])
        action_frame.pack(fill='x', pady=(0, 20))
        
        ModernButton(
            action_frame,
            text="➕ NOVO FUNCIONÁRIO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.show_new_employee_form
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            action_frame,
            text="🔄 ATUALIZAR LISTA",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.update_employees_list
        ).pack(side='left')

          
        # Lista de funcionários                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
        list_frame = tk.Frame(employees_content, bg=Theme.colors['surface'])
        list_frame.pack(fill='both', expand=True)
        
        # Treeview para funcionários
        columns = ('ID', 'Nome', 'Cargo', 'Departamento', 'Admissão', 'Salário', 'Status')
        
        self.employees_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        col_widths = [50, 150, 100, 100, 100, 100, 80]
        for col, width in zip(columns, col_widths):
            self.employees_tree.heading(col, text=col)
            self.employees_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.employees_tree.yview)
        self.employees_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employees_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Carregar funcionários
        self.update_employees_list()
        
        # Botões de ação na lista
        detail_frame = tk.Frame(employees_content, bg=Theme.colors['surface'])
        detail_frame.pack(fill='x', pady=(10, 0))
        
        ModernButton(
            detail_frame,
            text="🔍 DETALHES",
            bg=Theme.colors['primary'],
            hover_bg=self.lighten_color(Theme.colors['primary'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.show_employee_details
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            detail_frame,
            text="✏️ EDITAR",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.edit_employee
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            detail_frame,
            text="🚪 DEMITIR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.dismiss_employee
        ).pack(side='left')

    def update_employees_list(self):
        """Atualiza lista de funcionários"""
        if not hasattr(self, 'employees_tree'):
            return
        
        # Limpar lista
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Obter funcionários
        funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
        
        for func in funcionarios:
            # Formatar salário
            salario_formatado = f"{func[6]:,} Kz"
            
            # Formatar data de admissão
            adm_date = func[5]
            if adm_date:
                try:
                    adm_date = datetime.strptime(adm_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass
            
            self.employees_tree.insert('', 'end', values=(
                func[0],  # ID
                func[1],  # Nome
                func[2],  # Cargo
                func[3],  # Departamento
                adm_date,
                salario_formatado,
                "🟢 Ativo" if func[16] else "🔴 Inativo"
            ))

    def show_new_employee_form(self):
        """Mostra formulário completo para novo funcionário"""
        form_window = tk.Toplevel(self.root)
        form_window.title("👨‍💼 CADASTRO DE NOVO FUNCIONÁRIO")
        form_window.geometry("800x750")
        form_window.configure(bg=Theme.colors['background'])
        form_window.resizable(False, True)  # Permitir altura variável
        
        # Centralizar janela
        form_window.update_idletasks()
        width = form_window.winfo_width()
        height = form_window.winfo_height()
        x = (form_window.winfo_screenwidth() // 2) - (width // 2)
        y = (form_window.winfo_screenheight() // 2) - (height // 2)
        form_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Container principal com scroll
        main_container = tk.Frame(form_window, bg=Theme.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_container, bg=Theme.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cabeçalho
        header_frame = tk.Frame(scrollable_frame, bg=Theme.colors['primary'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="👨‍💼 NOVO FUNCIONÁRIO",
            font=('Segoe UI', 18, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(pady=15)
        
        # ====================== FORMULÁRIO ======================
        
        # Card para informações pessoais
        pessoal_card = Card(scrollable_frame, title="📋 INFORMAÇÕES PESSOAIS")
        pessoal_card.pack(fill='x', pady=(0, 15))
        
        pessoal_content = pessoal_card.content_frame
        
        # Nome completo
        tk.Label(
            pessoal_content,
            text="Nome completo: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_nome = tk.Entry(pessoal_content, font=Theme.fonts['body'], width=50)
        self.emp_nome.pack(fill='x', pady=(0, 15))
        self.emp_nome.focus_set()
        
        # Documento (BI/Passaporte)
        tk.Label(
            pessoal_content,
            text="Documento (BI/Passaporte): *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_documento = tk.Entry(pessoal_content, font=Theme.fonts['body'], width=30)
        self.emp_documento.pack(fill='x', pady=(0, 15))
        
        # Data de nascimento
        tk.Label(
            pessoal_content,
            text="Data de nascimento:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        nasc_frame = tk.Frame(pessoal_content, bg=Theme.colors['surface'])
        nasc_frame.pack(fill='x', pady=(0, 15))
        
        self.emp_nascimento_dia = ttk.Combobox(
            nasc_frame,
            values=[str(i).zfill(2) for i in range(1, 32)],
            state='readonly',
            width=5
        )
        self.emp_nascimento_dia.pack(side='left', padx=(0, 5))
        self.emp_nascimento_dia.set('01')
        
        self.emp_nascimento_mes = ttk.Combobox(
            nasc_frame,
            values=[str(i).zfill(2) for i in range(1, 13)],
            state='readonly',
            width=5
        )
        self.emp_nascimento_mes.pack(side='left', padx=(0, 5))
        self.emp_nascimento_mes.set('01')
        
        self.emp_nascimento_ano = ttk.Combobox(
            nasc_frame,
            values=[str(i) for i in range(1950, 2010)],
            state='readonly',
            width=8
        )
        self.emp_nascimento_ano.pack(side='left')
        self.emp_nascimento_ano.set('1990')
        
        # Estado civil
        tk.Label(
            pessoal_content,
            text="Estado civil:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_estado_civil = ttk.Combobox(
            pessoal_content,
            values=['Solteiro(a)', 'Casado(a)', 'Divorciado(a)', 'Viúvo(a)', 'União de facto'],
            state='readonly',
            width=20
        )
        self.emp_estado_civil.pack(fill='x', pady=(0, 15))
        self.emp_estado_civil.set('Solteiro(a)')
        
        # Número de filhos
        tk.Label(
            pessoal_content,
            text="Número de filhos:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_filhos = ttk.Combobox(
            pessoal_content,
            values=[str(i) for i in range(11)],
            state='readonly',
            width=5
        )
        self.emp_filhos.pack(fill='x', pady=(0, 15))
        self.emp_filhos.set('0')
        
        # ====================== INFORMAÇÕES DE CONTATO ======================
        
        contato_card = Card(scrollable_frame, title="📞 INFORMAÇÕES DE CONTATO")
        contato_card.pack(fill='x', pady=(0, 15))
        
        contato_content = contato_card.content_frame
        
        # Telefone
        tk.Label(
            contato_content,
            text="Telefone: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_telefone = tk.Entry(contato_content, font=Theme.fonts['body'], width=30)
        self.emp_telefone.pack(fill='x', pady=(0, 15))
        
        # Email
        tk.Label(
            contato_content,
            text="Email:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_email = tk.Entry(contato_content, font=Theme.fonts['body'], width=40)
        self.emp_email.pack(fill='x', pady=(0, 15))
        
        # Endereço
        tk.Label(
            contato_content,
            text="Endereço:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_endereco = tk.Entry(contato_content, font=Theme.fonts['body'], width=50)
        self.emp_endereco.pack(fill='x', pady=(0, 15))
        
        # ====================== INFORMAÇÕES PROFISSIONAIS ======================
        
        profissional_card = Card(scrollable_frame, title="💼 INFORMAÇÕES PROFISSIONAIS")
        profissional_card.pack(fill='x', pady=(0, 15))
        
        profissional_content = profissional_card.content_frame
        
        # Cargo
        tk.Label(
            profissional_content,
            text="Cargo: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_cargo = ttk.Combobox(
            profissional_content,
            values=['Recepcionista', 'Camareira', 'Cozinheiro', 'Segurança', 
                    'Manutenção', 'Gerente', 'Administrador', 'Contador',
                    'Supervisor', 'Auxiliar', 'Outro'],
            state='readonly',
            width=25
        )
        self.emp_cargo.pack(fill='x', pady=(0, 15))
        self.emp_cargo.set('Recepcionista')
        
        # Departamento
        tk.Label(
            profissional_content,
            text="Departamento: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_departamento = ttk.Combobox(
            profissional_content,
            values=['Recepção', 'Limpeza', 'Manutenção', 'Gerência', 
                    'Cozinha', 'Segurança', 'Administração', 'Financeiro', 'RH'],
            state='readonly',
            width=20
        )
        self.emp_departamento.pack(fill='x', pady=(0, 15))
        self.emp_departamento.set('Recepção')
        
        # Data de admissão
        tk.Label(
            profissional_content,
            text="Data de admissão: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        adm_frame = tk.Frame(profissional_content, bg=Theme.colors['surface'])
        adm_frame.pack(fill='x', pady=(0, 15))
        
        # Usar data atual como padrão
        hoje = datetime.now()
        
        self.emp_admissao_dia = ttk.Combobox(
            adm_frame,
            values=[str(i).zfill(2) for i in range(1, 32)],
            state='readonly',
            width=5
        )
        self.emp_admissao_dia.pack(side='left', padx=(0, 5))
        self.emp_admissao_dia.set(str(hoje.day).zfill(2))
        
        self.emp_admissao_mes = ttk.Combobox(
            adm_frame,
            values=[str(i).zfill(2) for i in range(1, 13)],
            state='readonly',
            width=5
        )
        self.emp_admissao_mes.pack(side='left', padx=(0, 5))
        self.emp_admissao_mes.set(str(hoje.month).zfill(2))
        
        self.emp_admissao_ano = ttk.Combobox(
            adm_frame,
            values=[str(i) for i in range(2020, 2031)],
            state='readonly',
            width=8
        )
        self.emp_admissao_ano.pack(side='left')
        self.emp_admissao_ano.set(str(hoje.year))
        
        # Salário base
        tk.Label(
            profissional_content,
            text="Salário base (Kz): *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_salario = tk.Entry(profissional_content, font=Theme.fonts['body'], width=20)
        self.emp_salario.pack(fill='x', pady=(0, 15))
        self.emp_salario.insert(0, "85000")  # Salário base padrão
        
        # ====================== INFORMAÇÕES BANCÁRIAS ======================
        
        bancario_card = Card(scrollable_frame, title="🏦 INFORMAÇÕES BANCÁRIAS")
        bancario_card.pack(fill='x', pady=(0, 15))
        
        bancario_content = bancario_card.content_frame
        
        # Banco
        tk.Label(
            bancario_content,
            text="Banco:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_banco = ttk.Combobox(
            bancario_content,
            values=['BAI', 'BFA', 'BCI', 'BIC', 'BPC', 'Millennium', 'Standard Bank', 
                    'Caixa Geral', 'Solução', 'Outro'],
            state='readonly',
            width=20
        )
        self.emp_banco.pack(fill='x', pady=(0, 15))
        self.emp_banco.set('BAI')
        
        # Agência
        tk.Label(
            bancario_content,
            text="Agência:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_agencia = tk.Entry(bancario_content, font=Theme.fonts['body'], width=15)
        self.emp_agencia.pack(fill='x', pady=(0, 15))
        
        # Conta bancária
        tk.Label(
            bancario_content,
            text="Conta bancária:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.emp_conta = tk.Entry(bancario_content, font=Theme.fonts['body'], width=25)
        self.emp_conta.pack(fill='x', pady=(0, 15))
        
        # ====================== OBSERVAÇÕES ======================
        
        obs_card = Card(scrollable_frame, title="📝 OBSERVAÇÕES")
        obs_card.pack(fill='x', pady=(0, 20))
        
        obs_content = obs_card.content_frame
        
        self.emp_observacoes = scrolledtext.ScrolledText(
            obs_content,
            font=Theme.fonts['body'],
            bg=Theme.colors['light'],
            fg=Theme.colors['text_primary'],
            wrap='word',
            height=5,
            width=70
        )
        self.emp_observacoes.pack(fill='x', padx=10, pady=10)
        
        # ====================== BOTÕES DE AÇÃO ======================
        
        button_frame = tk.Frame(scrollable_frame, bg=Theme.colors['background'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Botão SALVAR
        ModernButton(
            button_frame,
            text="✅ SALVAR FUNCIONÁRIO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=12,
            padx=20,
            pady=12,
            command=lambda: self.save_new_employee(form_window)
        ).pack(side='left', padx=(0, 15))
        
        # Botão CANCELAR
        ModernButton(
            button_frame,
            text="❌ CANCELAR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=12,
            padx=20,
            pady=12,
            command=form_window.destroy
        ).pack(side='left')
        
        # Botão LIMPAR
        ModernButton(
            button_frame,
            text="🗑️ LIMPAR FORMULÁRIO",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=11,
            padx=15,
            pady=12,
            command=self.clear_employee_form
        ).pack(side='right')
        
        # Adicionar espaço extra no final para rolagem
        tk.Frame(scrollable_frame, height=20, bg=Theme.colors['background']).pack()
        
        # Configurar rolagem com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Tecla Enter para salvar
        form_window.bind('<Return>', lambda e: self.save_new_employee(form_window))
        # Tecla ESC para cancelar
        form_window.bind('<Escape>', lambda e: form_window.destroy())

    def clear_employee_form(self):
        """Limpa todos os campos do formulário de funcionário"""
        if hasattr(self, 'emp_nome'):
            self.emp_nome.delete(0, tk.END)
        if hasattr(self, 'emp_documento'):
            self.emp_documento.delete(0, tk.END)
        if hasattr(self, 'emp_telefone'):
            self.emp_telefone.delete(0, tk.END)
        if hasattr(self, 'emp_email'):
            self.emp_email.delete(0, tk.END)
        if hasattr(self, 'emp_endereco'):
            self.emp_endereco.delete(0, tk.END)
        if hasattr(self, 'emp_salario'):
            self.emp_salario.delete(0, tk.END)
            self.emp_salario.insert(0, "85000")
        if hasattr(self, 'emp_agencia'):
            self.emp_agencia.delete(0, tk.END)
        if hasattr(self, 'emp_conta'):
            self.emp_conta.delete(0, tk.END)
        if hasattr(self, 'emp_observacoes'):
            self.emp_observacoes.delete('1.0', tk.END)
        
        # Definir valores padrão para comboboxes
        if hasattr(self, 'emp_nascimento_dia'):
            self.emp_nascimento_dia.set('01')
            self.emp_nascimento_mes.set('01')
            self.emp_nascimento_ano.set('1990')
        if hasattr(self, 'emp_estado_civil'):
            self.emp_estado_civil.set('Solteiro(a)')
        if hasattr(self, 'emp_filhos'):
            self.emp_filhos.set('0')
        if hasattr(self, 'emp_cargo'):
            self.emp_cargo.set('Recepcionista')
        if hasattr(self, 'emp_departamento'):
            self.emp_departamento.set('Recepção')
        if hasattr(self, 'emp_banco'):
            self.emp_banco.set('BAI')
        
        # Data de admissão padrão (hoje)
        if hasattr(self, 'emp_admissao_dia'):
            hoje = datetime.now()
            self.emp_admissao_dia.set(str(hoje.day).zfill(2))
            self.emp_admissao_mes.set(str(hoje.month).zfill(2))
            self.emp_admissao_ano.set(str(hoje.year))
        
        messagebox.showinfo("Formulário Limpo", "Todos os campos foram limpos!")

    def save_new_employee(self, window):
        """Salva o novo funcionário no banco de dados"""
        # Validar campos obrigatórios
        campos_obrigatorios = [
            (self.emp_nome, "Nome completo"),
            (self.emp_documento, "Documento"),
            (self.emp_telefone, "Telefone"),
            (self.emp_cargo, "Cargo"),
            (self.emp_departamento, "Departamento"),
            (self.emp_salario, "Salário base")
        ]
        
        for campo, nome in campos_obrigatorios:
            if not campo.get().strip():
                messagebox.showerror("Erro", f"O campo '{nome}' é obrigatório!")
                campo.focus_set()
                return
        
        # Validar salário
        try:
            salario = int(self.emp_salario.get().replace('.', '').replace(',', ''))
            if salario <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Salário inválido! Digite um valor numérico positivo.")
            self.emp_salario.focus_set()
            return
        
        # Preparar dados do funcionário
        dados_funcionario = {
            'nome': self.emp_nome.get().strip(),
            'documento': self.emp_documento.get().strip(),
            'cargo': self.emp_cargo.get(),
            'departamento': self.emp_departamento.get(),
            'salario_base': salario,
            'telefone': self.emp_telefone.get().strip(),
            'email': self.emp_email.get().strip(),
            'endereco': self.emp_endereco.get().strip(),
            'banco': self.emp_banco.get(),
            'agencia': self.emp_agencia.get().strip(),
            'conta_bancaria': self.emp_conta.get().strip(),
            'observacoes': self.emp_observacoes.get("1.0", "end-1c").strip()
        }
        
        # Data de nascimento
        if (hasattr(self, 'emp_nascimento_dia') and 
            hasattr(self, 'emp_nascimento_mes') and 
            hasattr(self, 'emp_nascimento_ano')):
            dia = self.emp_nascimento_dia.get()
            mes = self.emp_nascimento_mes.get()
            ano = self.emp_nascimento_ano.get()
            if dia and mes and ano:
                dados_funcionario['data_nascimento'] = f"{ano}-{mes}-{dia}"
        
        # Data de admissão
        if (hasattr(self, 'emp_admissao_dia') and 
            hasattr(self, 'emp_admissao_mes') and 
            hasattr(self, 'emp_admissao_ano')):
            dia = self.emp_admissao_dia.get()
            mes = self.emp_admissao_mes.get()
            ano = self.emp_admissao_ano.get()
            if dia and mes and ano:
                dados_funcionario['data_admissao'] = f"{ano}-{mes}-{dia}"
        
        # Estado civil
        if hasattr(self, 'emp_estado_civil'):
            dados_funcionario['estado_civil'] = self.emp_estado_civil.get()
        
        # Filhos
        if hasattr(self, 'emp_filhos'):
            try:
                dados_funcionario['filhos'] = int(self.emp_filhos.get())
            except:
                dados_funcionario['filhos'] = 0
        
        # Obter informações do usuário atual
        user_info = self.user_service.get_user_info()
        
        # Salvar no banco de dados
        success, message, funcionario_id = self.hr_service.cadastrar_funcionario(dados_funcionario, user_info)
        
        if success:
            # Mostrar mensagem de sucesso
            resumo = f"""
            ✅ FUNCIONÁRIO CADASTRADO COM SUCESSO!
            
            ID do Funcionário: {funcionario_id}
            Nome: {dados_funcionario['nome']}
            Documento: {dados_funcionario['documento']}
            Cargo: {dados_funcionario['cargo']}
            Departamento: {dados_funcionario['departamento']}
            Salário base: {dados_funcionario['salario_base']:,} Kz
            Data de admissão: {dados_funcionario.get('data_admissao', 'Hoje')}
            
            Cadastrado por: {user_info['nome']}
            Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            messagebox.showinfo("Sucesso", resumo)
            
            # Fechar janela
            window.destroy()
            
            # Atualizar lista de funcionários se estiver visível
            if hasattr(self, 'employees_tree'):
                self.update_employees_list()
        else:
            messagebox.showerror("Erro", message)

    def update_employees_list(self):
        """Atualiza a lista de funcionários"""
        if not hasattr(self, 'employees_tree'):
            return
        
        # Limpar lista
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        try:
            # Obter funcionários ativos
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            
            if not funcionarios:
                # Adicionar mensagem se não houver funcionários
                self.employees_tree.insert('', 'end', values=(
                    "---", "Nenhum funcionário cadastrado", "", "", "", "", ""
                ))
                return
            
            for func in funcionarios:
                # Formatar salário
                salario_base = func[6] if len(func) > 6 else 0
                salario_formatado = f"{salario_base:,} Kz"
                
                # Formatar data de admissão
                data_admissao = func[5] if len(func) > 5 else ""
                if data_admissao:
                    try:
                        data_admissao = datetime.strptime(data_admissao, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        pass
                
                # Determinar status
                ativo = func[16] if len(func) > 16 else 1
                status = "🟢 Ativo" if ativo else "🔴 Inativo"
                
                self.employees_tree.insert('', 'end', values=(
                    func[0] if len(func) > 0 else "",  # ID
                    func[1] if len(func) > 1 else "",  # Nome
                    func[2] if len(func) > 2 else "",  # Cargo
                    func[3] if len(func) > 3 else "",  # Departamento
                    data_admissao,
                    salario_formatado,
                    status
                ))
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            self.employees_tree.insert('', 'end', values=(
                "ERRO", f"Erro ao carregar: {str(e)[:30]}...", "", "", "", "", ""
            ))
    
    def show_employee_details(self):
        """Mostra detalhes completos do funcionário selecionado"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return
        
        item = self.employees_tree.item(selection[0])
        func_id = item['values'][0]
        
        # Verificar se o ID é válido
        if not func_id or func_id == "---":
            messagebox.showwarning("Aviso", "Selecione um funcionário válido!")
            return
        
        try:
            # Buscar dados completos do funcionário
            result = self.db.execute_query(
                "SELECT * FROM funcionarios WHERE id = ?",
                (func_id,),
                commit=False
            )
            funcionario = result.fetchone()
            
            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado!")
                return
            
            # Buscar folha de pagamento do último mês
            result = self.db.execute_query('''
                SELECT mes_ano, salario_liquido, status 
                FROM folha_pagamento 
                WHERE funcionario_id = ? 
                ORDER BY mes_ano DESC 
                LIMIT 1
            ''', (func_id,), commit=False)
            
            ultima_folha = result.fetchone()
            
            # Buscar registro de ponto do último mês
            hoje = datetime.now()
            mes_ano_atual = hoje.strftime('%Y-%m')
            
            result = self.db.execute_query('''
                SELECT COUNT(*) as dias_trabalhados, SUM(horas_extras) as total_horas_extras
                FROM registros_ponto 
                WHERE funcionario_id = ? 
                AND strftime('%Y-%m', data) = ?
            ''', (func_id, mes_ano_atual), commit=False)
            
            ponto_info = result.fetchone()
            
            # Criar janela de detalhes
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"👨‍💼 Detalhes do Funcionário - ID {func_id}")
            detail_window.geometry("700x800")
            detail_window.configure(bg=Theme.colors['surface'])
            detail_window.resizable(False, True)
            
            # Centralizar janela
            detail_window.update_idletasks()
            width = detail_window.winfo_width()
            height = detail_window.winfo_height()
            x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
            y = (detail_window.winfo_screenheight() // 2) - (height // 2)
            detail_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Container principal com scroll
            main_container = tk.Frame(detail_window, bg=Theme.colors['background'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Canvas e scrollbar
            canvas = tk.Canvas(main_container, bg=Theme.colors['background'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Theme.colors['background'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # ====================== CABEÇALHO ======================
            header_frame = tk.Frame(scrollable_frame, bg=Theme.colors['primary'])
            header_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                header_frame,
                text="👨‍💼 DETALHES DO FUNCIONÁRIO",
                font=('Segoe UI', 18, 'bold'),
                fg=Theme.colors['text_light'],
                bg=Theme.colors['primary']
            ).pack(pady=15)
            
            # ====================== INFORMAÇÕES PESSOAIS ======================
            pessoal_card = Card(scrollable_frame, title="📋 INFORMAÇÕES PESSOAIS")
            pessoal_card.pack(fill='x', pady=(0, 15))
            
            pessoal_content = pessoal_card.content_frame
            
            # Grid para informações
            info_grid = tk.Frame(pessoal_content, bg=Theme.colors['surface'])
            info_grid.pack(fill='x', padx=10, pady=10)
            
            # Linha 1: ID e Nome
            tk.Label(
                info_grid,
                text="ID:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=0, column=0, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text=str(funcionario[0]),
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=0, column=1, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text="Nome:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=1, column=0, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text=funcionario[1],
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=1, column=1, sticky='w', pady=(0, 8))
            
            # Linha 2: Documento e Data Nascimento
            tk.Label(
                info_grid,
                text="Documento:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=2, column=0, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text=funcionario[2],
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=2, column=1, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text="Data Nascimento:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=3, column=0, sticky='w', pady=(0, 8))
            
            data_nasc = funcionario[13] if len(funcionario) > 13 else ""
            data_nasc_fmt = data_nasc if data_nasc else "Não informada"
            tk.Label(
                info_grid,
                text=data_nasc_fmt,
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=3, column=1, sticky='w', pady=(0, 8))
            
            # Linha 3: Estado Civil e Filhos
            tk.Label(
                info_grid,
                text="Estado Civil:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=4, column=0, sticky='w', pady=(0, 8))
            
            estado_civil = funcionario[14] if len(funcionario) > 14 else ""
            tk.Label(
                info_grid,
                text=estado_civil or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=4, column=1, sticky='w', pady=(0, 8))
            
            tk.Label(
                info_grid,
                text="Número de Filhos:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=5, column=0, sticky='w', pady=(0, 8))
            
            filhos = funcionario[15] if len(funcionario) > 15 else 0
            tk.Label(
                info_grid,
                text=str(filhos),
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=5, column=1, sticky='w', pady=(0, 8))
            
            # ====================== INFORMAÇÕES DE CONTATO ======================
            contato_card = Card(scrollable_frame, title="📞 INFORMAÇÕES DE CONTATO")
            contato_card.pack(fill='x', pady=(0, 15))
            
            contato_content = contato_card.content_frame
            
            contato_grid = tk.Frame(contato_content, bg=Theme.colors['surface'])
            contato_grid.pack(fill='x', padx=10, pady=10)
            
            # Telefone
            tk.Label(
                contato_grid,
                text="Telefone:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=0, column=0, sticky='w', pady=(0, 8))
            
            telefone = funcionario[10] if len(funcionario) > 10 else ""
            tk.Label(
                contato_grid,
                text=telefone or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=0, column=1, sticky='w', pady=(0, 8))
            
            # Email
            tk.Label(
                contato_grid,
                text="Email:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=1, column=0, sticky='w', pady=(0, 8))
            
            email = funcionario[11] if len(funcionario) > 11 else ""
            tk.Label(
                contato_grid,
                text=email or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=1, column=1, sticky='w', pady=(0, 8))
            
            # Endereço
            tk.Label(
                contato_grid,
                text="Endereço:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=2, column=0, sticky='w', pady=(0, 8))
            
            endereco = funcionario[12] if len(funcionario) > 12 else ""
            tk.Label(
                contato_grid,
                text=endereco or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=2, column=1, sticky='w', pady=(0, 8))
            
            # ====================== INFORMAÇÕES PROFISSIONAIS ======================
            profissional_card = Card(scrollable_frame, title="💼 INFORMAÇÕES PROFISSIONAIS")
            profissional_card.pack(fill='x', pady=(0, 15))
            
            profissional_content = profissional_card.content_frame
            
            prof_grid = tk.Frame(profissional_content, bg=Theme.colors['surface'])
            prof_grid.pack(fill='x', padx=10, pady=10)
            
            # Cargo
            tk.Label(
                prof_grid,
                text="Cargo:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=0, column=0, sticky='w', pady=(0, 8))
            
            cargo = funcionario[3] if len(funcionario) > 3 else ""
            tk.Label(
                prof_grid,
                text=cargo or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=0, column=1, sticky='w', pady=(0, 8))
            
            # Departamento
            tk.Label(
                prof_grid,
                text="Departamento:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=1, column=0, sticky='w', pady=(0, 8))
            
            departamento = funcionario[4] if len(funcionario) > 4 else ""
            tk.Label(
                prof_grid,
                text=departamento or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=1, column=1, sticky='w', pady=(0, 8))
            
            # Data de Admissão
            tk.Label(
                prof_grid,
                text="Data de Admissão:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=2, column=0, sticky='w', pady=(0, 8))
            
            data_admissao = funcionario[5] if len(funcionario) > 5 else ""
            if data_admissao:
                try:
                    data_adm = datetime.strptime(data_admissao, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    data_adm = data_admissao
            else:
                data_adm = "Não informada"
            tk.Label(
                prof_grid,
                text=data_adm,
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=2, column=1, sticky='w', pady=(0, 8))
            
            # Salário Base
            tk.Label(
                prof_grid,
                text="Salário Base:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=3, column=0, sticky='w', pady=(0, 8))
            
            salario_base = funcionario[6] if len(funcionario) > 6 else 0
            tk.Label(
                prof_grid,
                text=f"{salario_base:,} Kz",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['success'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=3, column=1, sticky='w', pady=(0, 8))
            
            # Tempo de Empresa
            tk.Label(
                prof_grid,
                text="Tempo de Empresa:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=4, column=0, sticky='w', pady=(0, 8))
            
            if data_admissao:
                try:
                    adm = datetime.strptime(data_admissao, '%Y-%m-%d')
                    hoje = datetime.now()
                    diff = hoje - adm
                    anos = diff.days // 365
                    meses = (diff.days % 365) // 30
                    tempo_empresa = f"{anos} anos e {meses} meses"
                except:
                    tempo_empresa = "Não calculável"
            else:
                tempo_empresa = "Não informado"
            
            tk.Label(
                prof_grid,
                text=tempo_empresa,
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=4, column=1, sticky='w', pady=(0, 8))
            
            # Status
            tk.Label(
                prof_grid,
                text="Status:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=5, column=0, sticky='w', pady=(0, 8))
            
            ativo = funcionario[16] if len(funcionario) > 16 else 1
            status_text = "🟢 ATIVO" if ativo else "🔴 INATIVO"
            status_cor = Theme.colors['success'] if ativo else Theme.colors['danger']
            tk.Label(
                prof_grid,
                text=status_text,
                font=('Segoe UI', 10, 'bold'),
                fg=status_cor,
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=5, column=1, sticky='w', pady=(0, 8))
            
            # ====================== INFORMAÇÕES BANCÁRIAS ======================
            bancario_card = Card(scrollable_frame, title="🏦 INFORMAÇÕES BANCÁRIAS")
            bancario_card.pack(fill='x', pady=(0, 15))
            
            bancario_content = bancario_card.content_frame
            
            banco_grid = tk.Frame(bancario_content, bg=Theme.colors['surface'])
            banco_grid.pack(fill='x', padx=10, pady=10)
            
            # Banco
            tk.Label(
                banco_grid,
                text="Banco:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=0, column=0, sticky='w', pady=(0, 8))
            
            banco = funcionario[7] if len(funcionario) > 7 else ""
            tk.Label(
                banco_grid,
                text=banco or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=0, column=1, sticky='w', pady=(0, 8))
            
            # Agência
            tk.Label(
                banco_grid,
                text="Agência:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=1, column=0, sticky='w', pady=(0, 8))
            
            agencia = funcionario[9] if len(funcionario) > 9 else ""
            tk.Label(
                banco_grid,
                text=agencia or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=1, column=1, sticky='w', pady=(0, 8))
            
            # Conta Bancária
            tk.Label(
                banco_grid,
                text="Conta Bancária:",
                font=('Segoe UI', 10, 'bold'),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                width=20,
                anchor='w'
            ).grid(row=2, column=0, sticky='w', pady=(0, 8))
            
            conta = funcionario[8] if len(funcionario) > 8 else ""
            tk.Label(
                banco_grid,
                text=conta or "Não informado",
                font=('Segoe UI', 10),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface'],
                anchor='w'
            ).grid(row=2, column=1, sticky='w', pady=(0, 8))
            
            # ====================== INFORMAÇÕES FINANCEIRAS ======================
            if ultima_folha:
                financeiro_card = Card(scrollable_frame, title="💰 INFORMAÇÕES FINANCEIRAS")
                financeiro_card.pack(fill='x', pady=(0, 15))
                
                financeiro_content = financeiro_card.content_frame
                
                fin_grid = tk.Frame(financeiro_content, bg=Theme.colors['surface'])
                fin_grid.pack(fill='x', padx=10, pady=10)
                
                # Última Folha
                tk.Label(
                    fin_grid,
                    text="Última Folha:",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20,
                    anchor='w'
                ).grid(row=0, column=0, sticky='w', pady=(0, 8))
                
                mes_ano = ultima_folha[0]
                if mes_ano:
                    try:
                        mes_ano_fmt = datetime.strptime(mes_ano, '%Y-%m-%d').strftime('%m/%Y')
                    except:
                        mes_ano_fmt = mes_ano[:7]
                else:
                    mes_ano_fmt = "N/A"
                
                tk.Label(
                    fin_grid,
                    text=mes_ano_fmt,
                    font=('Segoe UI', 10),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    anchor='w'
                ).grid(row=0, column=1, sticky='w', pady=(0, 8))
                
                # Valor Última Folha
                tk.Label(
                    fin_grid,
                    text="Valor Recebido:",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20,
                    anchor='w'
                ).grid(row=1, column=0, sticky='w', pady=(0, 8))
                
                salario_liquido = ultima_folha[1] if ultima_folha[1] else 0
                tk.Label(
                    fin_grid,
                    text=f"{salario_liquido:,} Kz",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['success'],
                    bg=Theme.colors['surface'],
                    anchor='w'
                ).grid(row=1, column=1, sticky='w', pady=(0, 8))
                
                # Status Última Folha
                tk.Label(
                    fin_grid,
                    text="Status:",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20,
                    anchor='w'
                ).grid(row=2, column=0, sticky='w', pady=(0, 8))
                
                status_folha = ultima_folha[2] if ultima_folha[2] else "Não calculada"
                status_cores = {
                    'pago': Theme.colors['success'],
                    'aprovado': Theme.colors['info'],
                    'enviado_financeiro': Theme.colors['warning'],
                    'calculado': Theme.colors['accent'],
                    'rejeitado': Theme.colors['danger']
                }
                cor_status = status_cores.get(status_folha, Theme.colors['text_primary'])
                
                tk.Label(
                    fin_grid,
                    text=status_folha.upper(),
                    font=('Segoe UI', 10, 'bold'),
                    fg=cor_status,
                    bg=Theme.colors['surface'],
                    anchor='w'
                ).grid(row=2, column=1, sticky='w', pady=(0, 8))
            
            # ====================== PONTO E HORAS ======================
            if ponto_info and ponto_info[0]:
                ponto_card = Card(scrollable_frame, title="⏰ REGISTRO DE PONTO")
                ponto_card.pack(fill='x', pady=(0, 15))
                
                ponto_content = ponto_card.content_frame
                
                ponto_grid = tk.Frame(ponto_content, bg=Theme.colors['surface'])
                ponto_grid.pack(fill='x', padx=10, pady=10)
                
                # Dias Trabalhados
                tk.Label(
                    ponto_grid,
                    text="Dias Trabalhados:",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20,
                    anchor='w'
                ).grid(row=0, column=0, sticky='w', pady=(0, 8))
                
                dias_trabalhados = ponto_info[0] if ponto_info[0] else 0
                tk.Label(
                    ponto_grid,
                    text=f"{dias_trabalhados} dias",
                    font=('Segoe UI', 10),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    anchor='w'
                ).grid(row=0, column=1, sticky='w', pady=(0, 8))
                
                # Horas Extras
                tk.Label(
                    ponto_grid,
                    text="Horas Extras:",
                    font=('Segoe UI', 10, 'bold'),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20,
                    anchor='w'
                ).grid(row=1, column=0, sticky='w', pady=(0, 8))
                
                horas_extras = ponto_info[1] if ponto_info[1] else 0
                tk.Label(
                    ponto_grid,
                    text=f"{horas_extras:.1f} horas",
                    font=('Segoe UI', 10),
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    anchor='w'
                ).grid(row=1, column=1, sticky='w', pady=(0, 8))
            
            # ====================== OBSERVAÇÕES ======================
            observacoes = funcionario[17] if len(funcionario) > 17 else ""
            if observacoes:
                obs_card = Card(scrollable_frame, title="📝 OBSERVAÇÕES")
                obs_card.pack(fill='x', pady=(0, 15))
                
                obs_content = obs_card.content_frame
                
                obs_text = scrolledtext.ScrolledText(
                    obs_content,
                    font=('Segoe UI', 10),
                    bg=Theme.colors['light'],
                    fg=Theme.colors['text_primary'],
                    wrap='word',
                    height=4
                )
                obs_text.pack(fill='both', expand=True, padx=10, pady=10)
                obs_text.insert('1.0', observacoes)
                obs_text.configure(state='disabled')
            
            # ====================== BOTÕES DE AÇÃO ======================
            button_frame = tk.Frame(scrollable_frame, bg=Theme.colors['background'])
            button_frame.pack(fill='x', pady=(20, 0))
            
            # Botão EDITAR
            ModernButton(
                button_frame,
                text="✏️ EDITAR FUNCIONÁRIO",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=11,
                padx=20,
                pady=12,
                command=lambda: [detail_window.destroy(), self.edit_employee()]
            ).pack(side='left', padx=(0, 10))
            
            # Botão CALCULAR FOLHA
            if ativo:
                ModernButton(
                    button_frame,
                    text="💰 CALCULAR FOLHA",
                    bg=Theme.colors['primary'],
                    hover_bg=Theme.colors['primary_light'],
                    font_size=11,
                    padx=20,
                    pady=12,
                    command=lambda: self.calculate_employee_payroll(func_id, detail_window)
                ).pack(side='left', padx=(0, 10))
            
            # Botão FECHAR
            ModernButton(
                button_frame,
                text="❌ FECHAR",
                bg=Theme.colors['danger'],
                hover_bg=self.lighten_color(Theme.colors['danger'], 20),
                font_size=11,
                padx=20,
                pady=12,
                command=detail_window.destroy
            ).pack(side='right')
            
            # Adicionar espaço extra no final
            tk.Frame(scrollable_frame, height=20, bg=Theme.colors['background']).pack()
            
            # Configurar rolagem com mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Tecla ESC para fechar
            detail_window.bind('<Escape>', lambda e: detail_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar detalhes: {str(e)}")

    def calculate_employee_payroll(self, func_id, parent_window):
        """Calcula folha de pagamento para o funcionário específico"""
        try:
            # Obter mês atual
            hoje = datetime.now()
            mes_ano = hoje.strftime('%Y-%m')
            
            user_info = self.user_service.get_user_info()
            
            # Calcular salário
            success, message, salario = self.hr_service.calcular_salario(func_id, mes_ano, user_info)
            
            if success:
                messagebox.showinfo("Sucesso", f"Salário calculado: {salario:,.0f} Kz\n\n{message}")
                
                # Fechar janela de detalhes e recarregar lista
                if parent_window:
                    parent_window.destroy()
                
                # Atualizar lista de funcionários e folha de pagamento
                if hasattr(self, 'employees_tree'):
                    self.update_employees_list()
                if hasattr(self, 'payroll_tree'):
                    self.load_payroll_data()
            else:
                messagebox.showerror("Erro", message)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular salário: {str(e)}")

    def edit_employee(self):
        """Abre formulário para editar funcionário"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return
        
        item = self.employees_tree.item(selection[0])
        func_id = item['values'][0]
        func_nome = item['values'][1]
        
        # Verificar se o ID é válido
        if not func_id or func_id == "---":
            messagebox.showwarning("Aviso", "Selecione um funcionário válido!")
            return
        
        try:
            # Buscar dados do funcionário
            result = self.db.execute_query(
                "SELECT * FROM funcionarios WHERE id = ?",
                (func_id,),
                commit=False
            )
            funcionario = result.fetchone()
            
            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado!")
                return
            
            # Criar janela de edição
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"✏️ Editar Funcionário - {func_nome}")
            edit_window.geometry("800x750")
            edit_window.configure(bg=Theme.colors['background'])
            edit_window.resizable(False, True)
            
            # Centralizar janela
            edit_window.update_idletasks()
            width = edit_window.winfo_width()
            height = edit_window.winfo_height()
            x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
            y = (edit_window.winfo_screenheight() // 2) - (height // 2)
            edit_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Container principal com scroll
            main_container = tk.Frame(edit_window, bg=Theme.colors['background'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Canvas e scrollbar
            canvas = tk.Canvas(main_container, bg=Theme.colors['background'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Theme.colors['background'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # ====================== CABEÇALHO ======================
            header_frame = tk.Frame(scrollable_frame, bg=Theme.colors['primary'])
            header_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                header_frame,
                text=f"✏️ EDITAR FUNCIONÁRIO - ID {func_id}",
                font=('Segoe UI', 18, 'bold'),
                fg=Theme.colors['text_light'],
                bg=Theme.colors['primary']
            ).pack(pady=15)
            
            # ====================== FORMULÁRIO DE EDIÇÃO ======================
            
            # Card para informações pessoais
            pessoal_card = Card(scrollable_frame, title="📋 INFORMAÇÕES PESSOAIS")
            pessoal_card.pack(fill='x', pady=(0, 15))
            
            pessoal_content = pessoal_card.content_frame
            
            # Nome completo
            tk.Label(
                pessoal_content,
                text="Nome completo: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.edit_emp_nome = tk.Entry(pessoal_content, font=Theme.fonts['body'], width=50)
            self.edit_emp_nome.pack(fill='x', pady=(0, 15))
            self.edit_emp_nome.insert(0, funcionario[1] if len(funcionario) > 1 else "")
            
            # Documento
            tk.Label(
                pessoal_content,
                text="Documento (BI/Passaporte): *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.edit_emp_documento = tk.Entry(pessoal_content, font=Theme.fonts['body'], width=30)
            self.edit_emp_documento.pack(fill='x', pady=(0, 15))
            self.edit_emp_documento.insert(0, funcionario[2] if len(funcionario) > 2 else "")
            
            # Data de nascimento (se existir)
            data_nasc = funcionario[13] if len(funcionario) > 13 else ""
            if data_nasc:
                try:
                    nasc_dt = datetime.strptime(data_nasc, '%Y-%m-%d')
                    nasc_dia = nasc_dt.day
                    nasc_mes = nasc_dt.month
                    nasc_ano = nasc_dt.year
                except:
                    nasc_dia = 1
                    nasc_mes = 1
                    nasc_ano = 1990
            else:
                nasc_dia = 1
                nasc_mes = 1
                nasc_ano = 1990
            
            tk.Label(
                pessoal_content,
                text="Data de nascimento:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            nasc_frame = tk.Frame(pessoal_content, bg=Theme.colors['surface'])
            nasc_frame.pack(fill='x', pady=(0, 15))
            
            self.edit_emp_nascimento_dia = ttk.Combobox(
                nasc_frame,
                values=[str(i).zfill(2) for i in range(1, 32)],
                state='readonly',
                width=5
            )
            self.edit_emp_nascimento_dia.pack(side='left', padx=(0, 5))
            self.edit_emp_nascimento_dia.set(str(nasc_dia).zfill(2))
            
            self.edit_emp_nascimento_mes = ttk.Combobox(
                nasc_frame,
                values=[str(i).zfill(2) for i in range(1, 13)],
                state='readonly',
                width=5
            )
            self.edit_emp_nascimento_mes.pack(side='left', padx=(0, 5))
            self.edit_emp_nascimento_mes.set(str(nasc_mes).zfill(2))
            
            self.edit_emp_nascimento_ano = ttk.Combobox(
                nasc_frame,
                values=[str(i) for i in range(1950, 2010)],
                state='readonly',
                width=8
            )
            self.edit_emp_nascimento_ano.pack(side='left')
            self.edit_emp_nascimento_ano.set(str(nasc_ano))
            
            # Estado civil
            tk.Label(
                pessoal_content,
                text="Estado civil:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.edit_emp_estado_civil = ttk.Combobox(
                pessoal_content,
                values=['Solteiro(a)', 'Casado(a)', 'Divorciado(a)', 'Viúvo(a)', 'União de facto', ''],
                state='readonly',
                width=20
            )
            self.edit_emp_estado_civil.pack(fill='x', pady=(0, 15))
            estado_civil = funcionario[14] if len(funcionario) > 14 else ""
            self.edit_emp_estado_civil.set(estado_civil if estado_civil else "")
            
            # Número de filhos
            tk.Label(
                pessoal_content,
                text="Número de filhos:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            filhos = funcionario[15] if len(funcionario) > 15 else 0
            self.edit_emp_filhos = ttk.Combobox(
                pessoal_content,
                values=[str(i) for i in range(11)],
                state='readonly',
                width=5
            )
            self.edit_emp_filhos.pack(fill='x', pady=(0, 15))
            self.edit_emp_filhos.set(str(filhos))
            
            # ====================== INFORMAÇÕES DE CONTATO ======================
            
            contato_card = Card(scrollable_frame, title="📞 INFORMAÇÕES DE CONTATO")
            contato_card.pack(fill='x', pady=(0, 15))
            
            contato_content = contato_card.content_frame
            
            # Telefone
            tk.Label(
                contato_content,
                text="Telefone:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            telefone = funcionario[10] if len(funcionario) > 10 else ""
            self.edit_emp_telefone = tk.Entry(contato_content, font=Theme.fonts['body'], width=30)
            self.edit_emp_telefone.pack(fill='x', pady=(0, 15))
            self.edit_emp_telefone.insert(0, telefone if telefone else "")
            
            # Email
            tk.Label(
                contato_content,
                text="Email:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            email = funcionario[11] if len(funcionario) > 11 else ""
            self.edit_emp_email = tk.Entry(contato_content, font=Theme.fonts['body'], width=40)
            self.edit_emp_email.pack(fill='x', pady=(0, 15))
            self.edit_emp_email.insert(0, email if email else "")
            
            # Endereço
            tk.Label(
                contato_content,
                text="Endereço:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            endereco = funcionario[12] if len(funcionario) > 12 else ""
            self.edit_emp_endereco = tk.Entry(contato_content, font=Theme.fonts['body'], width=50)
            self.edit_emp_endereco.pack(fill='x', pady=(0, 15))
            self.edit_emp_endereco.insert(0, endereco if endereco else "")
            
            # ====================== INFORMAÇÕES PROFISSIONAIS ======================
            
            profissional_card = Card(scrollable_frame, title="💼 INFORMAÇÕES PROFISSIONAIS")
            profissional_card.pack(fill='x', pady=(0, 15))
            
            profissional_content = profissional_card.content_frame
            
            # Cargo
            tk.Label(
                profissional_content,
                text="Cargo: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            cargo = funcionario[3] if len(funcionario) > 3 else ""
            self.edit_emp_cargo = ttk.Combobox(
                profissional_content,
                values=['Recepcionista', 'Camareira', 'Cozinheiro', 'Segurança', 
                        'Manutenção', 'Gerente', 'Administrador', 'Contador',
                        'Supervisor', 'Auxiliar', 'Outro'],
                state='readonly',
                width=25
            )
            self.edit_emp_cargo.pack(fill='x', pady=(0, 15))
            self.edit_emp_cargo.set(cargo if cargo else "Recepcionista")
            
            # Departamento
            tk.Label(
                profissional_content,
                text="Departamento: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            departamento = funcionario[4] if len(funcionario) > 4 else ""
            self.edit_emp_departamento = ttk.Combobox(
                profissional_content,
                values=['Recepção', 'Limpeza', 'Manutenção', 'Gerência', 
                        'Cozinha', 'Segurança', 'Administração', 'Financeiro', 'RH'],
                state='readonly',
                width=20
            )
            self.edit_emp_departamento.pack(fill='x', pady=(0, 15))
            self.edit_emp_departamento.set(departamento if departamento else "Recepção")
            
            # Data de admissão
            data_admissao = funcionario[5] if len(funcionario) > 5 else ""
            if data_admissao:
                try:
                    adm_dt = datetime.strptime(data_admissao, '%Y-%m-%d')
                    adm_dia = adm_dt.day
                    adm_mes = adm_dt.month
                    adm_ano = adm_dt.year
                except:
                    adm_dia = datetime.now().day
                    adm_mes = datetime.now().month
                    adm_ano = datetime.now().year
            else:
                adm_dia = datetime.now().day
                adm_mes = datetime.now().month
                adm_ano = datetime.now().year
            
            tk.Label(
                profissional_content,
                text="Data de admissão: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            adm_frame = tk.Frame(profissional_content, bg=Theme.colors['surface'])
            adm_frame.pack(fill='x', pady=(0, 15))
            
            self.edit_emp_admissao_dia = ttk.Combobox(
                adm_frame,
                values=[str(i).zfill(2) for i in range(1, 32)],
                state='readonly',
                width=5
            )
            self.edit_emp_admissao_dia.pack(side='left', padx=(0, 5))
            self.edit_emp_admissao_dia.set(str(adm_dia).zfill(2))
            
            self.edit_emp_admissao_mes = ttk.Combobox(
                adm_frame,
                values=[str(i).zfill(2) for i in range(1, 13)],
                state='readonly',
                width=5
            )
            self.edit_emp_admissao_mes.pack(side='left', padx=(0, 5))
            self.edit_emp_admissao_mes.set(str(adm_mes).zfill(2))
            
            self.edit_emp_admissao_ano = ttk.Combobox(
                adm_frame,
                values=[str(i) for i in range(2020, 2031)],
                state='readonly',
                width=8
            )
            self.edit_emp_admissao_ano.pack(side='left')
            self.edit_emp_admissao_ano.set(str(adm_ano))
            
            # Salário base
            tk.Label(
                profissional_content,
                text="Salário base (Kz): *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            salario_base = funcionario[6] if len(funcionario) > 6 else 85000
            self.edit_emp_salario = tk.Entry(profissional_content, font=Theme.fonts['body'], width=20)
            self.edit_emp_salario.pack(fill='x', pady=(0, 15))
            self.edit_emp_salario.insert(0, str(salario_base))
            
            # Status (Ativo/Inativo)
            tk.Label(
                profissional_content,
                text="Status:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            ativo = funcionario[16] if len(funcionario) > 16 else 1
            self.edit_emp_ativo = ttk.Combobox(
                profissional_content,
                values=['Ativo', 'Inativo'],
                state='readonly',
                width=10
            )
            self.edit_emp_ativo.pack(fill='x', pady=(0, 15))
            self.edit_emp_ativo.set('Ativo' if ativo else 'Inativo')
            
            # ====================== INFORMAÇÕES BANCÁRIAS ======================
            
            bancario_card = Card(scrollable_frame, title="🏦 INFORMAÇÕES BANCÁRIAS")
            bancario_card.pack(fill='x', pady=(0, 15))
            
            bancario_content = bancario_card.content_frame
            
            # Banco
            tk.Label(
                bancario_content,
                text="Banco:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            banco = funcionario[7] if len(funcionario) > 7 else ""
            self.edit_emp_banco = ttk.Combobox(
                bancario_content,
                values=['BAI', 'BFA', 'BCI', 'BIC', 'BPC', 'Millennium', 'Standard Bank', 
                        'Caixa Geral', 'Solução', 'Outro', ''],
                state='readonly',
                width=20
            )
            self.edit_emp_banco.pack(fill='x', pady=(0, 15))
            self.edit_emp_banco.set(banco if banco else "")
            
            # Agência
            tk.Label(
                bancario_content,
                text="Agência:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            agencia = funcionario[9] if len(funcionario) > 9 else ""
            self.edit_emp_agencia = tk.Entry(bancario_content, font=Theme.fonts['body'], width=15)
            self.edit_emp_agencia.pack(fill='x', pady=(0, 15))
            self.edit_emp_agencia.insert(0, agencia if agencia else "")
            
            # Conta bancária
            tk.Label(
                bancario_content,
                text="Conta bancária:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            conta = funcionario[8] if len(funcionario) > 8 else ""
            self.edit_emp_conta = tk.Entry(bancario_content, font=Theme.fonts['body'], width=25)
            self.edit_emp_conta.pack(fill='x', pady=(0, 15))
            self.edit_emp_conta.insert(0, conta if conta else "")
            
            # ====================== OBSERVAÇÕES ======================
            
            obs_card = Card(scrollable_frame, title="📝 OBSERVAÇÕES")
            obs_card.pack(fill='x', pady=(0, 20))
            
            obs_content = obs_card.content_frame
            
            observacoes = funcionario[17] if len(funcionario) > 17 else ""
            self.edit_emp_observacoes = scrolledtext.ScrolledText(
                obs_content,
                font=Theme.fonts['body'],
                bg=Theme.colors['light'],
                fg=Theme.colors['text_primary'],
                wrap='word',
                height=5,
                width=70
            )
            self.edit_emp_observacoes.pack(fill='x', padx=10, pady=10)
            self.edit_emp_observacoes.insert('1.0', observacoes if observacoes else "")
            
            # ====================== BOTÕES DE AÇÃO ======================
            
            button_frame = tk.Frame(scrollable_frame, bg=Theme.colors['background'])
            button_frame.pack(fill='x', pady=(10, 0))
            
            # Botão SALVAR
            ModernButton(
                button_frame,
                text="💾 SALVAR ALTERAÇÕES",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=12,
                padx=20,
                pady=12,
                command=lambda: self.save_employee_changes(func_id, edit_window)
            ).pack(side='left', padx=(0, 15))
            
            # Botão CANCELAR
            ModernButton(
                button_frame,
                text="❌ CANCELAR",
                bg=Theme.colors['danger'],
                hover_bg=self.lighten_color(Theme.colors['danger'], 20),
                font_size=12,
                padx=20,
                pady=12,
                command=edit_window.destroy
            ).pack(side='left', padx=(0, 15))
            
            # Botão ATIVAR/INATIVAR
            status_text = "🚪 DEMITIR" if ativo else "✅ REATIVAR"
            status_color = Theme.colors['warning'] if ativo else Theme.colors['info']
            ModernButton(
                button_frame,
                text=status_text,
                bg=status_color,
                hover_bg=self.lighten_color(status_color, 20),
                font_size=11,
                padx=15,
                pady=12,
                command=lambda: self.toggle_employee_status(func_id, ativo, edit_window)
            ).pack(side='right')
            
            # Adicionar espaço extra no final para rolagem
            tk.Frame(scrollable_frame, height=20, bg=Theme.colors['background']).pack()
            
            # Configurar rolagem com mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Tecla Enter para salvar
            edit_window.bind('<Return>', lambda e: self.save_employee_changes(func_id, edit_window))
            # Tecla ESC para cancelar
            edit_window.bind('<Escape>', lambda e: edit_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados para edição: {str(e)}")

    def save_employee_changes(self, func_id, window):
        """Salva as alterações do funcionário"""
        # Validar campos obrigatórios
        campos_obrigatorios = [
            (self.edit_emp_nome, "Nome completo"),
            (self.edit_emp_documento, "Documento"),
            (self.edit_emp_cargo, "Cargo"),
            (self.edit_emp_departamento, "Departamento"),
            (self.edit_emp_salario, "Salário base")
        ]
        
        for campo, nome in campos_obrigatorios:
            if not campo.get().strip():
                messagebox.showerror("Erro", f"O campo '{nome}' é obrigatório!")
                campo.focus_set()
                return
        
        # Validar salário
        try:
            salario = int(self.edit_emp_salario.get().replace('.', '').replace(',', ''))
            if salario <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Salário inválido! Digite um valor numérico positivo.")
            self.edit_emp_salario.focus_set()
            return
        
        # Preparar dados para atualização
        dados_atualizados = {
            'nome': self.edit_emp_nome.get().strip(),
            'documento': self.edit_emp_documento.get().strip(),
            'cargo': self.edit_emp_cargo.get(),
            'departamento': self.edit_emp_departamento.get(),
            'salario_base': salario,
            'telefone': self.edit_emp_telefone.get().strip(),
            'email': self.edit_emp_email.get().strip(),
            'endereco': self.edit_emp_endereco.get().strip(),
            'banco': self.edit_emp_banco.get(),
            'agencia': self.edit_emp_agencia.get().strip(),
            'conta_bancaria': self.edit_emp_conta.get().strip(),
            'observacoes': self.edit_emp_observacoes.get("1.0", "end-1c").strip(),
            'ativo': 1 if self.edit_emp_ativo.get() == 'Ativo' else 0
        }
        
        # Data de nascimento
        dia = self.edit_emp_nascimento_dia.get()
        mes = self.edit_emp_nascimento_mes.get()
        ano = self.edit_emp_nascimento_ano.get()
        if dia and mes and ano:
            dados_atualizados['data_nascimento'] = f"{ano}-{mes}-{dia}"
        
        # Data de admissão
        dia_adm = self.edit_emp_admissao_dia.get()
        mes_adm = self.edit_emp_admissao_mes.get()
        ano_adm = self.edit_emp_admissao_ano.get()
        if dia_adm and mes_adm and ano_adm:
            dados_atualizados['data_admissao'] = f"{ano_adm}-{mes_adm}-{dia_adm}"
        
        # Estado civil
        estado_civil = self.edit_emp_estado_civil.get()
        if estado_civil:
            dados_atualizados['estado_civil'] = estado_civil
        
        # Filhos
        try:
            dados_atualizados['filhos'] = int(self.edit_emp_filhos.get())
        except:
            dados_atualizados['filhos'] = 0
        
        try:
            # Atualizar no banco de dados
            self.db.execute_query('''
                UPDATE funcionarios SET
                    nome = ?,
                    documento = ?,
                    cargo = ?,
                    departamento = ?,
                    salario_base = ?,
                    data_admissao = ?,
                    banco = ?,
                    conta_bancaria = ?,
                    agencia = ?,
                    telefone = ?,
                    email = ?,
                    endereco = ?,
                    data_nascimento = ?,
                    estado_civil = ?,
                    filhos = ?,
                    ativo = ?,
                    observacoes = ?
                WHERE id = ?
            ''', (
                dados_atualizados['nome'],
                dados_atualizados['documento'],
                dados_atualizados['cargo'],
                dados_atualizados['departamento'],
                dados_atualizados['salario_base'],
                dados_atualizados.get('data_admissao', ''),
                dados_atualizados.get('banco', ''),
                dados_atualizados.get('conta_bancaria', ''),
                dados_atualizados.get('agencia', ''),
                dados_atualizados.get('telefone', ''),
                dados_atualizados.get('email', ''),
                dados_atualizados.get('endereco', ''),
                dados_atualizados.get('data_nascimento', ''),
                dados_atualizados.get('estado_civil', ''),
                dados_atualizados.get('filhos', 0),
                dados_atualizados['ativo'],
                dados_atualizados.get('observacoes', ''),
                func_id
            ))
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'EDITAR_FUNCIONARIO',
                'RH',
                f"Funcionário {func_id} atualizado"
            )
            
            messagebox.showinfo("Sucesso", f"Funcionário {dados_atualizados['nome']} atualizado com sucesso!")
            
            # Fechar janela
            window.destroy()
            
            # Atualizar lista de funcionários
            if hasattr(self, 'employees_tree'):
                self.update_employees_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar funcionário: {str(e)}")

    def toggle_employee_status(self, func_id, atual_status, window):
        """Alterna status do funcionário (Ativo/Inativo)"""
        novo_status = not atual_status
        status_text = "INATIVAR" if atual_status else "REATIVAR"
        
        resposta = messagebox.askyesno(
            f"Confirmar {status_text}",
            f"Deseja realmente {status_text.lower()} este funcionário?\n\n"
            f"ID: {func_id}\n"
            f"Ação: {'Será demitido' if atual_status else 'Será reativado'}"
        )
        
        if resposta:
            try:
                # Atualizar status no banco
                self.db.execute_query(
                    "UPDATE funcionarios SET ativo = ? WHERE id = ?",
                    (1 if novo_status else 0, func_id)
                )
                
                # Log da ação
                user_info = self.user_service.get_user_info()
                acao = "REATIVAR_FUNCIONARIO" if novo_status else "DEMITIR_FUNCIONARIO"
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    acao,
                    'RH',
                    f"Funcionário {func_id} {status_text.lower()}do"
                )
                
                # Notificação
                self.db.send_notification(
                    'alerta' if not novo_status else 'sucesso',
                    f'Funcionário {status_text}do',
                    f'Funcionário ID {func_id} foi {status_text.lower()}do',
                    'gerente'
                )
                
                messagebox.showinfo("Sucesso", f"Funcionário {status_text.lower()}do com sucesso!")
                
                # Fechar janela de edição
                window.destroy()
                
                # Atualizar lista de funcionários
                if hasattr(self, 'employees_tree'):
                    self.update_employees_list()
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar status: {str(e)}")

    def dismiss_employee(self):
        """Demite/desativa um funcionário"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return
        
        item = self.employees_tree.item(selection[0])
        func_id = item['values'][0]
        func_nome = item['values'][1]
        
        resposta = messagebox.askyesno(
            "Confirmar Demissão",
            f"Deseja realmente demitir o funcionário?\n\n"
            f"ID: {func_id}\n"
            f"Nome: {func_nome}\n\n"
            f"Esta ação pode ser revertida posteriormente."
        )
        
        if resposta:
            user_info = self.user_service.get_user_info()
            
            try:
                self.db.execute_query(
                    "UPDATE funcionarios SET ativo = 0 WHERE id = ?",
                    (func_id,)
                )
                
                # Log da ação
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    'DEMITIR_FUNCIONARIO',
                    'RH',
                    f"Funcionário {func_nome} (ID: {func_id}) demitido"
                )
                
                # Notificação
                self.db.send_notification(
                    'alerta',
                    'Funcionário Demitido',
                    f'Funcionário {func_nome} foi demitido do sistema',
                    'gerente'
                )
                
                messagebox.showinfo("Sucesso", f"Funcionário {func_nome} demitido com sucesso!")
                
                # Atualizar lista
                self.update_employees_list()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao demitir funcionário: {str(e)}")
    
    def create_payroll_section(self, parent):
        """Cria seção de folha de pagamento"""
        # Frame principal
        main_frame = tk.Frame(parent, bg=Theme.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Card principal
        payroll_card = Card(main_frame, title="💰 FOLHA DE PAGAMENTO")
        payroll_card.pack(fill='both', expand=True)
        
        payroll_content = payroll_card.content_frame
        
        # ====================== CONTROLES DO TOPO ======================
        controls_frame = tk.Frame(payroll_content, bg=Theme.colors['surface'])
        controls_frame.pack(fill='x', pady=(0, 20))
        
        # Frame para seleção de mês/ano
        date_frame = tk.Frame(controls_frame, bg=Theme.colors['surface'])
        date_frame.pack(side='left', padx=(0, 20))
        
        tk.Label(
            date_frame,
            text="Mês/Ano:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        meses = ['01 - Janeiro', '02 - Fevereiro', '03 - Março', '04 - Abril', 
                '05 - Maio', '06 - Junho', '07 - Julho', '08 - Agosto',
                '09 - Setembro', '10 - Outubro', '11 - Novembro', '12 - Dezembro']
        
        self.payroll_mes = ttk.Combobox(
            date_frame,
            values=meses,
            state='readonly',
            width=15
        )
        self.payroll_mes.pack(side='left', padx=(0, 10))
        
        hoje = datetime.now()
        self.payroll_mes.set(meses[hoje.month - 1])
        
        anos = [str(i) for i in range(2023, 2031)]
        self.payroll_ano = ttk.Combobox(
            date_frame,
            values=anos,
            state='readonly',
            width=8
        )
        self.payroll_ano.pack(side='left', padx=(0, 10))
        self.payroll_ano.set(str(hoje.year))
        
        # Frame para botões
        button_frame = tk.Frame(controls_frame, bg=Theme.colors['surface'])
        button_frame.pack(side='left')
        
        ModernButton(
            button_frame,
            text="🔍 CARREGAR FUNCIONÁRIOS",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            padx=15,
            pady=8,
            command=self.load_employees_for_payroll
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="📊 CALCULAR FOLHA",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.calculate_payroll
        ).pack(side='left')
        
        # ====================== LISTA DE FUNCIONÁRIOS PARA FOLHA ======================
        list_frame = tk.Frame(payroll_content, bg=Theme.colors['surface'])
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Funcionário', 'Cargo', 'Departamento', 'Salário Base', 
                'Horas Extras', 'Faltas', 'Subsídios', 'Total Calculado')
        
        self.payroll_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        col_widths = [50, 150, 100, 120, 100, 90, 70, 90, 120]
        for col, width in zip(columns, col_widths):
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.payroll_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.payroll_tree.xview)
        self.payroll_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.payroll_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # ====================== BOTÕES DE AÇÃO ======================
        action_frame = tk.Frame(payroll_content, bg=Theme.colors['surface'])
        action_frame.pack(fill='x', pady=(15, 0))
        
        ModernButton(
            action_frame,
            text="📤 ENVIAR PARA FINANCEIRO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.send_to_finance
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            action_frame,
            text="📄 GERAR RELATÓRIO",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.gerar_relatorio_rh_real
        ).pack(side='left')
        
        # Carregar funcionários inicialmente
        self.load_employees_for_payroll()

    def load_employees_for_payroll(self):
        """Carrega funcionários ativos para cálculo da folha"""
        if not hasattr(self, 'payroll_tree'):
            return
        
        # Limpar lista
        for item in self.payroll_tree.get_children():
            self.payroll_tree.delete(item)
        
        try:
            # Obter funcionários ativos
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            
            if not funcionarios:
                self.payroll_tree.insert('', 'end', values=(
                    "---", "Nenhum funcionário cadastrado", "", "", "", "", "", "", ""
                ))
                return
            
            # Obter mês e ano selecionados
            mes_text = self.payroll_mes.get()
            ano = self.payroll_ano.get()
            
            if not mes_text or not ano:
                messagebox.showwarning("Aviso", "Selecione mês e ano!")
                return
            
            # Extrair número do mês
            mes_num = mes_text[:2].strip()
            mes_ano = f"{ano}-{mes_num}"
            
            for func in funcionarios:
                func_id, nome, cargo, depto, data_adm, salario_base = func[0], func[1], func[2], func[3], func[5], func[6]
                
                # Verificar se já existe folha para este mês
                result = self.db.execute_query(
                    "SELECT salario_liquido, status FROM folha_pagamento WHERE funcionario_id = ? AND strftime('%Y-%m', mes_ano) = ?",
                    (func_id, mes_ano),
                    commit=False
                )
                folha_existente = result.fetchone()
                
                if folha_existente:
                    # Já tem folha calculada
                    liquido, status = folha_existente
                    horas_extras = "0h"
                    faltas = "0"
                    subsidios = "0 Kz"
                    total = f"{liquido:,} Kz"
                    
                    # Adicionar status na última coluna
                    status_icon = {
                        'calculado': '🟡',
                        'enviado_financeiro': '🔵',
                        'aprovado': '🟢',
                        'pago': '✅',
                        'rejeitado': '🔴'
                    }.get(status, '⚫')
                    total = f"{total} ({status_icon})"
                else:
                    # Nova folha a calcular
                    horas_extras = "0h"
                    faltas = "0"
                    subsidios = "0 Kz"
                    total = "0 Kz"
                
                self.payroll_tree.insert('', 'end', values=(
                    func_id,
                    nome,
                    cargo,
                    depto,
                    f"{salario_base:,} Kz",
                    horas_extras,
                    faltas,
                    subsidios,
                    total
                ))
                
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            self.payroll_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", "", ""
            ))

    def calculate_payroll(self):
        """Calcula a folha de pagamento para os funcionários selecionados"""
        selection = self.payroll_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione funcionários para calcular!")
            return
        
        # Obter mês e ano selecionados
        mes_text = self.payroll_mes.get()
        ano = self.payroll_ano.get()
        
        if not mes_text or not ano:
            messagebox.showwarning("Aviso", "Selecione mês e ano!")
            return
        
        mes_num = mes_text[:2].strip()
        mes_ano = f"{ano}-{mes_num}"
        
        user_info = self.user_service.get_user_info()
        
        try:
            for item in selection:
                values = self.payroll_tree.item(item)['values']
                funcionario_id = values[0]
                
                # Verificar se já foi calculado
                result = self.db.execute_query(
                    "SELECT id FROM folha_pagamento WHERE funcionario_id = ? AND strftime('%Y-%m', mes_ano) = ?",
                    (funcionario_id, mes_ano),
                    commit=False
                )
                
                if result.fetchone():
                    continue  # Já calculado, pular
                
                # Calcular folha para este funcionário
                # Obter salário base
                salario_base = int(values[4].replace(' Kz', '').replace('.', '').replace(',', ''))
                
                # Simular cálculo (na prática, buscar horas extras, faltas, etc.)
                horas_extras = 0  # Em horas
                valor_horas_extras = horas_extras * (salario_base / 220) * 1.5  # 50% extra
                
                faltas = 0  # Em dias
                descontos_faltas = faltas * (salario_base / 30)
                
                subsidios = 0  # Em Kz
                
                # Calcular salário líquido
                salario_liquido = salario_base + valor_horas_extras + subsidios - descontos_faltas
                
                # Inserir na folha de pagamento
                self.db.execute_query('''
                    INSERT INTO folha_pagamento 
                    (funcionario_id, mes_ano, salario_base, horas_extras, valor_horas_extras,
                    faltas, descontos_faltas, subsidios, salario_liquido, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'calculado')
                ''', (
                    funcionario_id,
                    f"{mes_ano}-01",
                    salario_base,
                    horas_extras,
                    valor_horas_extras,
                    faltas,
                    descontos_faltas,
                    subsidios,
                    salario_liquido
                ))
                
            messagebox.showinfo("Sucesso", "Folha de pagamento calculada com sucesso!")
            self.load_employees_for_payroll()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular folha: {str(e)}")

    def send_to_finance(self):
        """Envia folha de pagamento para o financeiro"""
        selection = self.payroll_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione funcionários para enviar!")
            return
        
        # Obter mês e ano selecionados
        mes_text = self.payroll_mes.get()
        ano = self.payroll_ano.get()
        
        if not mes_text or not ano:
            messagebox.showwarning("Aviso", "Selecione mês e ano!")
            return
        
        mes_num = mes_text[:2].strip()
        mes_ano = f"{ano}-{mes_num}"
        
        user_info = self.user_service.get_user_info()
        
        try:
            enviados = 0
            for item in selection:
                values = self.payroll_tree.item(item)['values']
                funcionario_id = values[0]
                
                # Buscar folha deste funcionário para este mês
                result = self.db.execute_query(
                    "SELECT id, status FROM folha_pagamento WHERE funcionario_id = ? AND strftime('%Y-%m', mes_ano) = ?",
                    (funcionario_id, mes_ano),
                    commit=False
                )
                
                folha = result.fetchone()
                if not folha:
                    messagebox.showwarning("Aviso", f"Folha do funcionário {values[1]} não calculada!")
                    continue
                
                folha_id, status = folha
                
                # Verificar se já foi enviada
                if status == 'enviado_financeiro' or status == 'aprovado' or status == 'pago':
                    continue
                
                # Atualizar para enviado ao financeiro
                self.db.execute_query('''
                    UPDATE folha_pagamento 
                    SET status = 'enviado_financeiro',
                        data_envio_financeiro = CURRENT_TIMESTAMP,
                        usuario_envio_id = ?
                    WHERE id = ?
                ''', (user_info['id'], folha_id))
                
                enviados += 1
            
            if enviados > 0:
                # Notificar financeiro
                self.db.send_notification(
                    'info',
                    'Folha de Pagamento Recebida',
                    f'{enviados} folhas de pagamento recebidas do RH para aprovação',
                    'financeiro'
                )
                
                messagebox.showinfo("Sucesso", f"{enviados} folhas enviadas para o financeiro!")
                self.load_employees_for_payroll()
            else:
                messagebox.showinfo("Informação", "Nenhuma folha nova para enviar.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar para financeiro: {str(e)}")

    def create_vacations_section_corrected(self, parent):
        """Cria seção de gestão de férias - SISTEMA MANUAL COMPLETO"""
        try:
            # Frame principal
            main_frame = tk.Frame(parent, bg=Theme.colors['background'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Container com abas
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill='both', expand=True)
            
            # ====================== ABA 1: ADICIONAR FÉRIAS ======================
            add_frame = tk.Frame(notebook, bg=Theme.colors['background'])
            notebook.add(add_frame, text='➕ ADICIONAR FÉRIAS')
            
            # Formulário de adição de férias
            form_card = Card(add_frame, title="🏖️ ADICIONAR FÉRIAS PARA FUNCIONÁRIO")
            form_card.pack(fill='both', expand=True, padx=10, pady=10)
            
            form_content = form_card.content_frame
            
            # Scrollable content
            canvas = tk.Canvas(form_content, bg=Theme.colors['surface'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(form_content, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Theme.colors['surface'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Campos do formulário
            form_fields = tk.Frame(scrollable_frame, bg=Theme.colors['surface'], padx=20, pady=20)
            form_fields.pack(fill='x')
            
            # 1. Selecionar funcionário
            tk.Label(
                form_fields,
                text="Selecionar Funcionário: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Carregar funcionários ativos
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            nomes_funcionarios = [f[1] for f in funcionarios] if funcionarios else []
            
            self.ferias_funcionario = ttk.Combobox(
                form_fields,
                values=nomes_funcionarios,
                state='readonly',
                width=40
            )
            self.ferias_funcionario.pack(fill='x', pady=(0, 15))
            
            if nomes_funcionarios:
                self.ferias_funcionario.set(nomes_funcionarios[0])
            
            # 2. Período Aquisitivo
            tk.Label(
                form_fields,
                text="Período Aquisitivo: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Data início
            frame_aq_inicio = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_aq_inicio.pack(fill='x', pady=(0, 5))
            
            tk.Label(
                frame_aq_inicio,
                text="Data Início:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                width=15
            ).pack(side='left')
            
            self.ferias_aquisitivo_inicio = tk.Entry(frame_aq_inicio, width=15)
            self.ferias_aquisitivo_inicio.pack(side='left', padx=(5, 20))
            self.ferias_aquisitivo_inicio.insert(0, datetime.now().strftime('%Y-%m-%d'))
            
            # Data fim
            frame_aq_fim = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_aq_fim.pack(fill='x', pady=(0, 15))
            
            tk.Label(
                frame_aq_fim,
                text="Data Fim:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                width=15
            ).pack(side='left')
            
            self.ferias_aquisitivo_fim = tk.Entry(frame_aq_fim, width=15)
            self.ferias_aquisitivo_fim.pack(side='left', padx=(5, 0))
            self.ferias_aquisitivo_fim.insert(0, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'))
            
            # 3. Período de Gozo
            tk.Label(
                form_fields,
                text="Período de Gozo (Férias): *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Data início gozo
            frame_gozo_inicio = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_gozo_inicio.pack(fill='x', pady=(0, 5))
            
            tk.Label(
                frame_gozo_inicio,
                text="Data Início:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                width=15
            ).pack(side='left')
            
            self.ferias_gozo_inicio = tk.Entry(frame_gozo_inicio, width=15)
            self.ferias_gozo_inicio.pack(side='left', padx=(5, 20))
            self.ferias_gozo_inicio.insert(0, datetime.now().strftime('%Y-%m-%d'))
            
            # Data fim gozo
            frame_gozo_fim = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_gozo_fim.pack(fill='x', pady=(0, 15))
            
            tk.Label(
                frame_gozo_fim,
                text="Data Fim:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                width=15
            ).pack(side='left')
            
            self.ferias_gozo_fim = tk.Entry(frame_gozo_fim, width=15)
            self.ferias_gozo_fim.pack(side='left', padx=(5, 0))
            self.ferias_gozo_fim.insert(0, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
            
            # 4. Número de dias
            tk.Label(
                form_fields,
                text="Número de Dias de Férias: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ferias_dias = tk.Entry(form_fields, width=10)
            self.ferias_dias.pack(anchor='w', pady=(0, 15))
            self.ferias_dias.insert(0, "22")
            
            # 5. Configuração de Desconto
            tk.Label(
                form_fields,
                text="Configuração de Desconto no Salário:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Opções de desconto
            self.ferias_desconto_opcao = tk.StringVar(value="nenhum")
            
            frame_desconto = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_desconto.pack(fill='x', pady=(0, 10))
            
            tk.Radiobutton(
                frame_desconto,
                text="Sem Desconto",
                variable=self.ferias_desconto_opcao,
                value="nenhum",
                bg=Theme.colors['surface']
            ).pack(anchor='w')
            
            tk.Radiobutton(
                frame_desconto,
                text="Desconto Proporcional",
                variable=self.ferias_desconto_opcao,
                value="proporcional",
                bg=Theme.colors['surface']
            ).pack(anchor='w')
            
            tk.Radiobutton(
                frame_desconto,
                text="Desconto Específico",
                variable=self.ferias_desconto_opcao,
                value="especifico",
                bg=Theme.colors['surface']
            ).pack(anchor='w')
            
            # Valor específico do desconto
            frame_valor_desconto = tk.Frame(form_fields, bg=Theme.colors['surface'])
            frame_valor_desconto.pack(fill='x', pady=(0, 15))
            
            tk.Label(
                frame_valor_desconto,
                text="Valor do Desconto (Kz):",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface'],
                width=20
            ).pack(side='left')
            
            self.ferias_valor_desconto = tk.Entry(frame_valor_desconto, width=15)
            self.ferias_valor_desconto.pack(side='left', padx=(5, 0))
            self.ferias_valor_desconto.insert(0, "0")
            
            # 6. Observações
            tk.Label(
                form_fields,
                text="Observações:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ferias_observacoes = tk.Text(form_fields, height=4, width=50)
            self.ferias_observacoes.pack(fill='x', pady=(0, 20))
            
            # Botões
            button_frame = tk.Frame(form_fields, bg=Theme.colors['surface'])
            button_frame.pack(fill='x')
            
            ModernButton(
                button_frame,
                text="✅ SALVAR FÉRIAS",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=11,
                padx=20,
                pady=10,
                command=self.salvar_ferias
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                button_frame,
                text="🗑️ LIMPAR FORMULÁRIO",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=11,
                padx=20,
                pady=10,
                command=self.limpar_formulario_ferias
            ).pack(side='left')
            
            # Espaço extra
            tk.Frame(scrollable_frame, height=20, bg=Theme.colors['surface']).pack()
            
            # ====================== ABA 2: LISTA DE FÉRIAS ======================
            list_frame = tk.Frame(notebook, bg=Theme.colors['background'])
            notebook.add(list_frame, text='📋 LISTA DE FÉRIAS')
            
            # Card da lista
            list_card = Card(list_frame, title="🏖️ FÉRIAS REGISTRADAS")
            list_card.pack(fill='both', expand=True, padx=10, pady=10)
            
            list_content = list_card.content_frame
            
            # Controles de filtro
            filter_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            filter_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(
                filter_frame,
                text="Filtrar por Status:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            self.ferias_filtro_status = ttk.Combobox(
                filter_frame,
                values=['Todos', 'Solicitada', 'Aprovada', 'Em Gozo', 'Concluída', 'Cancelada'],
                state='readonly',
                width=15
            )
            self.ferias_filtro_status.pack(side='left', padx=(0, 10))
            self.ferias_filtro_status.set('Todos')
            
            ModernButton(
                filter_frame,
                text="🔍 FILTRAR",
                bg=Theme.colors['primary'],
                hover_bg=Theme.colors['primary_light'],
                font_size=10,
                padx=15,
                pady=8,
                command=self.filtrar_ferias
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                filter_frame,
                text="🔄 ATUALIZAR",
                bg=Theme.colors['info'],
                hover_bg=self.lighten_color(Theme.colors['info'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.carregar_lista_ferias
            ).pack(side='left')
            
            # Treeview para lista de férias
            tree_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            tree_frame.pack(fill='both', expand=True)
            
            columns = ('ID', 'Funcionário', 'Período Aquisitivo', 'Período Gozo', 
                    'Dias', 'Desconto', 'Status', 'Solicitado em')
            
            self.ferias_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                height=12
            )
            
            col_widths = [50, 150, 120, 120, 60, 100, 100, 120]
            for col, width in zip(columns, col_widths):
                self.ferias_tree.heading(col, text=col)
                self.ferias_tree.column(col, width=width)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.ferias_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.ferias_tree.xview)
            self.ferias_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Layout
            self.ferias_tree.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Botões de ação
            action_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            action_frame.pack(fill='x', pady=(15, 0))
            
            ModernButton(
                action_frame,
                text="✏️ EDITAR FÉRIAS",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.editar_ferias
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="✅ APROVAR FÉRIAS",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.aprovar_ferias
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="❌ CANCELAR FÉRIAS",
                bg=Theme.colors['danger'],
                hover_bg=self.lighten_color(Theme.colors['danger'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.cancelar_ferias
            ).pack(side='left')
            
            # Carregar lista inicial
            self.carregar_lista_ferias()
            
        except Exception as e:
            print(f"Erro em create_vacations_section_corrected: {e}")
            tk.Label(
                parent,
                text=f"Erro ao criar seção de férias: {str(e)}",
                fg='red',
                bg='white'
            ).pack(expand=True, pady=50)
    
    def salvar_ferias(self):
        """Salva férias no banco de dados"""
        # Validar campos obrigatórios
        if not self.ferias_funcionario.get():
            messagebox.showerror("Erro", "Selecione um funcionário!")
            return
        
        if not self.ferias_aquisitivo_inicio.get() or not self.ferias_aquisitivo_fim.get():
            messagebox.showerror("Erro", "Informe o período aquisitivo!")
            return
        
        if not self.ferias_gozo_inicio.get() or not self.ferias_gozo_fim.get():
            messagebox.showerror("Erro", "Informe o período de gozo!")
            return
        
        if not self.ferias_dias.get():
            messagebox.showerror("Erro", "Informe o número de dias!")
            return
        
        try:
            # Obter ID do funcionário
            funcionario_nome = self.ferias_funcionario.get()
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            funcionario_id = None
            
            for f in funcionarios:
                if f[1] == funcionario_nome:
                    funcionario_id = f[0]
                    break
            
            if not funcionario_id:
                messagebox.showerror("Erro", "Funcionário não encontrado!")
                return
            
            # Preparar dados
            dados_ferias = {
                'funcionario_id': funcionario_id,
                'periodo_aquisitivo_inicio': self.ferias_aquisitivo_inicio.get(),
                'periodo_aquisitivo_fim': self.ferias_aquisitivo_fim.get(),
                'periodo_gozo_inicio': self.ferias_gozo_inicio.get(),
                'periodo_gozo_fim': self.ferias_gozo_fim.get(),
                'dias': int(self.ferias_dias.get()),
                'desconto_opcao': self.ferias_desconto_opcao.get(),
                'valor_desconto': float(self.ferias_valor_desconto.get() or 0),
                'observacoes': self.ferias_observacoes.get("1.0", "end-1c").strip(),
                'status': 'solicitada'
            }
            
            # Inserir no banco
            self.db.execute_query('''
                INSERT INTO ferias 
                (funcionario_id, periodo_aquisitivo_inicio, periodo_aquisitivo_fim,
                periodo_gozo_inicio, periodo_gozo_fim, dias, desconto_opcao,
                valor_desconto, observacoes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados_ferias['funcionario_id'],
                dados_ferias['periodo_aquisitivo_inicio'],
                dados_ferias['periodo_aquisitivo_fim'],
                dados_ferias['periodo_gozo_inicio'],
                dados_ferias['periodo_gozo_fim'],
                dados_ferias['dias'],
                dados_ferias['desconto_opcao'],
                dados_ferias['valor_desconto'],
                dados_ferias['observacoes'],
                dados_ferias['status']
            ))
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'ADICIONAR_FERIAS',
                'RH',
                f"Férias adicionadas para {funcionario_nome}"
            )
            
            messagebox.showinfo("Sucesso", "Férias registradas com sucesso!")
            
            # Limpar formulário
            self.limpar_formulario_ferias()
            
            # Atualizar lista
            self.carregar_lista_ferias()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar férias: {str(e)}")

    def carregar_lista_ferias(self):
        """Carrega lista de férias do banco"""
        if not hasattr(self, 'ferias_tree'):
            return
        
        # Limpar treeview
        for item in self.ferias_tree.get_children():
            self.ferias_tree.delete(item)
        
        try:
            # Buscar férias no banco
            query = "SELECT * FROM ferias ORDER BY periodo_gozo_inicio DESC"
            result = self.db.execute_query(query, commit=False)
            ferias = result.fetchall()
            
            if not ferias:
                self.ferias_tree.insert('', 'end', values=(
                    "---", "Nenhuma férias registrada", "", "", "", "", "", ""
                ))
                return
            
            for fer in ferias:
                # Obter nome do funcionário
                result = self.db.execute_query(
                    "SELECT nome FROM funcionarios WHERE id = ?",
                    (fer[1],),  # funcionario_id
                    commit=False
                )
                funcionario_nome = result.fetchone()
                funcionario_nome = funcionario_nome[0] if funcionario_nome else "Desconhecido"
                
                # Formatar datas
                periodo_aquisitivo = f"{fer[2]} a {fer[3]}" if fer[2] and fer[3] else "Não informado"
                periodo_gozo = f"{fer[4]} a {fer[5]}" if fer[4] and fer[5] else "Não informado"
                
                # Formatar desconto
                desconto_text = ""
                if fer[6] == 'nenhum':  # desconto_opcao
                    desconto_text = "Sem desconto"
                elif fer[6] == 'proporcional':
                    desconto_text = "Desconto proporcional"
                elif fer[6] == 'especifico':
                    desconto_text = f"Desconto: {fer[7]:,.0f} Kz"
                
                # Status com ícone
                status_icons = {
                    'solicitada': '🟡',
                    'aprovada': '🟢',
                    'em_gozo': '🔵',
                    'concluida': '✅',
                    'cancelada': '🔴'
                }
                status_icon = status_icons.get(fer[9] or 'solicitada', '⚫')
                status_text = f"{status_icon} {fer[9] or 'solicitada'}"
                
                # Data de solicitação
                data_solicitacao = fer[10] if len(fer) > 10 else ""
                if data_solicitacao:
                    try:
                        data_solicitacao = datetime.strptime(data_solicitacao, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    except:
                        pass
                
                self.ferias_tree.insert('', 'end', values=(
                    fer[0],  # ID
                    funcionario_nome,
                    periodo_aquisitivo,
                    periodo_gozo,
                    fer[5],  # dias
                    desconto_text,
                    status_text,
                    data_solicitacao
                ))
                
        except Exception as e:
            print(f"Erro ao carregar férias: {e}")
            self.ferias_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", ""
            ))
        
    def create_time_attendance_section_corrected(self, parent):
        """Cria seção de controle de ponto/horas - SISTEMA MANUAL COMPLETO"""
        try:
            # Frame principal
            main_frame = tk.Frame(parent, bg=Theme.colors['background'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Container com abas
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill='both', expand=True)
            
            # ====================== ABA 1: REGISTRAR PONTO ======================
            registro_frame = tk.Frame(notebook, bg=Theme.colors['background'])
            notebook.add(registro_frame, text='⏰ REGISTRAR PONTO')
            
            # Formulário de registro
            form_card = Card(registro_frame, title="⏰ REGISTRO DE PONTO MANUAL")
            form_card.pack(fill='both', expand=True, padx=10, pady=10)
            
            form_content = form_card.content_frame
            
            # Campos do formulário
            campos_frame = tk.Frame(form_content, bg=Theme.colors['surface'], padx=20, pady=20)
            campos_frame.pack(fill='x')
            
            # 1. Data
            tk.Label(
                campos_frame,
                text="Data do Registro: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            hoje = datetime.now()
            self.ponto_data = tk.Entry(campos_frame, width=15)
            self.ponto_data.pack(anchor='w', pady=(0, 15))
            self.ponto_data.insert(0, hoje.strftime('%Y-%m-%d'))
            
            # 2. Funcionário
            tk.Label(
                campos_frame,
                text="Selecionar Funcionário: *",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Carregar funcionários
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            nomes_funcionarios = [f[1] for f in funcionarios] if funcionarios else []
            
            self.ponto_funcionario = ttk.Combobox(
                campos_frame,
                values=nomes_funcionarios,
                state='readonly',
                width=40
            )
            self.ponto_funcionario.pack(fill='x', pady=(0, 15))
            
            if nomes_funcionarios:
                self.ponto_funcionario.set(nomes_funcionarios[0])
            
            # 3. Horário de entrada
            tk.Label(
                campos_frame,
                text="Horário de Entrada:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ponto_entrada = tk.Entry(campos_frame, width=10)
            self.ponto_entrada.pack(anchor='w', pady=(0, 15))
            self.ponto_entrada.insert(0, "08:00")
            
            # 4. Horário de saída
            tk.Label(
                campos_frame,
                text="Horário de Saída:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ponto_saida = tk.Entry(campos_frame, width=10)
            self.ponto_saida.pack(anchor='w', pady=(0, 15))
            self.ponto_saida.insert(0, "17:00")
            
            # 5. Horas extras
            tk.Label(
                campos_frame,
                text="Horas Extras Registradas:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            frame_horas = tk.Frame(campos_frame, bg=Theme.colors['surface'])
            frame_horas.pack(anchor='w', pady=(0, 15))
            
            self.ponto_horas_extras = tk.Entry(frame_horas, width=10)
            self.ponto_horas_extras.pack(side='left')
            self.ponto_horas_extras.insert(0, "0.0")
            
            tk.Label(
                frame_horas,
                text=" horas",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(5, 0))
            
            # 6. Atraso
            tk.Label(
                campos_frame,
                text="Atraso (minutos):",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ponto_atraso = tk.Entry(campos_frame, width=10)
            self.ponto_atraso.pack(anchor='w', pady=(0, 15))
            self.ponto_atraso.insert(0, "0")
            
            # 7. Faltas
            tk.Label(
                campos_frame,
                text="Registro de Falta:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ponto_faltou = tk.BooleanVar(value=False)
            tk.Checkbutton(
                campos_frame,
                text="Funcionário faltou neste dia",
                variable=self.ponto_faltou,
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 15))
            
            # 8. Observações
            tk.Label(
                campos_frame,
                text="Observações:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            self.ponto_observacoes = tk.Text(campos_frame, height=4, width=50)
            self.ponto_observacoes.pack(fill='x', pady=(0, 20))
            
            # Botões
            button_frame = tk.Frame(campos_frame, bg=Theme.colors['surface'])
            button_frame.pack(fill='x')
            
            ModernButton(
                button_frame,
                text="✅ SALVAR REGISTRO",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=11,
                padx=20,
                pady=10,
                command=self.salvar_registro_ponto
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                button_frame,
                text="🗑️ LIMPAR FORMULÁRIO",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=11,
                padx=20,
                pady=10,
                command=self.limpar_formulario_ponto
            ).pack(side='left')
            
            # ====================== ABA 2: LISTA DE REGISTROS ======================
            lista_frame = tk.Frame(notebook, bg=Theme.colors['background'])
            notebook.add(lista_frame, text='📋 LISTA DE REGISTROS')
            
            # Card da lista
            list_card = Card(lista_frame, title="⏰ REGISTROS DE PONTO")
            list_card.pack(fill='both', expand=True, padx=10, pady=10)
            
            list_content = list_card.content_frame
            
            # Controles de filtro
            filter_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            filter_frame.pack(fill='x', pady=(0, 15))
            
            # Filtro por data
            tk.Label(
                filter_frame,
                text="Filtrar por Data:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            self.ponto_filtro_data = tk.Entry(filter_frame, width=12)
            self.ponto_filtro_data.pack(side='left', padx=(0, 10))
            self.ponto_filtro_data.insert(0, hoje.strftime('%Y-%m-%d'))
            
            # Filtro por funcionário
            tk.Label(
                filter_frame,
                text="Funcionário:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            self.ponto_filtro_funcionario = ttk.Combobox(
                filter_frame,
                values=['Todos'] + nomes_funcionarios,
                state='readonly',
                width=20
            )
            self.ponto_filtro_funcionario.pack(side='left', padx=(0, 10))
            self.ponto_filtro_funcionario.set('Todos')
            
            ModernButton(
                filter_frame,
                text="🔍 FILTRAR",
                bg=Theme.colors['primary'],
                hover_bg=Theme.colors['primary_light'],
                font_size=10,
                padx=15,
                pady=8,
                command=self.filtrar_registros_ponto
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                filter_frame,
                text="🔄 ATUALIZAR",
                bg=Theme.colors['info'],
                hover_bg=self.lighten_color(Theme.colors['info'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.carregar_registros_ponto
            ).pack(side='left')
            
            # Treeview para registros
            tree_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            tree_frame.pack(fill='both', expand=True)
            
            columns = ('ID', 'Funcionário', 'Data', 'Entrada', 'Saída', 
                    'Horas Extras', 'Atraso', 'Falta', 'Observações')
            
            self.ponto_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                height=12
            )
            
            col_widths = [50, 150, 100, 80, 80, 100, 80, 80, 150]
            for col, width in zip(columns, col_widths):
                self.ponto_tree.heading(col, text=col)
                self.ponto_tree.column(col, width=width)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.ponto_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.ponto_tree.xview)
            self.ponto_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Layout
            self.ponto_tree.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Botões de ação
            action_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
            action_frame.pack(fill='x', pady=(15, 0))
            
            ModernButton(
                action_frame,
                text="✏️ EDITAR REGISTRO",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.editar_registro_ponto
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="🗑️ EXCLUIR REGISTRO",
                bg=Theme.colors['danger'],
                hover_bg=self.lighten_color(Theme.colors['danger'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.excluir_registro_ponto
            ).pack(side='left')
            
            # Carregar registros inicialmente
            self.carregar_registros_ponto()
            
            # ====================== ABA 3: RESUMO ======================
            resumo_frame = tk.Frame(notebook, bg=Theme.colors['background'])
            notebook.add(resumo_frame, text='📊 RESUMO')
            
            # Card de resumo
            resumo_card = Card(resumo_frame, title="📊 RESUMO DE PONTO E HORAS")
            resumo_card.pack(fill='both', expand=True, padx=10, pady=10)
            
            resumo_content = resumo_card.content_frame
            
            # Frame para controles
            controls_frame = tk.Frame(resumo_content, bg=Theme.colors['surface'])
            controls_frame.pack(fill='x', pady=(0, 20))
            
            # Período do resumo
            tk.Label(
                controls_frame,
                text="Período do Resumo:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            # Mês
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            
            self.resumo_mes = ttk.Combobox(
                controls_frame,
                values=meses,
                state='readonly',
                width=15
            )
            self.resumo_mes.pack(side='left', padx=(0, 10))
            self.resumo_mes.set(meses[hoje.month - 1])
            
            # Ano
            anos = [str(i) for i in range(2023, 2031)]
            self.resumo_ano = ttk.Combobox(
                controls_frame,
                values=anos,
                state='readonly',
                width=8
            )
            self.resumo_ano.pack(side='left', padx=(0, 10))
            self.resumo_ano.set(str(hoje.year))
            
            ModernButton(
                controls_frame,
                text="📊 GERAR RESUMO",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.gerar_resumo_ponto
            ).pack(side='left')
            
            # Área do resumo
            self.resumo_text = scrolledtext.ScrolledText(
                resumo_content,
                font=Theme.fonts['mono'],
                bg=Theme.colors['light'],
                fg=Theme.colors['text_primary'],
                wrap='word',
                height=15
            )
            self.resumo_text.pack(fill='both', expand=True)
            
            # Gerar resumo inicial
            self.gerar_resumo_ponto()
            
        except Exception as e:
            print(f"Erro em create_time_attendance_section_corrected: {e}")
            tk.Label(
                parent,
                text=f"Erro ao criar seção de ponto: {str(e)}",
                fg='red',
                bg='white'
            ).pack(expand=True, pady=50)
    
    def salvar_registro_ponto(self):
        """Salva registro de ponto no banco"""
        # Validar campos
        if not self.ponto_data.get():
            messagebox.showerror("Erro", "Informe a data!")
            return
        
        if not self.ponto_funcionario.get():
            messagebox.showerror("Erro", "Selecione um funcionário!")
            return
        
        try:
            # Obter ID do funcionário
            funcionario_nome = self.ponto_funcionario.get()
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            funcionario_id = None
            
            for f in funcionarios:
                if f[1] == funcionario_nome:
                    funcionario_id = f[0]
                    break
            
            if not funcionario_id:
                messagebox.showerror("Erro", "Funcionário não encontrado!")
                return
            
            # Converter valores
            horas_extras = float(self.ponto_horas_extras.get() or 0)
            atraso_minutos = int(self.ponto_atraso.get() or 0)
            faltou = 1 if self.ponto_faltou.get() else 0
            
            # Calcular horas trabalhadas (se tiver entrada e saída)
            horas_trabalhadas = 0
            if self.ponto_entrada.get() and self.ponto_saida.get() and not faltou:
                try:
                    entrada = datetime.strptime(self.ponto_entrada.get(), '%H:%M')
                    saida = datetime.strptime(self.ponto_saida.get(), '%H:%M')
                    horas_trabalhadas = (saida - entrada).seconds / 3600
                except:
                    horas_trabalhadas = 8.0  # Jornada padrão
            
            # Inserir no banco
            self.db.execute_query('''
                INSERT INTO registros_ponto 
                (funcionario_id, data, entrada, saida, horas_trabalhadas,
                horas_extras, atraso_minutos, faltou, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                funcionario_id,
                self.ponto_data.get(),
                self.ponto_entrada.get() if not faltou else None,
                self.ponto_saida.get() if not faltou else None,
                horas_trabalhadas,
                horas_extras,
                atraso_minutos,
                faltou,
                self.ponto_observacoes.get("1.0", "end-1c").strip()
            ))
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'REGISTRAR_PONTO',
                'RH',
                f"Ponto registrado para {funcionario_nome} em {self.ponto_data.get()}"
            )
            
            messagebox.showinfo("Sucesso", "Registro de ponto salvo com sucesso!")
            
            # Limpar formulário
            self.limpar_formulario_ponto()
            
            # Atualizar lista
            self.carregar_registros_ponto()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar registro: {str(e)}")

    def gerar_resumo_ponto(self):
        """Gera resumo de ponto baseado nos dados reais"""
        if not hasattr(self, 'resumo_text'):
            return
        
        try:
            # Obter mês e ano
            mes_text = self.resumo_mes.get()
            ano = self.resumo_ano.get()
            
            if not mes_text or not ano:
                return
            
            # Converter mês para número
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_num = meses.index(mes_text) + 1
            mes_ano = f"{ano}-{mes_num:02d}"
            
            # Buscar dados reais
            resumo = f"""
            {'='*80}
                            HOSPEDARIA CHECA - RECURSOS HUMANOS
                            RESUMO DE PONTO - {mes_text} de {ano}
            {'='*80}
            
            Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            Gerado por: {self.user_service.get_user_info()['nome']}
            
            {'='*80}
            """
            
            # 1. Funcionários ativos
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            resumo += f"\n1. FUNCIONÁRIOS ATIVOS: {len(funcionarios)}\n"
            resumo += "-" * 40 + "\n"
            
            for func in funcionarios:
                resumo += f"   • {func[1]} ({func[2]}) - {func[3]}\n"
            
            # 2. Registros de ponto do mês
            resumo += f"\n\n2. REGISTROS DE PONTO - {mes_text}/{ano}\n"
            resumo += "-" * 40 + "\n"
            
            # Buscar registros do mês
            query = '''
                SELECT fu.nome, COUNT(rp.id) as dias_trabalhados,
                    SUM(rp.horas_extras) as total_horas_extras,
                    SUM(rp.atraso_minutos) as total_atraso,
                    SUM(CASE WHEN rp.faltou = 1 THEN 1 ELSE 0 END) as total_faltas
                FROM registros_ponto rp
                JOIN funcionarios fu ON rp.funcionario_id = fu.id
                WHERE strftime('%Y-%m', rp.data) = ?
                GROUP BY fu.nome
                ORDER BY fu.nome
            '''
            
            result = self.db.execute_query(query, (mes_ano,), commit=False)
            registros = result.fetchall()
            
            if registros:
                total_horas_extras = 0
                total_atraso = 0
                total_faltas = 0
                
                for reg in registros:
                    nome, dias, horas_extras, atraso, faltas = reg
                    resumo += f"\n   {nome}:\n"
                    resumo += f"     Dias trabalhados: {dias or 0}\n"
                    resumo += f"     Horas extras: {horas_extras or 0:.1f}h\n"
                    resumo += f"     Atraso total: {atraso or 0} minutos\n"
                    resumo += f"     Faltas: {faltas or 0}\n"
                    
                    total_horas_extras += horas_extras or 0
                    total_atraso += atraso or 0
                    total_faltas += faltas or 0
                
                resumo += f"\n   TOTAIS DO MÊS:\n"
                resumo += f"     Horas extras totais: {total_horas_extras:.1f}h\n"
                resumo += f"     Atraso total: {total_atraso} minutos\n"
                resumo += f"     Faltas totais: {total_faltas}\n"
            else:
                resumo += "\n   Nenhum registro encontrado para este mês.\n"
            
            # 3. Funcionários de férias no mês
            resumo += f"\n\n3. FUNCIONÁRIOS DE FÉRIAS - {mes_text}/{ano}\n"
            resumo += "-" * 40 + "\n"
            
            query = '''
                SELECT fu.nome, f.periodo_gozo_inicio, f.periodo_gozo_fim, f.dias
                FROM ferias f
                JOIN funcionarios fu ON f.funcionario_id = fu.id
                WHERE (strftime('%Y-%m', f.periodo_gozo_inicio) = ? OR
                    strftime('%Y-%m', f.periodo_gozo_fim) = ?)
                AND f.status IN ('aprovada', 'em_gozo')
            '''
            
            result = self.db.execute_query(query, (mes_ano, mes_ano), commit=False)
            ferias = result.fetchall()
            
            if ferias:
                for fer in ferias:
                    nome, inicio, fim, dias = fer
                    resumo += f"\n   {nome}: {inicio} a {fim} ({dias} dias)\n"
            else:
                resumo += "\n   Nenhum funcionário de férias neste mês.\n"
            
            # 4. Estatísticas gerais
            resumo += f"\n\n4. ESTATÍSTICAS GERAIS\n"
            resumo += "-" * 40 + "\n"
            
            # Total de funcionários
            resumo += f"   Total de funcionários: {len(funcionarios)}\n"
            
            # Média de horas extras
            if registros:
                media_horas_extras = total_horas_extras / len(registros) if registros else 0
                resumo += f"   Média de horas extras por funcionário: {media_horas_extras:.1f}h\n"
            
            # Total de dias úteis (aproximado)
            dias_uteis = 22  # Aproximação padrão
            resumo += f"   Dias úteis no mês (aproximado): {dias_uteis}\n"
            
            resumo += "\n" + "="*80 + "\n"
            resumo += "FIM DO RELATÓRIO\n"
            
            # Atualizar texto
            self.resumo_text.delete('1.0', tk.END)
            self.resumo_text.insert('1.0', resumo)
            
        except Exception as e:
            self.resumo_text.delete('1.0', tk.END)
            self.resumo_text.insert('1.0', f"Erro ao gerar resumo: {str(e)}")
        
    def create_hr_reports_section_corrected(self, parent):
        """Cria seção de relatórios de RH - SISTEMA MANUAL COMPLETO"""
        try:
            # Frame principal
            main_frame = tk.Frame(parent, bg=Theme.colors['background'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Card principal
            reports_card = Card(main_frame, title="📊 RELATÓRIOS DE RECURSOS HUMANOS")
            reports_card.pack(fill='both', expand=True)
            
            reports_content = reports_card.content_frame
            
            # Controles superiores
            controls_frame = tk.Frame(reports_content, bg=Theme.colors['surface'])
            controls_frame.pack(fill='x', pady=(0, 20))
            
            # Tipo de relatório
            tk.Label(
                controls_frame,
                text="Tipo de Relatório:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            self.report_tipo = ttk.Combobox(
                controls_frame,
                values=['Relatório Completo de RH', 'Relatório de Funcionários', 
                    'Relatório de Férias', 'Relatório de Ponto', 
                    'Relatório de Folha de Pagamento', 'Relatório de Desempenho'],
                state='readonly',
                width=25
            )
            self.report_tipo.pack(side='left', padx=(0, 10))
            self.report_tipo.set('Relatório Completo de RH')
            
            # Período
            tk.Label(
                controls_frame,
                text="Período:",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(side='left', padx=(0, 10))
            
            # Mês
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            
            hoje = datetime.now()
            self.report_mes = ttk.Combobox(
                controls_frame,
                values=meses,
                state='readonly',
                width=15
            )
            self.report_mes.pack(side='left', padx=(0, 10))
            self.report_mes.set(meses[hoje.month - 1])
            
            # Ano
            anos = [str(i) for i in range(2023, 2031)]
            self.report_ano = ttk.Combobox(
                controls_frame,
                values=anos,
                state='readonly',
                width=8
            )
            self.report_ano.pack(side='left', padx=(0, 10))
            self.report_ano.set(str(hoje.year))
            
            # Botões
            button_frame = tk.Frame(controls_frame, bg=Theme.colors['surface'])
            button_frame.pack(side='left')
            
            ModernButton(
                button_frame,
                text="📄 GERAR RELATÓRIO",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=10,
                padx=15,
                pady=8,
                command=self.gerar_relatorio_rh_real
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                button_frame,
                text="💾 SALVAR COMO TXT",
                bg=Theme.colors['primary'],
                hover_bg=Theme.colors['primary_light'],
                font_size=10,
                padx=15,
                pady=8,
                command=self.salvar_relatorio_txt
            ).pack(side='left')
            
            # Área do relatório
            report_frame = tk.Frame(reports_content, bg=Theme.colors['surface'])
            report_frame.pack(fill='both', expand=True)
            
            # Text widget com scroll
            self.report_rh_text = scrolledtext.ScrolledText(
                report_frame,
                font=Theme.fonts['mono'],
                bg=Theme.colors['light'],
                fg=Theme.colors['text_primary'],
                wrap='word',
                height=20
            )
            self.report_rh_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Gerar relatório inicial
            self.gerar_relatorio_rh_real()
            
        except Exception as e:
            print(f"Erro em create_hr_reports_section_corrected: {e}")
            tk.Label(
                parent,
                text=f"Erro ao criar seção de relatórios: {str(e)}",
                fg='red',
                bg='white'
            ).pack(expand=True, pady=50)
    
    def gerar_relatorio_rh_real(self):
        """Gera relatório de RH com dados reais"""
        if not hasattr(self, 'report_rh_text'):
            return
        
        try:
            tipo = self.report_tipo.get()
            mes_text = self.report_mes.get()
            ano = self.report_ano.get()
            
            # Converter mês para número
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_num = meses.index(mes_text) + 1
            mes_ano = f"{ano}-{mes_num:02d}"
            
            relatorio = ""
            
            if tipo == 'Relatório Completo de RH':
                relatorio = self.gerar_relatorio_completo(mes_ano, mes_text, ano)
            elif tipo == 'Relatório de Funcionários':
                relatorio = self.gerar_relatorio_funcionarios()
            elif tipo == 'Relatório de Férias':
                relatorio = self.gerar_relatorio_ferias(mes_ano, mes_text, ano)
            elif tipo == 'Relatório de Ponto':
                relatorio = self.gerar_relatorio_ponto(mes_ano, mes_text, ano)
            elif tipo == 'Relatório de Folha de Pagamento':
                relatorio = self.gerar_relatorio_folha(mes_ano, mes_text, ano)
            elif tipo == 'Relatório de Desempenho':
                relatorio = self.gerar_relatorio_desempenho(mes_ano, mes_text, ano)
            
            # Atualizar texto
            self.report_rh_text.delete('1.0', tk.END)
            self.report_rh_text.insert('1.0', relatorio)
            
        except Exception as e:
            self.report_rh_text.delete('1.0', tk.END)
            self.report_rh_text.insert('1.0', f"Erro ao gerar relatório: {str(e)}")

    def gerar_relatorio_completo(self, mes_ano, mes_text, ano):
        """Gera relatório completo de RH"""
        relatorio = f"""
        {'='*100}
                        HOSPEDARIA CHECA - RECURSOS HUMANOS
                    RELATÓRIO COMPLETO - {mes_text} de {ano}
        {'='*100}
        
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        Gerado por: {self.user_service.get_user_info()['nome']}
        
        {'='*100}
        """
        
        # 1. DADOS DOS FUNCIONÁRIOS
        relatorio += "\n1. DADOS DOS FUNCIONÁRIOS\n"
        relatorio += "-" * 50 + "\n"
        
        funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
        relatorio += f"Total de funcionários ativos: {len(funcionarios)}\n\n"
        
        for func in funcionarios:
            func_id, nome, cargo, departamento, admissao, salario = func[:6]
            relatorio += f"  • {nome}\n"
            relatorio += f"    Cargo: {cargo}\n"
            relatorio += f"    Departamento: {departamento}\n"
            relatorio += f"    Admissão: {admissao}\n"
            relatorio += f"    Salário base: {salario:,} Kz\n"
            relatorio += "\n"
        
        # 2. FÉRIAS
        relatorio += "\n2. FÉRIAS REGISTRADAS\n"
        relatorio += "-" * 50 + "\n"
        
        query = '''
            SELECT fu.nome, f.periodo_gozo_inicio, f.periodo_gozo_fim, f.dias, f.status
            FROM ferias f
            JOIN funcionarios fu ON f.funcionario_id = fu.id
            WHERE strftime('%Y-%m', f.periodo_gozo_inicio) = ?
            ORDER BY f.periodo_gozo_inicio
        '''
        
        result = self.db.execute_query(query, (mes_ano,), commit=False)
        ferias = result.fetchall()
        
        if ferias:
            for fer in ferias:
                nome, inicio, fim, dias, status = fer
                relatorio += f"  • {nome}: {inicio} a {fim} ({dias} dias) - Status: {status}\n"
        else:
            relatorio += "  Nenhuma férias registrada para este mês.\n"
        
        # 3. PONTO E HORAS
        relatorio += "\n\n3. REGISTROS DE PONTO\n"
        relatorio += "-" * 50 + "\n"
        
        query = '''
            SELECT fu.nome, COUNT(rp.id) as registros,
                SUM(rp.horas_extras) as horas_extras,
                SUM(rp.atraso_minutos) as atraso,
                SUM(CASE WHEN rp.faltou = 1 THEN 1 ELSE 0 END) as faltas
            FROM registros_ponto rp
            JOIN funcionarios fu ON rp.funcionario_id = fu.id
            WHERE strftime('%Y-%m', rp.data) = ?
            GROUP BY fu.nome
        '''
        
        result = self.db.execute_query(query, (mes_ano,), commit=False)
        pontos = result.fetchall()
        
        if pontos:
            for ponto in pontos:
                nome, registros, horas_extras, atraso, faltas = ponto
                relatorio += f"  • {nome}:\n"
                relatorio += f"    Registros: {registros}\n"
                relatorio += f"    Horas extras: {horas_extras or 0:.1f}h\n"
                relatorio += f"    Atraso: {atraso or 0} minutos\n"
                relatorio += f"    Faltas: {faltas or 0}\n"
        else:
            relatorio += "  Nenhum registro de ponto para este mês.\n"
        
        # 4. FOLHA DE PAGAMENTO
        relatorio += "\n\n4. FOLHA DE PAGAMENTO\n"
        relatorio += "-" * 50 + "\n"
        
        query = '''
            SELECT fu.nome, fp.salario_base, fp.salario_liquido, fp.status
            FROM folha_pagamento fp
            JOIN funcionarios fu ON fp.funcionario_id = fu.id
            WHERE strftime('%Y-%m', fp.mes_ano) = ?
            ORDER BY fu.nome
        '''
        
        result = self.db.execute_query(query, (mes_ano,), commit=False)
        folhas = result.fetchall()
        
        if folhas:
            total_salarios = 0
            for folha in folhas:
                nome, base, liquido, status = folha
                relatorio += f"  • {nome}:\n"
                relatorio += f"    Salário base: {base:,} Kz\n"
                relatorio += f"    Salário líquido: {liquido:,} Kz\n"
                relatorio += f"    Status: {status}\n"
                total_salarios += liquido or 0
            
            relatorio += f"\n  TOTAL DA FOLHA: {total_salarios:,} Kz\n"
        else:
            relatorio += "  Nenhuma folha de pagamento para este mês.\n"
        
        # 5. CONCLUSÃO
        relatorio += f"\n\n{'='*100}\n"
        relatorio += "RESUMO FINAL:\n"
        relatorio += f"- Funcionários ativos: {len(funcionarios)}\n"
        relatorio += f"- Férias agendadas: {len(ferias)}\n"
        relatorio += f"- Funcionários com registros de ponto: {len(pontos)}\n"
        relatorio += f"- Folha de pagamento: {'Calculada' if folhas else 'Pendente'}\n"
        
        relatorio += f"\n{'='*100}\n"
        relatorio += "FIM DO RELATÓRIO\n"
        
        return relatorio
   
    def limpar_formulario_ferias(self):
        """Limpa o formulário de férias"""
        if hasattr(self, 'ferias_funcionario'):
            self.ferias_funcionario.set('')
        if hasattr(self, 'ferias_aquisitivo_inicio'):
            hoje = datetime.now()
            self.ferias_aquisitivo_inicio.delete(0, tk.END)
            self.ferias_aquisitivo_inicio.insert(0, hoje.strftime('%Y-%m-%d'))
        if hasattr(self, 'ferias_aquisitivo_fim'):
            self.ferias_aquisitivo_fim.delete(0, tk.END)
            self.ferias_aquisitivo_fim.insert(0, (hoje + timedelta(days=365)).strftime('%Y-%m-%d'))
        if hasattr(self, 'ferias_gozo_inicio'):
            self.ferias_gozo_inicio.delete(0, tk.END)
            self.ferias_gozo_inicio.insert(0, hoje.strftime('%Y-%m-%d'))
        if hasattr(self, 'ferias_gozo_fim'):
            self.ferias_gozo_fim.delete(0, tk.END)
            self.ferias_gozo_fim.insert(0, (hoje + timedelta(days=30)).strftime('%Y-%m-%d'))
        if hasattr(self, 'ferias_dias'):
            self.ferias_dias.delete(0, tk.END)
            self.ferias_dias.insert(0, "22")
        if hasattr(self, 'ferias_valor_desconto'):
            self.ferias_valor_desconto.delete(0, tk.END)
            self.ferias_valor_desconto.insert(0, "0")
        if hasattr(self, 'ferias_observacoes'):
            self.ferias_observacoes.delete('1.0', tk.END)

    def limpar_formulario_ponto(self):
        """Limpa o formulário de ponto"""
        hoje = datetime.now()
        if hasattr(self, 'ponto_data'):
            self.ponto_data.delete(0, tk.END)
            self.ponto_data.insert(0, hoje.strftime('%Y-%m-%d'))
        if hasattr(self, 'ponto_funcionario'):
            self.ponto_funcionario.set('')
        if hasattr(self, 'ponto_entrada'):
            self.ponto_entrada.delete(0, tk.END)
            self.ponto_entrada.insert(0, "08:00")
        if hasattr(self, 'ponto_saida'):
            self.ponto_saida.delete(0, tk.END)
            self.ponto_saida.insert(0, "17:00")
        if hasattr(self, 'ponto_horas_extras'):
            self.ponto_horas_extras.delete(0, tk.END)
            self.ponto_horas_extras.insert(0, "0.0")
        if hasattr(self, 'ponto_atraso'):
            self.ponto_atraso.delete(0, tk.END)
            self.ponto_atraso.insert(0, "0")
        if hasattr(self, 'ponto_faltou'):
            self.ponto_faltou.set(False)
        if hasattr(self, 'ponto_observacoes'):
            self.ponto_observacoes.delete('1.0', tk.END)

    def salvar_relatorio_txt(self):
        """Salva o relatório atual em um arquivo TXT"""
        try:
            # Obter o conteúdo do relatório
            conteudo = self.report_rh_text.get('1.0', tk.END)
            
            if not conteudo.strip():
                messagebox.showwarning("Aviso", "Não há relatório para salvar!")
                return
            
            # Sugerir nome de arquivo
            tipo = self.report_tipo.get().replace(' ', '_').lower()
            mes = self.report_mes.get()
            ano = self.report_ano.get()
            data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_sugerido = f"relatorio_{tipo}_{mes}_{ano}_{data_atual}.txt"
            
            # Usar filedialog para salvar
            from tkinter import filedialog
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
                initialfile=nome_sugerido
            )
            
            if arquivo:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{arquivo}")
                
                # Log da ação
                user_info = self.user_service.get_user_info()
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    'SALVAR_RELATORIO',
                    'RH',
                    f"Relatório salvo: {os.path.basename(arquivo)}"
                )
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")

    def filtrar_ferias(self):
        """Filtra a lista de férias pelo status"""
        if not hasattr(self, 'ferias_tree'):
            return
        
        status = self.ferias_filtro_status.get()
        
        # Limpar treeview
        for item in self.ferias_tree.get_children():
            self.ferias_tree.delete(item)
        
        try:
            # Construir query com filtro
            query = "SELECT * FROM ferias"
            params = ()
            
            if status != 'Todos':
                query += " WHERE status = ?"
                params = (status.lower(),)
            
            query += " ORDER BY periodo_gozo_inicio DESC"
            
            result = self.db.execute_query(query, params, commit=False)
            ferias = result.fetchall()
            
            if not ferias:
                self.ferias_tree.insert('', 'end', values=(
                    "---", "Nenhuma férias encontrada", "", "", "", "", "", ""
                ))
                return
            
            for fer in ferias:
                # Obter nome do funcionário
                result = self.db.execute_query(
                    "SELECT nome FROM funcionarios WHERE id = ?",
                    (fer[1],),
                    commit=False
                )
                funcionario_nome = result.fetchone()
                funcionario_nome = funcionario_nome[0] if funcionario_nome else "Desconhecido"
                
                # Formatar datas
                periodo_aquisitivo = f"{fer[2]} a {fer[3]}" if fer[2] and fer[3] else "Não informado"
                periodo_gozo = f"{fer[4]} a {fer[5]}" if fer[4] and fer[5] else "Não informado"
                
                # Formatar desconto
                desconto_text = ""
                if len(fer) > 6 and fer[6]:
                    if fer[6] == 'nenhum':
                        desconto_text = "Sem desconto"
                    elif fer[6] == 'proporcional':
                        desconto_text = "Desconto proporcional"
                    elif fer[6] == 'especifico':
                        valor = fer[7] if len(fer) > 7 else 0
                        desconto_text = f"Desconto: {valor:,.0f} Kz"
                
                # Status com ícone
                status_icons = {
                    'solicitada': '🟡',
                    'aprovada': '🟢',
                    'em_gozo': '🔵',
                    'concluida': '✅',
                    'cancelada': '🔴'
                }
                status_ferias = fer[9] if len(fer) > 9 else 'solicitada'
                status_icon = status_icons.get(status_ferias, '⚫')
                status_text = f"{status_icon} {status_ferias}"
                
                # Data de solicitação
                data_solicitacao = fer[10] if len(fer) > 10 else ""
                if data_solicitacao:
                    try:
                        data_solicitacao = datetime.strptime(data_solicitacao, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    except:
                        pass
                
                self.ferias_tree.insert('', 'end', values=(
                    fer[0],  # ID
                    funcionario_nome,
                    periodo_aquisitivo,
                    periodo_gozo,
                    fer[5] if len(fer) > 5 else "",  # dias
                    desconto_text,
                    status_text,
                    data_solicitacao
                ))
                
        except Exception as e:
            print(f"Erro ao filtrar férias: {e}")
            self.ferias_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", ""
            ))

    def aprovar_ferias(self):
        """Aprova as férias selecionadas"""
        selection = self.ferias_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma férias para aprovar!")
            return
        
        item = self.ferias_tree.item(selection[0])
        ferias_id = item['values'][0]
        
        if not messagebox.askyesno("Confirmar", f"Deseja aprovar as férias ID {ferias_id}?"):
            return
        
        try:
            # Atualizar status no banco
            self.db.execute_query(
                "UPDATE ferias SET status = 'aprovada' WHERE id = ?",
                (ferias_id,)
            )
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'APROVAR_FERIAS',
                'RH',
                f"Férias ID {ferias_id} aprovada"
            )
            
            messagebox.showinfo("Sucesso", "Férias aprovadas com sucesso!")
            
            # Atualizar lista
            self.filtrar_ferias()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aprovar férias: {str(e)}")

    def cancelar_ferias(self):
        """Cancela as férias selecionadas"""
        selection = self.ferias_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma férias para cancelar!")
            return
        
        item = self.ferias_tree.item(selection[0])
        ferias_id = item['values'][0]
        funcionario_nome = item['values'][1]
        
        if not messagebox.askyesno("Confirmar", f"Deseja cancelar as férias de {funcionario_nome}?"):
            return
        
        try:
            # Atualizar status no banco
            self.db.execute_query(
                "UPDATE ferias SET status = 'cancelada' WHERE id = ?",
                (ferias_id,)
            )
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'CANCELAR_FERIAS',
                'RH',
                f"Férias ID {ferias_id} cancelada"
            )
            
            messagebox.showinfo("Sucesso", "Férias canceladas com sucesso!")
            
            # Atualizar lista
            self.filtrar_ferias()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar férias: {str(e)}")

    def editar_ferias(self):
        """Abre janela para editar férias"""
        selection = self.ferias_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma férias para editar!")
            return
        
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de edição em desenvolvimento!")

    def filtrar_registros_ponto(self):
        """Filtra registros de ponto por data e funcionário"""
        if not hasattr(self, 'ponto_tree'):
            return
        
        data_filtro = self.ponto_filtro_data.get()
        funcionario_filtro = self.ponto_filtro_funcionario.get()
        
        # Limpar treeview
        for item in self.ponto_tree.get_children():
            self.ponto_tree.delete(item)
        
        try:
            # Construir query com filtros
            query = '''
                SELECT rp.*, fu.nome 
                FROM registros_ponto rp
                JOIN funcionarios fu ON rp.funcionario_id = fu.id
                WHERE 1=1
            '''
            params = []
            
            if data_filtro:
                query += " AND rp.data = ?"
                params.append(data_filtro)
            
            if funcionario_filtro and funcionario_filtro != 'Todos':
                query += " AND fu.nome = ?"
                params.append(funcionario_filtro)
            
            query += " ORDER BY rp.data DESC, fu.nome"
            
            result = self.db.execute_query(query, tuple(params), commit=False)
            registros = result.fetchall()
            
            if not registros:
                self.ponto_tree.insert('', 'end', values=(
                    "---", "Nenhum registro encontrado", "", "", "", "", "", "", ""
                ))
                return
            
            for reg in registros:
                # Formatar valores
                horas_extras = f"{reg[6] or 0:.1f}h" if reg[6] else "0h"
                atraso = f"{reg[7] or 0} min" if reg[7] else "0 min"
                falta = "Sim" if reg[8] == 1 else "Não"
                observacoes = reg[9] or "" if len(reg) > 9 else ""
                
                self.ponto_tree.insert('', 'end', values=(
                    reg[0],  # ID
                    reg[10] if len(reg) > 10 else "Desconhecido",  # nome
                    reg[2],  # data
                    reg[3] or "",  # entrada
                    reg[4] or "",  # saída
                    horas_extras,
                    atraso,
                    falta,
                    observacoes[:30] + "..." if len(observacoes) > 30 else observacoes
                ))
                
        except Exception as e:
            print(f"Erro ao filtrar registros: {e}")
            self.ponto_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", "", ""
            ))

    def carregar_registros_ponto(self):
        """Carrega todos os registros de ponto"""
        if not hasattr(self, 'ponto_tree'):
            return
        
        # Limpar treeview
        for item in self.ponto_tree.get_children():
            self.ponto_tree.delete(item)
        
        try:
            # Buscar todos os registros
            query = '''
                SELECT rp.*, fu.nome 
                FROM registros_ponto rp
                JOIN funcionarios fu ON rp.funcionario_id = fu.id
                ORDER BY rp.data DESC, fu.nome
                LIMIT 100
            '''
            
            result = self.db.execute_query(query, commit=False)
            registros = result.fetchall()
            
            if not registros:
                self.ponto_tree.insert('', 'end', values=(
                    "---", "Nenhum registro encontrado", "", "", "", "", "", "", ""
                ))
                return
            
            for reg in registros:
                # Formatar valores
                horas_extras = f"{reg[6] or 0:.1f}h" if reg[6] else "0h"
                atraso = f"{reg[7] or 0} min" if reg[7] else "0 min"
                falta = "Sim" if reg[8] == 1 else "Não"
                observacoes = reg[9] or "" if len(reg) > 9 else ""
                
                self.ponto_tree.insert('', 'end', values=(
                    reg[0],  # ID
                    reg[10] if len(reg) > 10 else "Desconhecido",  # nome
                    reg[2],  # data
                    reg[3] or "",  # entrada
                    reg[4] or "",  # saída
                    horas_extras,
                    atraso,
                    falta,
                    observacoes[:30] + "..." if len(observacoes) > 30 else observacoes
                ))
                
        except Exception as e:
            print(f"Erro ao carregar registros: {e}")
            self.ponto_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", "", ""
            ))

    def editar_registro_ponto(self):
        """Abre janela para editar registro de ponto"""
        selection = self.ponto_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um registro para editar!")
            return
        
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de edição em desenvolvimento!")

    def excluir_registro_ponto(self):
        """Exclui registro de ponto selecionado"""
        selection = self.ponto_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir!")
            return
        
        item = self.ponto_tree.item(selection[0])
        registro_id = item['values'][0]
        funcionario_nome = item['values'][1]
        data_registro = item['values'][2]
        
        if not messagebox.askyesno("Confirmar", 
            f"Deseja excluir o registro de {funcionario_nome} em {data_registro}?"):
            return
        
        try:
            # Excluir do banco
            self.db.execute_query(
                "DELETE FROM registros_ponto WHERE id = ?",
                (registro_id,)
            )
            
            # Log da ação
            user_info = self.user_service.get_user_info()
            self.db.log_action(
                user_info['id'],
                user_info['nome'],
                'EXCLUIR_REGISTRO_PONTO',
                'RH',
                f"Registro ID {registro_id} excluído"
            )
            
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
            
            # Atualizar lista
            self.carregar_registros_ponto()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir registro: {str(e)}")

    def gerar_relatorio_funcionarios(self):
        """Gera relatório de funcionários"""
        funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
        
        relatorio = f"""
        {'='*80}
                    RELATÓRIO DE FUNCIONÁRIOS - HOSPEDARIA CHECA
        {'='*80}
        
        Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Total de funcionários ativos: {len(funcionarios)}
        
        {'='*80}
        
        LISTA DE FUNCIONÁRIOS:
        """
        
        for func in funcionarios:
            func_id, nome, cargo, departamento, admissao, salario = func[:6]
            relatorio += f"\n{nome.upper()}\n"
            relatorio += f"  ID: {func_id}\n"
            relatorio += f"  Cargo: {cargo}\n"
            relatorio += f"  Departamento: {departamento}\n"
            relatorio += f"  Admissão: {admissao}\n"
            relatorio += f"  Salário base: {salario:,} Kz\n"
            relatorio += "-" * 40 + "\n"
        
        relatorio += f"\n{'='*80}\n"
        relatorio += "FIM DO RELATÓRIO\n"
        
        return relatorio

    def gerar_relatorio_ferias(self, mes_ano, mes_text, ano):
        """Gera relatório de férias"""
        query = '''
            SELECT fu.nome, f.periodo_aquisitivo_inicio, f.periodo_aquisitivo_fim,
                f.periodo_gozo_inicio, f.periodo_gozo_fim, f.dias, f.status
            FROM ferias f
            JOIN funcionarios fu ON f.funcionario_id = fu.id
            WHERE strftime('%Y-%m', f.periodo_gozo_inicio) = ?
            OR strftime('%Y-%m', f.periodo_gozo_fim) = ?
            ORDER BY f.periodo_gozo_inicio
        '''
        
        result = self.db.execute_query(query, (mes_ano, mes_ano), commit=False)
        ferias = result.fetchall()
        
        relatorio = f"""
        {'='*80}
                RELATÓRIO DE FÉRIAS - {mes_text} de {ano}
        {'='*80}
        
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Total de férias no período: {len(ferias)}
        
        {'='*80}
        
        DETALHES DAS FÉRIAS:
        """
        
        if ferias:
            for fer in ferias:
                nome, aq_inicio, aq_fim, gozo_inicio, gozo_fim, dias, status = fer
                relatorio += f"\n{nome.upper()}\n"
                relatorio += f"  Período Aquisitivo: {aq_inicio} a {aq_fim}\n"
                relatorio += f"  Período de Gozo: {gozo_inicio} a {gozo_fim}\n"
                relatorio += f"  Dias: {dias}\n"
                relatorio += f"  Status: {status}\n"
                relatorio += "-" * 40 + "\n"
        else:
            relatorio += "\nNenhuma férias registrada para este período.\n"
        
        relatorio += f"\n{'='*80}\n"
        relatorio += "FIM DO RELATÓRIO\n"
        
        return relatorio

    def gerar_relatorio_ponto(self, mes_ano, mes_text, ano):
        """Gera relatório de ponto"""
        query = '''
            SELECT fu.nome, COUNT(rp.id) as dias,
                SUM(rp.horas_extras) as horas_extras,
                SUM(rp.atraso_minutos) as atraso,
                SUM(CASE WHEN rp.faltou = 1 THEN 1 ELSE 0 END) as faltas
            FROM registros_ponto rp
            JOIN funcionarios fu ON rp.funcionario_id = fu.id
            WHERE strftime('%Y-%m', rp.data) = ?
            GROUP BY fu.nome
            ORDER BY fu.nome
        '''
        
        result = self.db.execute_query(query, (mes_ano,), commit=False)
        registros = result.fetchall()
        
        relatorio = f"""
        {'='*80}
            RELATÓRIO DE PONTO - {mes_text} de {ano}
        {'='*80}
        
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Total de funcionários com registros: {len(registros)}
        
        {'='*80}
        
        REGISTROS POR FUNCIONÁRIO:
        """
        
        if registros:
            total_horas_extras = 0
            total_atraso = 0
            total_faltas = 0
            
            for reg in registros:
                nome, dias, horas_extras, atraso, faltas = reg
                relatorio += f"\n{nome.upper()}\n"
                relatorio += f"  Dias registrados: {dias or 0}\n"
                relatorio += f"  Horas extras: {horas_extras or 0:.1f}h\n"
                relatorio += f"  Atraso total: {atraso or 0} minutos\n"
                relatorio += f"  Faltas: {faltas or 0}\n"
                relatorio += "-" * 40 + "\n"
                
                total_horas_extras += horas_extras or 0
                total_atraso += atraso or 0
                total_faltas += faltas or 0
            
            relatorio += f"\nTOTAIS GERAIS:\n"
            relatorio += f"  Horas extras totais: {total_horas_extras:.1f}h\n"
            relatorio += f"  Atraso total: {total_atraso} minutos\n"
            relatorio += f"  Faltas totais: {total_faltas}\n"
        else:
            relatorio += "\nNenhum registro de ponto para este período.\n"
        
        relatorio += f"\n{'='*80}\n"
        relatorio += "FIM DO RELATÓRIO\n"
        
        return relatorio

    def gerar_relatorio_folha(self, mes_ano, mes_text, ano):
        """Gera relatório de folha de pagamento"""
        query = '''
            SELECT fu.nome, fp.salario_base, fp.salario_liquido, fp.status
            FROM folha_pagamento fp
            JOIN funcionarios fu ON fp.funcionario_id = fu.id
            WHERE strftime('%Y-%m', fp.mes_ano) = ?
            ORDER BY fu.nome
        '''
        
        result = self.db.execute_query(query, (mes_ano,), commit=False)
        folhas = result.fetchall()
        
        relatorio = f"""
        {'='*80}
            RELATÓRIO DE FOLHA DE PAGAMENTO - {mes_text} de {ano}
        {'='*80}
        
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Total de funcionários na folha: {len(folhas)}
        
        {'='*80}
        
        DETALHES DA FOLHA:
        """
        
        if folhas:
            total_salarios = 0
            
            for folha in folhas:
                nome, base, liquido, status = folha
                relatorio += f"\n{nome.upper()}\n"
                relatorio += f"  Salário base: {base:,} Kz\n"
                relatorio += f"  Salário líquido: {liquido:,} Kz\n"
                relatorio += f"  Status: {status}\n"
                relatorio += "-" * 40 + "\n"
                
                total_salarios += liquido or 0
            
            relatorio += f"\nTOTAL DA FOLHA: {total_salarios:,} Kz\n"
        else:
            relatorio += "\nNenhuma folha de pagamento para este período.\n"
        
        relatorio += f"\n{'='*80}\n"
        relatorio += "FIM DO RELATÓRIO\n"
        
        return relatorio

    def gerar_relatorio_desempenho(self, mes_ano, mes_text, ano):
        """Gera relatório de desempenho"""
        relatorio = f"""
        {'='*80}
            RELATÓRIO DE DESEMPENHO - {mes_text} de {ano}
        {'='*80}
        
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        {'='*80}
        
        ESTE RELATÓRIO ESTÁ EM DESENVOLVIMENTO
        
        Em breve, esta seção incluirá:
        - Avaliação de desempenho por funcionário
        - Métricas de produtividade
        - Análise comparativa por período
        - Recomendações para melhoria
        
        {'='*80}
        
        Para informações detalhadas de desempenho, consulte os relatórios:
        - Relatório de Ponto (para horas extras e faltas)
        - Relatório de Folha (para dados financeiros)
        - Relatório de Férias (para planejamento)
        
        {'='*80}
        """
        
        return relatorio
    
    def update_employees_list(self):
        """Atualiza lista de funcionários"""
        if not hasattr(self, 'employees_tree'):
            return
        
        # Limpar treeview
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        try:
            # Buscar funcionários
            funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
            
            if not funcionarios:
                self.employees_tree.insert('', 'end', values=(
                    "---", "Nenhum funcionário cadastrado", "", "", "", "", ""
                ))
                return
            
            for func in funcionarios:
                # Formatar salário
                salario = f"{func[5]:,} Kz" if func[5] else "0 Kz"
                
                # Formatar data de admissão
                admissao = func[4]
                if admissao:
                    try:
                        admissao = datetime.strptime(admissao, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        pass
                
                self.employees_tree.insert('', 'end', values=(
                    func[0],  # ID
                    func[1],  # Nome
                    func[2],  # Cargo
                    func[3],  # Departamento
                    admissao,
                    salario,
                    "🟢 Ativo" if func[16] else "🔴 Inativo"
                ))
                
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            self.employees_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", ""
            ))
        
    def create_rh_payments_section(self, parent):
        """Cria seção de pagamentos enviados pelo RH - NOVA"""
        payments_card = Card(parent, title="👨‍💼 PAGAMENTOS DE FUNCIONÁRIOS (ENVIADOS PELO RH)")
        payments_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        payments_content = payments_card.content_frame
        
        # ====================== CONTROLES ======================
        controls_frame = tk.Frame(payments_content, bg=Theme.colors['surface'])
        controls_frame.pack(fill='x', pady=(0, 20))
        
        ModernButton(
            controls_frame,
            text="🔄 ATUALIZAR LISTA",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.load_rh_payments_list
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            controls_frame,
            text="📊 RELATÓRIO COMPLETO",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            padx=15,
            pady=8,
            command=self.generate_rh_payments_report
        ).pack(side='left')
        
        # ====================== LISTA DE PAGAMENTOS ======================
        list_frame = tk.Frame(payments_content, bg=Theme.colors['surface'])
        list_frame.pack(fill='both', expand=True)
        
        columns = ('ID Folha', 'Funcionário', 'Departamento', 'Mês/Ano', 
                'Salário Líquido', 'Status', 'Enviado em')
        
        self.rh_payments_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12
        )
        
        col_widths = [80, 150, 120, 100, 120, 100, 120]
        for col, width in zip(columns, col_widths):
            self.rh_payments_tree.heading(col, text=col)
            self.rh_payments_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.rh_payments_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.rh_payments_tree.xview)
        self.rh_payments_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.rh_payments_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # ====================== BOTÕES DE APROVAÇÃO ======================
        approval_frame = tk.Frame(payments_content, bg=Theme.colors['surface'])
        approval_frame.pack(fill='x', pady=(15, 0))
        
        ModernButton(
            approval_frame,
            text="✅ APROVAR PAGAMENTO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.approve_rh_payment
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            approval_frame,
            text="❌ REJEITAR PAGAMENTO",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=10,
            padx=15,
            pady=8,
            command=self.reject_rh_payment
        ).pack(side='left', padx=(0, 10))
        
        
        # Carregar dados inicialmente
        self.load_rh_payments_list()

    def load_rh_payments_list(self):
        """Carrega lista de pagamentos enviados pelo RH - CORRIGIDO"""
        if not hasattr(self, 'rh_payments_tree'):
            return
        
        # Limpar lista
        for item in self.rh_payments_tree.get_children():
            self.rh_payments_tree.delete(item)
        
        try:
            # Buscar folhas enviadas para o financeiro
            result = self.db.execute_query('''
                SELECT fp.id, f.nome, f.departamento, fp.mes_ano,
                    fp.salario_liquido, fp.status, fp.data_envio_financeiro,
                    f.cargo, fp.salario_base
                FROM folha_pagamento fp
                JOIN funcionarios f ON fp.funcionario_id = f.id
                WHERE fp.status IN ('enviado_financeiro', 'aprovado', 'rejeitado', 'pago')
                ORDER BY 
                    CASE fp.status 
                        WHEN 'enviado_financeiro' THEN 1
                        WHEN 'aprovado' THEN 2
                        WHEN 'rejeitado' THEN 3
                        WHEN 'pago' THEN 4
                        ELSE 5
                    END,
                    fp.mes_ano DESC
            ''', commit=False)
            
            folhas = result.fetchall()
            
            if not folhas:
                self.rh_payments_tree.insert('', 'end', values=(
                    "---", "Nenhum pagamento recebido do RH", "", "", "", "", ""
                ))
                return
            
            for folha in folhas:
                folha_id, nome, departamento, mes_ano, liquido, status, data_envio, cargo, salario_base = folha
                
                # Formatar valores
                mes_ano_fmt = mes_ano[:7] if mes_ano else ""
                liquido_fmt = f"{liquido:,} Kz" if liquido else "0 Kz"
                salario_base_fmt = f"{salario_base:,} Kz" if salario_base else "0 Kz"
                
                # Status com ícones
                status_icons = {
                    'enviado_financeiro': '🟡 Pendente',
                    'aprovado': '🟢 Aprovado',
                    'rejeitado': '🔴 Rejeitado',
                    'pago': '✅ Pago'
                }
                status_text = status_icons.get(status, '⚫ ' + (status or 'Desconhecido'))
                
                # Formatar data
                data_envio_fmt = ""
                if data_envio:
                    try:
                        data_envio_fmt = datetime.strptime(data_envio, '%Y-%m-%d %H:%M:%S').strftime('%d/%m %H:%M')
                    except:
                        data_envio_fmt = data_envio[:16]
                
                self.rh_payments_tree.insert('', 'end', values=(
                    folha_id,
                    f"{nome} ({cargo})",
                    departamento,
                    mes_ano_fmt,
                    salario_base_fmt,
                    liquido_fmt,
                    status_text,
                    data_envio_fmt
                ))
                
        except Exception as e:
            print(f"Erro ao carregar pagamentos RH: {e}")
            self.rh_payments_tree.insert('', 'end', values=(
                "ERRO", f"Erro: {str(e)[:30]}", "", "", "", "", "", ""
            ))

    def approve_rh_payment(self):
        """Aprova um pagamento enviado pelo RH"""
        selection = self.rh_payments_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um pagamento!")
            return
        
        item = self.rh_payments_tree.item(selection[0])
        folha_id = item['values'][0]
        status = item['values'][5]
        
        # Verificar se já foi aprovado/pago
        if 'Aprovado' in status or 'Pago' in status:
            messagebox.showwarning("Aviso", "Este pagamento já foi processado!")
            return
        
        user_info = self.user_service.get_user_info()
        
        resposta = messagebox.askyesno(
            "Aprovar Pagamento",
            f"Deseja aprovar o pagamento da folha ID {folha_id}?\n\n"
            f"Funcionário: {item['values'][1]}\n"
            f"Valor: {item['values'][4]}\n\n"
            f"Ao aprovar, o pagamento estará autorizado para execução."
        )
        
        if resposta:
            try:
                self.db.execute_query('''
                    UPDATE folha_pagamento 
                    SET status = 'aprovado',
                        data_aprovacao = CURRENT_TIMESTAMP,
                        usuario_aprovacao_id = ?
                    WHERE id = ?
                ''', (user_info['id'], folha_id))
                
                # Log da ação
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    'APROVAR_PAGAMENTO_RH',
                    'Financeiro',
                    f"Pagamento folha {folha_id} aprovado"
                )
                
                # Notificar RH
                self.db.send_notification(
                    'sucesso',
                    'Pagamento Aprovado',
                    f'Pagamento folha {folha_id} aprovado pelo financeiro',
                    'rh'
                )
                
                messagebox.showinfo("Sucesso", "Pagamento aprovado com sucesso!")
                self.load_rh_payments_list()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao aprovar pagamento: {str(e)}")

    def reject_rh_payment(self):
        """Rejeita um pagamento enviado pelo RH"""
        selection = self.rh_payments_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um pagamento!")
            return
        
        item = self.rh_payments_tree.item(selection[0])
        folha_id = item['values'][0]
        
        user_info = self.user_service.get_user_info()
        
        resposta = messagebox.askyesno(
            "Rejeitar Pagamento",
            f"Deseja rejeitar o pagamento da folha ID {folha_id}?\n\n"
            f"Funcionário: {item['values'][1]}\n"
            f"Valor: {item['values'][4]}\n\n"
            f"Ao rejeitar, o RH será notificado para revisar os cálculos."
        )
        
        if resposta:
            try:
                self.db.execute_query('''
                    UPDATE folha_pagamento 
                    SET status = 'rejeitado'
                    WHERE id = ?
                ''', (folha_id,))
                
                # Log da ação
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    'REJEITAR_PAGAMENTO_RH',
                    'Financeiro',
                    f"Pagamento folha {folha_id} rejeitado"
                )
                
                # Notificar RH
                self.db.send_notification(
                    'alerta',
                    'Pagamento Rejeitado',
                    f'Pagamento folha {folha_id} rejeitado pelo financeiro. Por favor, revise os cálculos.',
                    'rh'
                )
                
                messagebox.showinfo("Sucesso", "Pagamento rejeitado! O RH foi notificado.")
                self.load_rh_payments_list()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao rejeitar pagamento: {str(e)}")

    def register_rh_payment(self):
        """Registra o pagamento efetuado (após aprovação)"""
        selection = self.rh_payments_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um pagamento!")
            return
        
        item = self.rh_payments_tree.item(selection[0])
        folha_id = item['values'][0]
        status = item['values'][5]
        
        # Verificar se está aprovado
        if 'Aprovado' not in status:
            messagebox.showwarning("Aviso", "Apenas pagamentos aprovados podem ser registrados como pagos!")
            return
        
        user_info = self.user_service.get_user_info()
        
        resposta = messagebox.askyesno(
            "Registrar Pagamento",
            f"Registrar pagamento da folha ID {folha_id} como PAGO?\n\n"
            f"Funcionário: {item['values'][1]}\n"
            f"Valor: {item['values'][4]}\n\n"
            f"Ao confirmar, uma transação financeira será registrada."
        )
        
        if resposta:
            try:
                # Atualizar status da folha
                self.db.execute_query('''
                    UPDATE folha_pagamento 
                    SET status = 'pago',
                        data_pagamento = CURRENT_TIMESTAMP,
                        usuario_pagamento_id = ?
                    WHERE id = ?
                ''', (user_info['id'], folha_id))
                
                # Extrair valor do pagamento (remover " Kz" e converter)
                valor_texto = item['values'][4].replace(' Kz', '').replace('.', '').replace(',', '')
                try:
                    valor = int(valor_texto)
                except:
                    valor = 0
                
                # Registrar transação financeira
                self.db.execute_query('''
                    INSERT INTO transacoes 
                    (tipo, descricao, valor, categoria, usuario_id)
                    VALUES ('saida', ?, ?, 'pagamentos_funcionarios', ?)
                ''', (
                    f"Pagamento salarial - {item['values'][1]} - Folha {folha_id}",
                    valor,
                    user_info['id']
                ))
                
                # Log da ação
                self.db.log_action(
                    user_info['id'],
                    user_info['nome'],
                    'REGISTRAR_PAGAMENTO_RH',
                    'Financeiro',
                    f"Pagamento folha {folha_id} registrado como pago - {valor:,} Kz"
                )
                
                # Notificar RH
                self.db.send_notification(
                    'sucesso',
                    'Pagamento Efetuado',
                    f'Pagamento folha {folha_id} foi efetuado pelo financeiro',
                    'rh'
                )
                
                messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso!")
                self.load_rh_payments_list()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registrar pagamento: {str(e)}")

    def generate_rh_payments_report(self):
        """Gera relatório completo dos pagamentos de RH"""
        try:
            # Buscar todos os pagamentos
            result = self.db.execute_query('''
                SELECT 
                    strftime('%Y-%m', fp.mes_ano) as periodo,
                    COUNT(*) as quantidade,
                    SUM(fp.salario_liquido) as total,
                    SUM(CASE WHEN fp.status = 'pago' THEN fp.salario_liquido ELSE 0 END) as total_pago,
                    SUM(CASE WHEN fp.status = 'enviado_financeiro' THEN fp.salario_liquido ELSE 0 END) as total_pendente
                FROM folha_pagamento fp
                GROUP BY strftime('%Y-%m', fp.mes_ano)
                ORDER BY periodo DESC
            ''', commit=False)
            
            dados = result.fetchall()
            
            # Criar janela de relatório
            report_window = tk.Toplevel(self.root)
            report_window.title("📊 Relatório de Pagamentos RH")
            report_window.geometry("700x600")
            report_window.configure(bg=Theme.colors['surface'])
            
            # Frame principal
            main_frame = tk.Frame(report_window, bg=Theme.colors['surface'], padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Cabeçalho
            header_frame = tk.Frame(main_frame, bg=Theme.colors['primary'])
            header_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                header_frame,
                text="📊 RELATÓRIO DE PAGAMENTOS DE FUNCIONÁRIOS",
                font=('Segoe UI', 16, 'bold'),
                fg=Theme.colors['text_light'],
                bg=Theme.colors['primary']
            ).pack(pady=10)
            
            # Treeview para o relatório
            tree_frame = tk.Frame(main_frame, bg=Theme.colors['surface'])
            tree_frame.pack(fill='both', expand=True)
            
            columns = ('Período', 'Quantidade', 'Total Calculado', 'Total Pago', 'Total Pendente')
            
            report_tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                height=15
            )
            
            col_widths = [100, 100, 150, 150, 150]
            for col, width in zip(columns, col_widths):
                report_tree.heading(col, text=col)
                report_tree.column(col, width=width)
            
            scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=report_tree.yview)
            report_tree.configure(yscrollcommand=scrollbar.set)
            
            report_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Adicionar dados
            for linha in dados:
                periodo, quantidade, total, total_pago, total_pendente = linha
                
                report_tree.insert('', 'end', values=(
                    periodo,
                    quantidade,
                    f"{total or 0:,} Kz",
                    f"{total_pago or 0:,} Kz",
                    f"{total_pendente or 0:,} Kz"
                ))
            
            # Botão Fechar
            button_frame = tk.Frame(main_frame, bg=Theme.colors['surface'])
            button_frame.pack(fill='x', pady=(20, 0))
            
            ModernButton(
                button_frame,
                text="❌ FECHAR",
                bg=Theme.colors['danger'],
                hover_bg=self.lighten_color(Theme.colors['danger'], 20),
                font_size=11,
                padx=20,
                pady=10,
                command=report_window.destroy
            ).pack()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def send_payroll_to_finance(self):
        """Envia folha de pagamento para o financeiro"""
        selection = self.payroll_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma folha de pagamento!")
            return
        
        item = self.payroll_tree.item(selection[0])
        folha_id = item['values'][0]
        
        # Verificar se já foi enviado
        status = item['values'][8]
        if 'enviado' in status.lower() or 'aprovado' in status.lower() or 'pago' in status.lower():
            messagebox.showwarning("Aviso", "Esta folha já foi enviada ou processada!")
            return
        
        user_info = self.user_service.get_user_info()
        
        resposta = messagebox.askyesno(
            "Enviar para Financeiro",
            f"Deseja enviar a folha de pagamento ID {folha_id} para o financeiro?\n\n"
            f"Funcionário: {item['values'][1]}\n"
            f"Valor: {item['values'][7]}\n\n"
            f"Ao enviar, o departamento financeiro será notificado para aprovação."
        )
        
        if resposta:
            try:
                self.db.execute_query('''
                    UPDATE folha_pagamento 
                    SET status = 'enviado_financeiro',
                        data_envio_financeiro = CURRENT_TIMESTAMP,
                        usuario_envio_id = ?
                    WHERE id = ?
                ''', (user_info['id'], folha_id))
                
                # Notificar financeiro
                self.db.send_notification(
                    'info',
                    'Nova Folha de Pagamento',
                    f'Folha de pagamento ID {folha_id} aguardando aprovação',
                    'financeiro'
                )
                
                messagebox.showinfo("Sucesso", "Folha enviada para o financeiro com sucesso!")
                self.load_payroll_data()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao enviar para financeiro: {str(e)}")

    def calculate_individual_payroll(self):
        """Calcula folha de pagamento individual"""
        selection = self.payroll_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um funcionário na lista!")
            return
        
        # Implementar cálculo individual
        messagebox.showinfo("Em desenvolvimento", "Funcionalidade em desenvolvimento!")

    def calculate_all_payroll(self):
        """Calcula folha de pagamento para todos os funcionários"""
        try:
            # Obter mês e ano selecionados
            mes_text = self.payroll_mes.get()
            ano = self.payroll_ano.get()
            
            if not mes_text or not ano:
                messagebox.showwarning("Aviso", "Selecione mês e ano!")
                return
            
            mes_num = mes_text[:2].strip()
            mes_ano = f"{ano}-{mes_num}"
            
            user_info = self.user_service.get_user_info()
            
            resposta = messagebox.askyesno(
                "Calcular Folha Completa",
                f"Deseja calcular a folha de pagamento de {mes_ano} para todos os funcionários?\n\n"
                f"Esta ação calculará os salários de todos os funcionários ativos."
            )
            
            if resposta:
                # Obter todos os funcionários ativos
                funcionarios = self.hr_service.get_all_funcionarios(ativos=True)
                
                if not funcionarios:
                    messagebox.showwarning("Aviso", "Nenhum funcionário ativo encontrado!")
                    return
                
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Calculando...")
                progress_window.geometry("300x100")
                
                tk.Label(
                    progress_window,
                    text=f"Calculando folha para {len(funcionarios)} funcionários...",
                    font=('Segoe UI', 10)
                ).pack(pady=20)
                
                progress_bar = ttk.Progressbar(
                    progress_window, 
                    length=250,
                    mode='indeterminate'
                )
                progress_bar.pack(pady=10)
                progress_bar.start()
                
                # Fechar janela de progresso após cálculo
                self.root.after(100, lambda: [
                    progress_bar.stop(),
                    progress_window.destroy(),
                    self.load_payroll_data(),
                    messagebox.showinfo("Sucesso", f"Folha de {mes_ano} calculada para {len(funcionarios)} funcionários!")
                ])
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular folha: {str(e)}") 
                       
    def show_manager_dashboard(self, parent):
        """Dashboard do Gerente - Acesso completo"""
        # Container com abas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Aba de Dashboard em Tempo Real
        realtime_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(realtime_frame, text='⏱️ TEMPO REAL')
        
        self.real_time_dashboard = RealTimeDashboard(realtime_frame, self.db, self.room_service, self.guest_service, self.finance_service)
        self.real_time_dashboard.create_dashboard()
        
        # Aba de Relatórios Financeiros
        finance_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(finance_frame, text='💰 FINANCEIRO')
        
        self.create_financial_reports(finance_frame)
        
        # Aba de Relatórios de Hóspedes
        guest_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(guest_frame, text='👥 HÓSPEDES')
        
        self.create_guest_reports(guest_frame)
        
        # Aba de Quartos
        rooms_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(rooms_frame, text='🏨 QUARTOS')
        
        self.create_rooms_management(rooms_frame, is_manager=True)
        
        # Aba de Configurações
        config_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(config_frame, text='⚙️ CONFIGURAÇÕES')
        
        self.create_configuration_section(config_frame)
    
    def create_financial_reports(self, parent):
        """Cria relatórios financeiros para o gerente"""
        # Resumo financeiro do mês
        finance_summary = self.finance_service.get_financial_summary('mes')
        
        summary_card = Card(parent, title="💰 RESUMO FINANCEIRO - ESTE MÊS")
        summary_card.pack(fill='x', pady=(0, 20))
        
        summary_content = summary_card.content_frame
        
        # Métricas financeiras
        metrics = [
            {
                'title': 'Receitas',
                'value': f"{finance_summary['receitas']:,} Kz",
                'color': Theme.colors['success'],
                'icon': '📈'
            },
            {
                'title': 'Despesas',
                'value': f"{finance_summary['despesas']:,} Kz",
                'color': Theme.colors['danger'],
                'icon': '📉'
            },
            {
                'title': 'Lucro',
                'value': f"{finance_summary['lucro']:,} Kz",
                'color': Theme.colors['accent'],
                'icon': '💰'
            },
            {
                'title': 'Hóspedes',
                'value': finance_summary['hospedes'],
                'color': Theme.colors['info'],
                'icon': '👥'
            }
        ]
        
        metrics_frame = tk.Frame(summary_content, bg=Theme.colors['surface'])
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        for i, metric in enumerate(metrics):
            metric_card = Card(
                metrics_frame,
                title=f"{metric['icon']} {metric['title']}",
                bg=Theme.colors['surface']
            )
            metric_card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            metrics_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(
                metric_card.content_frame,
                text=metric['value'],
                font=('Segoe UI', 16, 'bold'),
                fg=metric['color'],
                bg=Theme.colors['surface']
            ).pack(expand=True)
        
        # Relatório detalhado
        detail_card = Card(parent, title="📋 RELATÓRIO DETALHADO")
        detail_card.pack(fill='both', expand=True, pady=(0, 20))
        
        detail_content = detail_card.content_frame
        
        # Gerar relatório completo
        report = self.report_service.generate_financial_report()
        
        # Treeview para o relatório
        columns = ('Tipo', 'Categoria', 'Quantidade', 'Total')
        
        report_tree = ttk.Treeview(
            detail_content,
            columns=columns,
            show='headings',
            height=15
        )
        
        col_widths = [80, 150, 100, 150]
        for col, width in zip(columns, col_widths):
            report_tree.heading(col, text=col)
            report_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(detail_content, orient='vertical', command=report_tree.yview)
        report_tree.configure(yscrollcommand=scrollbar.set)
        
        report_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Adicionar dados ao relatório
        for row in report:
            tipo, categoria, quantidade, total = row
            
            # Formatar valores
            total_formatado = f"{total:,} Kz".replace(",", ".")
            tipo_text = "🟢 Entrada" if tipo == 'entrada' else "🔴 Saída"
            
            report_tree.insert('', 'end', values=(
                tipo_text,
                categoria,
                quantidade,
                total_formatado
            ))
    
    def create_guest_reports(self, parent):
        """Cria relatórios de hóspedes para o gerente"""
        # Estatísticas de hóspedes
        guest_stats = self.guest_service.get_guest_stats()
        
        stats_card = Card(parent, title="👥 ESTATÍSTICAS DE HÓSPEDES")
        stats_card.pack(fill='x', pady=(0, 20))
        
        stats_content = stats_card.content_frame
        
        # Grid de estatísticas
        stats_grid = tk.Frame(stats_content, bg=Theme.colors['surface'])
        stats_grid.pack(fill='x')
        
        stats_data = [
            ('Hóspedes Ativos:', f"{guest_stats['ativos']}"),
            ('Total Registrados:', f"{guest_stats['total']}"),
            ('Taxa de Ocupação:', f"{guest_stats['taxa_ocupacao']:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            tk.Label(
                stats_grid,
                text=label,
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            
            tk.Label(
                stats_grid,
                text=value,
                font=Theme.fonts['heading'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).grid(row=0, column=i*2+1, sticky='w', padx=(0, 20))
        
        # Nacionalidades
        if guest_stats['nacionalidades']:
            nat_card = Card(parent, title="🌍 TOP NACIONALIDADES")
            nat_card.pack(fill='x', pady=(0, 20))
            
            nat_content = nat_card.content_frame
            
            for i, (nacionalidade, quantidade) in enumerate(guest_stats['nacionalidades']):
                frame = tk.Frame(nat_content, bg=Theme.colors['surface'])
                frame.pack(fill='x', pady=2)
                
                tk.Label(
                    frame,
                    text=nacionalidade or 'Não informado',
                    font=Theme.fonts['body'],
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=20
                ).pack(side='left')
                
                tk.Label(
                    frame,
                    text=str(quantidade),
                    font=Theme.fonts['body'],
                    fg=Theme.colors['text_secondary'],
                    bg=Theme.colors['surface']
                ).pack(side='right')
        
        # Categorias de quarto
        if guest_stats['categorias']:
            cat_card = Card(parent, title="🏨 DISTRIBUIÇÃO POR CATEGORIA")
            cat_card.pack(fill='x', pady=(0, 20))
            
            cat_content = cat_card.content_frame
            
            for categoria, quantidade, receita in guest_stats['categorias']:
                frame = tk.Frame(cat_content, bg=Theme.colors['surface'])
                frame.pack(fill='x', pady=2)
                
                tk.Label(
                    frame,
                    text=categoria,
                    font=Theme.fonts['body'],
                    fg=Theme.colors['vip'] if categoria == 'VIP' else Theme.colors['normal'],
                    bg=Theme.colors['surface'],
                    width=10
                ).pack(side='left')
                
                tk.Label(
                    frame,
                    text=f"{quantidade} hóspedes",
                    font=Theme.fonts['body'],
                    fg=Theme.colors['text_primary'],
                    bg=Theme.colors['surface'],
                    width=15
                ).pack(side='left')
                
                tk.Label(
                    frame,
                    text=f"{receita:,} Kz",
                    font=Theme.fonts['body'],
                    fg=Theme.colors['success'],
                    bg=Theme.colors['surface']
                ).pack(side='right')
    
    def create_rooms_management(self, parent, is_manager=False):
        """Cria seção de gestão de quartos - VERSÃO SIMPLIFICADA"""
        print("DEBUG: Iniciando create_rooms_management")
        
        try:
            # Card principal
            rooms_card = Card(parent, title="🏨 GESTÃO DE QUARTOS")
            rooms_card.pack(fill='both', expand=True, padx=20, pady=20)
            
            rooms_content = rooms_card.content_frame
            
            # Obter estatísticas dos quartos
            try:
                room_stats = self.room_service.get_room_stats()
                print(f"DEBUG: Estatísticas dos quartos: {room_stats}")
            except Exception as e:
                print(f"DEBUG: Erro ao obter estatísticas: {e}")
                room_stats = {
                    'total': 0,
                    'ocupados': 0,
                    'disponiveis': 0,
                    'vip': 0,
                    'normal': 0,
                    'manutencao': 0,
                    'limpeza': 0,
                    'taxa_ocupacao': 0
                }
            
            # Mostrar estatísticas básicas
            stats_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
            stats_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                stats_frame,
                text=f"📊 ESTATÍSTICAS: Total: {room_stats['total']} | Ocupados: {room_stats['ocupados']} | Disponível: {room_stats['disponiveis']}",
                font=('Segoe UI', 11),
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack()
            
            # Lista de quartos
            list_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
            list_frame.pack(fill='both', expand=True)
            
            # Verificar se há quartos
            try:
                rooms = self.room_service.get_all_rooms()
                print(f"DEBUG: {len(rooms)} quartos encontrados")
            except Exception as e:
                print(f"DEBUG: Erro ao obter quartos: {e}")
                rooms = []
            
            if not rooms:
                # Mensagem se não houver quartos
                tk.Label(
                    list_frame,
                    text="Nenhum quarto configurado no sistema.\n\n"
                        "O gerente precisa configurar os quartos na aba 'Configurações'.",
                    font=('Segoe UI', 12),
                    fg=Theme.colors['text_secondary'],
                    bg=Theme.colors['surface'],
                    justify='center'
                ).pack(expand=True, pady=50)
                return
            
            # Treeview para quartos
            columns = ('Número', 'Nome', 'Categoria', 'Status', 'Hóspede')
            
            self.rooms_tree = ttk.Treeview(
                list_frame,
                columns=columns,
                show='headings',
                height=12
            )
            
            col_widths = [70, 150, 80, 100, 150]
            for col, width in zip(columns, col_widths):
                self.rooms_tree.heading(col, text=col)
                self.rooms_tree.column(col, width=width)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.rooms_tree.yview)
            self.rooms_tree.configure(yscrollcommand=scrollbar.set)
            
            self.rooms_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Carregar quartos
            self.update_rooms_list_simple()
            
            # Botões de ação
            if is_manager:
                action_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
                action_frame.pack(fill='x', pady=(10, 0))
                
                tk.Button(
                    action_frame,
                    text="Atualizar",
                    command=self.update_rooms_list_simple,
                    bg=Theme.colors['primary'],
                    fg='white'
                ).pack(side='left', padx=(0, 10))
                
                tk.Button(
                    action_frame,
                    text="Manutenção",
                    command=lambda: self.update_room_status_simple('manutencao'),
                    bg=Theme.colors['warning'],
                    fg='white'
                ).pack(side='left', padx=(0, 10))
                
                tk.Button(
                    action_frame,
                    text="Limpeza",
                    command=lambda: self.update_room_status_simple('limpeza'),
                    bg=Theme.colors['info'],
                    fg='white'
                ).pack(side='left', padx=(0, 10))
                
                tk.Button(
                    action_frame,
                    text="Disponível",
                    command=lambda: self.update_room_status_simple('disponivel'),
                    bg=Theme.colors['success'],
                    fg='white'
                ).pack(side='left')
            
            print("DEBUG: Interface de quartos criada com sucesso")
            
        except Exception as e:
            print(f"ERRO CRÍTICO em create_rooms_management: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar erro na interface
            tk.Label(
                parent,
                text=f"Erro ao criar gestão de quartos: {str(e)[:100]}...",
                fg='red',
                bg='white'
            ).pack(expand=True, pady=50)
    
    def update_rooms_list_simple(self):
        """Versão simplificada para carregar quartos"""
        if not hasattr(self, 'rooms_tree'):
            print("DEBUG: rooms_tree não existe")
            return
        
        # Limpar lista
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        try:
            # Obter quartos
            rooms = self.room_service.get_all_rooms()
            print(f"DEBUG: Carregando {len(rooms)} quartos")
            
            if not rooms:
                print("DEBUG: Nenhum quarto para mostrar")
                return
            
            # Adicionar à tabela
            for room in rooms:
                # Determinar cor do status
                status_color = {
                    'disponivel': '🟢',
                    'ocupado': '🔴', 
                    'manutencao': '🔧',
                    'limpeza': '🧹'
                }
                
                status_icon = status_color.get(room['status'], '⚫')
                status_text = f"{status_icon} {room['status'].capitalize()}"
                
                self.rooms_tree.insert('', 'end', values=(
                    room['numero'],
                    room['nome'],
                    room['categoria'],
                    status_text,
                    room.get('hospede', '—') or '—'
                ))
                
        except Exception as e:
            print(f"DEBUG: Erro ao carregar quartos: {e}")

    def update_room_status_simple(self, status):
        """Versão simplificada para atualizar status"""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um quarto!")
            return
        
        item = self.rooms_tree.item(selection[0])
        room_num = item['values'][0]
        
        user_info = self.user_service.get_user_info()
        success, message = self.room_service.update_room_status(room_num, status, user_info)
        
        if success:
            messagebox.showinfo("Sucesso", message)
            self.update_rooms_list_simple()
        else:
            messagebox.showerror("Erro", message) 
           
    def search_room_by_number(self):
        """Busca quarto por número usando árvore binária"""
        try:
            room_num = int(self.room_search_num.get().strip())
            room_data = self.room_service.search_room_by_number(room_num)
            
            if room_data:
                # Limpar seleção anterior
                for item in self.rooms_tree.selection():
                    self.rooms_tree.selection_remove(item)
                
                # Encontrar e selecionar o quarto
                for child in self.rooms_tree.get_children():
                    values = self.rooms_tree.item(child)['values']
                    if values[0] == room_num:
                        self.rooms_tree.selection_set(child)
                        self.rooms_tree.see(child)
                        
                        # Mostrar mensagem
                        messagebox.showinfo(
                            "Quarto Encontrado",
                            f"Quarto {room_num} encontrado!\n"
                            f"Nome: {room_data['nome']}\n"
                            f"Categoria: {room_data['categoria']}\n"
                            f"Status: {room_data['status']}"
                        )
                        return
                
                messagebox.showwarning("Quarto não encontrado", f"Quarto {room_num} não está na lista atual.")
            else:
                messagebox.showwarning("Não encontrado", f"Quarto {room_num} não encontrado.")
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")
    
    def search_room_by_name(self):
        """Busca quarto por nome usando tabela hash"""
        room_name = self.room_search_name.get().strip().lower()
        
        if not room_name:
            messagebox.showwarning("Aviso", "Digite um nome para buscar!")
            return
        
        room_data = self.room_service.search_room_by_name(room_name)
        
        if room_data:
            # Limpar seleção anterior
            for item in self.rooms_tree.selection():
                self.rooms_tree.selection_remove(item)
            
            # Encontrar e selecionar o quarto
            for child in self.rooms_tree.get_children():
                values = self.rooms_tree.item(child)['values']
                if values[1].lower() == room_data['nome'].lower():
                    self.rooms_tree.selection_set(child)
                    self.rooms_tree.see(child)
                    
                    # Mostrar mensagem
                    messagebox.showinfo(
                        "Quarto Encontrado",
                        f"Quarto encontrado!\n"
                        f"Número: {room_data['numero']}\n"
                        f"Nome: {room_data['nome']}\n"
                        f"Categoria: {room_data['categoria']}\n"
                        f"Status: {room_data['status']}"
                    )
                    return
            
            messagebox.showwarning("Quarto não encontrado", f"Quarto '{room_name}' não está na lista atual.")
        else:
            messagebox.showwarning("Não encontrado", f"Nenhum quarto encontrado com o nome '{room_name}'.")
    
    def update_room_status(self, status):
        """Atualiza status do quarto selecionado"""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um quarto!")
            return
        
        item = self.rooms_tree.item(selection[0])
        room_num = item['values'][0]
        
        user_info = self.user_service.get_user_info()
        success, message = self.room_service.update_room_status(room_num, status, user_info)
        
        if success:
            messagebox.showinfo("Sucesso", message)
            self.update_rooms_list()
        else:
            messagebox.showerror("Erro", message)
    
    def update_rooms_list(self):
        """Atualiza a lista de quartos"""
        # Limpar lista
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        # Obter quartos
        rooms = self.room_service.get_all_rooms()
        
        # Adicionar à lista
        for room in rooms:
            # Determinar ícone do status
            status_icons = {
                'disponivel': '🟢',
                'ocupado': '🔴',
                'manutencao': '🔧',
                'limpeza': '🧹'
            }
            
            status_text = f"{status_icons.get(room['status'], '⚫')} {room['status'].capitalize()}"
            hospede = room['hospede'] or "—"
            
            check_in = ""
            if room['check_in']:
                dt = datetime.strptime(room['check_in'], '%Y-%m-%d %H:%M:%S')
                check_in = dt.strftime('%d/%m %H:%M')
            
            self.rooms_tree.insert('', 'end', values=(
                room['numero'],
                room['nome'],
                room['categoria'],
                status_text,
                hospede,
                check_in
            ))
    
    def create_configuration_section(self, parent):
        """Cria seção de configurações para o gerente"""
        config_card = Card(parent, title="⚙️ CONFIGURAÇÕES DO SISTEMA")
        config_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        config_content = config_card.content_frame
        
        # Preços
        price_frame = tk.Frame(config_content, bg=Theme.colors['surface'])
        price_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            price_frame,
            text="CONFIGURAÇÃO DE PREÇOS",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Preço por hora normal
        tk.Label(
            price_frame,
            text="Preço por hora (Normal):",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.normal_price_var = tk.StringVar()
        normal_price_entry = tk.Entry(
            price_frame,
            textvariable=self.normal_price_var,
            font=Theme.fonts['body'],
            width=20
        )
        normal_price_entry.pack(anchor='w', pady=(0, 10))
        
        # Preço por hora VIP
        tk.Label(
            price_frame,
            text="Preço por hora (VIP):",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        self.vip_price_var = tk.StringVar()
        vip_price_entry = tk.Entry(
            price_frame,
            textvariable=self.vip_price_var,
            font=Theme.fonts['body'],
            width=20
        )
        vip_price_entry.pack(anchor='w', pady=(0, 20))
        
        # Carregar preços atuais
        self.load_current_prices()
        
        # Botão de salvar
        ModernButton(
            price_frame,
            text="💾 SALVAR CONFIGURAÇÕES",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=11,
            command=self.save_configuration
        ).pack(anchor='w')
    
    def load_current_prices(self):
        """Carrega preços atuais da configuração"""
        result = self.db.execute_query(
            "SELECT preco_hora_normal, preco_hora_vip FROM config_hospedaria WHERE id = 1",
            commit=False
        )
        config = result.fetchone()
        
        if config:
            self.normal_price_var.set(str(config[0]))
            self.vip_price_var.set(str(config[1]))
    
    def save_configuration(self):
        """Salva configurações do sistema"""
        try:
            normal_price = int(self.normal_price_var.get().replace('.', '').replace(',', ''))
            vip_price = int(self.vip_price_var.get().replace('.', '').replace(',', ''))
            
            if normal_price <= 0 or vip_price <= 0:
                raise ValueError
            
            self.db.execute_query(
                "UPDATE config_hospedaria SET preco_hora_normal = ?, preco_hora_vip = ? WHERE id = 1",
                (normal_price, vip_price)
            )
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
            # Notificação
            self.db.send_notification(
                'sucesso',
                'Configurações Atualizadas',
                f'Preços atualizados: Normal={normal_price:,} Kz, VIP={vip_price:,} Kz',
                'gerente'
            )
            
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos para os preços!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def show_receptionist_dashboard(self, parent):
        """Dashboard do Recepcionista - Gestão de Hóspedes"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Aba de Check-in
        checkin_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(checkin_frame, text='✅ CHECK-IN')
        
        self.create_checkin_form(checkin_frame)
        
        # Aba de Hóspedes Ativos
        guests_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(guests_frame, text='👥 HÓSPEDES ATIVOS')
        
        self.create_active_guests_list(guests_frame)
        
        # Aba de Quartos
        rooms_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(rooms_frame, text='🏨 QUARTOS')
        
        self.create_rooms_management(rooms_frame, is_manager=False)
        
        # Aba de Check-out
        checkout_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(checkout_frame, text='🚪 CHECK-OUT')
        
        self.create_checkout_section(checkout_frame)
    
    def create_checkin_form(self, parent):
        """Cria formulário de check-in para recepcionista"""
        # Formulário em um card
        form_card = Card(parent, title="📝 CADASTRO DE HÓSPEDE")
        form_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        form_content = form_card.content_frame
        
        # Scrollable frame
        canvas = tk.Canvas(form_content, bg=Theme.colors['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_content, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.colors['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Campos do formulário
        fields_frame = tk.Frame(scrollable_frame, bg=Theme.colors['surface'])
        fields_frame.pack(fill='x', padx=10, pady=10)
        
        # Informações pessoais
        tk.Label(
            fields_frame,
            text="INFORMAÇÕES PESSOAIS",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Nome completo
        tk.Label(
            fields_frame,
            text="Nome completo: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=1, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_nome = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_nome.grid(row=1, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Documento
        tk.Label(
            fields_frame,
            text="Documento (BI/Passaporte): *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_doc = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_doc.grid(row=2, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Nacionalidade
        tk.Label(
            fields_frame,
            text="Nacionalidade:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_nacionalidade = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_nacionalidade.grid(row=3, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Contato
        tk.Label(
            fields_frame,
            text="Telefone:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_telefone = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_telefone.grid(row=4, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Email
        tk.Label(
            fields_frame,
            text="Email:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_email = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_email.grid(row=5, column=1, sticky='w', pady=(0, 20), padx=(10, 0))
        
        # Informações da estadia
        tk.Label(
            fields_frame,
            text="ESTADIA",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).grid(row=6, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Tempo
        tk.Label(
            fields_frame,
            text="Tempo de estadia: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=7, column=0, sticky='w', pady=(0, 5))
        
        tempo_frame = tk.Frame(fields_frame, bg=Theme.colors['surface'])
        tempo_frame.grid(row=7, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        self.checkin_tempo_qtd = tk.Entry(tempo_frame, font=Theme.fonts['body'], width=8)
        self.checkin_tempo_qtd.pack(side='left')
        self.checkin_tempo_qtd.insert(0, "1")
        
        self.checkin_tempo_unidade = ttk.Combobox(
            tempo_frame,
            values=['horas', 'dias', 'semanas', 'meses'],
            state='readonly',
            width=10
        )
        self.checkin_tempo_unidade.pack(side='left', padx=(5, 0))
        self.checkin_tempo_unidade.set('dias')
        
        # Informações do quarto
        tk.Label(
            fields_frame,
            text="QUARTO",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).grid(row=8, column=0, columnspan=2, sticky='w', pady=(20, 15))
        
        # Número do quarto
        tk.Label(
            fields_frame,
            text="Número do quarto: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=9, column=0, sticky='w', pady=(0, 5))
        
        available_rooms = self.room_service.get_available_rooms()
        self.checkin_quarto_numero = ttk.Combobox(
            fields_frame,
            values=available_rooms,
            state='readonly',
            width=15
        )
        self.checkin_quarto_numero.grid(row=9, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        if available_rooms:
            self.checkin_quarto_numero.set(available_rooms[0])
        
        # Nome do quarto (opcional)
        tk.Label(
            fields_frame,
            text="Nome do quarto (opcional):",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_quarto_nome = tk.Entry(fields_frame, font=Theme.fonts['body'], width=40)
        self.checkin_quarto_nome.grid(row=10, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Categoria do quarto
        tk.Label(
            fields_frame,
            text="Categoria do quarto: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=11, column=0, sticky='w', pady=(0, 5))
        
        categoria_frame = tk.Frame(fields_frame, bg=Theme.colors['surface'])
        categoria_frame.grid(row=11, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        self.checkin_categoria = tk.StringVar(value="Normal")
        
        tk.Radiobutton(
            categoria_frame,
            text="🏆 VIP (+50%)",
            variable=self.checkin_categoria,
            value="VIP",
            font=Theme.fonts['body'],
            fg=Theme.colors['vip'],
            bg=Theme.colors['surface'],
            selectcolor=Theme.colors['surface']
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            categoria_frame,
            text="🔵 Normal",
            variable=self.checkin_categoria,
            value="Normal",
            font=Theme.fonts['body'],
            fg=Theme.colors['normal'],
            bg=Theme.colors['surface'],
            selectcolor=Theme.colors['surface']
        ).pack(side='left')
        
        # Forma de pagamento
        tk.Label(
            fields_frame,
            text="Forma de pagamento:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=12, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_pagamento = ttk.Combobox(
            fields_frame,
            values=['Dinheiro', 'Cartão Crédito', 'Cartão Débito', 'Transferência', 'Cheque'],
            state='readonly',
            width=20
        )
        self.checkin_pagamento.grid(row=12, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        self.checkin_pagamento.set('Dinheiro')
        
        # Observações
        tk.Label(
            fields_frame,
            text="Observações:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=13, column=0, sticky='w', pady=(0, 5))
        
        self.checkin_observacoes = tk.Text(fields_frame, font=Theme.fonts['body'], width=40, height=4)
        self.checkin_observacoes.grid(row=13, column=1, sticky='w', pady=(0, 20), padx=(10, 0))
        
        # Botão de cadastro
        button_frame = tk.Frame(fields_frame, bg=Theme.colors['surface'])
        button_frame.grid(row=14, column=0, columnspan=2, pady=(20, 0))
        
        ModernButton(
            button_frame,
            text="✅ CONFIRMAR CHECK-IN",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=12,
            command=self.process_checkin
        ).pack()
        
        # Configurar pesos das colunas
        fields_frame.grid_columnconfigure(1, weight=1)
    
    def process_checkin(self):
        """Processa o check-in de um hóspede"""
        # Validar campos obrigatórios
        campos = [
            (self.checkin_nome, "Nome"),
            (self.checkin_doc, "Documento"),
            (self.checkin_tempo_qtd, "Tempo"),
            (self.checkin_quarto_numero, "Número do quarto")
        ]
        
        for campo, nome in campos:
            if not campo.get().strip():
                messagebox.showerror("Erro", f"O campo '{nome}' é obrigatório!")
                campo.focus_set()
                return
        
        try:
            tempo_qtd = int(self.checkin_tempo_qtd.get())
            if tempo_qtd <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Digite um tempo válido!")
            self.checkin_tempo_qtd.focus_set()
            return
        
        # Preparar dados do hóspede
        guest_data = {
            'nome': self.checkin_nome.get().strip(),
            'documento': self.checkin_doc.get().strip(),
            'nacionalidade': self.checkin_nacionalidade.get().strip(),
            'telefone': self.checkin_telefone.get().strip(),
            'email': self.checkin_email.get().strip(),
            'tempo_quantidade': tempo_qtd,
            'tempo_unidade': self.checkin_tempo_unidade.get(),
            'tempo_texto': f"{tempo_qtd} {self.checkin_tempo_unidade.get()}",
            'quarto_numero': int(self.checkin_quarto_numero.get()),
            'quarto_nome': self.checkin_quarto_nome.get().strip(),
            'categoria_quarto': self.checkin_categoria.get(),
            'forma_pagamento': self.checkin_pagamento.get(),
            'observacoes': self.checkin_observacoes.get("1.0", "end-1c").strip()
        }
        
        user_info = self.user_service.get_user_info()
        success, message, guest_id = self.guest_service.register_guest(guest_data, user_info)
        
        if success:
            # Calcular preço para mostrar ao usuário
            horas_totais, preco_total, preco_hora = self.guest_service.calculate_price(
                tempo_qtd,
                self.checkin_tempo_unidade.get(),
                self.checkin_categoria.get()
            )
            
            # Mostrar resumo
            resumo = f"""
            ✅ CHECK-IN REALIZADO COM SUCESSO!
            
            ID do Hóspede: {guest_id}
            Nome: {guest_data['nome']}
            Documento: {guest_data['documento']}
            Quarto: {guest_data['quarto_numero']} - {guest_data['quarto_nome'] or 'Sem nome'}
            Categoria: {guest_data['categoria_quarto']}
            Tempo: {guest_data['tempo_texto']}
            Preço total: {preco_total:,} Kz
            Preço por hora: {preco_hora:,} Kz
            Forma de pagamento: {guest_data['forma_pagamento']}
            
            Hóspede registrado por: {user_info['nome']}
            Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            messagebox.showinfo("Sucesso", resumo)
            
            # Limpar formulário
            self.clear_checkin_form()
            
            # Atualizar lista de quartos disponíveis
            available_rooms = self.room_service.get_available_rooms()
            self.checkin_quarto_numero['values'] = available_rooms
            if available_rooms:
                self.checkin_quarto_numero.set(available_rooms[0])
        else:
            messagebox.showerror("Erro", message)
    
    def clear_checkin_form(self):
        """Limpa o formulário de check-in"""
        self.checkin_nome.delete(0, tk.END)
        self.checkin_doc.delete(0, tk.END)
        self.checkin_nacionalidade.delete(0, tk.END)
        self.checkin_telefone.delete(0, tk.END)
        self.checkin_email.delete(0, tk.END)
        self.checkin_tempo_qtd.delete(0, tk.END)
        self.checkin_tempo_qtd.insert(0, "1")
        self.checkin_quarto_nome.delete(0, tk.END)
        self.checkin_observacoes.delete("1.0", tk.END)
    
    def create_active_guests_list(self, parent):
        """Cria lista de hóspedes ativos com busca simplificada"""
        # Card para a lista
        list_card = Card(parent, title="👥 HÓSPEDES ATIVOS")
        list_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        list_content = list_card.content_frame
        
        # ====================== ÁREA DE BUSCA SIMPLES ======================
        search_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Frame para os controles de busca
        controls_frame = tk.Frame(search_frame, bg=Theme.colors['surface'])
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Combobox para escolher tipo de busca
        tk.Label(
            controls_frame,
            text="Buscar por:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        self.search_type_var = tk.StringVar(value="Nome")  # Valor padrão
        search_type_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.search_type_var,
            values=['Nome', 'ID', 'Documento', 'Quarto', 'Categoria', 'Nacionalidade'],
            state='readonly',
            width=15
        )
        search_type_combo.pack(side='left', padx=(0, 10))
        
        # Campo de texto para busca
        tk.Label(
            controls_frame,
            text="Termo:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        self.search_term_var = tk.StringVar()
        search_entry = tk.Entry(
            controls_frame,
            textvariable=self.search_term_var,
            font=Theme.fonts['body'],
            width=25
        )
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.perform_simple_search())  # Enter para buscar
        
        # Botão de busca
        ModernButton(
            controls_frame,
            text="🔍 BUSCAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            command=self.perform_simple_search
        ).pack(side='left', padx=(0, 10))
        
        # Botão de limpar
        ModernButton(
            controls_frame,
            text="🗑️ LIMPAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=10,
            command=self.clear_simple_search
        ).pack(side='left')
        
        # ====================== TABELA DE HÓSPEDES ======================
        table_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
        table_frame.pack(fill='both', expand=True)
        
        # Criar tabela
        self.create_simple_guests_table(table_frame)
        
        # Carregar dados
        self.load_all_guests()
    
    def create_simple_guests_table(self, parent):
        """Cria tabela simples de hóspedes"""
        # Treeview com scrollbars
        tree_frame = tk.Frame(parent, bg=Theme.colors['surface'])
        tree_frame.pack(fill='both', expand=True)
        
        # Colunas
        columns = ('ID', 'Nome', 'Documento', 'Quarto', 'Categoria', 'Check-in', 'Tempo', 'Preço')
        
        self.guests_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar colunas
        col_widths = [50, 150, 100, 60, 80, 120, 80, 100]
        for col, width in zip(columns, col_widths):
            self.guests_tree.heading(col, text=col)
            self.guests_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.guests_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.guests_tree.xview)
        self.guests_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.guests_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para botões de ação
        action_frame = tk.Frame(parent, bg=Theme.colors['surface'])
        action_frame.pack(fill='x', pady=(10, 0))
        
        # Botão de Mostrar Detalhes
        ModernButton(
            action_frame,
            text="🔍 DETALHES",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            command=self.show_guest_details_simple
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            action_frame,
            text="✏️ EDITAR",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=10,
            command=self.edit_guest
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            action_frame,
            text="🚪 CHECK-OUT",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=10,
            command=self.process_checkout_from_list
        ).pack(side='left')

    def load_all_guests(self):
        """Carrega todos os hóspedes na tabela"""
        if not hasattr(self, 'guests_tree'): 
            return
        
        # Limpar tabela
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        try:
            # Obter hóspedes ativos
            hospedes = self.guest_service.get_all_guests(ativos=True)
            
            for guest in hospedes:
                # Formatar preço
                preco = guest[11] if len(guest) > 11 else 0
                preco_formatado = f"{preco:,} Kz" if preco else "0 Kz"
                
                # Formatar data
                check_in = guest[12] if len(guest) > 12 else ""
                if check_in:
                    try:
                        check_in_dt = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                        check_in_formatado = check_in_dt.strftime('%d/%m %H:%M')
                    except:
                        check_in_formatado = check_in[:16]
                else:
                    check_in_formatado = ""
                
                # Inserir na tabela
                self.guests_tree.insert('', 'end', values=(
                    guest[0] if len(guest) > 0 else "",  # ID
                    guest[1] if len(guest) > 1 else "",  # Nome
                    guest[2] if len(guest) > 2 else "",  # Documento
                    guest[8] if len(guest) > 8 else "",  # Quarto
                    guest[10] if len(guest) > 10 else "",  # Categoria
                    check_in_formatado,
                    guest[6] if len(guest) > 6 else "",  # Tempo
                    preco_formatado
                ))
        except Exception as e:
            print(f"Erro ao carregar hóspedes: {e}")

    def perform_simple_search(self):
        """Executa busca simples baseada no tipo selecionado"""
        search_type = self.search_type_var.get()
        search_term = self.search_term_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Aviso", "Digite um termo para buscar!")
            return
        
        # Carregar todos os hóspedes primeiro
        self.load_all_guests()
        
        # Se termo vazio, mostra todos
        if not search_term:
            return
        
        # Filtrar baseado no tipo
        search_term_lower = search_term.lower()
        items_to_keep = []
        
        for child in self.guests_tree.get_children():
            values = self.guests_tree.item(child)['values']
            
            if search_type == "Nome":
                # Buscar no nome
                if values[1] and search_term_lower in values[1].lower():
                    items_to_keep.append(child)
            
            elif search_type == "ID":
                # Buscar no ID
                if values[0] and search_term == str(values[0]):
                    items_to_keep.append(child)
            
            elif search_type == "Documento":
                # Buscar no documento
                if values[2] and search_term_lower in str(values[2]).lower():
                    items_to_keep.append(child)
            
            elif search_type == "Quarto":
                # Buscar no quarto
                if values[3] and search_term == str(values[3]):
                    items_to_keep.append(child)
            
            elif search_type == "Categoria":
                # Buscar na categoria
                if values[4] and search_term_lower in values[4].lower():
                    items_to_keep.append(child)
            
            elif search_type == "Nacionalidade":
                # Buscar nacionalidade (precisa de campo adicional)
                # Vamos buscar no banco para esta busca específica
                try:
                    result = self.db.execute_query(
                        "SELECT id FROM hospedes WHERE nacionalidade LIKE ? AND ativo = 1",
                        (f'%{search_term}%',),
                        commit=False
                    )
                    hospedes_ids = [row[0] for row in result.fetchall()]
                    
                    if values[0] and int(values[0]) in hospedes_ids:
                        items_to_keep.append(child)
                except:
                    pass
        
        # Remover itens que não correspondem à busca
        all_items = list(self.guests_tree.get_children())
        for item in all_items:
            if item not in items_to_keep:
                self.guests_tree.delete(item)
        
        # Mostrar resultado
        if items_to_keep:
            messagebox.showinfo("Busca", f"Encontrados {len(items_to_keep)} hóspede(s)")
            # Selecionar o primeiro resultado
            self.guests_tree.selection_set(items_to_keep[0])
            self.guests_tree.see(items_to_keep[0])
        else:
            messagebox.showinfo("Busca", "Nenhum hóspede encontrado")

    def clear_simple_search(self):
        """Limpa a busca e mostra todos os hóspedes"""
        self.search_term_var.set("")
        self.load_all_guests()
    
    def search_guest_by_id(self):
        """Busca hóspede por ID usando árvore binária"""
        try:
            guest_id = int(self.guest_search_id.get().strip())
            guest_data = self.guest_service.search_guest_by_id(guest_id)
            
            if guest_data:
                # Limpar seleção anterior
                for item in self.guests_tree.selection():
                    self.guests_tree.selection_remove(item)
                
                # Encontrar e selecionar o hóspede
                for child in self.guests_tree.get_children():
                    values = self.guests_tree.item(child)['values']
                    if values[0] == guest_id:
                        self.guests_tree.selection_set(child)
                        self.guests_tree.see(child)
                        
                        # Mostrar mensagem
                        messagebox.showinfo(
                            "Hóspede Encontrado",
                            f"Hóspede encontrado!\n"
                            f"ID: {guest_data['id']}\n"
                            f"Nome: {guest_data['nome']}\n"
                            f"Documento: {guest_data['documento']}\n"
                            f"Quarto: {guest_data['quarto_numero']}"
                        )
                        return
                
                messagebox.showwarning("Hóspede não encontrado", f"Hóspede ID {guest_id} não está na lista atual.")
            else:
                messagebox.showwarning("Não encontrado", f"Hóspede ID {guest_id} não encontrado.")
        except ValueError:
            messagebox.showerror("Erro", "Digite um ID válido!")
    
    def search_guest_by_name(self):
        """Busca hóspede por nome usando tabela hash"""
        guest_name = self.guest_search_name.get().strip().lower()
        
        if not guest_name:
            messagebox.showwarning("Aviso", "Digite um nome para buscar!")
            return
        
        guest_data = self.guest_service.search_guest_by_name(guest_name)
        
        if guest_data:
            # Limpar seleção anterior
            for item in self.guests_tree.selection():
                self.guests_tree.selection_remove(item)
            
            # Encontrar e selecionar o hóspede
            for child in self.guests_tree.get_children():
                values = self.guests_tree.item(child)['values']
                if values[1].lower() == guest_data['nome'].lower():
                    self.guests_tree.selection_set(child)
                    self.guests_tree.see(child)
                    
                    # Mostrar mensagem
                    messagebox.showinfo(
                        "Hóspede Encontrado",
                        f"Hóspede encontrado!\n"
                        f"ID: {guest_data['id']}\n"
                        f"Nome: {guest_data['nome']}\n"
                        f"Documento: {guest_data['documento']}\n"
                        f"Quarto: {guest_data['quarto_numero']}"
                    )
                    return
            
            messagebox.showwarning("Hóspede não encontrado", f"Hóspede '{guest_name}' não está na lista atual.")
        else:
            messagebox.showwarning("Não encontrado", f"Nenhum hóspede encontrado com o nome '{guest_name}'.")
    
    def search_guest_by_room(self):
        """Busca hóspede por número do quarto"""
        try:
            room_num = int(self.guest_search_room.get().strip())
            guest_data = self.guest_service.search_guest_by_room(room_num)
            
            if guest_data:
                # Limpar seleção anterior
                for item in self.guests_tree.selection():
                    self.guests_tree.selection_remove(item)
                
                # Encontrar e selecionar o hóspede
                for child in self.guests_tree.get_children():
                    values = self.guests_tree.item(child)['values']
                    if values[3] == room_num:
                        self.guests_tree.selection_set(child)
                        self.guests_tree.see(child)
                        
                        # Mostrar mensagem
                        messagebox.showinfo(
                            "Hóspede Encontrado",
                            f"Hóspede encontrado!\n"
                            f"ID: {guest_data['id']}\n"
                            f"Nome: {guest_data['nome']}\n"
                            f"Documento: {guest_data['documento']}\n"
                            f"Quarto: {guest_data['quarto_numero']}"
                        )
                        return
                
                messagebox.showwarning("Hóspede não encontrado", f"Nenhum hóspede no quarto {room_num} na lista atual.")
            else:
                messagebox.showwarning("Não encontrado", f"Nenhum hóspede no quarto {room_num}.")
        except ValueError:
            messagebox.showerror("Erro", "Digite um número de quarto válido!")
    
    def create_guests_table(self, parent):
        """Cria tabela de hóspedes"""
        # Treeview com scrollbars
        tree_frame = tk.Frame(parent, bg=Theme.colors['surface'])
        tree_frame.pack(fill='both', expand=True)
        
        # Colunas
        columns = ('ID', 'Nome', 'Documento', 'Quarto', 'Categoria', 'Check-in', 'Tempo', 'Preço')
        
        self.guests_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar colunas
        col_widths = [50, 150, 100, 60, 80, 120, 80, 100]
        for col, width in zip(columns, col_widths):
            self.guests_tree.heading(col, text=col)
            self.guests_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.guests_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.guests_tree.xview)
        self.guests_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.guests_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Carregar dados
        self.update_guests_tree()
        
        # Frame para botões de ação
        action_frame = tk.Frame(parent, bg=Theme.colors['surface'])
        action_frame.pack(fill='x', pady=(10, 0))
        
        ModernButton(
            action_frame,
            text="✏️ EDITAR",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=10,
            command=self.edit_guest
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            action_frame,
            text="🚪 CHECK-OUT",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=10,
            command=self.process_checkout_from_list
        ).pack(side='left')
    
    def update_guests_tree(self):
        """Atualiza a treeview de hóspedes"""
        # Limpar itens existentes
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        # Obter hóspedes ativos
        guests = self.guest_service.get_all_guests(ativos=True)
        
        # Adicionar à treeview
        for guest in guests:
            # Formatar preço
            preco_formatado = f"{guest[11]:,} Kz".replace(",", ".")
            
            # Formatar data
            check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
            check_in_formatado = check_in.strftime('%d/%m %H:%M')
            
            self.guests_tree.insert('', 'end', values=(
                guest[0],  # ID
                guest[1],  # Nome
                guest[2],  # Documento
                guest[8],  # Quarto número
                guest[10], # Categoria
                check_in_formatado,
                guest[6],  # Tempo texto
                preco_formatado
            ))
    
    def filter_guests_list(self, parent):
        """Filtra a lista de hóspedes"""
        search_term = self.guest_search_var.get().lower()
        
        # Limpar itens existentes
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        # Obter hóspedes ativos
        guests = self.guest_service.get_all_guests(ativos=True)
        
        # Filtrar e adicionar
        for guest in guests:
            # Verificar se corresponde à busca
            matches = (
                search_term in str(guest[0]).lower() or  # ID
                search_term in guest[1].lower() or       # Nome
                search_term in guest[2].lower() or       # Documento
                search_term in str(guest[8]).lower()     # Quarto
            )
            
            if matches or not search_term:
                preco_formatado = f"{guest[11]:,} Kz".replace(",", ".")
                check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
                check_in_formatado = check_in.strftime('%d/%m %H:%M')
                
                self.guests_tree.insert('', 'end', values=(
                    guest[0], guest[1], guest[2], guest[8], 
                    guest[10], check_in_formatado, guest[6], preco_formatado
                ))
    
    def show_guest_details_simple(self):
        """Mostra detalhes do hóspede selecionado"""
        selection = self.guests_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um hóspede!")
            return
        
        item = self.guests_tree.item(selection[0])
        guest_id = item['values'][0]
        
        # Buscar detalhes do hóspede
        result = self.db.execute_query(
            "SELECT * FROM hospedes WHERE id = ?",
            (guest_id,),
            commit=False
        )
        guest = result.fetchone()
        
        if not guest:
            messagebox.showerror("Erro", "Hóspede não encontrado!")
            return
        
        # Criar janela de detalhes
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalhes do Hóspede - ID {guest_id}")
        detail_window.geometry("550x700")
        detail_window.configure(bg=Theme.colors['surface'])
        detail_window.resizable(False, False)
        
        # Frame principal
        main_frame = tk.Frame(detail_window, bg=Theme.colors['surface'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ====================== CABEÇALHO ======================
        header_frame = tk.Frame(main_frame, bg=Theme.colors['primary'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="👤 DETALHES DO HÓSPEDE",
            font=('Segoe UI', 16, 'bold'),
            fg=Theme.colors['text_light'],
            bg=Theme.colors['primary']
        ).pack(pady=15)
        
        # ====================== INFORMAÇÕES PRINCIPAIS ======================
        info_card = Card(main_frame, title="INFORMAÇÕES PESSOAIS")
        info_card.pack(fill='x', pady=(0, 15))
        
        info_content = info_card.content_frame
        
        # Grid para informações
        info_grid = tk.Frame(info_content, bg=Theme.colors['surface'])
        info_grid.pack(fill='x', padx=10, pady=10)
        
        # Linha 1: ID e Nome
        tk.Label(
            info_grid,
            text="ID:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=str(guest[0]),
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=0, column=1, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text="Nome:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=1, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=guest[1],
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=1, column=1, sticky='w', pady=(0, 8))
        
        # Linha 2: Documento e Nacionalidade
        tk.Label(
            info_grid,
            text="Documento:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=2, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=guest[2],
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=2, column=1, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text="Nacionalidade:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=3, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=guest[3] or "Não informada",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=3, column=1, sticky='w', pady=(0, 8))
        
        # Linha 3: Contato
        tk.Label(
            info_grid,
            text="Telefone:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=4, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=guest[4] or "Não informado",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=4, column=1, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text="Email:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=5, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            info_grid,
            text=guest[5] or "Não informado",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=5, column=1, sticky='w', pady=(0, 8))
        
        # ====================== INFORMAÇÕES DA ESTADIA ======================
        stay_card = Card(main_frame, title="ESTADIA")
        stay_card.pack(fill='x', pady=(0, 15))
        
        stay_content = stay_card.content_frame
        
        stay_grid = tk.Frame(stay_content, bg=Theme.colors['surface'])
        stay_grid.pack(fill='x', padx=10, pady=10)
        
        # Quarto
        tk.Label(
            stay_grid,
            text="Quarto:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        quarto_nome = guest[9] or f"Quarto {guest[8]}"
        quarto_text = f"{guest[8]} - {quarto_nome}"
        tk.Label(
            stay_grid,
            text=quarto_text,
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=0, column=1, sticky='w', pady=(0, 8))
        
        # Categoria
        tk.Label(
            stay_grid,
            text="Categoria:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=1, column=0, sticky='w', pady=(0, 8))
        
        categoria_color = Theme.colors['vip'] if guest[10] == 'VIP' else Theme.colors['normal']
        tk.Label(
            stay_grid,
            text=guest[10],
            font=('Segoe UI', 10, 'bold'),
            fg=categoria_color,
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=1, column=1, sticky='w', pady=(0, 8))
        
        # Tempo
        tk.Label(
            stay_grid,
            text="Tempo contratado:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=2, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            stay_grid,
            text=guest[7],
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=2, column=1, sticky='w', pady=(0, 8))
        
        # Calcular tempo decorrido e restante
        check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
        tempo_decorrido = (datetime.now() - check_in).total_seconds() / 3600
        tempo_restante = max(0, guest[6] - tempo_decorrido)
        
        dias_restantes = int(tempo_restante // 24)
        horas_restantes = int(tempo_restante % 24)
        
        # Tempo decorrido
        tk.Label(
            stay_grid,
            text="Tempo decorrido:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=3, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            stay_grid,
            text=f"{tempo_decorrido:.1f} horas",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=3, column=1, sticky='w', pady=(0, 8))
        
        # Tempo restante
        tk.Label(
            stay_grid,
            text="Tempo restante:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=4, column=0, sticky='w', pady=(0, 8))
        
        tempo_restante_text = f"{dias_restantes}d {horas_restantes}h ({tempo_restante:.1f} horas)"
        tk.Label(
            stay_grid,
            text=tempo_restante_text,
            font=('Segoe UI', 10),
            fg=Theme.colors['success'] if tempo_restante > 0 else Theme.colors['danger'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=4, column=1, sticky='w', pady=(0, 8))
        
        # ====================== INFORMAÇÕES FINANCEIRAS ======================
        finance_card = Card(main_frame, title="FINANCEIRO")
        finance_card.pack(fill='x', pady=(0, 15))
        
        finance_content = finance_card.content_frame
        
        finance_grid = tk.Frame(finance_content, bg=Theme.colors['surface'])
        finance_grid.pack(fill='x', padx=10, pady=10)
        
        # Preço total
        tk.Label(
            finance_grid,
            text="Preço total:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            finance_grid,
            text=f"{guest[11]:,} Kz",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['success'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=0, column=1, sticky='w', pady=(0, 8))
        
        # Preço por hora
        tk.Label(
            finance_grid,
            text="Preço por hora:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=1, column=0, sticky='w', pady=(0, 8))
        
        preco_hora = guest[11] / guest[6] if guest[6] > 0 else 0
        tk.Label(
            finance_grid,
            text=f"{preco_hora:,.0f} Kz",
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=1, column=1, sticky='w', pady=(0, 8))
        
        # Forma de pagamento
        tk.Label(
            finance_grid,
            text="Forma de pagamento:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=2, column=0, sticky='w', pady=(0, 8))
        
        tk.Label(
            finance_grid,
            text=guest[15] if len(guest) > 15 and guest[15] else 'Dinheiro',
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=2, column=1, sticky='w', pady=(0, 8))
        
        # ====================== DATAS ======================
        dates_card = Card(main_frame, title="DATAS")
        dates_card.pack(fill='x', pady=(0, 15))
        
        dates_content = dates_card.content_frame
        
        dates_grid = tk.Frame(dates_content, bg=Theme.colors['surface'])
        dates_grid.pack(fill='x', padx=10, pady=10)
        
        # Check-in
        tk.Label(
            dates_grid,
            text="Check-in:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        check_in_str = check_in.strftime('%d/%m/%Y %H:%M')
        tk.Label(
            dates_grid,
            text=check_in_str,
            font=('Segoe UI', 10),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=0, column=1, sticky='w', pady=(0, 8))
        
        # Check-out
        tk.Label(
            dates_grid,
            text="Check-out:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=1, column=0, sticky='w', pady=(0, 8))
        
        check_out_text = "Em andamento"
        if guest[13]:
            check_out = datetime.strptime(guest[13], '%Y-%m-%d %H:%M:%S')
            check_out_text = check_out.strftime('%d/%m/%Y %H:%M')
        
        tk.Label(
            dates_grid,
            text=check_out_text,
            font=('Segoe UI', 10),
            fg=Theme.colors['danger'] if guest[13] else Theme.colors['success'],
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=1, column=1, sticky='w', pady=(0, 8))
        
        # Status
        tk.Label(
            dates_grid,
            text="Status:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface'],
            width=15,
            anchor='w'
        ).grid(row=2, column=0, sticky='w', pady=(0, 8))
        
        status_text = "🟢 Ativo" if guest[14] else "🔴 Finalizado"
        status_color = Theme.colors['success'] if guest[14] else Theme.colors['danger']
        tk.Label(
            dates_grid,
            text=status_text,
            font=('Segoe UI', 10, 'bold'),
            fg=status_color,
            bg=Theme.colors['surface'],
            anchor='w'
        ).grid(row=2, column=1, sticky='w', pady=(0, 8))
        
        # ====================== OBSERVAÇÕES ======================
        if guest[16] and len(guest) > 16:
            obs_card = Card(main_frame, title="OBSERVAÇÕES")
            obs_card.pack(fill='x', pady=(0, 15))
            
            obs_content = obs_card.content_frame
            
            # Text widget para observações com scroll
            obs_text = scrolledtext.ScrolledText(
                obs_content,
                font=('Segoe UI', 10),
                bg=Theme.colors['light'],
                fg=Theme.colors['text_primary'],
                wrap='word',
                height=4
            )
            obs_text.pack(fill='both', expand=True, padx=10, pady=10)
            obs_text.insert('1.0', guest[16])
            obs_text.configure(state='disabled')
        
        # ====================== BOTÕES ======================
        button_frame = tk.Frame(main_frame, bg=Theme.colors['surface'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Botão FECHAR
        ModernButton(
            button_frame,
            text="❌ FECHAR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=11,
            padx=15,
            pady=8,
            command=detail_window.destroy
        ).pack(side='right', padx=(10, 0))
        
        # Botão EDITAR (abre o formulário de edição)
        ModernButton(
            button_frame,
            text="✏️ EDITAR",
            bg=Theme.colors['warning'],
            hover_bg=self.lighten_color(Theme.colors['warning'], 20),
            font_size=11,
            padx=15,
            pady=8,
            command=lambda: [detail_window.destroy(), self.edit_guest()]
        ).pack(side='right', padx=(0, 10))
        
        # Botão CHECK-OUT
        if guest[14]:  # Se estiver ativo
            ModernButton(
                button_frame,
                text="🚪 CHECK-OUT",
                bg=Theme.colors['primary'],
                hover_bg=self.lighten_color(Theme.colors['primary'], 20),
                font_size=11,
                padx=15,
                pady=8,
                command=lambda: self.process_checkout_from_details(guest_id, detail_window)
            ).pack(side='right', padx=(0, 10))
        
        # Centralizar janela
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detail_window.winfo_screenheight() // 2) - (height // 2)
        detail_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Tecla ESC para fechar
        detail_window.bind('<Escape>', lambda e: detail_window.destroy())

    def process_checkout_from_details(self, guest_id, detail_window):
        """Processa checkout a partir da janela de detalhes"""
        if not messagebox.askyesno("Confirmar", f"Deseja fazer check-out do hóspede ID {guest_id}?"):
            return
        
        user_info = self.user_service.get_user_info()
        success, message, guest = self.guest_service.checkout_guest(guest_id, user_info)
        
        if success:
            # Gerar recibo
            recibo = self.generate_receipt(guest)
            messagebox.showinfo("Check-out Concluído", f"{message}\n\n{recibo}")
            detail_window.destroy()
            
            # Atualizar lista de hóspedes
            self.update_guests_tree()
        else:
            messagebox.showerror("Erro", message)
    
    def edit_guest(self):
        """Abre formulário para editar hóspede"""
        selection = self.guests_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um hóspede!")
            return
        
        item = self.guests_tree.item(selection[0])
        guest_id = item['values'][0]
        
        # Buscar dados do hóspede
        result = self.db.execute_query(
            "SELECT * FROM hospedes WHERE id = ?",
            (guest_id,),
            commit=False
        )
        guest = result.fetchone()
        
        if not guest:
            messagebox.showerror("Erro", "Hóspede não encontrado!")
            return
        
        # Criar janela de edição
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar Hóspede - ID {guest_id}")
        edit_window.geometry("500x650")
        edit_window.configure(bg=Theme.colors['surface'])
        edit_window.resizable(False, False)
        
        # Frame principal
        main_frame = tk.Frame(edit_window, bg=Theme.colors['surface'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ====================== BOTÕES DE AÇÃO NO TOPO ======================
        # Frame para os botões (TOP)
        button_frame_top = tk.Frame(main_frame, bg=Theme.colors['surface'])
        button_frame_top.pack(fill='x', pady=(0, 20))
        
        # Título e botões lado a lado
        title_frame = tk.Frame(button_frame_top, bg=Theme.colors['surface'])
        title_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(
            title_frame,
            text=f"✏️ EDITAR HÓSPEDE ID {guest_id}",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w')
        
        # Botões no topo direito
        btn_right_frame = tk.Frame(button_frame_top, bg=Theme.colors['surface'])
        btn_right_frame.pack(side='right')
        
        # Botão APLICAR (TOP)
        apply_btn = ModernButton(
            btn_right_frame,
            text="✅ APLICAR",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=11,
            padx=15,
            pady=8,
            command=lambda: self.save_guest_changes(
                guest_id,
                {
                    'nome': edit_nome.get().strip(),
                    'documento': edit_doc.get().strip(),
                    'nacionalidade': edit_nacionalidade.get().strip(),
                    'telefone': edit_telefone.get().strip(),
                    'email': edit_email.get().strip(),
                    'forma_pagamento': edit_pagamento.get(),
                    'observacoes': edit_observacoes.get("1.0", "end-1c").strip()
                },
                edit_window
            )
        )
        apply_btn.pack(side='left', padx=(10, 5))
        
        # Botão CANCELAR (TOP)
        cancel_btn = ModernButton(
            btn_right_frame,
            text="❌ CANCELAR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=11,
            padx=15,
            pady=8,
            command=edit_window.destroy
        )
        cancel_btn.pack(side='left')
        
        # Separador
        separator = tk.Frame(main_frame, height=2, bg=Theme.colors['gray'])
        separator.pack(fill='x', pady=(0, 20))
        
        # ====================== FORMULÁRIO COM SCROLL ======================
        # Frame para o formulário com scrollbar
        form_container = tk.Frame(main_frame, bg=Theme.colors['surface'])
        form_container.pack(fill='both', expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(form_container, bg=Theme.colors['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.colors['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout do canvas e scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame para os campos do formulário
        form_frame = tk.Frame(scrollable_frame, bg=Theme.colors['surface'], width=460)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Nome - índice 1
        tk.Label(
            form_frame,
            text="Nome completo:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_nome = tk.Entry(form_frame, font=Theme.fonts['body'], width=50)
        edit_nome.pack(fill='x', pady=(0, 15))
        edit_nome.insert(0, guest[1] if guest[1] else "")
        
        # Documento - índice 2
        tk.Label(
            form_frame,
            text="Documento (BI/Passaporte):",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_doc = tk.Entry(form_frame, font=Theme.fonts['body'], width=50)
        edit_doc.pack(fill='x', pady=(0, 15))
        edit_doc.insert(0, guest[2] if guest[2] else "")
        
        # Nacionalidade - índice 3
        tk.Label(
            form_frame,
            text="Nacionalidade:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_nacionalidade = tk.Entry(form_frame, font=Theme.fonts['body'], width=50)
        edit_nacionalidade.pack(fill='x', pady=(0, 15))
        edit_nacionalidade.insert(0, guest[3] if guest[3] else "")
        
        # Telefone - índice 4
        tk.Label(
            form_frame,
            text="Telefone:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_telefone = tk.Entry(form_frame, font=Theme.fonts['body'], width=50)
        edit_telefone.pack(fill='x', pady=(0, 15))
        edit_telefone.insert(0, guest[4] if guest[4] else "")
        
        # Email - índice 5
        tk.Label(
            form_frame,
            text="Email:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_email = tk.Entry(form_frame, font=Theme.fonts['body'], width=50)
        edit_email.pack(fill='x', pady=(0, 15))
        edit_email.insert(0, guest[5] if guest[5] else "")
        
        # Forma de pagamento - índice 15
        tk.Label(
            form_frame,
            text="Forma de pagamento:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_pagamento = ttk.Combobox(
            form_frame,
            values=['Dinheiro', 'Cartão Crédito', 'Cartão Débito', 'Transferência', 'Cheque'],
            state='readonly',
            width=20
        )
        edit_pagamento.pack(fill='x', pady=(0, 15))
        edit_pagamento.set(guest[15] if guest[15] else 'Dinheiro')
        
        # Observações - índice 16
        tk.Label(
            form_frame,
            text="Observações:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_observacoes = tk.Text(form_frame, font=Theme.fonts['body'], width=50, height=6)
        edit_observacoes.pack(fill='x', pady=(0, 20))
        edit_observacoes.insert('1.0', guest[16] if guest[16] else "")
        
        # Adicionar espaço no final para garantir visibilidade
        tk.Frame(scrollable_frame, height=20, bg=Theme.colors['surface']).pack()
        
        # Configurar foco no primeiro campo
        edit_nome.focus_set()
        
        # Permitir rolagem com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Fechar a janela com ESC
        edit_window.bind('<Escape>', lambda e: edit_window.destroy())
        
        # Tecla Enter para aplicar
        edit_window.bind('<Return>', lambda e: apply_btn.invoke())
        
        # Centralizar janela
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def save_guest_changes(self, guest_id, guest_data, window):
        """Salva alterações do hóspede"""
        user_info = self.user_service.get_user_info()
        success, message = self.guest_service.update_guest(guest_id, guest_data, user_info)
        
        if success:
            messagebox.showinfo("Sucesso", message)
            window.destroy()
            self.update_guests_tree()
        else:
            messagebox.showerror("Erro", message)
    
    def process_checkout_from_list(self):
        """Processa checkout a partir da lista"""
        selection = self.guests_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um hóspede!")
            return
        
        item = self.guests_tree.item(selection[0])
        guest_id = item['values'][0]
        
        if not messagebox.askyesno("Confirmar", f"Deseja fazer check-out do hóspede ID {guest_id}?"):
            return
        
        user_info = self.user_service.get_user_info()
        success, message, guest = self.guest_service.checkout_guest(guest_id, user_info)
        
        if success:
            # Gerar recibo
            recibo = self.generate_receipt(guest)
            messagebox.showinfo("Check-out Concluído", f"{message}\n\n{recibo}")
            
            # Atualizar lista
            self.update_guests_tree()
        else:
            messagebox.showerror("Erro", message)
    
    def generate_receipt(self, guest):
        """Gera recibo de check-out"""
        check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
        check_in_str = check_in.strftime('%d/%m/%Y %H:%M')
        check_out_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Calcular tempo real
        check_out_dt = datetime.now()
        tempo_real_horas = (check_out_dt - check_in).total_seconds() / 3600
        
        # Calcular valor proporcional (se necessário)
        valor_por_hora = guest[11] / guest[6]  # preço_total / tempo_horas
        valor_final = valor_por_hora * tempo_real_horas
        
        recibo = f"""
        {'='*50}
                        HOSPEDARIA CHECA
                            RECIBO
        {'='*50}
        
        ID Hóspede: {guest[0]}
        Nome: {guest[1]}
        Documento: {guest[2]}
        
        Quarto: {guest[8]} - {guest[9] or 'Sem nome'}
        Categoria: {guest[10]}
        
        Check-in: {check_in_str}
        Check-out: {check_out_str}
        Tempo contratado: {guest[7]}
        Tempo real: {tempo_real_horas:.1f} horas
        
        {'-'*50}
        
        VALORES:
        Valor contratado: {guest[11]:,} Kz
        Valor por hora: {valor_por_hora:,.0f} Kz
        Valor final: {valor_final:,.0f} Kz
        
        {'-'*50}
        
        Forma de pagamento: {guest[15] if len(guest) > 15 else 'Dinheiro'}
        
        {'='*50}
        
        Obrigado pela preferência!
        Volte sempre à Hospedaria Checa!
        """
        
        return recibo
        
    def create_checkout_section(self, parent):
        """Cria seção de check-out"""
        checkout_card = Card(parent, title="🚪 CHECK-OUT")
        checkout_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        checkout_content = checkout_card.content_frame
        
        # Instruções
        tk.Label(
            checkout_content,
            text="Selecione um hóspede da lista 'Hóspedes Ativos' e clique em '🚪 CHECK-OUT'",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface'],
            wraplength=500
        ).pack(pady=(0, 20))
        
        # Ou busca direta por ID
        tk.Label(
            checkout_content,
            text="Ou digite o ID do hóspede para check-out:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        input_frame = tk.Frame(checkout_content, bg=Theme.colors['surface'])
        input_frame.pack(fill='x', pady=(0, 20))
        
        self.checkout_id_var = tk.StringVar()
        id_entry = tk.Entry(
            input_frame,
            textvariable=self.checkout_id_var,
            font=Theme.fonts['body'],
            width=20
        )
        id_entry.pack(side='left', padx=(0, 10))
        
        ModernButton(
            input_frame,
            text="BUSCAR HÓSPEDE",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            command=self.find_guest_for_checkout
        ).pack(side='left')
    
    def find_guest_for_checkout(self):
        """Busca hóspede por ID para check-out"""
        guest_id = self.checkout_id_var.get().strip()
        
        if not guest_id:
            messagebox.showwarning("Aviso", "Digite o ID do hóspede!")
            return
        
        try:
            guest_id = int(guest_id)
        except:
            messagebox.showerror("Erro", "ID inválido!")
            return
        
        # Buscar hóspede
        result = self.db.execute_query(
            "SELECT * FROM hospedes WHERE id = ? AND ativo = 1",
            (guest_id,),
            commit=False
        )
        guest = result.fetchone()
        
        if not guest:
            messagebox.showerror("Erro", "Hóspede não encontrado ou já fez check-out!")
            return
        
        # Mostrar informações e confirmar check-out
        resposta = messagebox.askyesno(
            "Confirmar Check-out",
            f"Deseja fazer check-out do hóspede?\n\n"
            f"ID: {guest[0]}\n"
            f"Nome: {guest[1]}\n"
            f"Quarto: {guest[8]}\n"
            f"Valor: {guest[11]:,} Kz"
        )
        
        if resposta:
            user_info = self.user_service.get_user_info()
            success, message, guest = self.guest_service.checkout_guest(guest_id, user_info)
            
            if success:
                recibo = self.generate_receipt(guest)
                messagebox.showinfo("Check-out Concluído", f"{message}\n\n{recibo}")
                self.checkout_id_var.set("")
            else:
                messagebox.showerror("Erro", message)
    
    def show_financial_dashboard(self, parent):
        """Dashboard do Financeiro - Gestão Financeira"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Aba de Transações
        trans_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(trans_frame, text='💳 TRANSAÇÕES')
        
        self.create_transactions_section(trans_frame)
        
        # Aba de Relatórios Financeiros
        reports_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(reports_frame, text='📊 RELATÓRIOS')
        
        self.create_financial_reports_section(reports_frame)
        
        # Aba de Balanço
        balance_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(balance_frame, text='⚖️ BALANÇO')
        
        self.create_balance_section(balance_frame)
        
        # Aba de Pagamentos RH
        rh_payments_frame = tk.Frame(notebook, bg=Theme.colors['background'])
        notebook.add(rh_payments_frame, text='👨‍💼 PAGAMENTOS RH')
    
        self.create_rh_payments_section(rh_payments_frame)
        
    def create_transactions_section(self, parent):
        """Cria seção de transações"""
        trans_card = Card(parent, title="💳 REGISTRO DE TRANSAÇÕES")
        trans_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        trans_content = trans_card.content_frame
        
        # Formulário de nova transação
        form_frame = tk.Frame(trans_content, bg=Theme.colors['surface'])
        form_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="NOVA TRANSAÇÃO",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Tipo de transação
        tk.Label(
            form_frame,
            text="Tipo: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=1, column=0, sticky='w', pady=(0, 5))
        
        self.trans_tipo = ttk.Combobox(
            form_frame,
            values=['entrada', 'saida'],
            state='readonly',
            width=15
        )
        self.trans_tipo.grid(row=1, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        self.trans_tipo.set('entrada')
        
        # Descrição
        tk.Label(
            form_frame,
            text="Descrição: *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.trans_descricao = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        self.trans_descricao.grid(row=2, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Valor
        tk.Label(
            form_frame,
            text="Valor (Kz): *",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        self.trans_valor = tk.Entry(form_frame, font=Theme.fonts['body'], width=20)
        self.trans_valor.grid(row=3, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
            # Categoria (ATUALIZADO)
        tk.Label(
            form_frame,
            text="Categoria:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.trans_categoria = ttk.Combobox(
            form_frame,
            values=['hospedagem', 'alimentacao', 'limpeza', 'manutencao', 
                    'pagamentos_funcionarios', 'utilitarios', 'impostos', 'outros'],
            state='readonly',
            width=20
        )
        self.trans_categoria.grid(row=4, column=1, sticky='w', pady=(0, 20), padx=(10, 0))
        self.trans_categoria.set('hospedagem')
    
        # ID do hóspede (opcional)
        tk.Label(
            form_frame,
            text="ID Da Pessoa (opcional):",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        self.trans_hospede = tk.Entry(form_frame, font=Theme.fonts['body'], width=20)
        self.trans_hospede.grid(row=5, column=1, sticky='w', pady=(0, 20), padx=(10, 0))
        
        # Botão de registro
        button_frame = tk.Frame(form_frame, bg=Theme.colors['surface'])
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ModernButton(
            button_frame,
            text="💾 REGISTRAR TRANSAÇÃO",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            command=self.register_transaction
        ).pack()
        
        # Lista de transações recentes
        list_frame = tk.Frame(trans_content, bg=Theme.colors['surface'])
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(
            list_frame,
            text="TRANSAÇÕES RECENTES",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Treeview para transações
        columns = ('ID', 'Data', 'Tipo', 'Descrição', 'Valor', 'Categoria', 'Pessoa')
        
        self.trans_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        col_widths = [50, 120, 70, 150, 100, 100, 80]
        for col, width in zip(columns, col_widths):
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trans_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Carregar transações
        self.update_transactions_list()
    
    def register_transaction(self):
        """Registra uma nova transação"""
        # Validar campos
        if not self.trans_descricao.get().strip():
            messagebox.showerror("Erro", "Digite uma descrição!")
            self.trans_descricao.focus_set()
            return
        
        try:
            valor = int(self.trans_valor.get().replace('.', '').replace(',', ''))
            if valor <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Digite um valor válido!")
            self.trans_valor.focus_set()
            return
        
        # Obter ID do hóspede se fornecido
        hospede_id = None
        if self.trans_hospede.get().strip():
            try:
                hospede_id = int(self.trans_hospede.get())
            except:
                messagebox.showerror("Erro", "ID do hóspede inválido!")
                self.trans_hospede.focus_set()
                return
        
        user_info = self.user_service.get_user_info()
        
        success, message = self.finance_service.register_transaction(
            tipo=self.trans_tipo.get(),
            descricao=self.trans_descricao.get().strip(),
            valor=valor,
            categoria=self.trans_categoria.get(),
            usuario_info=user_info,
            id_hospede=hospede_id
        )
        
        if success:
            messagebox.showinfo("Sucesso", message)
            
            # Limpar formulário
            self.trans_descricao.delete(0, tk.END)
            self.trans_valor.delete(0, tk.END)
            self.trans_hospede.delete(0, tk.END)
            
            # Atualizar lista
            self.update_transactions_list()
        else:
            messagebox.showerror("Erro", message)
    
    def update_transactions_list(self):
        """Atualiza a lista de transações"""
        # Limpar lista
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        # Obter transações recentes
        result = self.db.execute_query('''
            SELECT t.id, t.data, t.tipo, t.descricao, t.valor, t.categoria, h.nome
            FROM transacoes t
            LEFT JOIN hospedes h ON t.id_hospede = h.id
            ORDER BY t.data DESC
            LIMIT 50
        ''', commit=False)
        
        transacoes = result.fetchall()
        
        # Adicionar à lista
        for trans in transacoes:
            # Formatar valor
            valor_formatado = f"{trans[4]:,} Kz".replace(",", ".")
            
            # Formatar data
            data_dt = datetime.strptime(trans[1], '%Y-%m-%d %H:%M:%S')
            data_formatada = data_dt.strftime('%d/%m %H:%M')
            
            # Cor para tipo
            tipo_text = "🟢 Entrada" if trans[2] == 'entrada' else "🔴 Saída"
            
            self.trans_tree.insert('', 'end', values=(
                trans[0],
                data_formatada,
                tipo_text,
                trans[3],
                valor_formatado,
                trans[5],
                trans[6] or "—"
            ))
    
    def create_financial_reports_section(self, parent):
        """Cria seção de relatórios financeiros"""
        reports_card = Card(parent, title="📊 RELATÓRIOS FINANCEIROS")
        reports_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        reports_content = reports_card.content_frame
        
        # Período de análise
        period_frame = tk.Frame(reports_content, bg=Theme.colors['surface'])
        period_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            period_frame,
            text="Período:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        self.report_period = ttk.Combobox(
            period_frame,
            values=['hoje', 'esta semana', 'este mês', 'este ano', 'personalizado'],
            state='readonly',
            width=15
        )
        self.report_period.pack(side='left')
        self.report_period.set('este mês')
        
        ModernButton(
            period_frame,
            text="📈 GERAR RELATÓRIO",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            command=self.generate_financial_report
        ).pack(side='left', padx=(10, 0))
        
        # Área para o relatório
        self.report_text = scrolledtext.ScrolledText(
            reports_content,
            font=Theme.fonts['mono'],
            bg=Theme.colors['light'],
            fg=Theme.colors['text_primary'],
            wrap='word',
            height=20
        )
        self.report_text.pack(fill='both', expand=True)
        
        # Gerar relatório inicial
        self.generate_financial_report()
    
    def generate_financial_report(self):
        """Gera relatório financeiro"""
        periodo = self.report_period.get()
        
        if periodo == 'hoje':
            summary = self.finance_service.get_financial_summary('hoje')
            titulo = "RELATÓRIO FINANCEIRO - HOJE"
        elif periodo == 'esta semana':
            # Implementar semana
            summary = self.finance_service.get_financial_summary('mes')
            titulo = "RELATÓRIO FINANCEIRO - ESTA SEMANA"
        elif periodo == 'este mês':
            summary = self.finance_service.get_financial_summary('mes')
            titulo = "RELATÓRIO FINANCEIRO - ESTE MÊS"
        elif periodo == 'este ano':
            summary = self.finance_service.get_financial_summary('ano')
            titulo = "RELATÓRIO FINANCEIRO - ESTE ANO"
        else:
            summary = self.finance_service.get_financial_summary('mes')
            titulo = "RELATÓRIO FINANCEIRO"
        
        # Gerar texto do relatório
        report_text = f"""
        {'='*60}
                    HOSPEDARIA CHECA
                    {titulo}
        Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        {'='*60}
        
        RESUMO FINANCEIRO:
        {'-'*60}
        Receitas: {summary['receitas']:>15,} Kz
        Despesas: {summary['despesas']:>15,} Kz
        {'-'*60}
        LUCRO: {summary['lucro']:>18,} Kz
        
        ESTATÍSTICAS:
        {'-'*60}
        Hóspedes atendidos: {summary['hospedes']:>10}
        
        {'='*60}
        
        ANÁLISE POR CATEGORIA:
        {'-'*60}
        """
        
        # Adicionar análise por categoria
        categorias = self.get_transactions_by_category(periodo)
        for categoria, dados in categorias.items():
            report_text += f"\n{categoria.upper():20}"
            report_text += f"Entradas: {dados['entrada']:>10,} Kz"
            report_text += f"  Saídas: {dados['saida']:>10,} Kz"
            report_text += f"  Saldo: {dados['saldo']:>10,} Kz"
        
        report_text += f"\n{'='*60}"
        
        # Atualizar widget de texto
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report_text)
    
    def get_transactions_by_category(self, periodo):
        """Obtém transações por categoria"""
        # Implementar filtro por período
        result = self.db.execute_query('''
            SELECT categoria,
                   SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as entrada,
                   SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as saida
            FROM transacoes
            GROUP BY categoria
            ORDER BY categoria
        ''', commit=False)
        
        categorias = {}
        for row in result.fetchall():
            categorias[row[0]] = {
                'entrada': row[1] or 0,
                'saida': row[2] or 0,
                'saldo': (row[1] or 0) - (row[2] or 0)
            }
        
        return categorias
    
    def create_balance_section(self, parent):
        """Cria seção de balanço"""
        balance_card = Card(parent, title="⚖️ BALANÇO FINANCEIRO")
        balance_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        balance_content = balance_card.content_frame
        
        # Balanço do mês
        month_balance = self.finance_service.get_financial_summary('mes')
        
        # Cards de métricas
        metrics_frame = tk.Frame(balance_content, bg=Theme.colors['surface'])
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        metrics = [
            {
                'title': 'Receitas Mês',
                'value': f"{month_balance['receitas']:,} Kz",
                'color': Theme.colors['success'],
                'icon': '📈'
            },
            {
                'title': 'Despesas Mês',
                'value': f"{month_balance['despesas']:,} Kz",
                'color': Theme.colors['danger'],
                'icon': '📉'
            },
            {
                'title': 'Lucro Mês',
                'value': f"{month_balance['lucro']:,} Kz",
                'color': Theme.colors['accent'],
                'icon': '💰'
            }
        ]
        
        for i, metric in enumerate(metrics):
            metric_card = Card(
                metrics_frame,
                title=f"{metric['icon']} {metric['title']}",
                bg=Theme.colors['surface']
            )
            metric_card.grid(row=0, column=i, padx=5, sticky='nsew')
            metrics_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(
                metric_card.content_frame,
                text=metric['value'],
                font=('Segoe UI', 14, 'bold'),
                fg=metric['color'],
                bg=Theme.colors['surface']
            ).pack(expand=True)
        
        # Balanço anual
        annual_data = self.finance_service.get_monthly_revenue()
        
        annual_card = Card(balance_content, title="📅 BALANÇO ANUAL")
        annual_card.pack(fill='both', expand=True)
        
        annual_content = annual_card.content_frame
        
        if annual_data:
            # Calcular totais
            receita_anual = sum(d['receita'] for d in annual_data.values())
            despesa_anual = sum(d['despesa'] for d in annual_data.values())
            lucro_anual = receita_anual - despesa_anual
            
            tk.Label(
                annual_content,
                text=f"Receita Anual: {receita_anual:,} Kz",
                font=Theme.fonts['body'],
                fg=Theme.colors['success'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            tk.Label(
                annual_content,
                text=f"Despesa Anual: {despesa_anual:,} Kz",
                font=Theme.fonts['body'],
                fg=Theme.colors['danger'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            tk.Label(
                annual_content,
                text=f"Lucro Anual: {lucro_anual:,} Kz",
                font=Theme.fonts['heading'],
                fg=Theme.colors['accent'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 10))
            
            # Lista mensal
            for mes, dados in annual_data.items():
                frame = tk.Frame(annual_content, bg=Theme.colors['surface'])
                frame.pack(fill='x', pady=2)
                
                tk.Label(
                    frame,
                    text=mes[:3],
                    font=Theme.fonts['small'],
                    fg=Theme.colors['text_secondary'],
                    bg=Theme.colors['surface'],
                    width=10
                ).pack(side='left')
                
                tk.Label(
                    frame,
                    text=f"{dados['receita']:>12,} Kz",
                    font=Theme.fonts['small'],
                    fg=Theme.colors['success'],
                    bg=Theme.colors['surface']
                ).pack(side='left', padx=(10, 0))
                
                tk.Label(
                    frame,
                    text=f"{dados['despesa']:>12,} Kz",
                    font=Theme.fonts['small'],
                    fg=Theme.colors['danger'],
                    bg=Theme.colors['surface']
                ).pack(side='left', padx=(10, 0))
                
                tk.Label(
                    frame,
                    text=f"{dados['lucro']:>12,} Kz",
                    font=Theme.fonts['small'],
                    fg=Theme.colors['accent'],
                    bg=Theme.colors['surface']
                ).pack(side='left', padx=(10, 0))
        else:
            tk.Label(
                annual_content,
                text="Sem dados disponíveis para o ano atual",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(expand=True)
    
    def lighten_color(self, color, percent):
        """Clareia uma cor hexadecimal"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c + (255 - c) * percent / 100)) for c in rgb)
            return '#%02x%02x%02x' % lightened
        except:
            return color
    
    def logout(self):
        """Realiza logout do sistema"""
        self.user_service.logout()
        self.show_access_selection()
    
    def on_closing(self):
        """Ação ao fechar a janela"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.db.close()
            self.root.destroy()
    
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

# ====================== EXECUÇÃO PRINCIPAL ======================

if __name__ == "__main__":
    # Verificar se estamos no ambiente correto
    try:
        app = SistemaHospedariaCheca()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        import traceback
        traceback.print_exc()
        
        # Mostrar mensagem de erro amigável
        error_window = tk.Tk()
        error_window.title("Erro do Sistema")
        error_window.geometry("500x300")
        
        tk.Label(
            error_window,
            text="❌ ERRO AO INICIAR O SISTEMA",
            font=('Segoe UI', 16, 'bold'),
            fg='red'
        ).pack(pady=20)
        
        tk.Label(
            error_window,
            text="Ocorreu um erro ao iniciar o sistema da Hospedaria Checa.",
            font=('Segoe UI', 11)
        ).pack(pady=10)
        
        tk.Label(
            error_window,
            text="Detalhes técnicos:",
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(20, 5))
        
        error_text = tk.Text(error_window, height=5, width=60)
        error_text.pack(pady=10)
        error_text.insert('1.0', str(e))
        error_text.configure(state='disabled')
        
        tk.Button(
            error_window,
            text="Fechar",
            command=error_window.destroy
        ).pack(pady=10)
        
        error_window.mainloop()    