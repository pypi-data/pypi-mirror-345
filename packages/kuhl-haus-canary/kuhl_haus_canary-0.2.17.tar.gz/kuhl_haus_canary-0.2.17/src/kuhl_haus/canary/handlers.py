def script_handler(script_name: str):
    from typing import Dict
    from kuhl_haus.canary.scripts.canary import Canary

    __script_dict: Dict[str, callable] = {
        "canary": Canary,
    }

    if script_name in __script_dict:
        return __script_dict[script_name]
    raise ValueError(f"No handler for script {script_name}")
