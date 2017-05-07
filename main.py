import gzip
from git_analysis import git_analysis
from project_analysis import project_analysis

# TODO : rename
def update_local_file(project_directory, project_name):
    """
    Uncompress the project .als files
    Copies the content to a plain text file
    Returns the content
    """
    project_path = project_directory + project_name + ".als"
    with gzip.open(project_path, 'rb') as project:
        project_content = project.read()

        with open(project_directory + project_name, 'w+') as f:
            f.write(project_content)
        return project_content

def main():
    repository_name = "./tests"
    project_directory = repository_name + "/test Project/"
    project_name = "test"

    project_content = update_local_file(project_directory, project_name)

    elements = project_analysis(project_content)
    
    result = git_analysis(repository_name, elements)

if __name__ == "__main__":
    main()
