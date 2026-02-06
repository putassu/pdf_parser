class AnalyzerConfig:
    # Эвристики поиска
    GAP_TOLERANCE_ROW = 2  # Сколько пустых строк допустимо внутри одного блока
    GAP_TOLERANCE_COL = 3  # Сколько пустых колонок (часто в расчетках/анкетах)
    
    # Лимиты токенов
    MAX_TOKENS_BLOCK = 300
    MAX_TOKENS_FILE = 65000
    
    # Пороги классификации
    MIN_ROWS_FOR_TABLE = 5
    MIN_COLS_FOR_TABLE = 2
    LARGE_TABLE_THRESHOLD = 100
    DENSITY_THRESHOLD_TABLE = 0.6
    BLOCK_TYPES_LIBRARY = {
    "RECORD_FORM": "Набор пар 'Ключ: Значение'. Применяется для анкет, реквизитов, шапок документов и личных данных.",
    "DATA_GRID": "Регулярная таблица с повторяющимися строками данных и четкими заголовками (столбцами).",
    "NARRATIVE_TEXT": "Текстовые блоки: инструкции, комментарии, юридические дисклеймеры, условия договора.",
    "TECHNICAL_DATA": "Служебная информация: версии справочников, системные метки, не относящиеся к сути документа."
}

LLM_ENDPOINT = " http://localhost:11434"
LLM_TOKEN = ""
LLM_MODEL = "gemma3:4b"

# config.py

# Подробное описание параметров для LLM
# config.py

# config.py

# config.py

# --- ПАРАМЕТРЫ LLM ---
# config.py

# Параметры LLM
LLM_ENDPOINT = "http://localhost:11434"
LLM_MODEL = "gemma3:4b"
LLM_MAX_CONTEXT = 128000  # 128K токенов

# Библиотека типов блоков для промпта
BLOCK_TYPES_LIBRARY = {
    "RECORD_FORM": "Анкетные данные, пары Ключ:Значение, шапки документов.",
    "DATA_GRID": "Табличные данные, списки, реестры с колонками.",
    "NARRATIVE_TEXT": "Текстовые пояснения, инструкции, примечания.",
    "TECHNICAL_DATA": "Метаданные, версии систем, служебные пометки."
}

# Описание технических параметров (для справки)
PARSER_CONFIG_DESC = {
    "V_TOLERANCE": "GAP_TOLERANCE_ROW: сколько пустых строк допустимо внутри блока.",
    "H_TOLERANCE": "GAP_TOLERANCE_COL: сколько пустых колонок допустимо внутри блока.",
    "MAX_CHARS_BLOCK": "Лимит символов, после которого форма считается таблицей.",
    "MIN_TABLE_ROWS": "Минимум строк для определения таблицы."
}

# ПРЕСЕТЫ (Хардкод пресетов, чтобы LLM не ошибалась в числах)
PRESETS = {
    "Tight": {
        "V_TOLERANCE": 1, 
        "H_TOLERANCE": 1, 
        "MAX_CHARS_BLOCK": 1500,
        "MIN_TABLE_ROWS": 3
    },
    "Standard": {
        "V_TOLERANCE": 2, 
        "H_TOLERANCE": 3, 
        "MAX_CHARS_BLOCK": 3000,
        "MIN_TABLE_ROWS": 5
    },
    "Relaxed": {
        "V_TOLERANCE": 6, 
        "H_TOLERANCE": 5, 
        "MAX_CHARS_BLOCK": 6000,
        "MIN_TABLE_ROWS": 10
    }
}

DEFAULT_SETTINGS = {
    "V_TOLERANCE": 2,
    "H_TOLERANCE": 3,
    "MAX_CHARS_BLOCK": 3000,
    "MIN_TABLE_ROWS": 5,
    "VALIDATION_THRESHOLD": 0.98,
    "SHOW_MERGED_MAP": True
}
XLSX_PARSER_NUM_RETRIES = 3 # Максимум попыток тюнинга

BLOCK_TYPES_LIBRARY = {
    "RECORD_FORM": "Анкетные данные, пары Ключ:Значение, шапки документов.",
    "DATA_GRID": "Регулярные таблицы, реестры, списки с колонками.",
    "NARRATIVE_TEXT": "Текстовые пояснения, инструкции.",
    "TECHNICAL_DATA": "Метаданные, системные пометки."
}

PRESETS = {
    "Tight": {"V_TOLERANCE": 1, "H_TOLERANCE": 1, "MAX_CHARS_BLOCK": 1500, "MIN_TABLE_ROWS": 3},
    "Standard": {"V_TOLERANCE": 2, "H_TOLERANCE": 3, "MAX_CHARS_BLOCK": 3000, "MIN_TABLE_ROWS": 5},
    "Relaxed": {"V_TOLERANCE": 6, "H_TOLERANCE": 5, "MAX_CHARS_BLOCK": 6000, "MIN_TABLE_ROWS": 10}
}

DEFAULT_SETTINGS = {**PRESETS["Standard"], "VALIDATION_THRESHOLD": 0.98, "SHOW_MERGED_MAP": True}
