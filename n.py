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
                tipo TEXT NOT NULL CHECK(tipo IN ('gerente', 'recepcionista', 'financeiro')),
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
                telefone TEXT UNIQUE,
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
        
        # Serviços adicionais
        servicos_padrao = [
            ('Café da Manhã', 'Buffet completo', 5000),
            ('Almoço Executivo', 'Menu diário', 7500),
            ('Jantar', 'Menu à la carte', 10000),
            ('Lavanderia', 'Por peça', 1500),
            ('Internet Premium', '24 horas', 3000),
            ('Estacionamento', 'Diária', 2000),
            ('Transfer Aeroporto', 'Ida e volta', 15000)
        ]
        
        for servico in servicos_padrao:
            self.cursor.execute('''
                INSERT OR IGNORE INTO servicos (nome, descricao, preco)
                VALUES (?, ?, ?)
            ''', servico)
        
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
            'gerente': ['relatorios', 'configuracoes', 'usuarios', 'dashboard', 'notificacoes', 'relatorios_tempo_real'],
            'recepcionista': ['hospedes', 'quartos', 'checkin', 'checkout', 'servicos', 'editar_hospedes'],
            'financeiro': ['financeiro', 'transacoes', 'relatorios_financeiros']
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
        self.category_tree = BinarySearchTree()  # NOVO: Árvore para categorias
        self.nationality_hash = HashTable()  # NOVO: Tabela hash para nacionalidades
        self.load_guests_to_memory()
    
        def unified_search(self, search_term): 
    
            resultados = []
            estatisticas = {}
        
        # Tentativa 1: Busca por ID (árvore binária) - O(log n)
            start_time = time.perf_counter_ns()
            try:
               guest_id = int(search_term)
               result = self.guest_tree.search(guest_id)
               if result:
                  resultados.append(result)
            except ValueError:
               result = None
            end_time = time.perf_counter_ns()
            estatisticas['binary_search_id'] = (end_time - start_time) / 1e6  # ms
        
        # Tentativa 2: Busca por nome (tabela hash) - O(1)
            start_time = time.perf_counter_ns()
            result = self.guest_hash.search(search_term.lower())
            if result:
               resultados.append(result)
            end_time = time.perf_counter_ns()
            estatisticas['hash_search_name'] = (end_time - start_time) / 1e6  # ms
        
        # Tentativa 3: Busca por quarto (mapeamento direto) - O(1)
            start_time = time.perf_counter_ns()
            try:
                room_num = int(search_term)
                guest_id = self.room_guest_map.get(room_num)
                if guest_id:
                    result = self.guest_tree.search(guest_id)
                if result:
                    resultados.append(result)
            except ValueError:
                  pass
            end_time = time.perf_counter_ns()
            estatisticas['room_search'] = (end_time - start_time) / 1e6  # ms
        
        # Tentativa 4: Busca por categoria (árvore binária) - O(log n)
            start_time = time.perf_counter_ns()
            search_lower = search_term.lower()
            categoria_match = None
            if search_lower in ['vip', 'normal']:
                categoria = 'VIP' if search_lower == 'vip' else 'Normal'
                categoria_match = self.category_tree.search(categoria)
                if categoria_match:
                    resultados.extend(categoria_match)
            end_time = time.perf_counter_ns()
            estatisticas['category_search'] = (end_time - start_time) / 1e6  # ms
        
        # Tentativa 5: Busca por nacionalidade (tabela hash) - O(1)
            start_time = time.perf_counter_ns()
            nat_result = self.nationality_hash.search(search_term)
            if nat_result:
                resultados.extend(nat_result)
            end_time = time.perf_counter_ns()
            estatisticas['nationality_search'] = (end_time - start_time) / 1e6  # ms
        
        # Tentativa 6: Busca por documento (busca linear para documentos parciais)
            start_time = time.perf_counter_ns()
            doc_result = self.search_by_document_partial(search_term)
            if doc_result:
                resultados.extend(doc_result)
            end_time = time.perf_counter_ns()
            estatisticas['document_search'] = (end_time - start_time) / 1e6  # ms
        
        # Remover duplicatas
            unique_results = []
            seen_ids = set()
            for guest in resultados:
                if guest['id'] not in seen_ids:
                    seen_ids.add(guest['id'])
                    unique_results.append(guest)
        
        # Determinar tipo de busca mais rápido que encontrou resultados
            tipo_busca = "Nenhuma"
            if unique_results:
            # Encontrar o método mais rápido que retornou resultados
                min_time = float('inf')
                for metodo, tempo in estatisticas.items():
                    if tempo > 0 and tempo < min_time:
                        min_time = tempo
                        tipo_busca = metodo.replace('_', ' ').title()
        
            return unique_results, estatisticas, tipo_busca
    
    def search_by_document_partial(self, document_partial):
        """Busca por documento parcial (para demonstração de busca linear)"""
        result = self.db.execute_query(
            "SELECT id, nome, documento, quarto_numero, categoria_quarto, nacionalidade FROM hospedes WHERE ativo = 1 AND documento LIKE ?",
            (f'%{document_partial}%',),
            commit=False
        )
        
        guests = []
        for row in result.fetchall():
            guest_id, nome, documento, quarto_numero, categoria, nacionalidade = row
            guests.append({
                'id': guest_id,
                'nome': nome,
                'documento': documento,
                'quarto_numero': quarto_numero,
                'categoria': categoria,
                'nacionalidade': nacionalidade or 'Não informada'
            })
        return guests
    
    def get_search_statistics(self):
        """Retorna estatísticas das estruturas de dados"""
        # Contar elementos em cada estrutura
        id_count = len(self.guest_tree.inorder_traversal())
        name_count = sum(len(bucket) for bucket in self.guest_hash.table)
        room_count = len(self.room_guest_map)
        
        # Calcular complexidade teórica
        estatisticas = {
            'total_hospedes': id_count,
            'estruturas': {
                'Árvore Binária (ID)': {
                    'tamanho': id_count,
                    'complexidade_busca': 'O(log n)',
                    'uso': 'Busca por ID/Número'
                },
                'Tabela Hash (Nome)': {
                    'tamanho': name_count,
                    'complexidade_busca': 'O(1)',
                    'uso': 'Busca por Nome'
                },
                'Mapeamento Quarto-Hóspede': {
                    'tamanho': room_count,
                    'complexidade_busca': 'O(1)',
                    'uso': 'Busca por Quarto'
                },
                'Árvore de Categorias': {
                    'tamanho': len(self.category_tree.inorder_traversal()),
                    'complexidade_busca': 'O(log n)',
                    'uso': 'Busca por Categoria'
                },
                'Tabela Hash (Nacionalidade)': {
                    'tamanho': sum(len(bucket) for bucket in self.nationality_hash.table),
                    'complexidade_busca': 'O(1)',
                    'uso': 'Busca por Nacionalidade'
                }
            }
        }
        return estatisticas
    def load_guests_to_memory(self):
        """Carrega hóspedes para estruturas de dados em memória"""
        result = self.db.execute_query(
            "SELECT id, nome, documento, quarto_numero FROM hospedes WHERE ativo = 1",
            commit=False
        )
        
        for row in result.fetchall():
            guest_id, nome, documento, quarto_numero = row
    
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
            text="🔄 ATUALIZAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=9,
            command=self.update_notifications
        ).pack()
        
        # Iniciar atualização automática
        self.update_notifications()
        self.start_auto_refresh()
    
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
                'title': '💰 FINANCEIRO',
                'desc': 'Gestão financeira completa\nRelatórios e transações',
                'type': 'financeiro',
                'color': Theme.colors['success'],
                'icon': '💵'
            }
        ]
        
        for i, card_data in enumerate(cards_data):
            card = Card(
                cards_frame,
                title=f"{card_data['icon']} {card_data['title']}",
                bg=Theme.colors['surface'],
                width=280,
                height=180
            )
            card.grid(row=0, column=i, padx=10, ipadx=10, ipady=10)
            
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
            text="ℹ️ Primeiro acesso? use uma senha que possa se lembrar facilmente' para login",
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
        elif user_info['tipo'] == 'financeiro':
            self.show_financial_dashboard(main_area)
    
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
        """Cria seção de gestão de quartos"""
        rooms_card = Card(parent, title="🏨 GESTÃO DE QUARTOS")
        rooms_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        rooms_content = rooms_card.content_frame
        
        # Obter estatísticas dos quartos
        room_stats = self.room_service.get_room_stats()
        
        # Cards de estatísticas
        stats_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats_data = [
            {
                'title': 'Total',
                'value': room_stats['total'],
                'icon': '🏨',
                'color': Theme.colors['primary']
            },
            {
                'title': 'Ocupados',
                'value': room_stats['ocupados'],
                'icon': '🔒',
                'color': Theme.colors['secondary']
            },
            {
                'title': 'Disponíveis',
                'value': room_stats['disponiveis'],
                'icon': '🔓',
                'color': Theme.colors['success']
            },
            {
                'title': 'VIP',
                'value': room_stats['vip'],
                'icon': '🏆',
                'color': Theme.colors['vip']
            },
            {
                'title': 'Manutenção',
                'value': room_stats['manutencao'],
                'icon': '🔧',
                'color': Theme.colors['warning']
            },
            {
                'title': 'Limpeza',
                'value': room_stats['limpeza'],
                'icon': '🧹',
                'color': Theme.colors['info']
            }
        ]
        
        for i, stat in enumerate(stats_data):
            stat_card = StatCard(
                stats_frame,
                title=stat['title'],
                value=stat['value'],
                icon=stat['icon'],
                color=stat['color']
            )
            stat_card.grid(row=0, column=i, padx=2, sticky='nsew')
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Controles de busca
        controls_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Busca por número (árvore binária)
        tk.Label(
            controls_frame,
            text="Buscar por número:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 5))
        
        self.room_search_num = tk.Entry(
            controls_frame,
            font=Theme.fonts['body'],
            width=10
        )
        self.room_search_num.pack(side='left', padx=(0, 10))
        
        ModernButton(
            controls_frame,
            text="🔍 BUSCAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=9,
            command=self.search_room_by_number
        ).pack(side='left', padx=(0, 20))
        
        # Busca por nome (tabela hash)
        tk.Label(
            controls_frame,
            text="Buscar por nome:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 5))
        
        self.room_search_name = tk.Entry(
            controls_frame,
            font=Theme.fonts['body'],
            width=15
        )
        self.room_search_name.pack(side='left', padx=(0, 10))
        
        ModernButton(
            controls_frame,
            text="🔍 BUSCAR",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=9,
            command=self.search_room_by_name
        ).pack(side='left')
        
        # Lista de quartos
        list_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
        list_frame.pack(fill='both', expand=True)
        
        # Treeview para quartos
        columns = ('Número', 'Nome', 'Categoria', 'Status', 'Hóspede', 'Check-in')
        
        self.rooms_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12
        )
        
        col_widths = [70, 150, 80, 100, 150, 120]
        for col, width in zip(columns, col_widths):
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.rooms_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.rooms_tree.xview)
        self.rooms_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.rooms_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Carregar quartos
        self.update_rooms_list()
        
        # Botões de ação (apenas para gerente)
        if is_manager:
            action_frame = tk.Frame(rooms_content, bg=Theme.colors['surface'])
            action_frame.pack(fill='x', pady=(10, 0))
            
            ModernButton(
                action_frame,
                text="🔄 ATUALIZAR",
                bg=Theme.colors['primary'],
                hover_bg=Theme.colors['primary_light'],
                font_size=10,
                command=self.update_rooms_list
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="🔧 EM MANUTENÇÃO",
                bg=Theme.colors['warning'],
                hover_bg=self.lighten_color(Theme.colors['warning'], 20),
                font_size=10,
                command=lambda: self.update_room_status('manutencao')
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="🧹 EM LIMPEZA",
                bg=Theme.colors['info'],
                hover_bg=self.lighten_color(Theme.colors['info'], 20),
                font_size=10,
                command=lambda: self.update_room_status('limpeza')
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                action_frame,
                text="✅ DISPONÍVEL",
                bg=Theme.colors['success'],
                hover_bg=self.lighten_color(Theme.colors['success'], 20),
                font_size=10,
                command=lambda: self.update_room_status('disponivel')
            ).pack(side='left')
    
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
            """Cria lista de hóspedes ativos com busca unificada avançada"""
        # Card para a lista
        list_card = Card(parent, title="👥 HÓSPEDES ATIVOS - BUSCA AVANÇADA")
        list_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        list_content = list_card.content_frame
        
        # ====================== ÁREA DE BUSCA UNIFICADA ======================
        search_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Título da busca
        tk.Label(
            search_frame,
            text="🔍 BUSCA UNIFICADA AVANÇADA",
            font=Theme.fonts['heading'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Frame para entrada de busca
        input_frame = tk.Frame(search_frame, bg=Theme.colors['surface'])
        input_frame.pack(fill='x')
        
        # Campo de busca
        tk.Label(
            input_frame,
            text="Digite para buscar:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        ).pack(side='left', padx=(0, 10))
        
        self.search_unified_var = tk.StringVar()
        self.search_unified_entry = tk.Entry(
            input_frame,
            textvariable=self.search_unified_var,
            font=Theme.fonts['body'],
            width=40
        )
        self.search_unified_entry.pack(side='left', padx=(0, 10))
        self.search_unified_entry.bind('<KeyRelease>', lambda e: self.perform_unified_search())
        
        # Botão de busca
        ModernButton(
            input_frame,
            text="🚀 BUSCAR AVANÇADO",
            bg=Theme.colors['accent'],
            hover_bg=self.lighten_color(Theme.colors['accent'], 20),
            font_size=10,
            command=self.perform_unified_search
        ).pack(side='left', padx=(0, 10))
        
        # Botão para limpar busca
        ModernButton(
            input_frame,
            text="🗑️ LIMPAR",
            bg=Theme.colors['gray'],
            hover_bg=self.lighten_color(Theme.colors['gray'], 20),
            font_size=10,
            command=self.clear_unified_search
        ).pack(side='left')
        
        # ====================== INFORMAÇÕES DE BUSCA ======================
        info_frame = tk.Frame(search_frame, bg=Theme.colors['light'], padx=10, pady=8)
        info_frame.pack(fill='x', pady=(10, 0))
        
        self.search_info_label = tk.Label(
            info_frame,
            text="💡 Dica: Busque por ID, Nome, Quarto, Categoria (VIP/Normal), Nacionalidade ou Documento",
            font=Theme.fonts['small'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['light'],
            wraplength=800
        )
        self.search_info_label.pack(anchor='w')
        
        # ====================== ESTATÍSTICAS DE PERFORMANCE ======================
        stats_frame = tk.Frame(search_frame, bg=Theme.colors['surface'])
        stats_frame.pack(fill='x', pady=(10, 0))
        
        # Título das estatísticas
        tk.Label(
            stats_frame,
            text="⏱️ ESTATÍSTICAS DE PERFORMANCE",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        # Frame para métricas
        metrics_frame = tk.Frame(stats_frame, bg=Theme.colors['surface'])
        metrics_frame.pack(fill='x')
        
        # Métricas (serão atualizadas dinamicamente)
        self.metric_labels = {}
        
        metric_data = [
            ('binary_search_id', 'Árvore Binária (ID):', 'O(log n)'),
            ('hash_search_name', 'Tabela Hash (Nome):', 'O(1)'),
            ('room_search', 'Mapeamento Quarto:', 'O(1)'),
            ('category_search', 'Árvore Categorias:', 'O(log n)'),
            ('nationality_search', 'Hash Nacionalidade:', 'O(1)'),
            ('document_search', 'Busca Documento:', 'O(n)')
        ]
        
        for i, (key, label, complexity) in enumerate(metric_data):
            frame = tk.Frame(metrics_frame, bg=Theme.colors['surface'])
            frame.grid(row=i//3, column=i%3, sticky='w', padx=5, pady=2)
            
            tk.Label(
                frame,
                text=label,
                font=('Segoe UI', 8),
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(side='left')
            
            self.metric_labels[key] = tk.Label(
                frame,
                text="0.00 ms",
                font=('Segoe UI', 8, 'bold'),
                fg=Theme.colors['accent'],
                bg=Theme.colors['surface']
            )
            self.metric_labels[key].pack(side='left', padx=(5, 0))
            
            tk.Label(
                frame,
                text=f" [{complexity}]",
                font=('Segoe UI', 8, 'italic'),
                fg=Theme.colors['gray'],
                bg=Theme.colors['surface']
            ).pack(side='left')
        
        # ====================== RESULTADO DA BUSCA ======================
        result_frame = tk.Frame(search_frame, bg=Theme.colors['surface'])
        result_frame.pack(fill='x', pady=(10, 0))
        
        self.search_result_label = tk.Label(
            result_frame,
            text="🔎 Pronto para buscar...",
            font=('Segoe UI', 10, 'italic'),
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['surface']
        )
        self.search_result_label.pack(anchor='w')
        
        # ====================== CONTROLES DE AÇÃO ======================
        controls_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
        controls_frame.pack(fill='x', pady=(10, 10))
        
        ModernButton(
            controls_frame,
            text="🔄 ATUALIZAR LISTA",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            font_size=10,
            command=self.update_guests_tree
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            controls_frame,
            text="📊 VER ESTATÍSTICAS ESTRUTURAS",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            command=self.show_data_structures_stats
        ).pack(side='left', padx=(0, 10))
        
        # ====================== FRAME PARA A TABELA ======================
        table_frame = tk.Frame(list_content, bg=Theme.colors['surface'])
        table_frame.pack(fill='both', expand=True)
        
        # Criar tabela
        self.create_guests_table(table_frame)
    
        def create_guests_table(self, parent):
            """Cria tabela de hóspedes com suporte a animações"""
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
        
        # Configurar tags para animação
        self.guests_tree.tag_configure('normal', background=Theme.colors['surface'])
        
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
            text="👁️ VER DETALHES",
            bg=Theme.colors['info'],
            hover_bg=self.lighten_color(Theme.colors['info'], 20),
            font_size=10,
            command=self.show_guest_details
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
    
        def update_guests_tree(self):
            """Atualiza a treeview de hóspedes"""
        if not hasattr(self, 'guests_tree'):
            return
        
        # Limpar lista
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        # Obter hóspedes ativos
        guests = self.guest_service.get_all_guests(ativos=True)
        
        # Adicionar à lista
        for guest in guests:
            # Formatar preço
            preco_formatado = f"{guest[11]:,} Kz".replace(",", ".")
            
            # Formatar data
            try:
                check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
                check_in_formatado = check_in.strftime('%d/%m %H:%M')
            except:
                check_in_formatado = guest[12]
            
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
    
    def show_guest_details(self):
        """Mostra detalhes do hóspede selecionado"""
        selection = self.guests_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um hóspede!")
            return
        
        item = self.guests_tree.item(selection[0])
        guest_id = item['values'][0]
        
        # Buscar detalhes
        result = self.db.execute_query(
            "SELECT * FROM hospedes WHERE id = ?",
            (guest_id,),
            commit=False
        )
        guest = result.fetchone()
        
        if guest:
            # Formatar dados
            check_in = datetime.strptime(guest[12], '%Y-%m-%d %H:%M:%S')
            check_in_str = check_in.strftime('%d/%m/%Y %H:%M')
            
            check_out = ""
            if guest[13]:
                check_out_dt = datetime.strptime(guest[13], '%Y-%m-%d %H:%M:%S')
                check_out = check_out_dt.strftime('%d/%m/%Y %H:%M')
            
            # Calcular tempo restante
            tempo_restante = guest[6]  # tempo_horas em horas
            tempo_decorrido = (datetime.now() - check_in).total_seconds() / 3600
            tempo_falta = max(0, tempo_restante - tempo_decorrido)
            
            dias_falta = int(tempo_falta // 24)
            horas_falta = int(tempo_falta % 24)
            
            details = f"""
            🏨 HOSPEDARIA CHECA - DETALHES DO HÓSPEDE
            {'='*60}
            
            📋 IDENTIFICAÇÃO:
            {'-'*30}
            ID: {guest[0]}
            Nome: {guest[1]}
            Documento: {guest[2]}
            Nacionalidade: {guest[3] or 'Não informada'}
            Telefone: {guest[4] or 'Não informado'}
            Email: {guest[5] or 'Não informado'}
            
            🏠 ESTADIA:
            {'-'*30}
            Quarto: {guest[8]} - {guest[9] or 'Sem nome'}
            Categoria: {guest[10]}
            Tempo contratado: {guest[7]}
            Tempo decorrido: {tempo_decorrido:.1f} horas
            Tempo restante: {dias_falta} dias e {horas_falta} horas
            Preço total: {guest[11]:,} Kz
            Preço por hora: {guest[11] / guest[6]:,.0f} Kz
            
            ⏰ DATAS:
            {'-'*30}
            Check-in: {check_in_str}
            Check-out: {check_out or 'Em andamento'}
            Status: {'🟢 Ativo' if guest[15] else '🔴 Finalizado'}
            
            💰 PAGAMENTO:
            {'-'*30}
            Forma: {guest[16] or 'Não informada'}
            
            📝 OBSERVAÇÕES:
            {'-'*30}
            {guest[17] or 'Nenhuma observação'}
            """
            
            # Criar janela de detalhes
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Detalhes do Hóspede - ID {guest[0]}")
            detail_window.geometry("600x700")
            detail_window.configure(bg=Theme.colors['surface'])
            
            # Text widget para detalhes
            text_widget = scrolledtext.ScrolledText(
                detail_window,
                font=Theme.fonts['mono'],
                bg=Theme.colors['surface'],
                fg=Theme.colors['text_primary'],
                wrap='word'
            )
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', details)
            text_widget.configure(state='disabled')
            
            # Botão de fechar
            btn_frame = tk.Frame(detail_window, bg=Theme.colors['surface'])
            btn_frame.pack(fill='x', padx=10, pady=10)
            
            ModernButton(
                btn_frame,
                text="FECHAR",
                bg=Theme.colors['primary'],
                hover_bg=Theme.colors['primary_light'],
                command=detail_window.destroy
            ).pack()
    
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
        edit_window.geometry("500x600")
        edit_window.configure(bg=Theme.colors['surface'])
        
        # Formulário de edição
        form_frame = tk.Frame(edit_window, bg=Theme.colors['surface'], padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(
            form_frame,
            text=f"✏️ EDITAR HÓSPEDE ID {guest_id}",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 20))
        
        # Nome
        tk.Label(
            form_frame,
            text="Nome completo:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_nome = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        edit_nome.pack(fill='x', pady=(0, 15))
        edit_nome.insert(0, guest[1])
        
        # Documento
        tk.Label(
            form_frame,
            text="Documento:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_doc = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        edit_doc.pack(fill='x', pady=(0, 15))
        edit_doc.insert(0, guest[2])
        
        # Nacionalidade
        tk.Label(
            form_frame,
            text="Nacionalidade:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_nacionalidade = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        edit_nacionalidade.pack(fill='x', pady=(0, 15))
        edit_nacionalidade.insert(0, guest[3] or "")
        
        # Telefone
        tk.Label(
            form_frame,
            text="Telefone:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_telefone = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        edit_telefone.pack(fill='x', pady=(0, 15))
        edit_telefone.insert(0, guest[4] or "")
        
        # Email
        tk.Label(
            form_frame,
            text="Email:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_email = tk.Entry(form_frame, font=Theme.fonts['body'], width=40)
        edit_email.pack(fill='x', pady=(0, 15))
        edit_email.insert(0, guest[5] or "")
        
        # Forma de pagamento
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
        edit_pagamento.set(guest[16] or 'Dinheiro')
        
        # Observações
        tk.Label(
            form_frame,
            text="Observações:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).pack(anchor='w', pady=(0, 5))
        
        edit_observacoes = tk.Text(form_frame, font=Theme.fonts['body'], width=40, height=4)
        edit_observacoes.pack(fill='x', pady=(0, 20))
        edit_observacoes.insert('1.0', guest[17] or "")
        
        # Botões
        button_frame = tk.Frame(form_frame, bg=Theme.colors['surface'])
        button_frame.pack(fill='x')
        
        ModernButton(
            button_frame,
            text="💾 SALVAR ALTERAÇÕES",
            bg=Theme.colors['success'],
            hover_bg=self.lighten_color(Theme.colors['success'], 20),
            font_size=11,
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
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame,
            text="❌ CANCELAR",
            bg=Theme.colors['danger'],
            hover_bg=self.lighten_color(Theme.colors['danger'], 20),
            font_size=11,
            command=edit_window.destroy
        ).pack(side='left')
    
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
        
        Forma de pagamento: {guest[16]}
        
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
        
        # Categoria
        tk.Label(
            form_frame,
            text="Categoria:",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['surface']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.trans_categoria = ttk.Combobox(
            form_frame,
            values=['hospedagem', 'alimentacao', 'limpeza', 'manutencao', 'outros'],
            state='readonly',
            width=15
        )
        self.trans_categoria.grid(row=4, column=1, sticky='w', pady=(0, 20), padx=(10, 0))
        self.trans_categoria.set('hospedagem')
        
        # ID do hóspede (opcional)
        tk.Label(
            form_frame,
            text="ID Hóspede (opcional):",
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
        columns = ('ID', 'Data', 'Tipo', 'Descrição', 'Valor', 'Categoria', 'Hóspede')
        
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
        def perform_unified_search(self):
            """Executa busca unificada usando múltiplas estruturas de dados"""
        search_term = self.search_unified_var.get().strip()
        
        if not search_term:
            self.search_result_label.configure(
                text="🔎 Digite algo para buscar (ID, Nome, Quarto, Categoria, etc.)",
                fg=Theme.colors['text_secondary']
            )
            # Resetar métricas
            for key in self.metric_labels:
                self.metric_labels[key].configure(text="0.00 ms", fg=Theme.colors['accent'])
            self.update_guests_tree()  # Mostrar todos
            return
        
        # Executar busca unificada
        resultados, estatisticas, tipo_busca = self.guest_service.unified_search(search_term)
        
        # Atualizar métricas de tempo
        for key, label in self.metric_labels.items():
            tempo = estatisticas.get(key, 0)
            if tempo > 0:
                # Destacar o método mais rápido
                if tempo == min(v for k, v in estatisticas.items() if v > 0):
                    label.configure(text=f"{tempo:.2f} ms ⚡", fg=Theme.colors['success'])
                else:
                    label.configure(text=f"{tempo:.2f} ms", fg=Theme.colors['accent'])
            else:
                label.configure(text="0.00 ms", fg=Theme.colors['gray'])
        
        # Atualizar resultado da busca
        if resultados:
            # Filtrar treeview para mostrar apenas resultados
            self.filter_guests_tree([guest['id'] for guest in resultados])
            
            # Mostrar estatísticas
            tempo_total = sum(estatisticas.values())
            tipo_busca_str = tipo_busca if tipo_busca != "Nenhuma" else "Múltiplas Estruturas"
            
            self.search_result_label.configure(
                text=f"✅ Encontrados {len(resultados)} hóspede(s) | Método mais rápido: {tipo_busca_str} | Tempo total: {tempo_total:.2f} ms",
                fg=Theme.colors['success']
            )
            
            # Animar os resultados na treeview
            self.animate_search_results(resultados)
        else:
            self.search_result_label.configure(
                text=f"❌ Nenhum hóspede encontrado para '{search_term}'",
                fg=Theme.colors['danger']
            )
            self.update_guests_tree()  # Mostrar todos

    def filter_guests_tree(self, guest_ids):
        """Filtra a treeview para mostrar apenas hóspedes específicos"""
        # Limpar itens existentes
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        # Obter todos os hóspedes ativos
        all_guests = self.guest_service.get_all_guests(ativos=True)
        
        # Filtrar pelos IDs especificados
        id_set = set(guest_ids)
        for guest in all_guests:
            if guest[0] in id_set:  # guest[0] é o ID
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

    def animate_search_results(self, resultados):
        """Anima os resultados da busca na treeview"""
        # Primeiro, garantir que todos os itens estão visíveis
        for child in self.guests_tree.get_children():
            self.guests_tree.item(child, tags=('normal',))
        
        # Destacar os resultados encontrados
        for i, guest in enumerate(resultados):
            # Encontrar o item na treeview
            for child in self.guests_tree.get_children():
                values = self.guests_tree.item(child)['values']
                if values[0] == guest['id']:
                    # Destacar com cor diferente
                    tag_color = Theme.colors['accent_light'] if i % 2 == 0 else Theme.colors['info']
                    self.guests_tree.tag_configure(f'highlight_{i}', background=tag_color)
                    self.guests_tree.item(child, tags=(f'highlight_{i}',))
                    
                    # Animar scroll para o primeiro resultado
                    if i == 0:
                        self.guests_tree.see(child)
                        self.guests_tree.selection_set(child)
                    
                    # Efeito de piscar
                    self.root.after(i * 100, lambda c=child: self.blink_item(c))
                    break

    def blink_item(self, item_id, blink_count=3, current=0):
        """Faz um item piscar para chamar atenção"""
        if current < blink_count:
            current_tags = self.guests_tree.item(item_id, 'tags')
            if 'blink' in current_tags:
                self.guests_tree.item(item_id, tags=('normal',))
            else:
                self.guests_tree.tag_configure('blink', background=Theme.colors['warning'])
                self.guests_tree.item(item_id, tags=('blink',))
            
            self.root.after(200, lambda: self.blink_item(item_id, blink_count, current + 1))
        else:
            # Restaurar cor normal
            self.guests_tree.item(item_id, tags=('normal',))

    def clear_unified_search(self):
        """Limpa a busca e mostra todos os hóspedes"""
        self.search_unified_var.set("")
        self.search_result_label.configure(
            text="🔎 Busca limpa. Mostrando todos os hóspedes ativos.",
            fg=Theme.colors['text_secondary']
        )
        
        # Resetar métricas
        for key in self.metric_labels:
            self.metric_labels[key].configure(text="0.00 ms", fg=Theme.colors['accent'])
        
        # Atualizar lista completa
        self.update_guests_tree()

    def show_data_structures_stats(self):
        """Mostra estatísticas das estruturas de dados"""
        estatisticas = self.guest_service.get_search_statistics()
        
        # Criar janela de estatísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estatísticas das Estruturas de Dados")
        stats_window.geometry("600x500")
        stats_window.configure(bg=Theme.colors['surface'])
        
        # Título
        tk.Label(
            stats_window,
            text="🏗️ ESTRUTURAS DE DADOS EM MEMÓRIA",
            font=Theme.fonts['subtitle'],
            fg=Theme.colors['primary'],
            bg=Theme.colors['surface']
        ).pack(pady=20)
        
        # Informações gerais
        info_frame = tk.Frame(stats_window, bg=Theme.colors['light'], padx=15, pady=10)
        info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(
            info_frame,
            text=f"📈 Total de hóspedes ativos: {estatisticas['total_hospedes']}",
            font=Theme.fonts['body'],
            fg=Theme.colors['text_primary'],
            bg=Theme.colors['light']
        ).pack(anchor='w')
        
        tk.Label(
            info_frame,
            text="💡 Todas as estruturas são mantidas sincronizadas em tempo real",
            font=Theme.fonts['small'],
            fg=Theme.colors['text_secondary'],
            bg=Theme.colors['light']
        ).pack(anchor='w', pady=(5, 0))
        
        # Canvas com scroll para estruturas
        canvas = tk.Canvas(stats_window, bg=Theme.colors['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_window, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.colors['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=10)
        
        # Adicionar cards para cada estrutura
        row = 0
        for estrutura, dados in estatisticas['estruturas'].items():
            card = Card(
                scrollable_frame,
                title=f"📦 {estrutura}",
                bg=Theme.colors['surface']
            )
            card.grid(row=row, column=0, sticky='ew', padx=5, pady=5)
            scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Conteúdo do card
            content = card.content_frame
            
            # Tamanho
            tk.Label(
                content,
                text=f"🧮 Elementos: {dados['tamanho']}",
                font=Theme.fonts['body'],
                fg=Theme.colors['text_primary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Complexidade
            tk.Label(
                content,
                text=f"⚡ Complexidade de busca: {dados['complexidade_busca']}",
                font=Theme.fonts['body'],
                fg=Theme.colors['accent'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Uso
            tk.Label(
                content,
                text=f"🎯 Uso: {dados['uso']}",
                font=Theme.fonts['small'],
                fg=Theme.colors['text_secondary'],
                bg=Theme.colors['surface']
            ).pack(anchor='w', pady=(0, 5))
            
            # Exemplo visual da estrutura
            if "Árvore" in estrutura:
                tk.Label(
                    content,
                    text="🌳 Estrutura: Raiz → Filho Esquerdo → Filho Direito",
                    font=Theme.fonts['small'],
                    fg=Theme.colors['gray'],
                    bg=Theme.colors['surface']
                ).pack(anchor='w', pady=(5, 0))
            elif "Hash" in estrutura:
                tk.Label(
                    content,
                    text="🗂️ Estrutura: Buckets com listas encadeadas",
                    font=Theme.fonts['small'],
                    fg=Theme.colors['gray'],
                    bg=Theme.colors['surface']
                ).pack(anchor='w', pady=(5, 0))
            
            row += 1
        
        # Botão de fechar
        btn_frame = tk.Frame(stats_window, bg=Theme.colors['surface'])
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ModernButton(
            btn_frame,
            text="👌 ENTENDIDO",
            bg=Theme.colors['primary'],
            hover_bg=Theme.colors['primary_light'],
            command=stats_window.destroy
        ).pack()
        
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