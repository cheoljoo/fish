import psutil  # https://pypi.org/project/psutil/
import os
import sys

def get_parent_process(limit=10):
    '''Walk up the process tree until we find a process we like.
    Arguments:
        ok_names: Return the first one of these processes that we find
    '''

    depth = 0
    this_proc = psutil.Process(os.getpid())
    print(this_proc.name())
    allPath = this_proc.name() + ' ' + ' '.join(sys.argv)
    next_proc = parent = psutil.Process(this_proc.ppid())
    print(parent.name())
    while depth < limit:
        print(next_proc.pid)
        allPath = str(next_proc.name()) + ':' + allPath
        if int(next_proc.pid) < 2:
            return allPath

        next_proc = psutil.Process(next_proc.ppid())
        depth += 1

    return allPath


if __name__ == '__main__':
    print('name:',get_parent_process())
    print('memory:',psutil.virtual_memory())
    print('disk:',psutil.disk_usage('/home'))
    print('users:',psutil.users())
    print('boot_time:',psutil.boot_time())
    print('network:',psutil.net_if_addrs())
    p = psutil.Process(os.getpid())
    print('cwd:',p.cwd())
    print('cmdline:',p.cmdline())
    print('username:',p.username())
