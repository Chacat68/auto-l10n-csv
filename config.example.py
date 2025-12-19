# 配置文件示例

# CSV文件配置
CSV_CONFIG = {
    'source_column': 'ZH',  # 源语言列名
    'target_columns': ['TH', 'VN'],  # 目标语言列名
    'skip_existing': True,  # 是否跳过已有翻译
}

# 翻译配置
TRANSLATION_CONFIG = {
    'delay': 0.1,  # 每次翻译的延迟（秒），避免API速率限制
    'retry_times': 3,  # 失败重试次数
}

# 语言代码映射
LANGUAGE_MAP = {
    'ZH': 'zh-cn',  # 简体中文
    'TH': 'th',     # 泰语
    'VN': 'vi',     # 越南语
}
