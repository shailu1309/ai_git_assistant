from openai import OpenAI
import git
import os
from dotenv import load_dotenv
import fnmatch
import re

load_dotenv('/Users/sjr11/Work/SelfLearning/Git Chat Agent/ai_git_assistant/.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize the Git repository
repo_path = '/Users/sjr11/Work/SelfLearning/sql_python_etl/python_sql_etl'
repo = git.Repo(os.path.abspath(repo_path)) 

# Functions to read all files from the codebase
def get_all_code_files():
    code_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if fnmatch.fnmatch(file, '*.py') or fnmatch.fnmatch(file, '*.sql') or fnmatch.fnmatch(file, '*.js') or fnmatch.fnmatch(file, '*.java'):
                code_files.append(os.path.join(root, file))
    print(code_files)
    return code_files

# Function to search for SQL queries in code files
def search_for_sql_queries():
    project_files = get_all_code_files()
    sql_queries = []

    sql_pattern = re.compile(r'(SELECT|INSERT|UPDATE|DELETE)\s', re.IGNORECASE)

    for file_path in project_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            if sql_pattern.search(content):
                sql_queries.append((file_path, content))
    # print("sql files and queries \n :", sql_queries)
    return sql_queries

# Function to extract content from the codebase for project analysis
def analyze_codebase():
    project_files = get_all_code_files()
    project_content = ""

    for file_path in project_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            project_content += file.read() + "\n"

    return project_content

# Define a function to ask questions in natural language
def ask_gpt(question, context=""):
    response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"{context}\n\nQuestion: {question}\nAnswer:",
        }
    ],
    model="gpt-3.5-turbo")
    return response.choices[0].message.content

# Function to handle Git-related queries
def handle_git_queries(question):
    # Basic questions to map natural language to Git actions
    if "files changed in last commit" in question:
        last_commit = repo.head.commit
        return f"The following files were changed in the last commit: {', '.join(last_commit.stats.files.keys())}"
    elif "last commit" in question:
        last_commit = repo.head.commit
        return f"The last commit was made by {last_commit.author} with the message: '{last_commit.message.strip()}'"
    elif "branch" in question:
        branches = repo.branches
        return f"The current branches are: {', '.join([branch.name for branch in branches])}"
    elif "current branch" in question:
        return f"The current branch is: {repo.active_branch.name}"
    
# Function to handle advanced Git and project-related queries
def handle_project_queries(question):
    if "what is this project about" in question.lower():
        project_content = analyze_codebase()
        context = "This is the source code of a software project. Summarize what the project is about."
        return ask_gpt(f"Summarize this project: {project_content[:2000]}", context)
    
    if "are there any sql queries" in question.lower():
        sql_queries = search_for_sql_queries()
        if sql_queries:
            return f"SQL queries found in the following files:\n" + "\n".join([f"{file_path}" for file_path, _ in sql_queries])
        else:
            return "No SQL queries found in the project."
    
    return "I couldn't understand your query. Try asking something else related to the project or commits."


# Main interactive function
def chat_with_git():
    context = "You are chatting with your Git repository. You can ask questions about commits, branches, or files."

    while True:
        question = input("Ask about your Git repo: ")

        if question.lower() in ["exit", "quit"]:
            break

        # Check if the question is Git-related
        if "commit" in question or "branch" in question or "file" in question:
            answer = handle_git_queries(question)
        else:
            answer = handle_project_queries(question)

        print("Answer:", answer)

if __name__ == "__main__":
    chat_with_git()
