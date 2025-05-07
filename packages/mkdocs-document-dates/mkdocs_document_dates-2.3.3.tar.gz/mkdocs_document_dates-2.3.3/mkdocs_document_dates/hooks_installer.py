import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def get_config_dir():
    if platform.system().lower().startswith('win'):
        return Path(os.getenv('APPDATA', str(Path.home() / 'AppData' / 'Roaming')))
    else:
        return Path.home() / '.config'

def install():
    try:
        # 检查 git 是否可用
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True, encoding='utf-8')
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Tip: Git not detected, skip hooks installation")
            return False
        
        # 准备配置目录
        config_dir = get_config_dir() / 'mkdocs-document-dates' / 'hooks'
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Error: No permission to create directory: {config_dir}")
            return False
        except Exception as e:
            print(f"Error: Failed to create directory: {config_dir}, reason: {e}")
            return False

        hook_path = config_dir / 'pre-commit'

        # 复制 hook 文件到配置目录
        source_hook = Path(__file__).parent / 'hooks' / 'pre-commit'
        if not source_hook.exists():
            print(f"Error: Source hook file does not exist: {source_hook}")
            return False

        try:
            shutil.copy2(source_hook, hook_path)
        except PermissionError:
            print(f"Error: No permission to copy file to: {hook_path}")
            return False
        except Exception as e:
            print(f"Error: Failed to copy file, reason: {e}")
            return False

        # 设置文件权限
        try:
            os.chmod(config_dir, 0o755)
            os.chmod(hook_path, 0o755)
        except OSError as e:
            print(f"Warning: Error setting permissions: {e}")

        # 配置全局 git hooks 路径
        try:
            subprocess.run(['git', 'config', '--global', 'core.hooksPath', 
                          str(config_dir)], check=True, encoding='utf-8')
            # print(f"Git hooks are installed in the: {config_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error: Setting git hooks path failed: {e}")
            return False
            
    except Exception as e:
        print(f"Error installing hooks: {e}")
        return False

if __name__ == '__main__':
    install()