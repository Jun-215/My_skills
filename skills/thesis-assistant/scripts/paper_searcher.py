#!/usr/bin/env python3
"""
文献检索与验证脚本
用于从学术平台检索文献并提取字段信息

支持的平台:
- cnki: 中国知网
- wanfang: 万方数据
- cqvip: 维普资讯
- arxiv: arXiv预印本
- openalex: OpenAlex学术图谱
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional


def search_papers(keyword: str, platform: str = "cnki", max_results: int = 10) -> List[str]:
    """
    在指定学术平台检索文献，返回文献详情页URL列表

    Args:
        keyword: 检索关键词
        platform: 学术平台 (cnki/wanfang/cqvip/arxiv/openalex)
        max_results: 最大返回数量

    Returns:
        文献详情页URL列表
    """
    search_urls = {
        "cnki": f"https://search.cnki.com.cn/Search/Result?content={keyword}",
        "wanfang": f"https://www.wanfangdata.com.cn/search/searchAll.jsp?searchType=all&content={keyword}",
        "cqvip": f"https://search.qikan.cqvip.com/search/Result?content={keyword}",
        "arxiv": f"https://arxiv.org/search/?query={keyword}&search_type=all&max_results={max_results}",
        "openalex": f"https://openalex.org/works?search={keyword}&per-page={max_results}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if platform not in search_urls:
        raise ValueError(f"Unsupported platform: {platform}")

    url = search_urls[platform]
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    urls = []

    if platform == "cnki":
        for item in soup.select('.result-list li')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append(link['href'])

    elif platform == "wanfang":
        for item in soup.select('.search-list li')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append(link['href'])

    elif platform == "cqvip":
        for item in soup.select('.result-list li')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append(link['href'])

    elif platform == "arxiv":
        for item in soup.select('.list-lst')[:max_results]:
            link = item.select_one('.title a')
            if link and link.get('href'):
                urls.append("https://arxiv.org" + link['href'])

    elif platform == "openalex":
        for item in soup.select('.work')[:max_results]:
            link = item.select_one('a')
            if link and link.get('href'):
                urls.append("https://openalex.org" + link['href'])

    return urls


def get_paper_details(url: str, platform: str = "cnki") -> Optional[Dict]:
    """
    从文献详情页提取完整信息

    Args:
        url: 文献详情页URL
        platform: 学术平台

    Returns:
        包含论文信息的字典，失败返回None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        paper_info = {"url": url, "platform": platform}

        if platform == "cnki":
            title_elem = soup.select_one('#mainTitle') or soup.select_one('h1.title')
            paper_info["title"] = title_elem.get_text(strip=True) if title_elem else None

            authors = []
            for author in soup.select('.author a')[:5]:
                authors.append(author.get_text(strip=True))
            paper_info["authors"] = authors

            journal_elem = soup.select_one('.journal-name') or soup.select_one('.journal')
            paper_info["journal"] = journal_elem.get_text(strip=True) if journal_elem else None

            year_elem = soup.select_one('.publish-date') or soup.select_one('.year')
            if year_elem:
                text = year_elem.get_text(strip=True)
                paper_info["year"] = text[:4] if len(text) >= 4 else text

            doi_elem = soup.select_one('meta[name="citation_doi"]')
            paper_info["doi"] = doi_elem['content'] if doi_elem else None

        elif platform == "arxiv":
            title_elem = soup.select_one('meta[name="citation_title"]')
            paper_info["title"] = title_elem['content'] if title_elem else None

            authors = []
            for author in soup.select('.authors a'):
                authors.append(author.get_text(strip=True))
            paper_info["authors"] = authors

            journal_elem = soup.select_one('meta[name="citation_journal_title"]')
            paper_info["journal"] = journal_elem['content'] if journal_elem else "arXiv"

            year_elem = soup.select_one('meta[name="citation_date"]')
            if year_elem:
                paper_info["year"] = year_elem['content'][:4]

            doi_elem = soup.select_one('meta[name="citation_doi"]')
            paper_info["doi"] = doi_elem['content'] if doi_elem else None

        elif platform == "openalex":
            title_elem = soup.select_one('h1') or soup.select_one('.title')
            paper_info["title"] = title_elem.get_text(strip=True) if title_elem else None

            authors = []
            for author in soup.select('.authors span')[:5]:
                authors.append(author.get_text(strip=True))
            paper_info["authors"] = authors

            journal_elem = soup.select_one('.journal') or soup.select_one('.venue')
            paper_info["journal"] = journal_elem.get_text(strip=True) if journal_elem else None

            year_elem = soup.select_one('.year') or soup.select_one('.publication_date')
            if year_elem:
                text = year_elem.get_text(strip=True)
                paper_info["year"] = text[:4] if len(text) >= 4 else text

            paper_info["doi"] = None

        return paper_info

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def search_and_extract(keyword: str, platform: str = "cnki", max_results: int = 10) -> List[Dict]:
    """
    综合检索函数：搜索文献并提取详细信息

    Args:
        keyword: 检索关键词
        platform: 学术平台
        max_results: 最大文献数量

    Returns:
        包含所有文献信息的字典列表
    """
    urls = search_papers(keyword, platform, max_results)
    papers = []

    for url in urls:
        paper = get_paper_details(url, platform)
        if paper and paper.get('title'):
            papers.append(paper)
            print(f"Retrieved: {paper['title'][:50]}...")
        time.sleep(1)

    return papers


def generate_reference(paper: Dict) -> str:
    """
    根据论文信息生成标准格式的参考文献

    Args:
        paper: 包含论文信息的字典

    Returns:
        格式化的参考文献字符串
    """
    authors = ", ".join(paper.get('authors', [])) if paper.get('authors') else "未知作者"
    title = paper.get('title', '未知标题')
    journal = paper.get('journal', '未知期刊')
    year = paper.get('year', '0000')
    doi = paper.get('doi', '')
    url = paper.get('url', '')

    if doi:
        ref = f"[序号] {authors}. {title}[J]. {journal}, {year}. DOI: {doi}"
    else:
        ref = f"[序号] {authors}. {title}[J]. {journal}, {year}"

    if url:
        ref += f"\nSourceURL: {url}"

    return ref


def main():
    """主函数示例"""
    keyword = "深度学习 图像分类"

    print(f"Searching for: {keyword}")
    print("-" * 50)

    papers = search_and_extract(keyword, platform="cnki", max_results=5)

    print(f"\nFound {len(papers)} papers:")
    print("-" * 50)

    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}] {paper['title']}")
        print(f"    Authors: {', '.join(paper['authors'][:3]) if paper['authors'] else 'N/A'}")
        print(f"    Journal: {paper.get('journal', 'N/A')}")
        print(f"    Year: {paper.get('year', 'N/A')}")
        print(f"    URL: {paper['url']}")


if __name__ == "__main__":
    main()
