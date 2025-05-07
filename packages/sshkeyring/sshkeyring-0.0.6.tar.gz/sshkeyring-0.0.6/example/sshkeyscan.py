#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pydoc
import base64
import inspect

import argparse
import pkgstruct

import sshkeyring

def main():

    pkg_info=pkgstruct.PkgStruct(script_path=sys.argv[0])
    # #pkg_keydir_prefix=pkg_info.concat_path('home', '.ssh')
    pkg_keydir_prefix=pkg_info.concat_path('pkg_statedatadir', 'pki')

    # print(pkg_keydir_prefix)

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
                print(namespace)
                k = sshkeyring.SSHKeyUtil.Default_Key_Id(key_comment=namespace.key_id,
                                                         key_type=namespace.key_type) if sep=="" else kid
                v = kid if sep=="" else p
                self.buf_alist.update({k: v})

        def __call__(self, parser, namespace, values, option_string=None):
            self.chk_value(parser, namespace, values, option_string)
            setattr(namespace, self.dest, self.buf_alist)

    argpsr = argparse.ArgumentParser(description='SSH key utilities')

    argpsr.add_argument('-H', '--class-help', action='store_true', help='Show help for SSHKey**** classes')
    argpsr.add_argument('-v', '--verbose', action='store_true', help='Show verbose messages')

    argpsr.add_argument('-t', '--key-type', choices=sshkeyring.SSHKeyUtil.KEY_TYPES, default=None, help='Specify Key Type')
    argpsr.add_argument('-T', '--key-type-default', choices=sshkeyring.SSHKeyUtil.KEY_TYPES, default=None, help='Specify Key Type default')
    argpsr.add_argument('-b', '--key-bits', type=int, default=None, help='Specity Key length')
    argpsr.add_argument('-i', '--key-id',   default=None, help=('Specify key id: Default is %s' % ( sshkeyring.SSHKeyUtil.Default_Key_Id(),) ))
    argpsr.add_argument('-B', '--keyfile-basename', default=None, help='Key file basename')
    argpsr.add_argument('-P', '--keydir-prefix', default=pkg_keydir_prefix, help='Prefix of directory to store Key files')
    argpsr.add_argument('-d', '--private-key-directory', default=None, help='Directory to store Key files')
    argpsr.add_argument('-D', '--public-key-directory', default=None, help='Directory to put public Key files')
    argpsr.add_argument('-e', '--private-key-extension', default=None, help='Extenstion of private Key files')
    argpsr.add_argument('-E', '--public-key-extension', default=None, help='Extenstion of public Key files')
    argpsr.add_argument('-U', '--use-openssh-keys', default=None, action='store_true', help=( 'Use openssh keys (in %s)' % (sshkeyring.SSHKeyUtil.SEEK_OPENSSH_KEYDIR_DEFAULT,)))

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

        pydoc.help = pydoc.Helper(output=sys.stdout)
        help(sshkeyring.SSHKeyInfo)
        help(sshkeyring.SSHKeyUtil)
        help(sshkeyring.SSHKeyRing)
        sys.exit()

    use_key_id   = opts.key_id   if isinstance(opts.key_id,   str) and opts.key_id   else sshkeyring.SSHKeyRing.Default_Key_Id()
    use_key_type = opts.key_type if isinstance(opts.key_type, str) and opts.key_type else sshkeyring.SSHKeyUtil.KEY_TYPE_DEFAULT
    
    skyrng = sshkeyring.SSHKeyRing(key_id_use=use_key_id,
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
    
    # skyrng.setup_keyinfo(key_id_use=use_key_id,
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

    skyrng.refresh_keyinfo(use_local_key=True,
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
        skyrng.dump()
        sys.exit()

    if opts.list_fingerprint:
        skyrng.dump_agent_keys(key_name=opts.key_id, show_publickey=False)
        sys.exit()

    if opts.list_publickey:
        skyrng.dump_agent_keys(key_name=opts.key_id, show_publickey=True)
        sys.exit()

    if opts.verbose:
        sys.stderr.write("[%s.%s:%d] Info :  Key ID in use : %s, Key Type in use : %s\n"
                         % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                            skyrng.key_id_use, skyrng.key_type_use))

    picked_keyinfo = skyrng.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)

    if picked_keyinfo is None and opts.create_keys:
        new_keyinfo, ssh_add_status = skyrng.setup_new_sshkey(key_id=opts.key_id,
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
        picked_keyinfo = skyrng.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)

    if picked_keyinfo is None:
        sys.stderr.write("[%s.%s:%d] :  No key pair is found ( key id: %s, type: %s)\n"
                         % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                            skyrng.key_id_use, skyrng.key_type_use))
        sys.exit()

    if not opts.disuse_ssh_agent:
        if picked_keyinfo.agent_key is None:
            picked_keyinfo.set_passphrase(passphrase=opts.passphrase, overwrite=False, min_passphrase_length=8, verbose=opts.verbose)
            picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)
            skyrng.ssh_add_keyinfo(picked_keyinfo, verbose=opts.verbose)

    if opts.verbose:
        sys.stderr.write("[%s.%s:%d] Info : Stored KeyInfo : %s\n"
                         % (__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno, str(picked_keyinfo)))

    for data_idx, raw_data in enumerate(opts.data):
        if opts.disuse_ssh_agent or opts.verify_sign:
            picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)

        bytes_signed = picked_keyinfo.sign_ssh_data(data=raw_data, algorithm=opts.sign_algorithm, use_local_key=opts.disuse_ssh_agent, verbose=opts.verbose)

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
    
if __name__ == '__main__':
    main()
