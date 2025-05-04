#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import getpass
import pathlib
import subprocess
import inspect
import re
import itertools
import glob
import fnmatch

import base64
import hashlib

import cryptography
import cryptography.hazmat.primitives.asymmetric.types
import paramiko
import nacl

#import .paramiko_supplement
from .sshkeyinfo import SSHKeyInfo 

class SSHKeyUtil(object):
    """
    Utility Functions for SSH keys
    """
    KEY_TYPES                   = ("dsa", "ecdsa", "ed25519", "rsa")
    KEY_TYPE_DEFAULT            = 'rsa'
    KEY_BITS_DEFAULT            = {'dsa':1024, 'ecdsa': 2048, 'ed25519': 256, 'rsa': 4096 }
    KEYFILE_BASENAME_DEFAULT    = 'id_key'
    KEYFILE_EXT_DEFAULT         = {'private': '',   'public': '.pub' }
    KEYFILE_DIRECTORY_DEFAULT   = {'private': 'private_keys',   'public': 'public_keys' }
    OPENSSH_PATH_SSH_USER_DIR   = "~/.ssh"
    SEEK_OPENSSH_KEYDIR_DEFAULT = False
    KEYSCAN_EXCLUDES            = ["authorized_keys*", "known_hosts*", "config*", "*~", "*.bak", "*.back*up"]

    PRIVATEKEY_HEADER_PATTERN = re.compile(r'^-{5}BEGIN .* PRIVATE KEY-{5}$')
    PUBLICKEY_HEADER_PATTERN  = re.compile(r'^(?P<sshkey_type>ssh-(?P<key_type>'
                                           + r'|'.join(KEY_TYPES)
                                           + r')) +(?P<key_cont>[^ ]*) +(?P<key_id>.*)$')

    def __init__(self,
                 **kwds):
        pass

    @classmethod
    def Get_Key_Type(cls, keyobj, sshformat=False):
        ecdsa_key_types = { "secp256r1": "ecdsa-sha2-nistp256",
                            "secp384r1": "ecdsa-sha2-nistp384",
                            "secp521r1": "ecdsa-sha2-nistp521"}
        key_type = None

        if isinstance(keyobj, (cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey,
                               cryptography.hazmat.primitives.asymmetric.rsa,RSAPrivateKey)):
            key_type = "rsa"
        elif isinstance(keyobj, (cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey,
                                 cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey)):
            key_type = "dss" if sshformat else "dsa"
        elif isinstance(keyobj, (cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PublicKey,
                                 cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PrivateKey)):
            key_type = "ed25519"
        elif isinstance(keyobj, (cryptography.hazmat.primitives.asymmetric.ed488.Ed488PublicKey,
                                 cryptography.hazmat.primitives.asymmetric.ed488.Ed488PrivateKey)):
            key_type = "ed488"
        elif isinstance(keyobj, cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey):
            key_type = ecdsa_key_types.get(keyobj.public_key().curve.name)
        elif isinstance(keyobj, cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey):
            key_type = ecdsa_key_types.get(keyobj.curve.name)

        if isinstance(key_type, str) and key_type:
            return key_type

        raise ValueError('[%s.%s:%d] invalid key type %s'
                         % (cls.__name__, inspect.currentframe().f_code.co_name,
                            inspect.currentframe().f_lineno, keyobj.__name__) )

    @classmethod
    def Keydirectory_Path(cls,
                          keydir_prefix    : str = None,
                          privatekey_dir   : str = None,
                          publickey_dir    : str = None, **kwds):

        prvt_ksubdir = privatekey_dir if isinstance(privatekey_dir,str) else cls.KEYFILE_DIRECTORY_DEFAULT['private']
        prvt_kdir    = os.path.join(keydir_prefix, prvt_ksubdir) if isinstance(keydir_prefix,str) else prvt_ksubdir

        # pblc_ksubdir = publickey_dir if isinstance(publickey_dir,str) and publickey_dir else prvt_ksubdir
        pblc_ksubdir = publickey_dir if isinstance(publickey_dir,str) else cls.KEYFILE_DIRECTORY_DEFAULT['public']
        pblc_kdir    = os.path.join(keydir_prefix, pblc_ksubdir) if isinstance(keydir_prefix,str) else pblc_ksubdir
        return (prvt_kdir, pblc_kdir)

    @classmethod
    def OpeSSH_Keydirectory_Path(cls, **kwds):
        return (os.path.expanduser(cls.OPENSSH_PATH_SSH_USER_DIR), os.path.expanduser(cls.OPENSSH_PATH_SSH_USER_DIR))

    @classmethod
    def KeyPair_Filename(cls, key_type    : str = None,
                         keyfile_basename : str = None,
                         privatekey_ext   : str = None,
                         publickey_ext    : str = None,
                         **kwds):

        ktyp  = cls.KEY_TYPE_DEFAULT.lower() if key_type is None else ( key_type.lower() if isinstance(key_type, str) else "" )
        if not ktyp in cls.KEY_TYPES:
            raise ValueError('[%s.%s:%d] key_type must be one of (%s) but %s'
                             % (cls.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno, " ".join(cls.KEY_TYPES), key_type) )

        kyfl_bn = keyfile_basename  if isinstance(keyfile_basename, str) and keyfile_basename  else cls.KEYFILE_BASENAME_DEFAULT
        fbn     = kyfl_bn if kyfl_bn.endswith(ktyp) else (kyfl_bn+'_'+ktyp)

        prvt_kext = privatekey_ext if isinstance(privatekey_ext,str) else cls.KEYFILE_EXT_DEFAULT['private']
        pblc_kext = publickey_ext  if isinstance(publickey_ext,str)  else cls.KEYFILE_EXT_DEFAULT['public']

        prvt_kext =  prvt_kext if (not prvt_kext) or prvt_kext.startswith(".") else "."+prvt_kext
        pblc_kext =  pblc_kext if (not pblc_kext) or pblc_kext.startswith(".") else "."+pblc_kext

        private_key_filename = fbn+prvt_kext
        public_key_filename  = fbn+pblc_kext

        return (private_key_filename, public_key_filename)

    @classmethod
    def Openssh_KeyPair_Filename(cls, key_type : str = None, **kwds):
        ktyp  = cls.KEY_TYPE_DEFAULT.lower() if key_type is None else ( key_type.lower() if isinstance(key_type, str) else "" )
        if not ktyp in cls.KEY_TYPES:
            raise ValueError('[%s.%s:%d] key_type must be one of (%s) but %s'
                             % (cls.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno, " ".join(cls.KEY_TYPES), key_type))
        return ('id_'+ktyp, 'id_'+ktyp+'.pub')

    @classmethod
    def KeyPair_Path(cls, key_type    : str = None,
                     keydir_prefix    : str = None,
                     privatekey_dir   : str = None,
                     publickey_dir    : str = None,
                     keyfile_basename : str = None,
                     privatekey_ext   : str = None,
                     publickey_ext    : str = None,
                     **kwds):

        prvt_kdir, pblc_kdir = cls.Keydirectory_Path(keydir_prefix=keydir_prefix,
                                                     privatekey_dir=privatekey_dir,
                                                     publickey_dir=publickey_dir, **kwds)


        private_key_filename, public_key_filename = cls.KeyPair_Filename(key_type=key_type,
                                                                         keyfile_basename=keyfile_basename,
                                                                         privatekey_ext=privatekey_ext,
                                                                         publickey_ext=publickey_ext, **kwds)

        private_key_path = os.path.join(prvt_kdir, private_key_filename)
        public_key_path  = os.path.join(pblc_kdir, public_key_filename)

        return (os.path.expanduser(private_key_path), os.path.expanduser(public_key_path))

    @classmethod
    def Openssh_KeyPair_Path(cls, key_type : str = None, **kwds):

        prvt_kdir, pblc_kdir = cls.Openssh_Keydirectory_Path(**kwds)
        private_key_filename, public_key_filename = cls.Openssh_KeyPair_Filename(key_type=key_type, **kwds)

        private_key_path = os.path.join(prvt_kdir, private_key_filename)
        public_key_path  = os.path.join(pblc_kdir, public_key_filename)
        return (os.path.expanduser(private_key_path), os.path.expanduser(public_key_path))

    @classmethod
    def Default_Key_Id(cls, key_comment:str=None, key_type:str=None) -> str :
        key_id_base = (getpass.getuser()+'@'+os.uname().nodename) if key_comment is None else key_comment
        key_type_suffix = key_type if isinstance(key_type,str) and key_type else cls.KEY_TYPE_DEFAULT
        #return key_id_base+":"+key_type_suffix if isinstance(key_type_suffix,str) and key_type_suffix else key_id_base
        return key_id_base

    @classmethod
    def Gen_Key_Obj(cls,
                    key_type            : str = None,
                    key_bits            : int = 0,
                    ecdsa_ec_type       : str = "secp256r1",
                    rsa_public_exponent : int = 65537, **kwds):

        ktyp  = cls.KEY_TYPE_DEFAULT.lower() if key_type is None else ( key_type.lower() if isinstance(key_type, str) else "" )
        if not ktyp in cls.KEY_TYPES:
            raise ValueError('[%s.%s:%d] key_type must be one of (%s) but %s'
                             % (cls.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno, " ".join(cls.KEY_TYPES), key_type) )
        kbits= key_bits if key_bits>0 else cls.KEY_BITS_DEFAULT.get(ktyp)

        if ktyp=='dsa':
            key_obj = cryptography.hazmat.primitives.asymmetric.dsa.generate_private_key(key_size=kbits)
        elif ktyp=='ecdsa':
            if ecdsa_ec_type in ["NIST P-192", "p192", "P-192", "prime192v1", "secp192r1"]:
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP192R1()
            elif ecdsa_ec_type in ["NIST P-224", "p224", "P-224", "prime224v1", "secp224r1"]:
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP224R1()
            elif ecdsa_ec_type in ["NIST P-256", "p256", "P-256", "prime256v1", "secp256r1"]:
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP256R1()
            elif ecdsa_ec_type in ["NIST P-384", "p384", "P-384", "prime384v1", "secp384r1"]:
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP384R1()
            elif ecdsa_ec_type in ["NIST P-521", "p521", "P-521", "prime521v1", "secp521r1"]:
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP521R1()
            elif ecdsa_ec_type == "secp256k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP256K1()
            elif ecdsa_ec_type == "sect163k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT163K1()
            elif ecdsa_ec_type == "sect233k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT233K1()
            elif ecdsa_ec_type == "sect283k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT283K1()
            elif ecdsa_ec_type == "sect409k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT409K1()
            elif ecdsa_ec_type == "sect571k1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT571K1()
            elif ecdsa_ec_type == "sect163r2":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT163R2()
            elif ecdsa_ec_type == "sect233r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT233R1()
            elif ecdsa_ec_type == "sect283r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT283R1()
            elif ecdsa_ec_type == "sect409r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT409R1()
            elif ecdsa_ec_type == "sect571r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.SECT571R1()
            elif ecdsa_ec_type == "brainpoolP256r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.BrainpoolP256R1()
            elif ecdsa_ec_type == "brainpoolP384r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.BrainpoolP384R1()
            elif ecdsa_ec_type == "brainpoolP512r1":
                ec_curve = cryptography.hazmat.primitives.asymmetric.ec.BrainpoolP512R1()
            else:
                raise ValueError('[%s.%s] Invalid ec_curve' % (cls.__name__, __name__) )
            key_obj = cryptography.hazmat.primitives.asymmetric.ec.generate_private_key(ec_curve)
        elif ktyp=='ed25519' or ktyp=='Ed25519':
            key_obj = cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PrivateKey.generate()
        elif ktyp=='rsa':
            key_obj = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(public_exponent=rsa_public_exponent, key_size=kbits)


        pubkey_obj = key_obj.public_key()
        
        # return ( key_obj, pubkey_obj )
        return SSHKeyInfo(key_type=ktyp,
                          private_key=key_obj,
                          public_key=pubkey_obj)

    @classmethod
    def Encode_Key_Contents(cls,
                            key_info = None, 
                            private_key_object = None,
                            public_key_object = None,
                            passphrase  : str = None,
                            key_comment : str = None,
                            min_passphrase_length :int = 8, **kwds):

        sshkey_info = key_info if isinstance(key_info, SSHKeyInfo) else SSHKeyInfo()
        
        if isinstance(sshkey_info.private_key,
                      cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPrivateKeyTypes):
            prvt_key_obj = sshkey_info.private_key
            if isinstance(sshkey_info.key_type, str) and sshkey_info.key_type:
                pass
            else:
                sshkey_info.key_type = cls.Get_Key_Type(sshkey_info.key_type)
            ktyp = sshkey_info.key_type
        elif isinstance(private_key_object,
                        cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPrivateKeyTypes):
            sshkey_info.private_key = private_key_object
            sshkey_info.key_type=cls.Get_Key_Type(private_key_object)
            ktyp         = sshkey_info.key_type
            prvt_key_obj = private_key_object,
        else:
            raise ValueError('[%s.%s:%d] private_key_object be one of (%s)'
                             % (cls.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno,
                                " ".join([x.__name__ for x in cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPrivateKeyTypes])))
        if isinstance(sshkey_info.public_key,
                       cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPublicKeyTypes):
            pblc_key_obj = sshkey_info.public_key
        if isinstance(public_key_object,
                      cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPublicKeyTypes):
            sshkey_info.public_key = public_key_object
            pblc_key_obj = public_key_object
        elif public_key_object is None:
            sshkey_info.public_key = prvt_key_obj.public_key()
            pblc_key_obj = sshkey_info.public_key
        else:
            raise ValueError('[%s.%s:%d] public_key_object be one of (%s)'
                             % (cls.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno,
                                " ".join([x.__name__ for x in cryptography.hazmat.primitives.asymmetric.types.CertificateIssuerPublicKeyTypes])))

        if isinstance(sshkey_info.passphrase, str) and (len(sshkey_info.passphrase) >= min_passphrase_length):
            passphrs = sshkey_info.passphrase
        elif isinstance(passphrase,str) and ( len(passphrase) >= min_passphrase_length ):
            passphrs               = passphrase
            sshkey_info.passphrase = passphrase
        else:
            passphrs                = getpass.getpass(prompt=('[%s.%s:%d] private key passphrase: ')
                                                      % (cls.__name__, inspect.currentframe().f_code.co_name,
                                                         inspect.currentframe().f_lineno))
            sshkey_info.passphrase = passphrs
                    
        ky_cmnt = cls.Default_Key_Id(key_comment=key_comment if isinstance(key_comment,str) and key_comment else sshkey_info.key_id,
                                     key_type=ktyp)
        if sshkey_info.key_id is None:
           sshkey_info.key_id = ky_cmnt
        
        prvt_key_contents = prvt_key_obj.private_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
                                                       format=cryptography.hazmat.primitives.serialization.PrivateFormat.OpenSSH,
                                                       encryption_algorithm=cryptography.hazmat.primitives.serialization.BestAvailableEncryption(passphrs.encode('utf-8')))

        pblc_key_contents = pblc_key_obj.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.OpenSSH,
                                                      format=cryptography.hazmat.primitives.serialization.PublicFormat.OpenSSH)

        pblc_key_contents += b' '+ky_cmnt.encode('utf-8')

        # return (prvt_key_contents, pblc_key_contents)

        sshkey_info.public_key_data  = pblc_key_contents
        sshkey_info.private_key_data = prvt_key_contents 

        return sshkey_info

    @classmethod
    def Save_Contents(cls, contents, pathobj, dir_mode, file_mode, 
                      force_overwrite: bool = False):
        if not pathobj.parent.exists():
            pathobj.parent.mkdir(mode=dir_mode, parents=True, exist_ok=True)
        elif not pathobj.parent.is_dir():
            raise FileExistsError("Non-directory is exists: %s" % (str(pathobj.parent), ))
        if ( not force_overwrite ) and pathobj.exists():
            raise FileExistsError("Path is exists: %s (force_overwrite : %s)" % (str(pathobj), str(force_overwrite)))
        with pathobj.open(mode="wb") as f:
            f.write(contents)
            pathobj.chmod(file_mode)

    @classmethod
    def Save_KeyPair(cls,
                     private_key_contents : bytes = None,
                     public_key_contents  : bytes = None,
                     key_type         : str = None,
                     keydir_prefix    : str = None,
                     privatekey_dir   : str = None,
                     publickey_dir    : str = None,
                     keyfile_basename : str = None,
                     privatekey_ext   : str = None,
                     publickey_ext    : str = None,
                     force_overwrite  : bool = False,
                     **kwds):

        prv_path, pub_path = cls.KeyPair_Path(key_type=key_type,
                                              keydir_prefix=keydir_prefix,
                                              privatekey_dir=privatekey_dir,
                                              publickey_dir=publickey_dir,
                                              keyfile_basename=keyfile_basename,
                                              privatekey_ext=privatekey_ext,
                                              publickey_ext=publickey_ext, **kwds)
        
        if private_key_contents is not None:
            cls.Save_Contents(contents=private_key_contents,
                              pathobj=pathlib.Path(prv_path),
                              dir_mode=0o700, file_mode=0o600,
                              force_overwrite=force_overwrite)

        if public_key_contents is not None:
            cls.Save_Contents(contents=public_key_contents,
                              pathobj=pathlib.Path(pub_path),
                              dir_mode=0o755, file_mode=0o644,
                              force_overwrite=force_overwrite)

        return {'private' :  prv_path, "public": pub_path }

    @classmethod
    def Generate_SSHKey(cls, key_type    : str = None,
                        key_bits         : int = 0,
                        passphrase       : str = None,
                        key_comment      : str = None,
                        keydir_prefix    : str = None,
                        privatekey_dir   : str = None,
                        publickey_dir    : str = None,
                        keyfile_basename : str = None,
                        privatekey_ext   : str = None,
                        publickey_ext    : str = None,
                        force_overwrite  : bool = False,
                        ecdsa_ec_type       : str = "secp256r1",
                        rsa_public_exponent : int = 65537,
                        min_passphrase_length :int = 8,
                        **kwds):

        ssh_keyinfo = cls.Gen_Key_Obj(key_type=key_type, key_bits=key_bits,
                                      ecdsa_ec_type=ecdsa_ec_type,
                                      rsa_public_exponent=rsa_public_exponent, **kwds)
        ssh_keyinfo.key_id = key_comment

        pssphrs = ( passphrase
                    if isinstance(passphrase,str) and len(passphrase)>=min_passphrase_length
                    else getpass.getpass(prompt=('[%s.%s:%d] private key passphrase for key_id="%s": ')
                                         % (cls.__name__, inspect.currentframe().f_code.co_name,
                                            inspect.currentframe().f_lineno, ssh_keyinfo.key_id)))
        
        ssh_keyinfo = cls.Encode_Key_Contents(key_info=ssh_keyinfo,
                                              private_key_object = ssh_keyinfo.private_key,
                                              public_key_object = ssh_keyinfo.public_key,
                                              passphrase=pssphrs,
                                              key_comment=key_comment,
                                              min_passphrase_length=min_passphrase_length, **kwds)
        path_alist = cls.Save_KeyPair(private_key_contents=ssh_keyinfo.private_key_data,
                                      public_key_contents=ssh_keyinfo.public_key_data,
                                      key_type=ssh_keyinfo.key_type, keydir_prefix=keydir_prefix,
                                      privatekey_dir=privatekey_dir, publickey_dir=publickey_dir,
                                      keyfile_basename=keyfile_basename,
                                      privatekey_ext=privatekey_ext, publickey_ext=publickey_ext,
                                      force_overwrite=force_overwrite, **kwds)
        
        ssh_keyinfo.path_private_key = path_alist['private']
        ssh_keyinfo.path_public_key  = path_alist['public']
        ssh_keyinfo.passphrase       = pssphrs
        
        ssh_keyinfo.load_local_key(passphrase=pssphrs.encode('utf-8'))
        ssh_keyinfo.load_public_blob()
        
        return ssh_keyinfo

    @classmethod
    def Openssh_List_Keyfile_Pairs(cls, exclude_pattern : list =None, **kwds):
        excld_pttrns = exclude_pattern if isinstance(exclude_pattern, list) else cls.KEYSCAN_EXCLUDES
        scan_dir = os.path.expanduser(cls.OPENSSH_PATH_SSH_USER_DIR)
        private_keys = []
        public_keys  = []

        if os.path.isdir(scan_dir):
            for kf_cand in os.listdir(scan_dir):
                flg_exclude=False
                for pat in excld_pttrns:
                    if fnmatch.fnmatch(kf_cand, pat):
                        flg_exclude=True
                        break
                if flg_exclude:
                    continue
                kf_cand_path = pathlib.Path(scan_dir, kf_cand)
                if not kf_cand_path.is_file():
                    continue
                try:
                    fin = kf_cand_path.open(mode="r")
                    data = fin.readline().rstrip()
                    fin.close()
                except:
                    continue
                m1 = cls.PRIVATEKEY_HEADER_PATTERN.match(data)
                if m1:
                    private_keys.append((kf_cand, kf_cand_path))
                    continue
                m2 = cls.PUBLICKEY_HEADER_PATTERN.match(data)
                if m2:
                    b_keycont = base64.b64decode(m2.group('key_cont'))
                    hashobj=hashlib.sha256(b_keycont)
                    public_keys.append((kf_cand, kf_cand_path, m2.group('key_id'), m2.group('key_type')))
                    continue

        buf=[]
        for pblc_kfname, pblc_kf_path, key_id, key_type in public_keys:
            for prvt_kfname, prvt_kf_path in private_keys:
                if (prvt_kfname+'.pub') != pblc_kfname:
                    continue
                buf.append(SSHKeyInfo(key_id=key_id,
                                      key_type=key_type,
                                      path_private_key=str(prvt_kf_path),
                                      path_public_key=str(pblc_kf_path)))
        return buf

    @classmethod
    def List_Keyfile_Pairs(cls,
                           seek_openssh_dir : bool = False,
                           keydir_prefix    : str  = None,
                           privatekey_dir   : str  = None,
                           publickey_dir    : str  = None,
                           exclude_pattern  : list = None,
                           **kwds):

        excld_pttrns = exclude_pattern if isinstance(exclude_pattern, list) else cls.KEYSCAN_EXCLUDES

        prvt_kdir, pblc_kdir = cls.Keydirectory_Path(keydir_prefix=keydir_prefix,
                                                     privatekey_dir=privatekey_dir,
                                                     publickey_dir=publickey_dir, **kwds)
        private_keys = []
        public_keys  = []

        for d in (pblc_kdir, prvt_kdir):
            d_path = os.path.expanduser(d)
            if not os.path.isdir(d_path):
                continue
            for kf_cand in os.listdir(d_path):
                flg_exclude=False
                for pat in excld_pttrns:
                    if fnmatch.fnmatch(kf_cand, pat):
                        flg_exclude=True
                        break
                if flg_exclude:
                    continue
                kf_cand_path = pathlib.Path(d_path, kf_cand)
                if not kf_cand_path.is_file():
                    continue
                try:
                    fin = kf_cand_path.open(mode="r")
                    data = fin.readline().rstrip()
                    fin.close()
                except:
                    continue
                m1 = cls.PRIVATEKEY_HEADER_PATTERN.match(data)
                if m1:
                    private_keys.append((kf_cand, kf_cand_path))
                    continue
                m2 = cls.PUBLICKEY_HEADER_PATTERN.match(data)
                if m2:
                    b_keycont = base64.b64decode(m2.group('key_cont'))
                    hashobj=hashlib.sha256(b_keycont)
                    public_keys.append((kf_cand, kf_cand_path, m2.group('key_id'), m2.group('key_type')))
                    continue

        buf=[]
        for pblc_kfname, pblc_kf_path, key_id, key_type in public_keys:
            pblc_kf_bn = os.path.splitext(pblc_kfname)[0]
            for prvt_kfname, prvt_kf_path in private_keys:
                prvt_kf_bn = os.path.splitext(prvt_kfname)[0]
                if pblc_kf_bn != prvt_kf_bn and pblc_kf_bn != prvt_kfname and prvt_kf_bn!=pblc_kfname:
                    continue
                buf.append(SSHKeyInfo(key_id=key_id,
                                      key_type=key_type,
                                      path_private_key=str(prvt_kf_path),
                                      path_public_key=str(pblc_kf_path)))
        if seek_openssh_dir and not cls.OPENSSH_PATH_SSH_USER_DIR in (pblc_kdir, prvt_kdir):
            buf.extend(cls.Openssh_List_Keyfile_Pairs(exclude_pattern=exclude_pattern, **kwds))
        return buf

    @classmethod
    def List_Key_Pairs(cls,
                       seek_openssh_dir   : bool = False,
                       decode_private_key : bool = False,
                       passphrase         : str  = None,
                       passphrase_alist   : dict = None,
                       keydir_prefix      : str  = None,
                       privatekey_dir     : str  = None,
                       publickey_dir      : str  = None,
                       exclude_pattern    : list = None,
                       **kwds):
        buf = cls.List_Keyfile_Pairs(seek_openssh_dir=seek_openssh_dir,
                                     keydir_prefix=keydir_prefix,
                                     privatekey_dir=privatekey_dir,
                                     publickey_dir=publickey_dir,
                                     exclude_pattern=exclude_pattern, **kwds)
        for sshkey_info in buf:
            if isinstance(sshkey_info.path_public_key,str) and sshkey_info.path_public_key:
                try:
                    fin = open(sshkey_info.path_public_key, "rb")
                    pblckey_data = fin.read()
                    fin.close()
                    sshkey_info.public_key      = cryptography.hazmat.primitives.serialization.load_ssh_public_key(data=pblckey_data)
                    sshkey_info.public_key_data = pblckey_data
                    sshkey_info.load_public_blob()
                except Exception as ex:
                    sys.stderr.write("[%s.%s:%d] Error : public_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        sshkey_info.key_id, sshkey_info.key_type, sshkey_info.path_public_key))
                    
            if decode_private_key and isinstance(sshkey_info.path_private_key,str) and sshkey_info.path_private_key:
                pssphrs = sshkey_info.passphrase
                flg_pssphrs_store = False
                if passphrs is None:
                    passphrase_alist.get(sshkey_info.key_id, passphrase) if isinstance(passphrase_alist,dict) else None
                    flg_pssphrs_store = True
                if passphrs is None:
                    pssphrs = getpass.getpass(prompt=('[%s.%s:%d] private key passphrase for key_id="%s": ')
                                              % (cls.__name__, inspect.currentframe().f_code.co_name,
                                                 inspect.currentframe().f_lineno, sshkey_info.key_id))
                    flg_pssphrs_store = True
                try:
                    fin = open(sshkey_info.path_private_key, "rb")
                    prvtkey_data = fin.read()
                    fin.close()
                    sshkey_info.private_key = cryptography.hazmat.primitives.serialization.load_ssh_private_key(data=prvtkey_data,
                                                                                                                password=pssphrs.encode('utf-8'))
                    sshkey_info.private_key_data = prvtkey_data
                    sshkey_info.load_local_key(passphrase=pssphrs.encode('utf-8'))
                    if flg_pssphrs_store:
                        sshkey_info.passphrase = pssphrs
                except:
                    sys.stderr.write("[%s.%s:%d] Error : private_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        sshkey_info.key_id, sshkey_info.key_type, sshkey_info.path_private_key))
                try:
                    sshkey_info.local_key = paramiko.pkey.PKey.from_path(sshkey_info.path_private_key, passphrase=pssphrs.encode('utf-8'))
                    if ( isinstance(sshkey_info.local_key, paramiko.ed25519key.Ed25519Key)
                         and sshkey_info.local_key._verifying_key is None ):
                        sshkey_info.local_key._verifying_key = nacl.signing.VerifyKey(sshkey_info.local_key._signing_key.verify_key.encode())
                except:
                    sys.stderr.write("[%s.%s:%d] Error : local_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        sshkey_info.key_id, sshkey_info.key_type, sshkey_info.path_private_key))
                    
        return buf


    @classmethod
    def Refresh_Key_Pairs(cls,
                          key_stored         : dict = {},
                          seek_openssh_dir   : bool = False,
                          decode_private_key : bool = False,
                          passphrase         : str  = None,
                          passphrase_alist   : dict = None,
                          keydir_prefix      : str  = None,
                          privatekey_dir     : str  = None,
                          publickey_dir      : str  = None,
                          exclude_pattern    : list = None,
                          **kwds):

        keyfile_exists = cls.List_Keyfile_Pairs(seek_openssh_dir=seek_openssh_dir,
                                                keydir_prefix=keydir_prefix,
                                                privatekey_dir=privatekey_dir,
                                                publickey_dir=publickey_dir,
                                                exclude_pattern=exclude_pattern, **kwds)
        keep_list = []
        missing_list = []
        update_alist = {}
        for kidx, kinfo in key_stored.items():
            key_id, key_type = kidx
            for kinfo_exists in keyfile_exists:
                if kinfo.is_same_localfile(kinfo_exists):
                    keep_list.append(kidx)
                    break
            else:
                for kinfo_exists in keyfile_exists:
                    if kinfo.is_same_keyindex(kinfo_exists):
                        update_alist.update({kidx: (kinfo_exists, False)})
                        break
                else:
                    missing_list.append(kidx)

        update_list = update_alist.keys()
        for kinfo_exists in keyfile_exists:
            nkidx = (kinfo_exists.key_id, kinfo_exists.key_type) 
            if ( nkidx in keep_list ) or ( nkidx in update_list ):
                continue
            update_alist.update( { nkidx: (kinfo_exists, True) } )
        
        for m_kindx in missing_list:
            key_stored.pop(m_kindx)

        for n_kidx, ninfos in update_alist.items():
            new_keyinfo, flg_new = ninfos
            if flg_new:
                key_stored.update( { n_kidx :  new_keyinfo } )
            else:
                key_stored.get(n_kidx).path_private_key = new_keyinfo.path_private_key
                key_stored.get(n_kidx).path_public_key  = new_keyinfo.path_public_key
            ptr_keyinfo = key_stored.get(n_kidx)
            if isinstance(ptr_keyinfo.path_public_key,str) and ptr_keyinfo.path_public_key:
                try:
                    fin = open(ptr_keyinfo.path_public_key, "rb")
                    pblckey_data = fin.read()
                    fin.close()
                    ptr_keyinfo.public_key      = cryptography.hazmat.primitives.serialization.load_ssh_public_key(data=pblckey_data)
                    ptr_keyinfo.public_key_data = pblckey_data
                    ptr_keyinfo.load_public_blob()
                except Exception as ex:
                    sys.stderr.write("[%s.%s:%d] Error : public_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        ptr_keyinfo.key_id, ptr_keyinfo.key_type, ptr_keyinfo.path_public_key))
                    
            if decode_private_key and isinstance(ptr_keyinfo.path_private_key,str) and ptr_keyinfo.path_private_key:
                pssphrs = ptr_keyinfo.passphrase
                flg_pssphrs_store = False
                if passphrs is None:
                    passphrase_alist.get(ptr_keyinfo.key_id, passphrase) if isinstance(passphrase_alist,dict) else None
                    flg_pssphrs_store = True
                if passphrs is None:
                    pssphrs = getpass.getpass(prompt=('[%s.%s:%d] private key passphrase for key_id="%s": ')
                                              % (cls.__name__, inspect.currentframe().f_code.co_name,
                                                 inspect.currentframe().f_lineno, ptr_keyinfo.key_id))
                    flg_pssphrs_store = True
                try:
                    fin = open(ptr_keyinfo.path_private_key, "rb")
                    prvtkey_data = fin.read()
                    fin.close()
                    ptr_keyinfo.private_key = cryptography.hazmat.primitives.serialization.load_ssh_private_key(data=prvtkey_data,
                                                                                                                password=pssphrs.encode('utf-8'))
                    ptr_keyinfo.private_key_data = prvtkey_data
                    ptr_keyinfo.load_local_key(passphrase=pssphrs.encode('utf-8'))
                    if flg_pssphrs_store:
                        ptr_keyinfo.passphrase = pssphrs
                except:
                    sys.stderr.write("[%s.%s:%d] Error : private_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        ptr_keyinfo.key_id, ptr_keyinfo.key_type, ptr_keyinfo.path_private_key))
                try:
                    ptr_keyinfo.local_key = paramiko.pkey.PKey.from_path(ptr_keyinfo.path_private_key, passphrase=pssphrs.encode('utf-8'))
                    if ( isinstance(ptr_keyinfo.local_key, paramiko.ed25519key.Ed25519Key)
                         and ptr_keyinfo.local_key._verifying_key is None ):
                        ptr_keyinfo.local_key._verifying_key = nacl.signing.VerifyKey(ptr_keyinfo.local_key._signing_key.verify_key.encode())
                except:
                    sys.stderr.write("[%s.%s:%d] Error : local_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                     % (__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                        ptr_keyinfo.key_id, ptr_keyinfo.key_type, ptr_keyinfo.path_private_key))
                    
        return key_stored
    
    @classmethod
    def Connect_SSHAgent(cls, sock_path : str, restore_environ : bool = False, **kwds):
        verbose         = kwds.get('verbose', False)
        
        sock_env_orig = os.environ['SSH_AUTH_SOCK']
        client_obj    = None
        if sock_path is None or not pathlib.Path(sock_path).is_socket():
            if verbose:
                sys.stderr.write('[%s.%s:%d] Fail to connect agent : %s\n'
                                 % (cls.__name__, inspect.currentframe().f_code.co_name,
                                    inspect.currentframe().f_lineno, sock_path))
        else:
            try:
                os.environ['SSH_AUTH_SOCK'] = sock_path
                agent_client_obj = paramiko.agent.Agent()
                if agent_client_obj._conn is None:
                    # if verbose:
                    #     sys.stderr.write('[%s.%s:%d] Fail to connect agent : %s\n'
                    #                      % (cls.__name__, inspect.currentframe().f_code.co_name,
                    #                         inspect.currentframe().f_lineno, sock_path))
                    pass
                else:
                    client_obj = agent_client_obj
            except Exception as ex:
                if verbose:
                    sys.stderr.write('[%s.%s:%d] Fail to connect agent : %s\n'
                                     % (cls.__name__, inspect.currentframe().f_code.co_name,
                                        inspect.currentframe().f_lineno, sock_path))
        if restore_environ:
            os.environ['SSH_AUTH_SOCK'] = sock_env_orig
        return client_obj

    @classmethod
    def SSHAgent_SocketPath_Lists(cls, **kwds):
        sock_cands = []
        if sys.platform == 'darwin':
            sock_seek_dirs = [ '/private/tmp', os.environ.get('TMPDIR', '/tmp') ]
            sock_seek_patterns = [ ('com.apple.launchd.*', 'Listeners'),  ('ssh-*', 'agent.*') ]
        else:
            sock_seek_dirs = [ os.environ.get('TMPDIR', '/tmp'), '/var/tmp' ]
            sock_seek_patterns = [  ('ssh-*', 'agent.*') ]
        for pd,pttn in itertools.product(sock_seek_dirs, sock_seek_patterns):
            sd, pn = pttn
            for sdpth in [ dpth for dpth in glob.glob(os.path.join(pd, sd))
                           if os.path.isdir(dpth) and os.access(dpth, os.R_OK|os.X_OK) ]:
                sock_cands.extend([spth for spth in glob.glob(os.path.join(sdpth, pn))
                                   if ( pathlib.Path(spth).is_socket() and os.access(spth, os.R_OK|os.W_OK))])
                
        return sock_cands
    
    @classmethod
    def Invoke_SSHAgent(cls, restore_environ : bool = False, **kwds):
        verbose         = kwds.get('verbose', False)
        sock_env_orig = os.environ['SSH_AUTH_SOCK']

        child_proc = subprocess.Popen([os.environ.get("SSH_AGENT", "ssh-agent"), "-s"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        child_proc.wait()
        child_proc_stdout = child_proc.stdout.read()
        child_proc_stderr = child_proc.stderr.read()

        pttrn_spliter=re.compile(r'[;\n]')
        pttrn_seek_sock=re.compile(r'^ *(?P<cmd>setenv +)?SSH_AUTH_SOCK(=| ) *(?P<val>.*)\s*$')
        pttrn_seek_pid=re.compile(r'^.*agent.*pid\s+(?P<val>\d+)\D*.*$', re.I)
        agent_pid = -1
        for sout in [s for s in pttrn_spliter.split(child_proc_stdout.decode('utf-8')) if len(s)>0]:
            m1 = pttrn_seek_sock.search(sout)
            if m1:
                ssh_agent_sock = str(m1.group('val'))
            m2 = pttrn_seek_pid.search(sout)
            if m2:
                agent_pid = int(m2.group('val'))

        if len(child_proc_stderr)>0 and verbose :
            for serr in child_proc_stderr.split("\n"):
                sys.stderr.write('[%s.%s:%d] stderr (%d) : %s\n'
                                 % (cls.__name__, inspect.currentframe().f_code.co_name,
                                    inspect.currentframe().f_lineno, agent_pid, serr))

        if restore_environ:
            os.environ['SSH_AUTH_SOCK'] = sock_env_orig

        return (ssh_agent_sock, agent_pid)

    @classmethod
    def List_SSHAgent(cls, invoke_agent : bool =False,
                      restore_environ : bool = False, **kwds):
        verbose = kwds.get('verbose', False)

        buf = []
        for sock_cand in cls.SSHAgent_SocketPath_Lists(**kwds):
            agent_client = cls.Connect_SSHAgent(sock_cand,
                                                restore_environ=restore_environ, **kwds)
            if isinstance(agent_client, paramiko.agent.Agent):
                buf.append( (sock_cand, agent_client) )

        if len(buf)<1 and invoke_agent:
            new_sock, new_pid = cls.Invoke_SSHAgent(restore_environ=restore_environ, **kwds)
            if new_sock is None:
                sys.stderr.write('[%s.%s:%d] Warning: Fail to invoke new agent\n'
                                 % (cls.__name__, inspect.currentframe().f_code.co_name,
                                    inspect.currentframe().f_lineno))
            else:
                if verbose:
                    sys.stderr.write('[%s.%s:%d] Warning: ssh-agent is invoked: (pid=%d, socket="%s"\n'
                                     % (cls.__name__, inspect.currentframe().f_code.co_name,
                                        inspect.currentframe().f_lineno, new_pid, new_sock))
                    
                new_client = cls.Connect_SSHAgent(new_sock,
                                                  restore_environ=restore_environ, **kwds)
                if isinstance(new_client, paramiko.agent.Agent):
                    buf.append( (new_sock, new_client) )

        return buf

    @classmethod
    def Refresh_SSHAgent_Alist(cls,
                               sshagent_alist  : dict = {},
                               invoke_agent    : bool = False,
                               restore_environ : bool = False, 
                               force_reconnect : bool = False, **kwds):
        flg_verbose = kwds.get('verbose', False)
        sockpath_candidate = cls.SSHAgent_SocketPath_Lists(**kwds)
        unavaiable_socks = []
        for sockpath,client in sshagent_alist.items():
            if sockpath in sockpath_candidate:
                if force_reconnect:
                    client.close()
                if client._conn is None:
                    sock_env_orig = os.environ['SSH_AUTH_SOCK']
                    os.environ['SSH_AUTH_SOCK'] = sockpath
                    client.__init__()
                    os.environ['SSH_AUTH_SOCK'] = sock_env_orig
                    if client_obj._conn is None and flg_verbose:
                        sys.stderr.write('[%s.%s:%d] Fail to connect agent : %s\n'
                                         % (cls.__name__, inspect.currentframe().f_code.co_name,
                                            inspect.currentframe().f_lineno, sockpath))
            else:
                unavaiable_socks.append(sockpath)
        avaiable_socks = sshagent_alist.keys()

        for sock in unavaiable_socks:
            invalid_client = sshagent_alist.pop(sock)
            try:
                invalid_client.close()
            except:
                pass
        for sock in sockpath_candidate:
            if sock in avaiable_socks:
                continue
            agent_client = cls.Connect_SSHAgent(sock, restore_environ=restore_environ, **kwds)
            if isinstance(agent_client, paramiko.agent.Agent):
                sshagent_alist.update({sock: agent_client})

        if len(sshagent_alist)<1 and invoke_agent:
            new_sock, new_pid = cls.Invoke_SSHAgent(restore_environ=restore_environ, **kwds)
            if new_sock is None:
                sys.stderr.write('[%s.%s:%d] Warning: Fail to invoke new agent\n'
                                 % (cls.__name__, inspect.currentframe().f_code.co_name,
                                    inspect.currentframe().f_lineno))
            else:
                if flg_verbose:
                    sys.stderr.write('[%s.%s:%d] Info: ssh-agent is invoked: (pid=%d, socket="%s"\n'
                                     % (cls.__name__, inspect.currentframe().f_code.co_name,
                                        inspect.currentframe().f_lineno, new_pid, new_sock))
                new_client = cls.Connect_SSHAgent(new_sock,
                                                  restore_environ=restore_environ, **kwds)
                if isinstance(new_client, paramiko.agent.Agent):
                    sshagent_alist.update( { new_sock: new_client} )
        return sshagent_alist


    @classmethod
    def List_Key_SSHAgent(cls,
                          agent_list : list = None, 
                          invoke_agent : bool =False,
                          restore_environ : bool = False, **kwds):
        buf = []
        agent_list_scan = ( agent_list
                            if isinstance(agent_list,list)
                            else cls.List_SSHAgent(invoke_agent=invoke_agent,
                                                   restore_environ=restore_environ, **kwds))
        for sock_path,agent_client in agent_list_scan:
            for key in agent_client.get_keys():
                buf.append( (key, agent_client, sock_path) )
        return buf
    

    @classmethod
    def List_KeyInfo_SSHAgent(cls,
                              agent_list : list = None,
                              invoke_agent : bool =False,
                              restore_environ : bool = False, **kwds):
        buf = [SSHKeyInfo(key_id=agent_key.comment,
                          key_type=agent_key.get_type(),
                          agent_key=agent_key,
                          agent_sock=sock_path,
                          agent_client=agent_client)
               for agent_key, agent_client, sock_path in cls.List_Key_SSHAgent(agent_list=agent_list,
                                                                               invoke_agent=invoke_agent,
                                                                               restore_environ=restore_environ, **kwds)]
        return buf


    @classmethod
    def Refresh_KeyInfo_SSHAgent(cls,
                                 key_stored      : dict = {},
                                 sshagent_alist  : dict = {},
                                 invoke_agent    : bool = False,
                                 restore_environ : bool = False, 
                                 force_reconnect : bool = False, **kwds):
        sshagent_alist = cls.Refresh_SSHAgent_Alist(sshagent_alist=sshagent_alist,
                                                    invoke_agent=invoke_agent,
                                                    restore_environ=restore_environ,
                                                    force_reconnect=force_reconnect, **kwds)
        agent_keybox = {}
        for sock,client in sshagent_alist.items():
            for agentkey in client.get_keys():
                kidx = (agentkey.comment, agentkey.get_type())
                if agent_keybox.get(kidx) is None:
                    agent_keybox.update({ kidx: {} })
                if agent_keybox.get(kidx).get(sock) is None:
                    agent_keybox.get(kidx).update( { sock: [] } )
                agent_keybox.get(kidx).get(sock).append((client, agentkey))

        for kidx,kinfo in key_stored.items():
            key_id, key_type = kidx
            match_socks = agent_keybox.get(kidx,{})
            if len(match_socks)<1:
                kinfo.agent_key    = None
                kinfo.agent_sock   = None
                kinfo.agent_client = None
                continue

            client_cands = match_socks.get(kinfo.agent_sock)
            if client_cands is not None:
                for cl,akey in client_cands:
                    if cl is kinfo.agent_client and akey is kinfo.agent_key:
                        break
                else:
                    kinfo.agent_client, kinfo.agent_key = client_cands[0]
            else:
                for sock,clientakeys in match_socks.items():
                    for cl,akey in clientakeys:
                        kinfo.agent_key    = akey
                        kinfo.agent_sock   = sock
                        kinfo.agent_client = cl
                        break
                    break
        
        for kidx,sockalist in agent_keybox.items():
            if key_stored.get(kidx) is not None:
                continue
            for sock,clientakeys in sockalist.items():
                for cl,akey in clientakeys:
                    key_stored.update( { kidx : 
                                         SSHKeyInfo(key_id=akey.comment, key_type=akey.get_type(),
                                                    agent_key=akey, agent_sock=sock, agent_client=cl) } )
                    break
                break
        return key_stored


    @classmethod
    def Refresh_KeyInfo(cls,
                        key_stored         : dict = {},
                        sshagent_alist        : dict = {},
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

        if use_local_key:
            key_stored_buf = cls.Refresh_Key_Pairs(key_stored=key_stored,
                                                   seek_openssh_dir=seek_openssh_dir,
                                                   decode_private_key=decode_private_key,
                                                   passphrase=passphrase,
                                                   passphrase_alist=passphrase_alist,
                                                   keydir_prefix=keydir_prefix,
                                                   privatekey_dir=privatekey_dir,
                                                   publickey_dir=publickey_dir,
                                                   exclude_pattern=exclude_pattern, **kwds)
        if use_ssg_agent:
            key_stored_ret = cls.Refresh_KeyInfo_SSHAgent(key_stored=key_stored,
                                                          sshagent_alist=sshagent_alist,
                                                          invoke_agent=invoke_agent,
                                                          restore_environ=restore_environ,
                                                          force_reconnect=force_reconnect, **kwds)

        return key_stored




    @classmethod
    def KeyInfo_AddToAgent(cls, keyinfo : SSHKeyInfo, 
                           socket_path      : str                  = None,
                           ssh_agent_client : paramiko.agent.Agent = None,
                           **kwds):
        return keyinfo.add_to_agent(socket_path=socket_path,
                                    ssh_agent_client=ssh_agent_client, **kwds)
