from git_analysis import git_analysis
from project_analysis import project_analysis

def main():
    project_name = "./tests/test1 Project/test1.als"
    repository_name = "./tests"

    project_linenos = project_analysis(project_name)
    
    result = git_analysis(repository_name, project_linenos)

if __name__ == '__main__':
    main()
