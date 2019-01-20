# map logfileparsers against paths
logfile_map = {
    'postgresql': './tests/file_assets/postgresql/postgresql-9.5-main.log',
    'apache2-access': './tests/file_assets/apache2/access.log',
    'apache2-error': './tests/file_assets/apache2/error.log',
}

# map shellparsers against commands
# ATTENTION! shell=True is set, so think before firing your commands!
shellcmd_map = {
    'journal': 'journalctl -o short-iso --no-pager',
}

# filter may also be passed as arguments from pf_sherlock
'''
# each line must contain 'kernel' and is less than 24 hours old
filter_map = {
    'kw': 'kernel',  # keyword=kernel
    'lh': 24         # lasthours=24
}
'''

# display keyword
display = 'table'
