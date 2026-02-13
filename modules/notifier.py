import os
import threading
import time

from modules.config_global import global_config

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class Notifier:
    @staticmethod
    def notify(title, message, sound_path=None):
        """
        Envia uma notificação desktop e toca um som se disponível.
        Funciona em Windows e Linux.
        """
        # 1. Notificação Visual (Thread separada para não travar a UI)
        if PLYER_AVAILABLE:
            threading.Thread(
                target=Notifier._show_notification,
                args=(title, message),
                daemon=True
            ).start()
        else:
            print(f"Plyer não disponível. Notificação: {title} - {message}")

        # 2. Som de Notificação
        if not sound_path:
            sound_path = global_config.get("notification_sound_path")
            
        if sound_path == "mute":
            return

        if sound_path:
            if not os.path.isabs(sound_path) and not os.path.exists(sound_path):
                # Tenta resolver relativo ao raiz do projeto
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                test_path = os.path.join(project_root, sound_path)
                if os.path.exists(test_path):
                    sound_path = test_path

            if os.path.exists(sound_path):
                Notifier.play_sound(sound_path)
            else:
                Notifier.play_default_sound()
        else:
            # Tentar um som padrão se nenhum path estiver configurado
            Notifier.play_default_sound()

    @staticmethod
    def _show_notification(title, message):
        # Tenta usar Plyer primeiro
        success = False
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Editor 9:16",
                    timeout=10
                )
                success = True
            except Exception as e:
                print(f"Erro ao enviar via Plyer: {e}")

        # Fallback para notify-send no Linux com prioridade crítica
        if not success and os.name == 'posix':
            try:
                import subprocess
                # Adiciona urgência crítica para aparecer sobre qualquer janela
                subprocess.run([
                    'notify-send', 
                    '-u', 'critical',  # Urgência crítica
                    '-t', '10000',      # 10 segundos
                    title, 
                    message
                ], check=False)
            except Exception as e:
                print(f"Erro ao enviar via notify-send: {e}")

    @staticmethod
    def play_sound(sound_path):
        if not PYGAME_AVAILABLE:
            return

        volume = global_config.get("notification_volume")

        def _play():
            try:
                # Inicialização robusta do mixer
                if not pygame.mixer.get_init():
                    try:
                        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                    except Exception as e:
                        print(f"Erro na init do mixer, tentando padrão: {e}")
                        pygame.mixer.init()
                
                if not os.path.exists(sound_path):
                    print(f"Som não encontrado: {sound_path}")
                    return

                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(volume)
                sound.play()
                # Pequena pausa para garantir que o som comece e termine
                time.sleep(sound.get_length() + 0.1)
            except Exception as e:
                print(f"Erro ao tocar som: {e}")

        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def play_default_sound():
        """Tenta encontrar um som do sistema no Linux ou toca um beep no Windows"""
        if os.name == 'posix':  # Linux
            # Caminho absoluto para a pasta de sons
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            local_media_path = os.path.join(project_root, "audio_notification")
            
            system_sounds = [
                os.path.join(local_media_path, "done1.mp3"), # Nova prioridade
                os.path.join(local_media_path, "responseReceived1.mp3"),
                os.path.join(local_media_path, "taskCompleted.mp3"),
                os.path.join(local_media_path, "success.mp3"),
                "/usr/share/sounds/linuxmint-login.wav",
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/freedesktop/stereo/notify.oga",
                "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"
            ]
            for sound in system_sounds:
                if os.path.exists(sound):
                    Notifier.play_sound(sound)
                    return
        elif os.name == 'nt':  # Windows
            try:
                import winsound
                winsound.MessageBeep()
            except ImportError:
                pass

if __name__ == "__main__":
    # Teste manual
    print("Testando notificação...")
    Notifier.notify("Teste de Renderização", "Esta é uma notificação de teste.")
    time.sleep(2)  # Dar tempo para a thread processar
