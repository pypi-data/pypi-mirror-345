from pathlib import Path
import importlib.util

def load_translations():
    translations = {}
    translations_dir = Path(__file__).parent
    
    for lang_file in translations_dir.glob('*.py'):
        if lang_file.stem == '__init__':
            continue
            
        spec = importlib.util.spec_from_file_location(
            f"translations.{lang_file.stem}",
            lang_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'translations'):
            translations[lang_file.stem] = module.translations
            
    return translations