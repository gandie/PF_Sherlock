# map logfileparsers against paths
logfile_map = {
    ('postgresql', './tests/file_assets/postgresql/postgresql-9.5-main.log'),
    ('apache2-access', './tests/file_assets/apache2/access.log'),
    ('apache2-error', './tests/file_assets/apache2/error.log'),
}

# map shellparsers against commands
# ATTENTION! shell=True is set, so think before firing your commands!
shellcmd_map = {
    ('journal', 'journalctl -o short-iso --no-pager'),
    #('journal', 'dmesg --time-format iso -P'),
}

'''
shellcmd_map = set()

for num in range(2, 32):
    shellcmd_map.add(
        ('apache2-error', 'zcat /apache2/error.log.%s.gz' % num)
    )
    shellcmd_map.add(
        ('apache2-access', 'zcat /apache2/access.log.%s.gz' % num)
    )
    if num <= 5:
        shellcmd_map.add(
            ('postgresql', 'zcat /postgresql-10-main.log.%s.gz' % num)
        )
'''

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
