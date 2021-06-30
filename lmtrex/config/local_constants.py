"""Local configuration values for lmtrex

Note:
    This is a temporary file for testing that is deleted on build.  The RPM build will
    create this file from local_constants.py.in with roll-specific values. 
"""

# Filled on RPM build
APP_PATH = '/opt/lifemapper'
SCRATCH_PATH = '/state/partition1/lmscratch'

# Filled post-install
FQDN = 'notyeti-192.lifemapper.org'