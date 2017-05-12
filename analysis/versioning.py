from pygit2 import Repository, Oid
from pygit2 import GIT_STATUS_CURRENT

from lxml import etree
from pprint import pprint
import re

ADDITION = True
SUPPRESSION = False

OPERATION_TYPE = {
        "ADDITION": "added",
        "SUPPRESSION": "removed",
        "MODIFICATION": "modified"
}

TARGET_NAME = {}

def line_removed(line):
    return line.new_lineno == -1

def line_added(line):
    return line.old_lineno == -1

def target_name(target_tag):
    return TARGET_NAME[target_tag] if TARGET_NAME.get(target_tag) else target_tag

def get_chunk_content(chunk):
    return "".join([ line.content for line in chunk["lines"] ])

def label_modifications(chunks, recursion = False):
    """
    Rename a chunk operation to MODIFICATION if needed
    """
    index = 0
    while index < len(chunks):
        subindex = index + 1

        while subindex < len(chunks):
            if  chunks[subindex]["xml"] is not None \
            and chunks[index]["xml"] is not None \
            and chunks[subindex]["xml"].tag == chunks[index]["xml"].tag\
            and chunks[index]["operation_type"] != "MODIFICATION"\
            and chunks[subindex]["operation_type"] != "MODIFICATION":

                 chunks[index]["replaced_by"] = subindex
                 chunks[subindex]["replacing"] = index

                 chunks[index]["operation_type"] = "MODIFICATION"
                 chunks[subindex]["operation_type"] = "MODIFICATION"
            subindex += 1

        index += 1
    return chunks

def eval_operations(chunks):
    res = []
    for chunk in chunks:
        chunk_content = get_chunk_content(chunk)
        try:
            chunk["xml"] = etree.fromstring(chunk_content)
            res.append(chunk)
        except Exception as e:
            # use the lines instead of the all chunk
            for line in chunk["lines"]:
                try:
                    new_chunk = create_chunk([line], ADDITION if chunk["operation_type"]  == "ADDITION" else SUPPRESSION)
                    new_chunk["xml"] = etree.fromstring(line.content)
                    res.append(new_chunk)
                except Exception as e:
                    pass
    return res


def begin_lineno(chunk):
    return chunk[0].old_lineno if chunk[0].new_lineno == -1 else chunk[0].new_lineno + 1

def end_lineno(chunk):
    return chunk[-1].old_lineno if chunk[-1].new_lineno == -1 else chunk[-1].new_lineno

def create_chunk(lines, operation_type):
    return { "operation_type" : "ADDITION" if operation_type == ADDITION else "SUPPRESSION",
             "lines" : lines,
             "begin_lineno" : begin_lineno(lines),
             "end_lineno" : end_lineno(lines)}

def bind_objects(patches):
    """
    Group lines by operations into chunks
    """
    operation = SUPPRESSION
    line_operation = SUPPRESSION
    operation_chunks = []

    addition_buffer = []
    suppression_buffer = []

#    operation = line_added(hunks[0].lines[0]) # TODO : get the first line where line.new_lineno != line.old_lineno

    index = 0

    for patch in patches:
        for hunk in patch.hunks:
            for line in hunk.lines:
                if line_added(line) or line_removed(line):
                    line_operation = line_added(line)

                    # when operation type change, so is the buffer
                    if line_operation != operation:
                        if operation == ADDITION and len(addition_buffer) > 0:
                            operation_chunks.append(create_chunk(addition_buffer, ADDITION))
                            addition_buffer = []
                        elif operation == SUPPRESSION and len(suppression_buffer) > 0:
                            operation_chunks.append(create_chunk(suppression_buffer, SUPPRESSION))
                            suppression_buffer = []

                        operation = not operation
 
                    if line_operation == ADDITION:
                        addition_buffer.append(line)
                    else:
                        suppression_buffer.append(line)

            # create a new chunk when the chunk is done and flush the buffers
            if len(addition_buffer) > 0:
                operation_chunks.append(create_chunk(addition_buffer, ADDITION))
                addition_buffer = []
            elif len(suppression_buffer) > 0:
                operation_chunks.append(create_chunk(suppression_buffer, SUPPRESSION))
                suppression_buffer = []

            index += 1

    return operation_chunks

BLACK_LIST = ["Selected", "FloatEvent", "CurrentTime", "SavedPlayingSlot", "AnchorTime", "OtherTime", "CurrentZoom", "ScrollerPos", "ClientSize", "ChooserBar", "Highlighted", "NextColorIndex", "UserName"]

def whitelisted(chunk):
    tag = chunk["xml"].tag
    for one in BLACK_LIST:
        if tag.find(one) != -1:
            return False
    return True

def filter_blacklisted(chunks):
    return filter(whitelisted, chunks)

def print_chunk_tags(chunks):
    for chunk in chunks:
        if chunk["xml"] is not None:
            print chunk["xml"].tag

def git_analysis(repository_name, commita, commitb):
    repo = Repository(repository_name)
    d = repo.diff(commita, commitb)

    patches = [p for p in d]

    if len(patches) == 0:
        print "No modification applied"
        exit(-1)

    chunks = bind_objects(patches)
    chunks = eval_operations(chunks)
    chunks = filter_blacklisted(chunks)
    chunks = label_modifications(chunks)

    if len(chunks) == 0:
        print "No modification applied"
        exit(-1)

#    print_chunk_tags(chunks)
    
    return chunks

#FIXME : DEBUG
CURRENT_HEAD = Oid(hex='385898f83750ac84f6e2989c42752f1a4e8927c5')
#def checkout_commit_state(repository, commita, commitb):
#    stashed = False
#    try:
#        repository.stash(repository.default_signature)
#        stashed = True
#    except Exception as e:
#        print "Nothing to stash"
##        print e
#
#    commitaref = repository.revparse_single(commita)
#
#    if commitb is not None:
#        commitbref = repository.revparse_single(commitb)
#
#        if max(commitaref.author.time, commitbref.author.time)\
#            == commitaref.author.time:
##            repository.head.set_target(Oid(hex=commitaref.hex))
#            pass
#        else:
#            pass
##            repository.head.set_target(Oid(hex=commitbref.hex))
##            repository.checkout_tree(commitbref)
##            from subprocess import call
##           repository.head.set_target(CURRENT_HEAD)
#    else:
#        pass
##        repository.checkout(commitaref)
#
#    return stashed

# FIXME : reimplement without using git-python
from git import Repo

def stash(repository):
    git = Repo(repository.path).git

    stashed = False
    try:
        git.stash()
        stashed = True
        print "Modifications stashed"
    except Exception as e:
        print "Nothing to stash"

    return stashed

def checkout_commit_state(repository, commita, commitb):
    git = Repo(repository.path).git

    # FIXME : swap commita and commitb by date
    #         it should make more sense

    commitaref = repository.revparse_single(commita)

    if commitb is not None:
        commitbref = repository.revparse_single(commitb)
        if max(commitaref.author.time, commitbref.author.time)\
            == commitaref.author.time:
            git.checkout(commita)
        else:
            git.checkout(commitb)
    else:
        git.checkout(commita)

#def restore_state(repository, stashed, previous_head):
#    if stashed == True:
#        repository.stash_pop()
#
#    if repository.head.target != previous_head:
#        repository.head.set_target(previous_head)
 

def restore_state(repository, stashed, previous_head):
    git = Repo(repository.path).git
        
    if repository.head.name != previous_head:
        # print "WORKED : %s" % previous_head.split('/')[-1]
        git.checkout(previous_head.split('/')[-1])
    
    if stashed == True:
        repository.stash_pop()


def get_repository(repository_name):
    return Repository(repository_name)

GIT_STATUS_WT_MODIFIED = 256
GIT_STATUS_INDEX_MODIFIED = 2

def repository_clean(repository):
    status = repository.status()
    for filepath, flags in status.items():
        if flags & GIT_STATUS_WT_MODIFIED\
            or flags & GIT_STATUS_INDEX_MODIFIED:
            return False
    return True
