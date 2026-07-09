import json
from pathlib import Path

MEMORY_FILE = Path(__file__).with_name("memory.json")


DEFAULT_MEMORY = {
    "interests": "",
}


def init_memory(default_memory: dict) -> dict:
    """
    初始化 memory.json
    """
    MEMORY_FILE.write_text(
        json.dumps(default_memory, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return default_memory


def load_memory() -> dict:
    """
    从memory.json中读取记忆
    """

    if not MEMORY_FILE.exists():
        return {}

    text = MEMORY_FILE.read_text(encoding="utf-8")

    if not text:
        return init_memory(DEFAULT_MEMORY)

    return json.loads(text)


def update_memory(key, value: str) -> dict:
    """
    保存记忆到memory.json
    """

    memory = load_memory()
    memory[key] = value
    MEMORY_FILE.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return memory
