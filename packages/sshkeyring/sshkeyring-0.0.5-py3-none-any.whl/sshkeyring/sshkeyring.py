#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import copy
#import .paramiko_supplement
from .sshkeyinfo import SSHKeyInfo
from .sshkeyutil import SSHKeyUtil

class SSHKeyRing(SSHKeyUtil):
    """
    Utility for storing the information of the avaiable SSH Keys 
    """
    def __init__(self,
                 key_id_use                        :  str = None,
                 key_type_use                      :  str = None,
                 key_type_default                  :  str = None,
                 key_bits_default                  : dict = None,
                 dsa_key_bits_default              :  int = None,
                 ecdsa_key_bits_default            :  int = None,
                 ed25519_key_bits_default          :  int = None,
                 rsa_key_bits_default              :  int = None,
                 keyfile_basename_default          :  str = None,
                 keyfile_ext_default               : dict = None,
                 private_keyfile_ext_default       :  str = None,
                 public_keyfile_ext_default        :  str = None,
                 keyfile_directory_default         : dict = None,
                 private_keyfile_directory_default :  str = None,
                 public_keyfile_directory_default  :  str = None,
                 keydir_prefix                     :  str = None,
                 seek_openssh_keydir_default       : bool = None,
                 passphrase                        :  str = None,
                 passphrase_alist                  : dict = None,
                 keyscan_excludes                  : list = None,
                 keyscan_excludes_add              : dict | list | tuple | str = None,
                 **kwds):
        super().__init__(**kwds)

        self.key_type_default = key_type_default if isinstance(key_type_default,str) else self.__class__.KEY_TYPE_DEFAULT
        self.key_bits_default = { kv : int(locals().get(kv+'_'+'key_bits_default',key_bits_default.get(kv,v)))
                                  for kv,v in self.__class__.KEY_BITS_DEFAULT.items()
                                 } if isinstance(key_bits_default, dict) else {
                                     kv : v if locals().get(kv+'_'+'key_bits_default') is None else int(locals().get(kv+'_'+'key_bits_default',v))
                                     for kv,v in self.__class__.KEY_BITS_DEFAULT.items() }

        self.keyfile_basename_default = keyfile_basename_default if isinstance(keyfile_basename_default,str) else self.__class__.KEYFILE_BASENAME_DEFAULT
        self.keyfile_ext_default = { kv : int(locals().get(kv+'_'+'keyfile_ext_default',keyfile_ext_default.get(kv,v)))
                                     for kv,v in self.__class__.KEYFILE_EXT_DEFAULT.items()
                                    } if isinstance(keyfile_ext_default, dict) else {
                                        kv : v if locals().get(kv+'_'+'keyfile_ext_default') is None else locals().get(kv+'_'+'keyfile_ext_default',v)
                                        for kv,v in self.__class__.KEYFILE_EXT_DEFAULT.items() }
        self.keyfile_directory_default = { kv : int(locals().get(kv+'_'+'keyfile_directory_default',keyfile_directory_default.get(kv,v)))
                                     for kv,v in self.__class__.KEYFILE_DIRECTORY_DEFAULT.items()
                                    } if isinstance(keyfile_directory_default, dict) else {
                                        kv : v if locals().get(kv+'_'+'keyfile_directory_default') is None else locals().get(kv+'_'+'keyfile_directory_default',v)
                                        for kv,v in self.__class__.KEYFILE_DIRECTORY_DEFAULT.items() }

        self.seek_openssh_keydir_default = seek_openssh_keydir_default if isinstance(seek_openssh_keydir_default,bool) else self.__class__.SEEK_OPENSSH_KEYDIR_DEFAULT

        self.passphrase       = passphrase
        self.passphrase_alist = copy.deepcopy(passphrase_alist) if isinstance(passphrase_alist, dict) else {}

        self.keyscan_excludes = copy.deepcopy(keyscan_excludes) if isinstance(keyscan_excludes, list) else copy.deepcopy(self.__class__.KEYSCAN_EXCLUDES)

        if isinstance(keyscan_excludes_add, dict):
            self.keyscan_excludes.extend( [ v for k,v in keyscan_excludes_add.items() if v not in self.keyscan_excludes ] )
        elif isinstance(keyscan_excludes_add, (list, tuple)):
            self.keyscan_excludes.extend( [ v for v in keyscan_excludes_add if v not in self.keyscan_excludes ] )
        elif isinstance(keyscan_excludes_add, str) and keyscan_excludes_add and (keyscan_excludes_add not in self.keyscan_excludes) :
            self.keyscan_excludes.append(keyscan_excludes_add)

        self.keydir_prefix = keydir_prefix if isinstance(keydir_prefix,str) and keydir_prefix else ""


        self.key_id_use   = key_id_use if isinstance(key_id_use,str) and key_id_use else self.default_key_id()
        self.key_type_use = key_type_use if isinstance(key_type_use,str) and key_type_use else self.key_type_default

        self.key_stored     = {}
        self.ssh_agent_alist = {}
        
    def keydirectory_path(self,
                          keydir_prefix    : str = None,
                          privatekey_dir   : str = None,
                          publickey_dir    : str = None,
                          **kwds):
        return self.__class__.Keydirectory_Path(
            keydir_prefix  if keydir_prefix is not None else self.keydir_prefix,
            privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
            publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
            **kwds)

    def opessh_keydirectory_path(self, **kwds):
        return self.__class__.OpeSSH_Keydirectory_Path(**kwds)

    def keypair_filename(self,
                         key_type         : str = None,
                         keyfile_basename : str = None,
                         privatekey_ext   : str = None,
                         publickey_ext    : str = None,
                         **kwds):

        return self.__class__.KeyPair_Filename(
            key_type if isinstance(key_type, str) and key_type else self.key_type_default,
            keyfile_basename if isinstance(keyfile_basename, str) and keyfile_basename else self.keyfile_basename_default,
            privatekey_ext if isinstance(privatekey_ext, str) and privatekey_ext else self.keyfile_ext_default['private'],
            publickey_ext  if isinstance(publickey_ext, str)  and publickey_ext  else self.keyfile_ext_default['public'],
            **kwds)

    def openssh_keypair_filename(cls, key_type : str = None, **kwds):
        return self.__class__.Openssh_KeyPair_Filename(key_type=key_type, **kwds)

    def keypair_path(self,
                     key_type         : str = None,
                     keydir_prefix    : str = None,
                     privatekey_dir   : str = None,
                     publickey_dir    : str = None,
                     keyfile_basename : str = None,
                     privatekey_ext   : str = None,
                     publickey_ext    : str = None,
                     **kwds):
        return self.__class__.KeyPair_Path(
            key_type if isinstance(key_type, str) and key_type else self.key_type_default,
            keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
            privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
            publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
            keyfile_basename if isinstance(keyfile_basename, str) and keyfile_basename else self.keyfile_basename_default,
            privatekey_ext if isinstance(privatekey_ext, str) and privatekey_ext else self.keyfile_ext_default['private'],
            publickey_ext  if isinstance(publickey_ext, str)  and publickey_ext  else self.keyfile_ext_default['public'],
            **kwds)

    def openssh_keypair_path(self, key_type : str = None, **kwds):
        self.__class__.Openssh_KeyPair_Path(key_type=key_type, **kwds)

    def default_key_id(self, key_comment:str=None, key_type:str=None) -> str :
        #return self.__class__.Default_Key_Id(key_comment=key_comment,
        #                                     key_type=(self.key_type_default if key_type is None else key_type))
        return self.__class__.Default_Key_Id(key_comment=key_comment, key_type=None)
    def gen_key_obj(self,
                    key_type            : str = None,
                    key_bits            : int = 0,
                    ecdsa_ec_type       : str = "secp256r1",
                    rsa_public_exponent : int = 65537,
                    **kwds):

        ktyp  = self.key_type_default.lower() if key_type is None else ( key_type.lower() if isinstance(key_type, "str") else "" )
        kbits = key_bits if key_bits>0 else self.key_bits_default.get(ktyp, 0)
        return self.__class__.Gen_Key_Obj(key_type=ktyp, key_bits=kbits,
                                          ecdsa_ec_type=ecdsa_ec_type, rsa_public_exponent=rsa_public_exponent, **kwds)

    def encode_key_contents(self,
                            key_info = None,
                            private_key_object = None,
                            public_key_object = None,
                            passphrase  : str = None,
                            key_comment : str = None,
                            min_passphrase_length :int = 8, **kwds):

        sshkey_info = key_info if isinstance(key_info, SSHKeyInfo) else SSHKeyInfo()

        ky_cmnt = self.__class__.Default_Key_Id(key_comment=key_comment if isinstance(key_comment,str) and key_comment else sshkey_info.key_id,
                                                key_type=self.get_key_type(private_key_object))
        if sshkey_info.key_id is None:
            sshkey_info.key_id = ky_cmnt
        
        return self.__class__.Encode_Key_Contents(key_info=sshkey_info,
                                                  private_key_object=private_key_object,
                                                  public_key_object=public_key_object,
                                                  passphrase=passphrase,
                                                  key_comment=key_comment,
                                                  min_passphrase_length=min_passphrase_length, **kwds)

    def save_keypair(self,
                     private_key_contents : bytes = None,
                     public_key_contents  : bytes = None,
                     key_type             : str = None,
                     keydir_prefix    : str = None,
                     privatekey_dir   : str = None,
                     publickey_dir    : str = None,
                     keyfile_basename : str = None,
                     privatekey_ext   : str = None,
                     publickey_ext    : str = None,
                     force_overwrite   : bool = False,
                     **kwds):

        return self.__class__.Save_KeyPair(private_key_contents=private_key_contents,
                                           public_key_contents=public_key_contents,
                                           key_type=key_type if isinstance(key_type, str) and key_type else self.key_type_default,
                                           keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                           privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                           publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                           keyfile_basename=keyfile_basename if isinstance(keyfile_basename, str) and keyfile_basename else self.keyfile_basename_default,
                                           privatekey_ext=privatekey_ext if isinstance(privatekey_ext, str) and privatekey_ext else self.keyfile_ext_default['private'],
                                           publickey_ext=publickey_ext  if isinstance(publickey_ext, str)  and publickey_ext  else self.keyfile_ext_default['public'],
                                           force_overwrite=force_overwrite,
                                           **kwds)

    def generate_sshkey(self, key_type      : str  = None,
                        key_bits            : int  = 0,
                        passphrase          : str  = None,
                        key_comment         : str  = None,
                        keydir_prefix       : str  = None,
                        privatekey_dir      : str  = None,
                        publickey_dir       : str  = None,
                        keyfile_basename    : str  = None,
                        privatekey_ext      : str  = None,
                        publickey_ext       : str  = None,
                        force_overwrite     : bool = False,
                        use_ssh_agent       : bool = False,
                        invoke_agent        : bool = False,
                        restore_environ     : bool = False,
                        ecdsa_ec_type       : str  = "secp256r1",
                        rsa_public_exponent : int  = 65537,
                        min_passphrase_length :int = 8,
                        **kwds):

        ktyp   = key_type if isinstance(key_type, str) and key_type else self.key_type_default
        key_id = self.default_key_id(key_comment=key_comment, key_type=ktyp)
        pssphrs = ( passphrase
                    if isinstance(passphrase,str) and len(passphrase)>=min_passphrase_length
                    else self.passphrase_alist.get(key_id, self.passphrase) )

        kf_basename=keyfile_basename if isinstance(keyfile_basename,str) and keyfile_basename else ("%s_%s" % (key_id, ktyp))

        kyinfo = self.__class__.Generate_SSHKey(key_type=ktyp,
                                                key_bits=key_bits if ( isinstance(key_bits,int) and key_bits > 0 ) else self.key_bits_default.get(ktyp, 0),
                                                passphrase=pssphrs,
                                                key_comment=key_id,
                                                keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                                privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                                publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                                keyfile_basename=kf_basename,
                                                privatekey_ext=privatekey_ext if isinstance(privatekey_ext, str) and privatekey_ext else self.keyfile_ext_default['private'],
                                                publickey_ext=publickey_ext  if isinstance(publickey_ext, str)  and publickey_ext  else self.keyfile_ext_default['public'],
                                                force_overwrite=force_overwrite,
                                                ecdsa_ec_type=ecdsa_ec_type,
                                                rsa_public_exponent=rsa_public_exponent,
                                                min_passphrase_length=min_passphrase_length,
                                                **kwds)

        self.key_stored.update({ (key_id, ktyp) : kyinfo})

        if use_ssh_agent:

            for agent_keyinfo in self.__class__.List_KeyInfo_SSHAgent(agent_list=self.ssh_agent_alist,
                                                                      invoke_agent=invoke_agent,
                                                                      restore_environ=restore_environ, **kwds):
                if self.key_stored.get((agent_keyinfo.key_id, agent_keyinfo.key_type)) is None:
                    self.key_stored.update({(agent_keyinfo.key_id, agent_keyinfo.key_type): agent_keyinfo })
                else:
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_key    = agent_keyinfo.agent_key
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_sock   = agent_keyinfo.agent_sock
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_client = agent_keyinfo.agent_client



        return kyinfo

    def prepare_new_sshkey(self,key_id           : str = None,
                           key_type              : str = None,
                           key_bits              : int = 0,
                           passphrase            : str = None,
                           keydir_prefix         : str = None,
                           privatekey_dir        : str = None,
                           publickey_dir         : str = None,
                           keyfile_basename      : str = None,
                           privatekey_ext        : str = None,
                           publickey_ext         : str = None,
                           force_overwrite       : bool = False,
                           ecdsa_ec_type         : str = "secp256r1",
                           rsa_public_exponent   : int = 65537,
                           min_passphrase_length : int = 8,
                           **kwds):
        
        idx_use = (key_id, key_type)

        if self.key_stored.get(idx_use) is None:
            new_keyinfo = self.generate_sshkey(key_type=key_type,
                                               key_bits=key_bits,
                                               passphrase=passphrase,
                                               key_comment=key_id,
                                               keydir_prefix=keydir_prefix,
                                               privatekey_dir=privatekey_dir,
                                               publickey_dir=publickey_dir,
                                               keyfile_basename=keyfile_basename,
                                               privatekey_ext=privatekey_ext,
                                               publickey_ext=publickey_ext,
                                               force_overwrite=force_overwrite,
                                               ecdsa_ec_type=ecdsa_ec_type,
                                               rsa_public_exponent=rsa_public_exponent,
                                               min_passphrase_length=min_passphrase_length, **kwds)
            self.key_stored.update({idx_use : new_keyinfo})
        return self.key_stored.get(idx_use)

    def ssh_add_keyinfo(self, keyinfo : SSHKeyInfo, **kwds):
        flg_verbose = kwds.get('verbose', False)
        flg_add_ok = False
        if len(self.ssh_agent_alist)<=0:
            if flg_verbose:
                sys.stderr.write("[%s.%s:%d] Error : No ssh-agent is running.)\n"
                                 % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno))
        else:
            for agent_sock, agent_client in self.ssh_agent_alist.items():
                try:
                    flg_add_ok = keyinfo.add_to_agent(agent_sock, agent_client, **kwds)
                    if flg_add_ok:
                        sys.stderr.write("[%s.%s:%d] Info ssh-add : ssh-agent ( key id: %s, type: %s, sock :  %s)\n"
                                         % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                            keyinfo.key_id, keyinfo.key_type,  agent_sock))
                        break
                except Exception as ex:
                    if kwds.get('verbose', False):
                        sys.stderr.write("[%s.%s:%d] Error : Failed to add key to ssh-agent ( key id: %s, type: %s, sock :  %s) : %s\n"
                                         % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                            keyinfo.key_id, keyinfo.key_type,  agent_sock, str(ex)))
                        
                    continue
            if ( not flg_add_ok ) and kwds.get('verbose', False):
                sys.stderr.write("[%s.%s:%d] Error : Failed to add key to ssh-agent ( key id: %s, type: %s, sock :  %s)\n"
                                 % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    keyinfo.key_id, keyinfo.key_type,  agent_sock))
        return flg_add_ok

    def setup_new_sshkey(self,
                         key_id                : str = None,
                         key_type              : str  = None,
                         key_bits              : int  = 0,
                         passphrase            : str  = None,
                         register_agent        : bool = False,
                         keydir_prefix         : str  = None,
                         privatekey_dir        : str  = None,
                         publickey_dir         : str  = None,
                         keyfile_basename      : str  = None,
                         privatekey_ext        : str  = None,
                         publickey_ext         : str  = None,
                         force_overwrite       : bool = False,
                         ecdsa_ec_type         : str  = "secp256r1",
                         rsa_public_exponent   : int  = 65537,
                         min_passphrase_length : int  = 8, **kwds):

        new_keyinfo = self.prepare_new_sshkey(key_id=key_id,
                                              key_type=key_type,
                                              key_bits=key_bits,
                                              passphrase=passphrase,
                                              keydir_prefix=keydir_prefix,
                                              privatekey_dir=privatekey_dir,
                                              publickey_dir=publickey_dir,
                                              keyfile_basename=keyfile_basename,
                                              privatekey_ext=privatekey_ext,
                                              publickey_ext=publickey_ext,
                                              force_overwrite=force_overwrite,
                                              ecdsa_ec_type=ecdsa_ec_type,
                                              rsa_public_exponent=rsa_public_exponent,
                                              min_passphrase_length=min_passphrase_length, **kwds)
        sshadd_ok = False
        if isinstance(new_keyinfo, SSHKeyInfo) and register_agent:
            sshadd_ok = self.ssh_add_keyinfo(new_keyinfo, **kwds)
        return (new_keyinfo, sshadd_ok)
    
    def openssh_list_keyfile_pairs(self, exclude_pattern:list =None, **kwds):
        self.__class__.Openssh_List_Keyfile_Pairs(exclude_pattern=exclude_pattern, **kwds)

    def list_keyfile_pairs(self,
                           seek_openssh_dir : bool = False,
                           keydir_prefix    : str  = None,
                           privatekey_dir   : str  = None,
                           publickey_dir    : str  = None,
                           exclude_pattern  : list = None,
                           **kwds):

        return self.__class__.List_Keyfile_Pairs(seek_openssh_dir=seek_openssh_dir,
                                                 keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                                 privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                                 publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                                 exclude_pattern=exclude_pattern if isinstance(exclude_pattern, list) else self.keyscan_excludes, **kwds)

    def list_key_pairs(self,
                       seek_openssh_dir   : bool = False,
                       decode_private_key : bool = False,
                       passphrase         : str  = None,
                       passphrase_alist   : dict = None,
                       keydir_prefix      : str  = None,
                       privatekey_dir     : str  = None,
                       publickey_dir      : str  = None,
                       exclude_pattern    : list = None,
                       **kwds):
        return self.__class__.List_Key_Pairs(seek_openssh_dir=seek_openssh_dir,
                                             decode_private_key=decode_private_key,
                                             passphrase=passphrase if passphrase is not None else self.passphrase,
                                             passphrase_alist=passphrase_alist if isinstance(passphrase_alist,dict) else self.passphrase_alist,
                                             keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                             privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                             publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                             exclude_pattern=exclude_pattern if isinstance(exclude_pattern, list) else self.keyscan_excludes, **kwds)


    def refresh_key_pairs(self,
                          seek_openssh_dir   : bool = False,
                          decode_private_key : bool = False,
                          passphrase         : str  = None,
                          passphrase_alist   : dict = None,
                          keydir_prefix      : str  = None,
                          privatekey_dir     : str  = None,
                          publickey_dir      : str  = None,
                          exclude_pattern    : list = None,
                          **kwds):

        return self.__class__.Refresh_Key_Pairs(key_stored=self.key_stored,
                                                seek_openssh_dir=seek_openssh_dir,
                                                decode_private_key=decode_private_key,
                                                passphrase=passphrase if passphrase is not None else self.passphrase,
                                                passphrase_alist=passphrase_alist if isinstance(passphrase_alist,dict) else self.passphrase_alist,
                                                keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                                privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                                publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                                exclude_pattern=exclude_pattern if isinstance(exclude_pattern, list) else self.keyscan_excludes, **kwds)

    def refresh_sshagent_alist(self,
                               invoke_agent    : bool =False,
                               restore_environ : bool = False, 
                               force_reconnect : bool = False, **kwds):
        return self.__class__.Refresh_SSHAgent_Alist(sshagent_alist=self.ssh_agent_alist,
                                                     invoke_agent=invoke_agent,
                                                     restore_environ=restore_environ,
                                                     force_reconnect=force_reconnect, **kwds)


    def refresh_keyinfo_sshagent(self,
                                 invoke_agent    : bool  = False,
                                 restore_environ : bool  = False, 
                                 force_reconnect : bool = False, **kwds):
        return self.__class__.Refresh_KeyInfo_SSHAgent(key_stored=self.key_stored,
                                                       sshagent_alist=self.ssh_agent_alist,
                                                       invoke_agent=invoke_agent,
                                                       restore_environ=restore_environ,
                                                       force_reconnect=force_reconnect, **kwds)

    def setup_keyinfo(self,
                      key_id_use            : str  = None,
                      key_type_use          : str  = None,
                      use_ssh_agent          : bool = True,
                      seek_openssh_dir      : bool = False,
                      decode_private_key    : bool = False,
                      passphrase            : str  = None,
                      passphrase_alist      : dict = None,
                      keydir_prefix         : str  = None,
                      privatekey_dir        : str  = None,
                      publickey_dir         : str  = None,
                      exclude_pattern       : list = None,
                      invoke_agent          : bool = False,
                      restore_environ       : bool = False,
                      generate_key          : bool = False,
                      register_agent        : bool = False,
                      register_agent_all    : bool = False,
                      key_bits              : int  = 0,
                      keyfile_basename      : str  = None,
                      privatekey_ext        : str  = None,
                      publickey_ext         : str  = None,
                      force_overwrite       : bool = False,
                      ecdsa_ec_type         : str  = "secp256r1",
                      rsa_public_exponent   : int  = 65537,
                      min_passphrase_length : int  = 8,
                      **kwds):
        
        use_key_id   = key_id_use   if isinstance(key_id_use,str)   and key_id_use   else self.key_id_use
        use_key_type = key_type_use if isinstance(key_type_use,str) and key_type_use else self.key_type_use

        self.key_stored.update({ (sskkey_info.key_id, sskkey_info.key_type) : sskkey_info
                                 for sskkey_info in self.list_key_pairs(seek_openssh_dir=seek_openssh_dir,
                                                                        decode_private_key=decode_private_key,
                                                                        passphrase=passphrase,
                                                                        passphrase_alist=passphrase_alist,
                                                                        keydir_prefix=keydir_prefix,
                                                                        privatekey_dir=privatekey_dir,
                                                                        publickey_dir=publickey_dir,
                                                                        exclude_pattern=exclude_pattern, **kwds)})

        self.ssh_agent_alist = { sock : client for sock, client in self.__class__.List_SSHAgent(invoke_agent=invoke_agent,
                                                                                               restore_environ=restore_environ, **kwds)}
        
        if use_ssh_agent:
            for agent_keyinfo in self.__class__.List_KeyInfo_SSHAgent(agent_list=self.ssh_agent_alist,
                                                                      invoke_agent=invoke_agent,
                                                                      restore_environ=restore_environ, **kwds):
                if self.key_stored.get((agent_keyinfo.key_id, agent_keyinfo.key_type)) is None:
                    self.key_stored.update({(agent_keyinfo.key_id, agent_keyinfo.key_type): agent_keyinfo })
                else:
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_key    = agent_keyinfo.agent_key
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_sock   = agent_keyinfo.agent_sock
                    self.key_stored[(agent_keyinfo.key_id, agent_keyinfo.key_type)].agent_client = agent_keyinfo.agent_client
                    
        idx_use = (use_key_id,use_key_type)
        if self.key_stored.get(idx_use) is None and generate_key:
            new_keyinfo, ssh_add_status = self.setup_new_sshkey(key_id=use_key_id,
                                                                key_type=use_key_type,
                                                                key_bits=key_bits,
                                                                passphrase=passphrase,
                                                                register_agent=(use_ssh_agent and register_agent),
                                                                keydir_prefix=keydir_prefix,
                                                                privatekey_dir=privatekey_dir,
                                                                publickey_dir=publickey_dir,
                                                                keyfile_basename=keyfile_basename,
                                                                privatekey_ext=privatekey_ext,
                                                                publickey_ext=publickey_ext,
                                                                force_overwrite=force_overwrite,
                                                                ecdsa_ec_type=ecdsa_ec_type,
                                                                rsa_public_exponent=rsa_public_exponent,
                                                                min_passphrase_length=min_passphrase_length, **kwds)

        if use_ssh_agent and register_agent and len(self.ssh_agent_alist)>0:
            for kidx,ky_info in self.key_stored.items():
                c_key_id, c_key_type = kidx
                if (not register_agent_all) and (c_key_id!=use_key_id or c_key_type!=use_key_type):
                    continue
                if ky_info.agent_key is not None:
                    continue
                flg_add_ok = False
                for agent_sock, agent_client in self.ssh_agent_alist.items():
                    try:
                        flg_add_ok = new_keyinfo.add_to_agent(agent_sock, agent_client, **kwds)
                        if flg_add_ok:
                            break
                    except:
                        continue
                if ( not flg_add_ok ) and kwds.get('verbose', False):
                    sys.stderr.write("[%s.%s:%d] Error : Failed to add key to ssh-agent ( key id: %s, type: %s, sock :  %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        c_key_id, c_key_type,  agent_sock))


    def refresh_keyinfo(self,
                        use_local_key      : bool = True,
                        use_ssg_agent      : bool = False,
                        seek_openssh_dir   : bool = False,
                        decode_private_key : bool = False,
                        passphrase         : str  = None,
                        passphrase_alist   : dict = None,
                        keydir_prefix      : str  = None,
                        privatekey_dir     : str  = None,
                        publickey_dir      : str  = None,
                        exclude_pattern    : list = None,
                        invoke_agent       : bool = False,
                        restore_environ    : bool = False,
                        force_reconnect    : bool = False, **kwds):

        p = self.__class__.Refresh_KeyInfo(key_stored=self.key_stored,
                                           sshagent_alist=self.ssh_agent_alist,
                                           use_local_key=use_local_key,
                                           use_ssg_agent=use_ssg_agent,
                                           seek_openssh_dir=seek_openssh_dir,
                                           decode_private_key=decode_private_key,
                                           passphrase=passphrase if passphrase is not None else self.passphrase,
                                           passphrase_alist=passphrase_alist if isinstance(passphrase_alist,dict) else self.passphrase_alist,
                                           keydir_prefix=keydir_prefix if keydir_prefix is not None else self.keydir_prefix,
                                           privatekey_dir=privatekey_dir if isinstance(privatekey_dir, str) and privatekey_dir else self.keyfile_directory_default['private'],
                                           publickey_dir=publickey_dir  if isinstance(publickey_dir,  str) and publickey_dir  else self.keyfile_directory_default['public'],
                                           exclude_pattern=exclude_pattern if isinstance(exclude_pattern, list) else self.keyscan_excludes,
                                           invoke_agent=invoke_agent,
                                           restore_environ=restore_environ,
                                           force_reconnect=force_reconnect, **kwds)
        
        return p

    def dump(self, **kwds):
        for k,key_info in self.key_stored.items():
            key_id, key_type = k
            print("(%s:%s) : %s" % (key_id, key_type, key_info))

    def dump_agent_keys(self, key_name=None, key_type=None,
                        show_publickey:bool=False, stream=sys.stdout):
        for k,key_info in self.key_stored.items():
            k_id, k_type = k
            if isinstance(key_name, str) and key_name and (k_id!=key_name):
                continue
            if isinstance(key_type, str) and key_type and (k_type!=key_type):
                continue
            if key_info.agent_key is not None:
                key_info.agent_key.dump(show_publickey=show_publickey, stream=sys.stdout)

    def pickup_keyinfo(self, key_id : str = None, key_type : str = None, **kwds):
        kyid = key_id if isinstance(key_id,str) and key_id else self.key_id_use
        ktyp = key_type if isinstance(key_type,str) and key_type else self.key_type_use
        return self.key_stored.get( (kyid, ktyp) )

if __name__ == '__main__':

    def main():
        import pkgstruct
        pkg_info=pkgstruct.PkgStruct(script_path=sys.argv[0])
        # #pkg_keydir_prefix=pkg_info.concat_path('home', '.ssh')
        pkg_keydir_prefix=pkg_info.concat_path('pkg_statedatadir', 'pki')
    
        # print(pkg_keydir_prefix)
    
        import argparse
    
        class DictUpdater(argparse.Action):
            def __init__(self, option_strings, dest, nargs=None, **kwargs):
                self.separator = kwargs.pop('separater', ':')
                self.buf_alist = {}
                super().__init__(option_strings, dest, **kwargs)
    
            def chk_value(self, parser, namespace, values, option_string=None):
                if isinstance(values, (list, tuple)):
                    for v in values:
                        self.chk_value(parser, namespace, v, option_string)
                elif isinstance(values, str):
                    kid,sep,p = values.partition(self.separator)
                    k = SSHKeyUtil.Default_Key_Id(key_comment=namespace.key_id,
                                                  key_type=namespace.key_type) if sep=="" else kid
                    v = kid if sep=="" else p
                    self.buf_alist.update({k: v})
    
            def __call__(self, parser, namespace, values, option_string=None):
                self.chk_value(parser, namespace, values, option_string)
                setattr(namespace, self.dest, self.buf_alist)
    
        argpsr = argparse.ArgumentParser(description='SSH key utilities')
    
        argpsr.add_argument('-H', '--class-help', action='store_true', help='Show help for SSHKey**** classes')
        argpsr.add_argument('-v', '--verbose', action='store_true', help='Show verbose messages')
    
        argpsr.add_argument('-t', '--key-type', choices=SSHKeyUtil.KEY_TYPES, default=None, help='Specify Key Type')
        argpsr.add_argument('-T', '--key-type-default', choices=SSHKeyUtil.KEY_TYPES, default=None, help='Specify Key Type default')
        argpsr.add_argument('-b', '--key-bits', type=int, default=None, help='Specity Key length')
        argpsr.add_argument('-i', '--key-id',   default=None, help=('Specify key id: Default is %s' % ( SSHKeyUtil.Default_Key_Id(),) ))
        argpsr.add_argument('-B', '--keyfile-basename', default=None, help='Key file basename')
        argpsr.add_argument('-P', '--keydir-prefix', default=pkg_keydir_prefix, help='Prefix of directory to store Key files')
        argpsr.add_argument('-d', '--private-key-directory', default=None, help='Directory to store Key files')
        argpsr.add_argument('-D', '--public-key-directory', default=None, help='Directory to put public Key files')
        argpsr.add_argument('-e', '--private-key-extension', default=None, help='Extenstion of private Key files')
        argpsr.add_argument('-E', '--public-key-extension', default=None, help='Extenstion of public Key files')
        argpsr.add_argument('-U', '--use-openssh-keys', default=None, action='store_true', help=( 'Use openssh keys (in %s)' % (SSHKeyUtil.SEEK_OPENSSH_KEYDIR_DEFAULT,)))
    
        argpsr.add_argument('-p', '--passphrase', type=str, default=None, help='SSH key passphrase (common)')
        argpsr.add_argument('-A', '--passphrase-alist', action=DictUpdater, help='SSH key alist passphrase (keyid:passphrase)')
        argpsr.add_argument('-x', '--keyscan-exclude-list', action='append', default=None, help='Exclude Pattern list')
        argpsr.add_argument('-X', '--keyscan-exclude-add', action='append', default=[], help='Exclude Pattern list')
        argpsr.add_argument('-m', '--passphrase-length-min', type=int, default=8, help='Minimum length of key passphrase')
    
        argpsr.add_argument('-K', '--check-private', action='store_true', help='Decode private key')
        argpsr.add_argument('-N', '--disuse-ssh-agent', action='store_true', help='run without ssh-agent')
    
        argpsr.add_argument('-L', '--list-keyinfo', action='store_true', help='Show keyinfo list avaiable')
    
        argpsr.add_argument('-C', '--create-keys', action='store_true', help='Create Key Pairs if there is no key pair')
        argpsr.add_argument('-W', '--allow-keyfile-overwrite', action='store_true', help='Allow overwrite keyfile if already exists')
    
        argpsr.add_argument('-I', '--invoke-ssh-agent', action='store_true', help='invoke ssh-agent if no ssh-agent is running')
    
        argpsr.add_argument('-a', '--sign-algorithm', type=str, default="rsa-sha2-512", help='SSH key passphrase (common)')
    
        
        argpsr.add_argument('-l', '--list-fingerprint', action='store_true', help='Show list of fingerprint of the registered keys')
        argpsr.add_argument('-z', '--list-publickey',   action='store_true', help='Show list of public part of the registered keys')
    
        argpsr.add_argument('-V', '--verify-sign',      action='store_true', help='Verify with local key file')
    
        argpsr.add_argument('data', nargs='*', type=str, default=None,  help='Date to sign')
        opts = argpsr.parse_args()
    
        if opts.class_help:
            import pydoc,sys
            pydoc.help = pydoc.Helper(output=sys.stdout)
            help(SSHKeyInfo)
            help(SSHKeyUtil)
            help(SSHKeyRing)
            sys.exit()
    
        use_key_id   = opts.key_id   if isinstance(opts.key_id,   str) and opts.key_id   else SSHKeyRing.Default_Key_Id()
        use_key_type = opts.key_type if isinstance(opts.key_type, str) and opts.key_type else SSHKeyUtil.KEY_TYPE_DEFAULT
        
        sshkeyring = SSHKeyRing(key_id_use=use_key_id,
                                key_type_use=use_key_type,
                                key_type_default=opts.key_type_default,
                                key_bits_default=None,
                                dsa_key_bits_default    = opts.key_bits if isinstance(opts.key_bits,int) and opts.key_types == "dsa"     else None,
                                ecdsa_key_bits_default  = opts.key_bits if isinstance(opts.key_bits,int) and opts.key_types == "ecdsa"   else None,
                                ed25519_key_bits_default= opts.key_bits if isinstance(opts.key_bits,int) and opts.key_types == "ed25519" else None,
                                rsa_key_bits_default    = opts.key_bits if isinstance(opts.key_bits,int) and opts.key_types == "rsa"     else None,
                                keyfile_basename_default = opts.keyfile_basename,
                                keyfile_ext_default=None,
                                private_keyfile_ext_default       = None,
                                public_keyfile_ext_default        = None,
                                keyfile_directory_default         = None,
                                private_keyfile_directory_default = opts.private_key_directory,
                                public_keyfile_directory_default  = opts.public_key_directory,
                                keydir_prefix                     = opts.keydir_prefix,
                                seek_openssh_keydir_default       = opts.use_openssh_keys,
                                passphrase                        = opts.passphrase,
                                passphrase_alist                  = opts.passphrase_alist,
                                keyscan_excludes                  = opts.keyscan_exclude_list,
                                keyscan_excludes_add              = opts.keyscan_exclude_add)
    
        # sshkeyring.setup_keyinfo(key_id_use=use_key_id,
        #                          key_type_use=use_key_type,
        #                          use_ssh_agent=(not opts.disuse_ssh_agent),
        #                          seek_openssh_dir=opts.use_openssh_keys,
        #                          decode_private_key =opts.check_private,
        #                          generate_key=False,
        #                          passphrase=None,
        #                          passphrase_alist=None,
        #                          keydir_prefix=None,
        #                          privatekey_dir=None,
        #                          publickey_dir=None,
        #                          exclude_pattern=None,
        #                          invoke_agent=opts.invoke_ssh_agent,
        #                          restore_environ=False, 
        #                          verbose=opts.verbose)
    
        sshkeyring.refresh_keyinfo(use_local_key=True,
                                   use_ssg_agent=(not opts.disuse_ssh_agent),
                                   seek_openssh_dir=opts.use_openssh_keys,
                                   decode_private_key=False,
                                   passphrase= None,
                                   passphrase_alist=None,
                                   keydir_prefix=None,
                                   privatekey_dir=None,
                                   publickey_dir=None,
                                   exclude_pattern=None,
                                   invoke_agent=opts.invoke_ssh_agent,
                                   restore_environ=False,
                                   force_reconnect=False,
                                   verbose=opts.verbose)
    
        if opts.list_keyinfo:
            sshkeyring.dump()
            sys.exit()
    
        if opts.list_fingerprint:
            sshkeyring.dump_agent_keys(key_name=opts.key_id, show_publickey=False)
            sys.exit()
    
        if opts.list_publickey:
            sshkeyring.dump_agent_keys(key_name=opts.key_id, show_publickey=True)
            sys.exit()
    
        if opts.verbose:
            sys.stderr.write("[%s.%s:%d] Info :  Key ID in use : %s, Key Type in use : %s\n"
                             % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                sshkeyring.key_id_use, sshkeyring.key_type_use))
    
        picked_keyinfo = sshkeyring.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)
    
        if picked_keyinfo is None and opts.create_keys:
            new_keyinfo, ssh_add_status = sshkeyring.setup_new_sshkey(key_id=opts.key_id,
                                                                      key_type=opts.key_type,
                                                                      key_bits=opts.key_bits,
                                                                      passphrase=opts.passphrase,
                                                                      register_agent=(not opts.disuse_ssh_agent),
                                                                      keydir_prefix=None,
                                                                      privatekey_dir=None,
                                                                      publickey_dir=None,
                                                                      keyfile_basename=opts.keyfile_basename,
                                                                      privatekey_ext=None,
                                                                      publickey_ext=None,
                                                                      force_overwrite=opts.allow_keyfile_overwrite,
                                                                      ecdsa_ec_type="secp256r1",
                                                                      rsa_public_exponent=65537,
                                                                      min_passphrase_length=opts.passphrase_length_min,
                                                                      verbose=opts.verbose)
            picked_keyinfo = sshkeyring.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)
    
        if picked_keyinfo is None:
            sys.stderr.write("[%s.%s:%d] :  No key pair is found ( key id: %s, type: %s)\n"
                             % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                sshkeyring.key_id_use, sshkeyring.key_type_use))
            sys.exit()
    
        if not opts.disuse_ssh_agent:
            if picked_keyinfo.agent_key is None:
                picked_keyinfo.set_passphrase(passphrase=opts.passphrase, overwrite=False, min_passphrase_length=8, verbose=opts.verbose)
                picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)
                sshkeyring.ssh_add_keyinfo(picked_keyinfo, verbose=opts.verbose)
    
        if opts.verbose:
            sys.stderr.write("[%s.%s:%d] Info : Stored KeyInfo : %s\n"
                             % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno, str(picked_keyinfo)))
    
        for data_idx, raw_data in enumerate(opts.data):
            if opts.disuse_ssh_agent or opts.verify_sign:
                picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)
    
            bytes_signed = picked_keyinfo.sign_ssh_data(data=raw_data, algorithm=opts.sign_algorithm, use_local_key=opts.disuse_ssh_agent, verbose=opts.verbose)
    
            import base64
    
            b64data_signed = base64.b64encode(bytes_signed).decode('utf-8')
            if opts.verify_sign:
                flg_verified = picked_keyinfo.verify_ssh_sig_by_keyfile(data=raw_data, sig=bytes_signed, verbose=opts.verbose)
                verified_status_txt = "Verified" if flg_verified else "Invalid"
            else:
                flg_verified = None
                verified_status_txt = "Unverified"
    
            if data_idx==0:
                print("--------------------------------------------------")
            print("Raw Data  : %s" % (raw_data, ))
            print("Signature : %s" % (b64data_signed,))
            print("Status    : %s" % (verified_status_txt,))
            print("--------------------------------------------------")
    
        sys.exit()
    
    main()
