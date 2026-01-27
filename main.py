import sys
import os
import datetime
from pathlib import Path

# ---------------- 配置区域 ----------------  
try:
    from config.settings import (
        Q_FIN_SEARCH_CONFIG, Q_FIN_QUERY,
        SEARCH_RECOMMENDATION_SEARCH_CONFIG, SEARCH_RECOMMENDATION_QUERY,
        LLM_CONFIG
    )
    # 从 LLM_CONFIG 中获取 API_KEY
    API_KEY = LLM_CONFIG.get('api_key')
except ImportError:
    # 备用默认配置
    Q_FIN_SEARCH_CONFIG = {'categories': ['q-fin.CP'], 'max_total_results': 5}
    Q_FIN_QUERY = "quantitative finance"
    SEARCH_RECOMMENDATION_SEARCH_CONFIG = {'categories': ['cs.IR'], 'max_total_results': 5}
    SEARCH_RECOMMENDATION_QUERY = "recommendation system"
    API_KEY = None

# === 关键修正：环境变量覆盖 ===
# 这行代码的意思是：如果系统环境变量里有 LLM_API_KEY（GitHub 设置的），就用它的；
# 如果没有，就用上面从 settings 读到的或者 None。
API_KEY = os.getenv("LLM_API_KEY") or API_KEY
# ----------------------------------------

# 修复路径问题
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.arxiv_client import ArxivClient
    from src.paper_summarizer import PaperSummarizer
except ImportError as e:
    print(f"错误：找不到必要的模块，请检查文件结构。{e}")
    sys.exit(1)

def process_domain(domain_name, search_config, query, paper_summarizer, base_dir, output_dir):
    """处理单个领域的论文搜索和摘要生成"""
    print(f"\n{'='*60}")
    print(f"开始处理 {domain_name} 领域论文")
    print(f"{'='*60}")
    
    # 初始化 Arxiv 客户端（使用特定领域的配置）
    try:
        arxiv_client = ArxivClient(search_config, domain_name=domain_name)
    except Exception as e:
        print(f"初始化 {domain_name} ArxivClient 失败: {e}")
        return None
    
    # 搜索论文
    print(f"正在搜索 {domain_name} 最新论文...")
    results = arxiv_client.search_papers(
        categories=search_config.get('categories', []),
        query=query
    )
    
    # 过滤掉下载失败或无内容的论文
    valid_results = []
    for paper in results:
        content = paper.get('full_text') or paper.get('summary')
        if content and "下载失败" not in content and "404" not in content:
            valid_results.append(paper)
        else:
            print(f"⚠️ 跳过论文: {paper.get('title', '未知标题')} (原因: 获取内容失败)")
    
    results = valid_results
    
    if not results:
        print(f"没有发现新的 {domain_name} 论文。")
        return None
    
    # 生成摘要
    print(f"\n找到 {len(results)} 篇 {domain_name} 论文，开始生成摘要...")
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # 使用领域名称作为文件名前缀
    domain_prefix = "qfin" if "q-fin" in domain_name.lower() else "search"
    output_file = os.path.join(output_dir, f"summary_{domain_prefix}_{timestamp}.md")
    
    try:
        success = paper_summarizer.summarize_papers(results, output_file, domain_name=domain_name)
        if success:
            print(f"✅ {domain_name} 日报已保存到: {output_file}")
            
            # 保存最后处理的论文ID
            try:
                if results:
                    last_paper = results[-1]
                    paper_id = last_paper.get('paper_id')
                    if not paper_id:
                        entry_id = last_paper.get('entry_id', '')
                        if entry_id:
                            paper_id = arxiv_client._extract_paper_id(entry_id)
                    
                    if paper_id:
                        arxiv_client._save_latest_paper_id(paper_id)
                        print(f"✅ 已记录 {domain_name} 最后处理的论文ID: {paper_id}")
            except Exception as e:
                print(f"⚠️ 保存 {domain_name} 已处理论文记录失败: {e}")
            
            return output_file
        else:
            print(f"❌ {domain_name} 摘要生成失败，请检查错误信息")
            return None
    except Exception as e:
        print(f"生成 {domain_name} 摘要时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print(f"=== Arxiv Q-Fin & 搜推 Daily (中文版) 开始运行 {datetime.datetime.now().strftime('%H:%M:%S')} ===")
    
    # 1. 初始化 Paper Summarizer（两个领域共用）
    try:
        model = LLM_CONFIG.get('model', 'deepseek-v3')
        paper_summarizer = PaperSummarizer(API_KEY, model)
    except Exception as e:
        print(f"初始化 PaperSummarizer 失败: {e}")
        return
    
    base_dir = Path(__file__).parent
    output_dir = base_dir / "data"
    output_dir.mkdir(exist_ok=True)
    
    # 2. 分别处理 q-fin 和搜推领域
    output_files = []
    
    # 处理 q-fin 领域
    qfin_output = process_domain(
        "Q-Fin (量化金融)",
        Q_FIN_SEARCH_CONFIG,
        Q_FIN_QUERY,
        paper_summarizer,
        base_dir,
        output_dir
    )
    if qfin_output:
        output_files.append(qfin_output)
    
    # 处理搜推领域
    search_output = process_domain(
        "搜推 (搜索推荐)",
        SEARCH_RECOMMENDATION_SEARCH_CONFIG,
        SEARCH_RECOMMENDATION_QUERY,
        paper_summarizer,
        base_dir,
        output_dir
    )
    if search_output:
        output_files.append(search_output)
    
    # 3. 发送邮件（如果有生成的文件）
    if output_files:
        try:
            from src.mailer import Mailer
            mailer = Mailer()
            # 发送所有生成的文件
            for output_file in output_files:
                try:
                    mailer.send_daily_summary(output_file)
                except Exception as e:
                    print(f"⚠️ 发送 {output_file} 邮件失败: {e}")
        except Exception as e:
            print(f"⚠️ 邮件模块调用失败: {e}")
    else:
        print("\n没有发现新论文。")
        print("提示：将使用已有的摘要文件生成网站。")
        
        # 发送无新论文通知
        try:
            from src.mailer import Mailer
            mailer = Mailer()
            mailer.send_no_papers_message()
        except Exception as e:
            print(f"⚠️ 邮件模块调用失败: {e}")

if __name__ == "__main__":
    main()