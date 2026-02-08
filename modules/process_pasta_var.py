import os
import threading
import queue

class FolderProcessor:
    _queue = queue.Queue()
    _worker_thread = None
    _is_processing = False

    def __init__(self, editor):
        self.editor = editor

    def get_videos_in_folder(self, folder_path):
        video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
        return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if f.lower().endswith(video_extensions)]

    def process_folder(self, input_video_path, output_folder, style, color, subtitles, emoji_manager, audio_settings, status_callback, completion_callback, process_all_folder=True, watermark_data=None, tab_number=None, enable_enhancement=False):
        if process_all_folder:
            folder_path = os.path.dirname(input_video_path)
            videos = self.get_videos_in_folder(folder_path)
        else:
            videos = [input_video_path]
        
        if not videos:
            status_callback("Nenhum vídeo encontrado na pasta.")
            completion_callback(0, 0, ["Nenhum vídeo encontrado na pasta."])
            return

        # Adicionar vídeos à fila
        for video_path in videos:
            task = {
                'video_path': video_path,
                'output_folder': output_folder,
                'style': style,
                'color': color,
                'subtitles': subtitles,
                'emoji_manager': emoji_manager,
                'audio_settings': audio_settings,
                'watermark_data': watermark_data,
                'mesclagem_data': mesclagem_data,
                'status_callback': status_callback,
                'completion_callback': completion_callback,
                'total_in_batch': len(videos),
                'tab_number': tab_number,
                'enable_enhancement': enable_enhancement
            }
            FolderProcessor._queue.put(task)

        status_callback(f"{len(videos)} vídeos adicionados à fila de espera.")
        
        # Iniciar worker se não estiver rodando
        if not FolderProcessor._worker_thread or not FolderProcessor._worker_thread.is_alive():
            FolderProcessor._worker_thread = threading.Thread(target=self._worker, daemon=True)
            FolderProcessor._worker_thread.start()

    def _worker(self):
        FolderProcessor._is_processing = True
        batch_results = {} # Para agrupar callbacks por lote se necessário

        while True:
            try:
                # Tenta pegar uma tarefa com timeout para permitir que a thread morra se a fila ficar vazia
                task = FolderProcessor._queue.get(timeout=5)
                
                video_path = task['video_path']
                video_name = os.path.basename(video_path)
                status_cb = task['status_callback']
                
                status_cb(f"Processando da fila: {video_name}")
                
                success, result = self.editor.render_video(
                    video_path, 
                    task['output_folder'], 
                    task['style'], 
                    task['color'], 
                    task['subtitles'], 
                    task['emoji_manager'], 
                    task['audio_settings'],
                    watermark_data=task.get('watermark_data'),
                    mesclagem_data=task.get('mesclagem_data'),
                    tab_number=task.get('tab_number'),
                    enable_enhancement=task.get('enable_enhancement', False)
                )
                
                # Aqui simplificamos: cada vídeo termina e avisa. 
                # Para manter o comportamento original de 'completion_callback' por pasta,
                # precisaríamos de uma lógica mais complexa de rastreamento de lotes.
                # Por agora, vamos apenas notificar o status.
                
                if success:
                    status_cb(f"Concluído: {video_name}")
                else:
                    status_cb(f"Erro em {video_name}: {result}")
                
                FolderProcessor._queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                print(f"Erro no worker de processamento: {e}")
                break
        
        FolderProcessor._is_processing = False
