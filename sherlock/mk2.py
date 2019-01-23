def readLogfile(path):
    logfile = open(path, 'r', encoding='utf-8')
    while True:
        line = logfile.readline()
        if line:
            yield line
        else:
            logfile.close()
            break


def runProcess(exe):
    p = subprocess.Popen(
        exe,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    while True:
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline().decode('utf-8')
        '''
        plugin parser here! yielded item must be a dict
        '''
        yield line
        if retcode is not None and not line:
            break
