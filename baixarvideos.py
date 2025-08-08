import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, OptionMenu, StringVar

class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixador de Mídia ◉ Cauã Moreto")
        self.root.geometry("500x300")  # Aumentando a altura da janela
        self.root.resizable(False, False)
        self.root.config(bg="#f0f0f0") # Cor de fundo suave

        self.formatos_disponiveis = {}

        # --- Estilos ---
        fonte_principal = ('Segoe UI', 10)
        cor_botao_video = "#4CAF50"  # Verde mais vivo
        cor_botao_audio = "#FF9800"  # Laranja
        cor_texto_botao = "white"

        # --- Widgets ---
        url_frame = tk.Frame(root, bg="#f0f0f0", pady=5, padx=10)
        url_frame.pack(fill='x')
        tk.Label(url_frame, text="URL da Mídia:", font=fonte_principal, bg="#f0f0f0").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(url_frame, font=fonte_principal)
        self.url_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=5)
        self.buscar_btn = tk.Button(url_frame, text="Buscar Qualidades", command=self.buscar_formatos, font=fonte_principal)
        self.buscar_btn.pack(side=tk.LEFT)

        pasta_frame = tk.Frame(root, bg="#f0f0f0", pady=5, padx=10)
        pasta_frame.pack(fill='x')
        tk.Label(pasta_frame, text="Salvar em:", font=fonte_principal, bg="#f0f0f0").pack(side=tk.LEFT)
        self.pasta_entry = tk.Entry(pasta_frame, font=fonte_principal)
        self.pasta_entry.insert(0, "downloads") # Pasta padrão mais intuitiva
        self.pasta_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=5)
        tk.Button(pasta_frame, text="Selecionar Pasta", command=self.selecionar_pasta, font=fonte_principal).pack(side=tk.LEFT)

        qualidade_frame = tk.Frame(root, bg="#f0f0f0", pady=10, padx=10)
        qualidade_frame.pack(fill='x')
        tk.Label(qualidade_frame, text="Qualidade do Vídeo:", font=fonte_principal, bg="#f0f0f0").pack(side=tk.LEFT, pady=5)
        self.qualidade_var = StringVar(root)
        self.qualidade_var.set("Insira uma URL e clique em buscar")
        self.qualidade_menu = OptionMenu(qualidade_frame, self.qualidade_var, "")
        self.qualidade_menu.config(font=fonte_principal, state="disabled")
        self.qualidade_menu.pack(expand=True, fill='x', padx=5)

        # Frame para os botões de download
        download_frame = tk.Frame(root, bg="#f0f0f0", pady=15)
        download_frame.pack()

        self.download_btn_video = tk.Button(download_frame, text="Baixar Vídeo", command=self.baixar_video, bg=cor_botao_video, fg=cor_texto_botao, font=('Segoe UI', 10, 'bold'), padx=20, pady=8, state="disabled")
        self.download_btn_video.pack(side=tk.LEFT, padx=10)

        self.download_btn_audio = tk.Button(download_frame, text="Baixar Áudio (MP3)", command=self.baixar_audio_mp3, bg=cor_botao_audio, fg=cor_texto_botao, font=('Segoe UI', 10, 'bold'), padx=20, pady=8, state="disabled")
        self.download_btn_audio.pack(side=tk.LEFT, padx=10)

        self.status_var = StringVar()
        self.status_var.set("Pronto")
        status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', font=fonte_principal, bg="#e0e0e0", bd=1)
        status_bar.pack(side=tk.BOTTOM, fill='x')

    def buscar_formatos(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL válida.")
            return

        self.status_var.set("Buscando qualidades...")
        self.root.update_idletasks()

        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])

            self.formatos_disponiveis.clear()
            menu = self.qualidade_menu['menu']
            menu.delete(0, 'end')

            formatos_video = {}
            for f in sorted(formats, key=lambda x: x.get('height', 0) or 0, reverse=True):
                if f.get('vcodec') != 'none' and f.get('height'):
                    label = f"{f['height']}p ({f['ext']}) - {f.get('format_note', '') or 'Padrão'}"
                    formatos_video.setdefault(label, f['format_id'])

            if formatos_video:
                for label, format_id in formatos_video.items():
                    self.formatos_disponiveis['Vídeo - ' + label] = format_id
                    menu.add_command(label='Vídeo - ' + label, command=lambda value='Vídeo - ' + label: self.qualidade_var.set(value))
                primeira_opcao_video = list(formatos_video.keys())
                if primeira_opcao_video:
                    self.qualidade_var.set('Vídeo - ' + primeira_opcao_video[-1]) # Seleciona a menor resolução por padrão

            if not self.formatos_disponiveis:
                self.qualidade_var.set("Nenhuma qualidade de vídeo encontrada")
                self.download_btn_video.config(state="disabled")
                self.download_btn_audio.config(state="normal") # Permite baixar só o áudio se não houver vídeo
                self.qualidade_menu.config(state="disabled")
                messagebox.showwarning("Aviso", "Não foi possível encontrar formatos de vídeo para esta URL. Tentando baixar apenas o áudio.")
            else:
                self.qualidade_menu.config(state="normal")
                self.download_btn_video.config(state="normal")
                self.download_btn_audio.config(state="normal")
                self.status_var.set("Qualidades encontradas! Selecione uma e baixe.")

        except Exception as e:
            self.status_var.set("Erro ao buscar qualidades")
            messagebox.showerror("Erro", f"Não foi possível obter informações da mídia.\nDetalhes: {e}")

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)

    def baixar_video(self):
        url = self.url_entry.get()
        pasta = self.pasta_entry.get() or 'downloads'
        qualidade_selecionada = self.qualidade_var.get()

        if not all([url, pasta, qualidade_selecionada]):
            messagebox.showerror("Erro", "Verifique se todos os campos estão preenchidos.")
            return

        format_id = self.formatos_disponiveis.get(qualidade_selecionada)
        if not format_id:
            messagebox.showerror("Erro", "Qualidade selecionada inválida.")
            return

        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'outtmpl': f'{pasta}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [self.on_progress],
        }

        try:
            self.status_var.set(f"Baixando vídeo na qualidade '{qualidade_selecionada.split(' - ')[-1]}'... Por favor, aguarde.")
            self.set_ui_state("disabled")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                    messagebox.showinfo("Sucesso", "Download do vídeo concluído!")
                    self.status_var.set("Download concluído!")
                except yt_dlp.utils.DownloadError as e:
                    if "ffmpeg not found" in str(e):
                        messagebox.showerror("Erro de FFmpeg", "O FFmpeg não foi encontrado!\n\nPara baixar esta qualidade de vídeo, o FFmpeg é necessário.\n\nPor favor, certifique-se de que o FFmpeg está instalado e no PATH do seu sistema.")
                        self.status_var.set("Erro: FFmpeg não encontrado.")
                    else:
                        raise e
        except Exception as e:
            messagebox.showerror("Erro no Download", f"Ocorreu um erro ao baixar o vídeo: {e}")
            self.status_var.set("Erro no download.")
        finally:
            self.set_ui_state("normal")

    def baixar_audio_mp3(self):
        url = self.url_entry.get()
        pasta = self.pasta_entry.get() or 'downloads'

        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL válida.")
            return

        ydl_opts = {
            'extract_audio': True,
            'audio_format': 'mp3',
            'outtmpl': f'{pasta}/%(title)s.%(ext)s',
            'progress_hooks': [self.on_progress],
        }

        try:
            self.status_var.set("Baixando áudio em MP3... Por favor, aguarde.")
            self.set_ui_state("disabled")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Sucesso", "Download do áudio em MP3 concluído!")
            self.status_var.set("Download concluído!")
        except Exception as e:
            messagebox.showerror("Erro no Download", f"Ocorreu um erro ao baixar o áudio: {e}")
            self.status_var.set("Erro no download.")
        finally:
            self.set_ui_state("normal")

    def on_progress(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0.0%').strip()
            speed_str = d.get('_speed_str', 'N/A').strip()
            self.status_var.set(f"Baixando: {percent_str} a {speed_str}")
            self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.status_var.set("Download finalizado.")
            self.root.update_idletasks()

    def set_ui_state(self, state):
        for widget in [self.buscar_btn, self.download_btn_video, self.download_btn_audio, self.qualidade_menu]:
            widget.config(state=state)
        self.url_entry.config(state="readonly" if state == "disabled" else "normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()

"""
COMANDO UTILIZADO PARA FAZER UM EXECUTÁVEL

pip install pyinstaller # (para instalar a biblioteca que possibilita isso)
pyinstaller --onefile --windowed --icon=icone.ico baixarvideos.py

📌 Explicação dos argumentos:

--onefile: Gera um único arquivo .exe.
--windowed: Oculta o terminal (modo GUI).
--icon=icone.ico: Define um ícone personalizado (opcional).

"""