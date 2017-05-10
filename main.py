import gzip
from sys import argv
from analysis.git import git_analysis
from analysis.project import project_analysis

from description.description import describe_operation

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

# FIXME : add option --checkout :
#             checkout a version, commit etc
#             compress the version to the file name
# 
#         add option --save :
#             commit project
#
#         add option --create :
#             create a folder .ableton in the project
#             keep data in there like .git does
#             if current folder has a .ableton allow code to be executed
#             or target folder idem

def main(commita = None, commitb = None):
    repository_name = "./tests"
    project_directory = repository_name + "/test Project/"
    project_name = "test"

    # try:
    # FIXME : implement that + checkout
    # commitaref = repo.revparse_single(commita)
    # commitbref = repo.revparse_single(commitb)
    #         + project analysis of the checkout
    #         repo.stash if needed
    # print commitaref.author.time
    # print commitbref.author.time
    # print max(commitaref.author.time, commitbref.author.time)
    
    project_content = update_local_file(project_directory, project_name)

    elements = project_analysis(project_content)

    chunks = git_analysis(repository_name, commita, commitb)

    describe_operation(chunks, elements)

    # finally:
    # FIXME : repo.stash_pop

if __name__ == "__main__":

    if len(argv) == 3:
        main(argv[1], argv[2])
    elif len(argv) == 2:
        main(argv[1])
    else:
        main()
