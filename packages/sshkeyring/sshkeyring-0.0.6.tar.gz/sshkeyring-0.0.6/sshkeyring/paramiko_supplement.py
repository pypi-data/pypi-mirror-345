#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import base64
import cryptography
import paramiko

#
# Add functions to paramiko.agent.AgentKey
#

def paramiko_agent_agentkey_get_openssh_pubkey(self, verbose=False):
    """
    Return the public key (string) with openssh compatible format
    """
    return ' '.join([self.get_name(), self.get_base64(), self.comment]).encode('utf-8')
setattr(paramiko.agent.AgentKey, 'get_openssh_pubkey', paramiko_agent_agentkey_get_openssh_pubkey)

def paramiko_agent_agentkey_dump(self, show_publickey=False, stream=sys.stdout):
    """
    Output (fingerprint) of the public key (string) with compatible format `ssh-add -l/-L`
    """
    if show_publickey:
        stream.write("%s %s %s\n" % (self.get_name(), self.get_base64(), self.comment))
    else:
        stream.write("%s %s %s (%s)\n" % (self.get_bits(), self.fingerprint, self.comment, self.get_name().split('-')[-1].upper()))
setattr(paramiko.agent.AgentKey, 'dump', paramiko_agent_agentkey_dump)

def paramiko_agent_agentkey_get_type(self):
    """
    Return the key type from agent_key.
    """
    return self.get_name().removeprefix("ssh-")
setattr(paramiko.agent.AgentKey, 'get_type', paramiko_agent_agentkey_get_type)

paramiko.agent.SSH_AGENT_FAILURE = 5
paramiko.agent.SSH_AGENT_SUCCESS = 6
paramiko.agent.cSSH2_AGENTC_ADD_IDENTITY = paramiko.common.byte_chr(17)

def paramiko_agent_agent_ssh_add_key(self, key : paramiko.pkey.PKey, key_comment: str=""):
    """
    Register the private key to ssh-agent
    """
    ptype, result = (None, None)
    if isinstance(key, paramiko.rsakey.RSAKey):
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.agent.cSSH2_AGENTC_ADD_IDENTITY)
        msg.add_string(key.get_name())
        msg.add_mpint(key.public_numbers.n)
        msg.add_mpint(key.public_numbers.e)
        msg.add_mpint(key.key.private_numbers().d)
        msg.add_mpint(key.key.private_numbers().iqmp)
        msg.add_mpint(key.key.private_numbers().p)
        msg.add_mpint(key.key.private_numbers().q)
        msg.add_string(key_comment)
        ptype, result = self._send_message(msg)
    elif isinstance(key, paramiko.ecdsakey.ECDSAKey):
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.agent.cSSH2_AGENTC_ADD_IDENTITY)
        # msg.add_bytes(key.asbytes())
        msg.add_string(key.ecdsa_curve.key_format_identifier)
        msg.add_string(key.ecdsa_curve.nist_name)
        msg.add_string(key.verifying_key.public_bytes(encoding=cryptography.hazmat.primitives.serialization.Encoding.X962,
                                                      format=cryptography.hazmat.primitives.serialization.PublicFormat.UncompressedPoint))
        msg.add_mpint(key.signing_key.private_numbers().private_value)
        msg.add_string(key_comment)
        ptype, result = self._send_message(msg)
    elif isinstance(key, paramiko.ed25519key.Ed25519Key):
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.agent.cSSH2_AGENTC_ADD_IDENTITY)
        msg.add_string(key.get_name())
        msg.add_string(key._signing_key.verify_key._key)
        msg.add_string(key._signing_key._seed+key._signing_key.verify_key._key)
        msg.add_string(key_comment)
        ptype, result = self._send_message(msg)
    elif isinstance(key, paramiko.dsskey.DSSKey):
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.agent.cSSH2_AGENTC_ADD_IDENTITY)
        msg.add_string(key.get_name())
        msg.add_mpint(key.p)
        msg.add_mpint(key.q)
        msg.add_mpint(key.g)
        msg.add_mpint(key.y)
        msg.add_mpint(key.x)
        msg.add_string(key_comment)
        ptype, result = self._send_message(msg)
    else:
        raise NotImplementedError("Unknown key type : "+str(key))
    return (ptype, result)
setattr(paramiko.agent.Agent, 'ssh_add_key', paramiko_agent_agent_ssh_add_key)

def paramiko_agent_agent_fetch_agent_keylist(self, verbose=False):
    """
    Fetch the list of the registered keys from ssh-agent
    """
    ptype, result = self._send_message(paramiko.agent.cSSH2_AGENTC_REQUEST_IDENTITIES)
    if ptype != paramiko.agent.SSH2_AGENT_IDENTITIES_ANSWER:
        raise SSHException("could not get keys from ssh-agent")
    keys = []
    for i in range(result.get_int()):
        keys.append(paramiko.agent.AgentKey(agent=self,
                                            blob=result.get_binary(),
                                            comment=result.get_text()))
    self._keys = tuple(keys)
setattr(paramiko.agent.Agent, 'fetch_agent_keylist', paramiko_agent_agent_fetch_agent_keylist)
