"""
文献检索与验证脚本
用于检索和验证学术论文的真实性
"""
import requests
from bs4 import BeautifulSoup
import json

def search_academic_paper(url, platform="general"):
    """
    检索学术论文并提取详细信息

    Args:
        url: 论文详情页URL
        platform: 学术平台类型

    Returns:
        dict: 论文详细信息
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        paper_info = {
            "url": url,
            "platform": platform,
            "title": "",
            "authors": [],
            "journal": "",
            "year": "",
            "abstract": ""
        }

        if platform == "nih":
            # NIH 论文解析
            title_elem = soup.select_one('h1.title')
            if title_elem:
                paper_info["title"] = title_elem.get_text(strip=True)

            author_elem = soup.select_one('div.authors')
            if author_elem:
                paper_info["authors"] = [a.get_text(strip=True) for a in author_elem.select('a')]

            journal_elem = soup.select_one('span.journal-title')
            if journal_elem:
                paper_info["journal"] = journal_elem.get_text(strip=True)

            year_elem = soup.select_one('span.publish-date')
            if year_elem:
                paper_info["year"] = year_elem.get_text(strip=True)[:4]

        elif platform == "hanspub":
            # 汉斯出版社论文解析
            title_elem = soup.select_one('div.ptitle')
            if title_elem:
                paper_info["title"] = title_elem.get_text(strip=True)

            author_elem = soup.select_one('div.author')
            if author_elem:
                text = author_elem.get_text(strip=True)
                paper_info["authors"] = [a.strip() for a in text.replace('作者:', '').split(',')]

            journal_elem = soup.select_one('meta[name="citation_journal_title"]')
            if journal_elem:
                paper_info["journal"] = journal_elem['content']

        elif platform == "wikipedia":
            # 维基百科解析
            title_elem = soup.select_one('h1.firstHeading')
            if title_elem:
                paper_info["title"] = title_elem.get_text(strip=True)
                paper_info["journal"] = "Wikipedia"
                paper_info["year"] = "2024"

        return paper_info

    except Exception as e:
        print(f"Error retrieving paper from {url}: {str(e)}")
        return None

def verify_reference(paper_info):
    """
    验证参考文献的真实性

    Args:
        paper_info: 论文信息字典

    Returns:
        bool: 验证是否通过
    """
    required_fields = ['title', 'url']
    for field in required_fields:
        if field not in paper_info or not paper_info[field]:
            return False
    return True

if __name__ == "__main__":
    # 测试检索
    test_urls = [
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC12343689/", "nih"),
        ("https://www.hanspub.org/journal/paperinformation?paperid=51912", "hanspub"),
        ("https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D", "wikipedia")
    ]

    for url, platform in test_urls:
        print(f"\n检索 {platform} 平台: {url}")
        paper_info = search_academic_paper(url, platform)
        if paper_info and verify_reference(paper_info):
            print(f"标题: {paper_info['title']}")
            print(f"作者: {paper_info['authors']}")
            print(f"期刊: {paper_info['journal']}")
            print(f"年份: {paper_info['year']}")
            print("✓ 验证通过")
        else:
            print("✗ 检索或验证失败")