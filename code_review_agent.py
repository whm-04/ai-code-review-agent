import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import git
import requests

load_dotenv()


class CodeReviewAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4-turbo",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.repo = None
        
    def load_repository(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        return self.repo
        
    def get_changed_files(self, commit_hash: str = None) -> List[str]:
        if not self.repo:
            raise ValueError("Repository not loaded")
            
        if commit_hash:
            diff = self.repo.git.diff(f"{commit_hash}~1", commit_hash, name_only=True)
        else:
            diff = self.repo.git.diff("--cached", name_only=True)
            
        files = diff.splitlines() if diff else []
        return [f for f in files if f.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c'))]
        
    def get_file_content(self, file_path: str, commit_hash: str = None) -> str:
        if not self.repo:
            raise ValueError("Repository not loaded")
            
        if commit_hash:
            try:
                return self.repo.git.show(f"{commit_hash}:{file_path}")
            except:
                return ""
        else:
            with open(os.path.join(self.repo.working_dir, file_path), 'r', encoding='utf-8') as f:
                return f.read()
                
    def analyze_code(self, code: str, file_path: str) -> Dict[str, Any]:
        system_prompt = """你是一位经验丰富的高级代码审查专家。你的任务是：
1. 识别代码中的潜在bug和逻辑错误
2. 检查代码风格和最佳实践遵循情况
3. 发现安全漏洞和性能问题
4. 提供具体的改进建议和重构方案

请以JSON格式返回审查结果，包含以下字段：
- issues: 问题列表（每个问题包含description, severity, line_number, suggestion）
- suggestions: 改进建议列表
- score: 总体评分（0-100）
- summary: 简短总结
"""

        human_prompt = f"""请审查以下代码文件：{file_path}

代码内容：
{code}

请进行全面的代码审查。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            import json
            result = json.loads(response.content)
            return result
        except:
            return {
                "issues": [],
                "suggestions": [response.content],
                "score": 70,
                "summary": "审查完成"
            }
            
    def generate_pr_description(self, commit_hash: str) -> str:
        files = self.get_changed_files(commit_hash)
        changes_summary = []
        
        for file in files:
            content = self.get_file_content(file, commit_hash)
            changes_summary.append(f"## {file}\n\n```\n{content[:500]}...\n```")
            
        system_prompt = """你是一位专业的PR描述生成专家。根据提交的代码变更，生成一份清晰、专业的PR描述，包括：
1. 变更概述
2. 主要改动点
3. 影响范围
4. 测试建议（如适用）
"""

        human_prompt = f"""请为以下代码变更生成PR描述：

{chr(10).join(changes_summary)}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
        
    def full_review(self, repo_path: str, commit_hash: str = None) -> Dict[str, Any]:
        self.load_repository(repo_path)
        files = self.get_changed_files(commit_hash)
        
        results = {}
        total_score = 0
        issue_count = 0
        
        for file in files:
            content = self.get_file_content(file, commit_hash)
            review = self.analyze_code(content, file)
            results[file] = review
            total_score += review["score"]
            issue_count += len(review["issues"])
            
        avg_score = total_score / len(files) if files else 0
        pr_desc = self.generate_pr_description(commit_hash) if commit_hash else ""
        
        return {
            "reviewed_files": files,
            "results": results,
            "overall_score": avg_score,
            "total_issues": issue_count,
            "pr_description": pr_desc,
            "token_usage": {
                "estimated": len(str(results)) // 4
            }
        }


def main():
    agent = CodeReviewAgent()
    
    repo_path = "./test-repo"
    if os.path.exists(repo_path):
        result = agent.full_review(repo_path)
        print(f"审查完成！总体评分：{result['overall_score']}")
        print(f"发现问题数：{result['total_issues']}")
        print(f"已审查文件：{', '.join(result['reviewed_files'])}")
    else:
        print(f"请将代码仓库放在 {repo_path} 目录下")


if __name__ == "__main__":
    main()