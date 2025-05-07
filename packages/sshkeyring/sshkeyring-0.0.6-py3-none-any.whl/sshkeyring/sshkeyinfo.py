#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

import getpass
import inspect
import base64

import cryptography
import cryptography.hazmat.primitives.asymmetric.types
import paramiko
import nacl

#import .paramiko_supplement

class SSHKeyInfo(object):
    """
    Structure to store the key information
    """
    PROPERTY_NAMES = ['key_id',
                      'key_type',
                      'agent_key',
                      'agent_sock',
                      'agent_client',
                      'local_key',
                      'path_private_key',
                      'path_public_key',
                      'public_blob',
                      'public_key',
                      'private_key',
                      'public_key_data',
                      'private_key_data',
                      'passphrase']

    def __init__(self, **kwds):
        self.info = { k: kwds.get(k, None) for k in self.__class__.PROPERTY_NAMES }

    def __repr__(self):
        return self.__class__.__name__+'('+', '.join([str(k)+"="+(("'%s'" % (v,)) if isinstance(v, str) else v.__repr__()) for k,v in self.info.items()])+')'

    def __str__(self):
        #return self.__class__.__name__+'('+', '.join([str(k)+"="+(("'%s'" % (v,)) if isinstance(v, str) else str(v)) for k,v in self.info.items()])+')'
        return self.__class__.__name__+'('+', '.join([str(k)+"="+(("'%s'" % (v,)) if isinstance(v, str) else v.__repr__()) for k,v in self.info.items()])+')'

    def load_public_key(self, **kwds):
        if isinstance(self.path_public_key,str) and self.path_public_key:
            try:
                fin = open(self.path_public_key, "rb")
                pblckey_data = fin.read()
                fin.close()
                self.public_key      = cryptography.hazmat.primitives.serialization.load_ssh_public_key(data=pblckey_data)
                self.public_key_data = pblckey_data
            except Exception as ex:
                sys.stderr.write("[%s.%s:%d] Error : public_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    sshkey_info.key_id, sshkey_info.key_type, sshkey_info.path_public_key))
    def load_public_blob(self, **kwds):
        if isinstance(self.path_public_key,str) and self.path_public_key:
            self.public_blob  = paramiko.pkey.PublicBlob.from_file(self.path_public_key)
         

    def load_private_key(self, passphrase=None, **kwds):
        if isinstance(self.path_private_key,str) and self.path_private_key:
            pssphrs = self.passphrase if passphrase is None else passphrase 
            try:
                fin = open(self.path_private_key, "rb")
                prvtkey_data = fin.read()
                fin.close()
                self.private_key = cryptography.hazmat.primitives.serialization.load_ssh_private_key(data=prvtkey_data,
                                                                                                     password=pssphrs.encode('utf-8'))
                self.private_key_data = prvtkey_data
                self.passphrase = pssphrs
            except:
                sys.stderr.write("[%s.%s:%d] Error : private_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    self.key_id, self.key_type, self.path_private_key))

    def load_local_key(self, passphrase=None, **kwds):
        if isinstance(self.path_private_key,str) and self.path_private_key:
            pssphrs = self.passphrase if passphrase is None else passphrase 
            try:
                self.local_key = paramiko.pkey.PKey.from_path(self.path_private_key, passphrase=pssphrs.encode('utf-8'))
                if ( isinstance(self.local_key, paramiko.ed25519key.Ed25519Key) and self.local_key._verifying_key is None ):
                    self.local_key._verifying_key = nacl.signing.VerifyKey(self.local_key._signing_key.verify_key.encode())
                if self.passphrase is None:
                    self.passphrase = pssphrs
            except:
                sys.stderr.write("[%s.%s:%d] Error : local_key can not be loaded ( key id: %s, type: %s : %s)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    self.key_id, self.key_type, self.path_private_key))


    def set_passphrase(self, passphrase:str=None, overwrite:bool=False, min_passphrase_length:int=8, **kwds):
        flg_verbose = kwds.get('verbose', False)
        if (not overwrite) and isinstance(self.passphrase,str) and len(self.passphrase)>=min_passphrase_length:
            if flg_verbose:
                sys.stderr.write("[%s.%s:%d] Info : passphrase is not overwritten  ( key id: %s, type: %s : length = %d > min: %d)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    self.key_id, self.key_type, len(self.passphrase), min_passphrase_length))
            return False
        elif isinstance(passphrase,str) and len(passphrase) >= min_passphrase_length:
            self.passphrase = passphrase
        else:
            self.passphrase = getpass.getpass(prompt=('[%s.%s:%d] private key passphrase: ')
                                              % (self.__class__.__name__, inspect.currentframe().f_code.co_name,
                                                 inspect.currentframe().f_lineno))
            if len(self.passphrase)<min_passphrase_length and flg_verbose:
                sys.stderr.write("[%s.%s:%d] Warning : entered passphrase length is less than minimium ( key id: %s, type: %s : length = %d > min: %d)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno,
                                    self.key_id, self.key_type, len(self.passphrase), min_passphrase_length))
        return True

    def dump(self, show_publickey=False, stream=sys.stdout, **kwds):
        """
        Output (fingerprint) of the public key (string) with compatible format `ssh-add -l/-L`
        """
        if isinstance(self.agent_key, paramiko.agent.AgentKey):
            self.agent_key.dump(show_publickey=show_publickey, stream=stream)
        else:
            if show_publickey:
                pblob_msg  = paramiko.message.Message(self.public_blob.key_blob)
                pblob_type = pblob_msg.get_string().decode('utf-8')
                pblob_data = pblob_msg.asbytes()
                stream.write("%s %s %s\n" % (pblob_type, base64.b64encode(pblob_data).decode('utf-8'),
                                             self.public_blob.comment))
            else:
                pass

        # if show_publickey:
        #     stream.write("%s %s %s\n" % (self.get_name(), self.get_base64(), self.comment))
        # else:
        #     stream.write("%s %s %s (%s)\n" % (self.get_bits(), self.fingerprint, self.comment, self.get_name().split('-')[-1].upper()))


    def add_to_agent(self, 
                     socket_path      : str                  = None,
                     ssh_agent_client : paramiko.agent.Agent = None,
                     **kwds):
        sock         = self.agent_sock   if self.agent_sock is not None                         else socket_path
        agent_client = self.agent_client if isinstance(self.agent_client, paramiko.agent.Agent) else ssh_agent_client

        if isinstance(agent_client, paramiko.agent.Agent):
            agent_client.ssh_add_key(key=self.local_key, key_comment=self.key_id)
            agent_client.close()
            sock_env_orig = os.environ['SSH_AUTH_SOCK']
            os.environ['SSH_AUTH_SOCK'] = sock
            agent_client.__init__()
            os.environ['SSH_AUTH_SOCK'] = sock_env_orig
            for k in agent_client.get_keys():

                if ( self.key_id != k.comment or self.key_type != k.get_type() ):
                    continue
                self.agent_key    = k
                self.agent_sock   = sock
                self.agent_client = agent_client
                return True
        return False


    def disconnect_agent(self, **kwds):
        if isinstance(self.agent_client, paramiko.agent.Agent):
            try:
                self.agent_client.close()
            except:
                pass    
            self.agent_client = None
            self.agent_key    = None
            self.agent_sock   = None

    def sign_ssh_data(self, data, algorithm:str=None, use_local_key:bool=False, **kwds):
        flg_verbose = kwds.get('verbose', False)
        if (not use_local_key) and isinstance(self.agent_key, paramiko.agent.AgentKey):
            return self.agent_key.sign_ssh_data(paramiko.util.asbytes(data), algorithm)
        if self.local_key is not None:
            msg = self.local_key.sign_ssh_data(paramiko.util.asbytes(data), algorithm)
            msg.rewind()
            return msg.asbytes()
        if flg_verbose:
            sys.stderr.write("[%s.%s:%d] Error : Neither agent_key nor local_key are available. (%s)\n"
                             % (self.__class__.__name__, inspect.currentframe().f_code.co_name, inspect.currentframe().f_lineno, str(self)))
        return None

    def sign_data(self, data, algorithm:str=None, use_local_key:bool=False, **kwds):
        msg = self.sign_ssh_data(data=data, algorithm=algorithm, use_local_key=use_local_key, **kwds)
        if msg is not None:
            return self.__class__.Decode_Signature_Message(msg)
        return None

    def verify_ssh_data(self, data, sig, use_local_key:bool=True, **kwds):
        if isinstance(sig, paramiko.message.Message):
            msg = sig
        else:
            msg = paramiko.message.Message()
            msg.add_bytes(paramiko.util.asbytes(sig))
        msg.rewind()

        if use_local_key:
            if self.local_key is not None:
                return self.local_key.verify_ssh_sig(paramiko.util.asbytes(data), msg)
            else:
                sys.stderr.write("[%s.%s:%d] Error : local_key is unavailable. (%s)\n"
                                 % (self.__class__.__name__, inspect.currentframe().f_code.co_name,
                                    inspect.currentframe().f_lineno, str(self)))
                return False

        if self.agent_key is not None:
            return self.agent_key.verify_ssh_sig(paramiko.util.asbytes(data), msg)
        sys.stderr.write("[%s.%s:%d] Error : agent_key is not unavailable. (%s)\n"
                         % (self.__class__.__name__, inspect.currentframe().f_code.co_name,
                            inspect.currentframe().f_lineno, str(self)))
        return False

    def verify_ssh_sig_by_keyfile(self, data, sig, **kwds):
        if isinstance(sig, paramiko.message.Message):
            msg = sig
        else:
            msg = paramiko.message.Message()
            msg.add_bytes(paramiko.util.asbytes(sig))
        msg.rewind()
        
        if self.local_key is not None:
            return self.local_key.verify_ssh_sig(paramiko.util.asbytes(data), msg)
        else:
            sys.stderr.write("[%s.%s:%d] Error : local_key is unavailable. (%s)\n"
                             % (self.__class__.__name__, inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno, str(self)))
        return False

    @classmethod 
    def Is_Same_KeyIndex(cls, obj_a, obj_b, **kwd):
        return (obj_a.key_id           == obj_b.key_id and
                obj_a.key_type         == obj_b.key_type )

    def is_same_keyindex(self, obj, **kwd):
        return self.__class__.Is_Same_KeyIndex(self, obj, **kwd)

    @classmethod 
    def Is_Same_Localfile(cls, obj_a, obj_b, **kwd):
        return (cls.Is_Same_KeyIndex(obj_a, obj_b, **kwd) and
                obj_a.path_private_key == obj_b.path_private_key and
                obj_a.path_public_key  == obj_b.path_public_key )

    def is_same_localfile(self, obj, **kwd):
        return self.__class__.Is_Same_Localfile(self, obj, **kwd)

    @classmethod
    def Decode_Signature_Message(cls, message, **kwds):
        if isinstance(message, paramiko.message.Message):
            msg = message
        else:
            msg = paramiko.message.Message()
            msg.add_bytes(paramiko.util.asbytes(message))

        msg.rewind()
        sig_algorithm = msg.get_text()
        if sig_algorithm[:7] == "ssh-rsa":
            signature     = msg.get_binary()
        elif sig_algorithm[:5] == "ecdsa":
            sig = paramiko.message.Message(msg.get_binary())
            sigR = sig.get_mpint()
            sigS = sig.get_mpint()
            signature = cryptography.hazmat.primitives.asymmetric.utils.encode_dss_signature(sigR, sigS)
        elif sig_algorithm[:11] == "ssh-ed25519":
            signature = msg.get_binary()
        elif sig_algorithm[:7] == "ssh-dss":
            sig = paramiko.message.Message(msg.get_binary())
            sigR = msg.get_mpint()
            sigS = msg.get_mpint()
            signature = cryptography.hazmat.primitives.asymmetric.utils.encode_dss_signature(sigR, sigS)
        else:
            sys.stderr.write("[%s.%s:%d] Error : Unknown KeyType(algorithm). (%s)\n"
                             % (self.__class__.__name__, inspect.currentframe().f_code.co_name, 
                                inspect.currentframe().f_lineno, str(sig_algorithm)))
            raise NotImplementedError("Unknown key type")
        return signature

    class __custumproperty__(property):
        def __init__(self, name:str, **kwds):
            self.name=name
            super().__init__(fget=self.get, fset=self.set)
        def get(self, cls):
            return getattr(cls, 'info').get(self.name)
        def set(self, cls, val):
            return getattr(cls, 'info').update({self.name: val})

for prop in SSHKeyInfo.PROPERTY_NAMES:
    setattr(SSHKeyInfo, prop, SSHKeyInfo.__custumproperty__(name=prop))
