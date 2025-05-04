#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .paramiko_supplement import paramiko_agent_agentkey_get_openssh_pubkey, paramiko_agent_agentkey_dump, paramiko_agent_agentkey_get_type, paramiko_agent_agent_ssh_add_key,paramiko_agent_agent_fetch_agent_keylist
from .sshkeyinfo    import SSHKeyInfo
from .sshkeyutil    import SSHKeyUtil
from .sshkeyring    import SSHKeyRing


__copyright__    = 'Copyright (c) 2025, Nanigashi Uji'
__version__      = '0.0.5'
__license__      = 'BSD-3-Clause'
__author__       = 'Nanigashi Uji'
__author_email__ = '53845049+nanigashi-uji@users.noreply.github.com'
__url__          = 'https://github.com/nanigashi-uji/sshkeyring.git'

__all__ = [ paramiko_agent_agentkey_get_openssh_pubkey,
            paramiko_agent_agentkey_dump,
            paramiko_agent_agentkey_get_type,
            paramiko_agent_agent_ssh_add_key,
            paramiko_agent_agent_fetch_agent_keylist,
            SSHKeyInfo,
            SSHKeyUtil,
            SSHKeyRing ]
