#!/usr/bin/env python3
"""
文献检索与验证脚本
用于从学术平台检索校园信息智能响应系统相关文献

支持的平台:
- cnki: 中国知网
- wanfang: 万方数据
- arxiv: arXiv预印本
- openalex: OpenAlex学术图谱
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Optional


def search_cnki(keyword: str, max_results: int = 10) -> List[str]:
    """从知网检索文献"""
    search_url = f"https://search.cnki.com.cn/Search/Result?content={keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = []
        for item in soup.select('.result-list li')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append(link['href'])
        return urls
    except Exception as e:
        print(f"CNKI搜索错误: {e}")
        return []


def search_wanfang(keyword: str, max_results: int = 10) -> List[str]:
    """从万方数据检索文献"""
    search_url = f"https://www.wanfangdata.com.cn/search/searchAll.jsp?searchType=all&content={keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = []
        for item in soup.select('.search-list li')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append(link['href'])
        return urls
    except Exception as e:
        print(f"万方搜索错误: {e}")
        return []


def search_arxiv(keyword: str, max_results: int = 10) -> List[str]:
    """从arXiv检索文献"""
    search_url = f"https://arxiv.org/search/?query={keyword}&search_type=all&max_results={max_results}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = []
        for item in soup.select('.list-lst')[:max_results]:
            link = item.select_one('.title a')
            if link and link.get('href'):
                urls.append("https://arxiv.org" + link['href'])
        return urls
    except Exception as e:
        print(f"arXiv搜索错误: {e}")
        return []


def search_openalex(keyword: str, max_results: int = 10) -> List[str]:
    """从OpenAlex检索文献"""
    search_url = f"https://openalex.org/works?search={keyword}&per-page={max_results}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = []
        for item in soup.select('.work')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append("https://openalex.org" + link['href'])
        return urls
    except Exception as e:
        print(f"OpenAlex搜索错误: {e}")
        return []


def get_cnki_paper_details(url: str) -> Optional[Dict]:
    """获取知网论文详情"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paper_info = {"url": url, "platform": "cnki"}
        
        title_elem = soup.select_one('#mainTitle') or soup.select_one('h1')
        paper_info["title"] = title_elem.get_text(strip=True) if title_elem else None
        
        authors = []
        for author in soup.select('.author a')[:5]:
            authors.append(author.get_text(strip=True))
        paper_info["authors"] = authors
        
        journal_elem = soup.select_one('.journal-name')
        paper_info["journal"] = journal_elem.get_text(strip=True) if journal_elem else None
        
        year_elem = soup.select_one('.publish-date')
        if year_elem:
            text = year_elem.get_text(strip=True)
            match = re.search(r'(\d{4})', text)
            paper_info["year"] = match.group(1) if match else text[:4]
        
        doi_elem = soup.select_one('meta[name="citation_doi"]')
        paper_info["doi"] = doi_elem['content'] if doi_elem else None
        
        return paper_info if paper_info.get('title') else None
    except Exception as e:
        print(f"获取详情错误: {e}")
        return None


def get_arxiv_paper_details(url: str) -> Optional[Dict]:
    """获取arXiv论文详情"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paper_info = {"url": url, "platform": "arxiv"}
        
        title_elem = soup.select_one('meta[name="citation_title"]')
        paper_info["title"] = title_elem['content'] if title_elem else None
        
        authors = []
        for author in soup.select('.authors a'):
            authors.append(author.get_text(strip=True))
        paper_info["authors"] = authors
        
        journal_elem = soup.select_one('meta[name="citation_journal_title"]')
        paper_info["journal"] = journal_elem['content'] if journal_elem else "arXiv preprint"
        
        date_elem = soup.select_one('meta[name="citation_date"]')
        paper_info["year"] = date_elem['content'][:4] if date_elem else None
        
        doi_elem = soup.select_one('meta[name="citation_doi"]')
        paper_info["doi"] = doi_elem['content'] if doi_elem else None
        
        return paper_info if paper_info.get('title') else None
    except Exception as e:
        print(f"获取arXiv详情错误: {e}")
        return None


def main():
    """主函数：检索校园信息智能Agent相关文献"""
    
    # 检索关键词
    keywords = [
        "大语言模型 智能Agent",
        "校园信息系统 AI对话",
        "LLM Agent 对话系统",
        "校园服务 chatbot"
    ]
    
    all_papers = []
    
    print("=" * 60)
    print("开始文献检索...")
    print("=" * 60)
    
    # 从知网检索
    print("\n[1] 检索知网...")
    for kw in keywords[:2]:
        print(f"  关键词: {kw}")
        urls = search_cnki(kw, 5)
        for url in urls[:3]:
            paper = get_cnki_paper_details(url)
            if paper and paper.get('title'):
                all_papers.append(paper)
                print(f"    ✓ {paper['title'][:40]}...")
        time.sleep(1)
    
    # 从arXiv检索
    print("\n[2] 检索arXiv...")
    for kw in keywords[:2]:
        print(f"  关键词: {kw}")
        urls = search_arxiv(kw, 5)
        for url in urls[:3]:
            paper = get_arxiv_paper_details(url)
            if paper and paper.get('title'):
                all_papers.append(paper)
                print(f"    ✓ {paper['title'][:40]}...")
        time.sleep(1)
    
    # 去重
    seen_titles = set()
    unique_papers = []
    for paper in all_papers:
        title = paper.get('title', '').strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_papers.append(paper)
    
    print(f"\n" + "=" * 60)
    print(f"共检索到 {len(unique_papers)} 篇独特文献")
    print("=" * 60)
    
    # 保存结果
    with open('retrieved_papers.json', 'w', encoding='utf-8') as f:
        json.dump(unique_papers, f, ensure_ascii=False, indent=2)
    
    return unique_papers


if __name__ == "__main__":
    main()
