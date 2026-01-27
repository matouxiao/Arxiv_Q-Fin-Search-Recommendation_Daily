"""
ArXiv API 配置文件 - Q-Fin & 搜推 Edition
"""
import os
from dotenv import load_dotenv
load_dotenv()
# q-fin 量化金融分类
Q_FIN_CATEGORIES = [
    "q-fin.CP",  # Computational Finance
    "q-fin.GN",  # General Finance
    "q-fin.PR",  # Pricing of Securities
    "q-fin.RM",  # Risk Management
    "q-fin.ST",  # Statistical Finance
    "q-fin.TR",  # Trading and Market Microstructure
]

# 搜推相关分类
SEARCH_RECOMMENDATION_CATEGORIES = [
    "cs.IR",     # Information Retrieval
    "cs.LG",     # Machine Learning
]

# 兼容旧代码
CATEGORIES = Q_FIN_CATEGORIES + SEARCH_RECOMMENDATION_CATEGORIES

# q-fin 搜索查询配置
Q_FIN_QUERY = '("quantitative finance" OR "algorithmic trading" OR "portfolio optimization" OR "risk management" OR "financial modeling" OR "market microstructure" OR "option pricing" OR "derivatives pricing" OR "asset pricing" OR "trading strategy" OR "high-frequency trading")'

# 搜推搜索查询配置
SEARCH_RECOMMENDATION_QUERY = '("recommendation system" OR "search engine" OR "information retrieval" OR "collaborative filtering" OR "ranking" OR "recommender system" OR "personalized recommendation" OR "learning to rank" OR "neural information retrieval")'

# 兼容旧代码（默认使用 q-fin）
QUERY = Q_FIN_QUERY

# arXiv API 搜索配置（基础配置）
BASE_SEARCH_CONFIG = {
    'max_total_results': 58,          # 每次获取的最大论文数量，建议控制在50以内以节省Token
    'sort_by': 'SubmittedDate',       # 按提交时间排序
    'sort_order': 'Ascending',        # 最老在前（从旧到新）
    'include_cross_listed': True,
    'abstracts': True,
    'id_list': None,
    'title_only': False,
    'author_only': False,
    'abstract_only': False,
    'search_mode': 'all',
    'days_back': 4,                   # 只查询最近N天的论文
}

# q-fin 搜索配置
Q_FIN_SEARCH_CONFIG = {
    **BASE_SEARCH_CONFIG,
    'categories': Q_FIN_CATEGORIES,
}

# 搜推搜索配置
SEARCH_RECOMMENDATION_SEARCH_CONFIG = {
    **BASE_SEARCH_CONFIG,
    'categories': SEARCH_RECOMMENDATION_CATEGORIES,
}

# 兼容旧代码（默认使用 q-fin 配置）
SEARCH_CONFIG = Q_FIN_SEARCH_CONFIG

# 语言模型API配置 (DashScope / DeepSeek)
LLM_CONFIG = {
    # 优先从环境变量读取，如果没有则使用你提供的（本地测试用）
    # 生产环境请务必使用环境变量！
    'api_key': os.getenv("LLM_API_KEY"),
    
    # DashScope 兼容模式模型名称 (DeepSeek-V3)
    'model': 'deepseek-v3', 
    
    # 你的 API Base URL
    'api_url': os.getenv("LLM_API_URL"),
    
    'temperature': 0.3,           # 降低温度，让总结更准确
    'max_output_tokens': 4000,
    'top_p': 0.8,
    'top_k': 40,
    'retry_count': 3,
    'retry_delay': 5,
    'timeout': 120,               # 适当增加超时时间
}

# 输出配置
OUTPUT_DIR = "data"
LAST_RUN_FILE = "last_run.json"
METADATA_FILE = "metadata.json"
LLM_API_KEY = LLM_CONFIG['api_key'] # 兼容 main.py 的引用

# PDF 处理配置
PDF_CONFIG = {
    'extract_key_sections': True,  # True: 提取关键章节（摘要、Introduction、Related Work、Conclusion）, False: 只使用摘要
    'max_chars': 20000,             # 每篇论文最大字符数（避免 token 超限）
}

# Embedding API 配置
EMBEDDING_CONFIG = {
    'api_url': os.getenv("EMBEDDING_API_URL"),
    'timeout': 30,
    'batch_size': 200,  # 每次批量处理的论文数量
}

# DBSCAN 聚类配置
CLUSTERING_CONFIG = {
    'method': 'kmeans',     # 'dbscan' 或 'kmeans'
    'n_clusters': 4,        # K-Means 的聚类数量（建议 3-5）

    'eps': 0.28,  # 邻域半径
    'min_samples': 2,  # 最小样本数
    'n_jobs': -1,  # 使用所有CPU核心
    'top_clusters': 5,  # 选择最大的N个聚类
}

# 邮件配置
# 优先从环境变量读取，如果没有则使用默认值（本地运行时使用）
MAIL_CONFIG = {
    'smtp_server': os.getenv("SMTP_SERVER", "smtp.feishu.cn"),
    'smtp_port': int(os.getenv("SMTP_PORT", "465")),
    'sender_email': os.getenv("SENDER_EMAIL" ),  # 默认使用你的邮箱作为发件人
    'sender_password': os.getenv("SENDER_PASSWORD" ),  # 需要设置环境变量或使用应用专用密码
    'receiver_email': os.getenv("RECEIVER_EMAIL",),  # 默认发送到你的邮箱
}