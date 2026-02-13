import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from modules.batch_queue_manager import batch_queue_manager
from modules.queue_file_manager import queue_file_manager


class GerenciadorFilas(ttk.Frame):
    """Interface para gerenciar arquivos de fila de lotes"""
    
    def __init__(self, parent, editor_ui):
        super().__init__(parent, padding=20)
        self.editor_ui = editor_ui
        
        # Registrar callback para atualizar ao trocar fila
        batch_queue_manager.on_queue_switch = self.on_queue_changed
        
        self._setup_ui()
        self.update_display()
    
    def _setup_ui(self):
        # Título
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="📂 Gerenciador de Arquivos de Lotes",
            font=("Segoe UI", 14, "bold")
        ).pack()
        
        ttk.Label(
            title_frame,
            text="Cada terminal pode trabalhar com uma fila isolada",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack()
        
        # Frame central para fila atual
        current_frame = ttk.LabelFrame(
            self,
            text=" Fila Ativa Atual ",
            padding=20
        )
        current_frame.pack(fill="both", expand=True, pady=20)
        
        # Label grande mostrando fila atual
        self.current_queue_label = ttk.Label(
            current_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            foreground="#2ecc71",
            anchor="center"
        )
        self.current_queue_label.pack(pady=30)
        
        # Frame de botões
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x")
        
        # Botão criar nova fila
        ttk.Button(
            button_frame,
            text="➕ Criar Nova Fila",
            command=self.create_new_queue,
            style="Accent.TButton"
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Botão selecionar fila
        ttk.Button(
            button_frame,
            text="🔄 Selecionar Outra Fila",
            command=self.select_queue_file
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        # Botão voltar para global
        self.btn_global = ttk.Button(
            button_frame,
            text="🏠 Voltar para Global",
            command=self.switch_to_global
        )
        self.btn_global.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Informação sobre arquivos disponíveis
        info_frame = ttk.LabelFrame(self, text=" Filas Personalizadas Disponíveis ", padding=10)
        info_frame.pack(fill="x", pady=(20, 0))
        
        self.queues_list_label = ttk.Label(
            info_frame,
            text="",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.queues_list_label.pack()
    
    def update_display(self):
        """Atualiza display mostrando fila atual"""
        current_name = batch_queue_manager.get_current_queue_name()
        
        # Atualizar label principal
        self.current_queue_label.config(text=f"🟢  {current_name}")
        
        # Habilitar/desabilitar botão global
        if current_name == "global":
            self.btn_global.config(state="disabled")
            self.current_queue_label.config(foreground="#2ecc71")  # Verde
        else:
            self.btn_global.config(state="normal")
            self.current_queue_label.config(foreground="#3498db")  # Azul
        
        # Listar filas disponíveis
        custom_queues = queue_file_manager.list_custom_queues()
        if custom_queues:
            queues_text = ", ".join(custom_queues)
            self.queues_list_label.config(text=f"Disponíveis: {queues_text}")
        else:
            self.queues_list_label.config(text="Nenhuma fila personalizada criada ainda")
    
    def create_new_queue(self):
        """Cria nova fila personalizada"""
        # Diálogo para nome
        queue_name = simpledialog.askstring(
            "Criar Nova Fila",
            "Digite o nome da nova fila:\n(apenas letras, números, _ e -)",
            parent=self
        )
        
        if not queue_name:
            return
        
        queue_name = queue_name.strip()
        
        if not queue_name:
            messagebox.showerror("Erro", "Nome da fila não pode estar vazio")
            return
        
        # Criar e trocar
        if batch_queue_manager.create_and_switch_to_queue(queue_name):
            messagebox.showinfo(
                "Sucesso",
                f"✅ Fila '{queue_name}' criada e ativada!"
            )
            self.update_display()
            
            # Atualizar aba de lotes se existir
            self.update_lotes_tab()
        else:
            messagebox.showerror(
                "Erro",
                f"Não foi possível criar a fila '{queue_name}'\n" +
                "Verifique se o nome é válido ou se já existe."
            )
    
    def select_queue_file(self):
        """Abre file browser para selecionar arquivo de fila"""
        # Diretório inicial
        initial_dir = os.path.abspath("batch_queues")
        
        # Se pasta não existe, criar
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir, exist_ok=True)
        
        # Abrir file dialog
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo de Fila",
            initialdir=initial_dir,
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        # Trocar para arquivo selecionado
        if batch_queue_manager.switch_from_file_path(file_path):
            queue_name = batch_queue_manager.get_current_queue_name()
            messagebox.showinfo(
                "Sucesso",
                f"✅ Fila trocada para: {queue_name}"
            )
            self.update_display()
            
            # Atualizar aba de lotes
            self.update_lotes_tab()
        else:
            messagebox.showerror(
                "Erro",
                "Não foi possível carregar o arquivo selecionado.\n" +
                "Verifique se é um arquivo JSON válido."
            )
    
    def switch_to_global(self):
        """Volta para fila global"""
        batch_queue_manager.switch_to_global()
        messagebox.showinfo("Sucesso", "✅ Voltou para fila global")
        self.update_display()
        
        # Atualizar aba de lotes
        self.update_lotes_tab()
    
    def on_queue_changed(self):
        """Callback chamado quando fila é trocada"""
        self.update_display()
        self.update_lotes_tab()
    
    def update_lotes_tab(self):
        """Atualiza a aba de Lotes para mostrar nova fila"""
        # Tentar encontrar a aba de lotes no notebook
        try:
            notebook = self.master  # Notebook
            for i in range(notebook.index("end")):
                tab = notebook.nametowidget(notebook.tabs()[i])
                if hasattr(tab, 'refresh_from_manager'):
                    tab.refresh_from_manager()
        except:
            pass  # Se não encontrar, tudo bem
