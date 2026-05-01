import os
from github import Github
from dotenv import load_dotenv
from code_review_agent import CodeReviewAgent

load_dotenv()


class GitHubIntegration:
    def __init__(self):
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.agent = CodeReviewAgent()
        
    def review_pr(self, repo_name: str, pr_number: int):
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        self.agent.load_repository(".")
        
        review_results = {}
        for file in pr.get_files():
            if file.filename.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c')):
                content = file.patch
                review = self.agent.analyze_code(content, file.filename)
                review_results[file.filename] = review
                
                for issue in review["issues"]:
                    pr.create_review_comment(
                        body=f"❌ **{issue['severity']}**: {issue['description']}\n\n💡 建议：{issue['suggestion']}",
                        commit=pr.get_commits().reversed[0],
                        path=file.filename,
                        line=issue.get("line_number", 1)
                    )
        
        overall_score = sum(r["score"] for r in review_results.values()) / len(review_results) if review_results else 0
        
        pr.create_issue_comment(
            f"""🤖 **AI代码审查报告**

📊 总体评分：{overall_score:.1f}/100
📁 审查文件：{len(review_results)} 个
🐛 发现问题：{sum(len(r["issues"]) for r in review_results.values())} 个

---
*此审查由AI自动生成，请结合人工评审使用*"""
        )
        
        return review_results


if __name__ == "__main__":
    integration = GitHubIntegration()
    # 使用示例：integration.review_pr("owner/repo", 123)
