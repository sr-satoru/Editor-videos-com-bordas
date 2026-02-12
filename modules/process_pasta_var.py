import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.config_global import global_config

class FolderProcessor:
    def __init__(self, editor):
        self.editor = editor

    def get_videos_in_folder(self, folder_path):
        video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
        all_extensions = video_extensions + image_extensions
        return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if f.lower().endswith(all_extensions)]

    def process_folder(self, input_video_path, output_folder, style, color, subtitles, emoji_manager, audio_settings, status_callback, completion_callback, process_all_folder=True, watermark_data=None, mesclagem_data=None, tab_number=None, enable_enhancement=False, video_width_ratio=0.78, video_height_ratio=0.70):
        if process_all_folder:
            folder_path = os.path.dirname(input_video_path)
            videos = self.get_videos_in_folder(folder_path)
        else:
            videos = [input_video_path]
        
        if not videos:
            status_callback("Nenhum vídeo/imagem encontrado na pasta.")
            completion_callback(0, 0, ["Nenhum vídeo/imagem encontrado na pasta."])
            return

        # Obter número de jobs paralelos e threads das configurações globais
        max_workers = global_config.get("parallel_jobs")
        num_threads = global_config.get("num_threads")
        
        status_callback(f"🚀 Iniciando processamento de {len(videos)} arquivo(s) com {max_workers} job(s) simultâneo(s) e {num_threads} threads por job...")
        
        # Processar em paralelo usando ThreadPoolExecutor (ao invés de ProcessPoolExecutor)
        # Threads compartilham memória, evitando problemas de serialização
        threading.Thread(
            target=self._process_parallel,
            args=(videos, output_folder, style, color, subtitles, emoji_manager, 
                  audio_settings, watermark_data, mesclagem_data, tab_number, 
                  enable_enhancement, video_width_ratio, video_height_ratio,
                  status_callback, completion_callback, max_workers, num_threads),
            daemon=True
        ).start()

    def _process_parallel(self, videos, output_folder, style, color, subtitles, 
                         emoji_manager, audio_settings, watermark_data, mesclagem_data,
                         tab_number, enable_enhancement, video_width_ratio, 
                         video_height_ratio, status_callback, completion_callback, max_workers, num_threads):
        """Processa vídeos em paralelo usando o Executor Global Compartilhado"""
        
        from modules.global_executor import global_executor
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Usar o executor global compartilhado de toda a aplicação
        # Isso permite que múltiplas abas submetam jobs para o mesmo pool
        executor = global_executor.get_executor()
        
        # Submeter todas as tasks para o pool global
        future_to_video = {}
        for video_path in videos:
            future = executor.submit(
                self._process_single_video,
                video_path, output_folder, style, color, subtitles,
                emoji_manager, audio_settings, watermark_data, mesclagem_data,
                tab_number, enable_enhancement, video_width_ratio, 
                video_height_ratio, num_threads
            )
            future_to_video[future] = os.path.basename(video_path)
        
        # Processar resultados conforme completam
        from concurrent.futures import as_completed
        for future in as_completed(future_to_video):
            video_name = future_to_video[future]
            try:
                success, result = future.result()
                if success:
                    success_count += 1
                    status_callback(f"✅ Concluído ({success_count}/{len(videos)}): {video_name}")
                else:
                    error_count += 1
                    errors.append(f"{video_name}: {result}")
                    status_callback(f"❌ Erro ({error_count}/{len(videos)}): {video_name}")
            except Exception as e:
                error_count += 1
                errors.append(f"{video_name}: {str(e)}")
                status_callback(f"❌ Exceção ({error_count}/{len(videos)}): {video_name}")
        
        # Callback final
        completion_callback(success_count, error_count, errors)

    def _process_single_video(self, video_path, output_folder, style, color, subtitles,
                              emoji_manager, audio_settings, watermark_data, mesclagem_data,
                              tab_number, enable_enhancement, video_width_ratio, 
                              video_height_ratio, num_threads):
        """Processa um único vídeo (executado em thread separada)"""
        try:
            success, result = self.editor.render_video(
                video_path,
                output_folder,
                style,
                color,
                subtitles,
                emoji_manager,
                audio_settings,
                watermark_data=watermark_data,
                mesclagem_data=mesclagem_data,
                tab_number=tab_number,
                enable_enhancement=enable_enhancement,
                video_width_ratio=video_width_ratio,
                video_height_ratio=video_height_ratio
            )
            return success, result
        except Exception as e:
            return False, str(e)
