import gzip
from sys import argv
from analysis.versioning import git_analysis, get_repository, checkout_commit_state, repository_clean, restore_state, stash
from analysis.project import project_analysis

from description.description import describe_operation

def read_project(project_directory, project_name):
    project_path = project_directory + project_name
    with open(project_path, 'rb') as project:
        project_content = project.read()
        return project_content

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
#             get back to an anterior version
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
#
#         add project folder as an option

def main(commita = None, commitb = None):
    repository_name = "./tests"
    project_directory = repository_name + "/test Project/"
    project_name = "test"
    
    stashed = False

    repository = get_repository(repository_name)
    previous_head = repository.head.name
    project_content = None

    try:
        if repository_clean(repository) and commitb is None:
            print "Clean work directory"
            project_content = update_local_file(project_directory, project_name)

        if commitb is not None:
            # if there is two commit to compare and not a simple comparison
            # to the actual state
            # we need to stash
            # and checkout the project of the most recent commit
            print "Stashing and checking out"
            stashed = stash(repository)
            checkout_commit_state(repository, commita, commitb)
#            print repository.head_is_detached
            project_content = read_project(project_directory, project_name)
        elif project_content is None:
            project_content = read_project(project_directory, project_name)

        elements = project_analysis(project_content)

        chunks = git_analysis(repository_name, commita, commitb)

        print chunks[1]['begin_lineno']
        print elements[chunks[1]['begin_lineno']]
        exit(-1)

        describe_operation(chunks, elements)

#    except Exception as e:
#        print "Global error: %s"  % e
    finally:
       restore_state(repository, stashed, previous_head)
#       print repository.head_is_detached
       pass

if __name__ == "__main__":

    if len(argv) == 3:
        main(argv[1], argv[2])
    elif len(argv) == 2:
        main(argv[1])
    else:
        main()
