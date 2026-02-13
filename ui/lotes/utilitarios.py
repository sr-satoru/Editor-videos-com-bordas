from tkinter import filedialog

def selecionar_arquivo(variavel, pai=None):
    """Abre diálogo para selecionar um arquivo de vídeo ou imagem"""
    caminho = filedialog.askopenfilename(
        parent=pai,
        title="Selecionar Vídeo ou Imagem",
        filetypes=[
            ("Vídeos e Imagens", "*.mp4 *.mov *.avi *.mkv *.jpg *.jpeg *.png"),
            ("Todos os arquivos", "*.*")
        ]
    )
    if caminho:
        variavel.set(caminho)

def selecionar_pasta(variavel, pai=None):
    """Abre diálogo para selecionar uma pasta"""
    pasta = filedialog.askdirectory(parent=pai, title="Selecionar Pasta")
    if pasta:
        variavel.set(pasta)
