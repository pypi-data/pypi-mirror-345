sshkeyring
==========

Utilities to manage SSH key in key files and ssh-agent.

It can be used the query ssh key infomation from the local directory
and/or ssh-agent, and the sign the data by selected ssh-key, and etc.

Requirement
-----------

- cryptography
- paramiko
- PyNaCl
- setuptools
- pkgstruct : for the example script

Usage
-----

- class ``SSHKeyInfo`` : Structure to store the key information

- class ``SSHKeyUtil`` : Utilities functions to manage SSH keys with
  file I/O and/or ssh-agent

- class SSHKeyRing (inherited from SSHKeyUtil) : Utility for storing the
  information of the avaiable SSH Keys

Functionalities
---------------

- sshkeyring.paramiko_supplement: Add member functions to class
  ``paramiko.agent.AgentKey`` and class ``paramiko.agent.Agent``.

  - ``paramiko.agent.AgentKey.get_openssh_pubkey(verbose=False)`` :
    Return the public key (string) with openssh compatible format
  - ``paramiko.agent.AgentKey.dump(show_publickey=False, stream=sys.stdout)``
    : Output (fingerprint) of the public key (string) with compatible
    format by ``ssh-add -l/-L``
  - ``paramiko.agent.AgentKey.get_type()`` : Return the key
    type(``dsa``, ``ecdsa``, ``ed25519``, ``rsa``)
  - ``paramiko.agent.Agent.ssh_add_key(key : paramiko.pkey.PKey, key_comment: str="")``
    : Register the private key to ssh-agent
  - ``paramiko.agent.Agent.fetch_agent_keylist(verbose=False)`` : Fetch
    the list of the registered keys from ssh-agent

- sshkeyring.sshkeyutil: ``class SSHKeyInfo``

  - Key information properties

    ::

         - `key_id` : `str` : The name of the key
         - `key_type` : `str` :  Key type strings (`dsa`, `ecdsa`, `ed25519`, `rsa`)
         - `agent_client` : `paramiko.agent.Agent` object that connects to ssh-agent contains this key.
         - `agent_key` : `paramiko.agent.AgentKey` object that contains ssh-agent key information.
         - `agent_sock` : `str` : path of the socket file for the connection w/ ssh-agent.
         - `local_key` : `paramiko.pkey.PKey` : object that is constructed with local private key file
         - `public_blob` : `paramiko.pkey.PublicBlob` : public key contents constructed with local public key file
         - `path_private_key` : `str` : the path of the private key file. 
         - `path_public_key` : `str` : the path of the public key file. 
         - `private_key` : one of `cryptography.hazmat.primitives.asymmetric.types.PrivateKeyTypes` : private key object
         - `public_key` : one of `cryptography.hazmat.primitives.asymmetric.types.PublicKeyTypes`:  public key object
         - `private_key_data` : `str` : private key strings read from key file
         - `public_key_data` : `str` : public key strings read from key file
         - `passphrase` : `str` : buffer to store the pashphrase for the  encryption of the privete key file

Install
-------

::

   % pip install sshkeyring

Examples
--------

– see ``example/sshkeyscan.py``

::

   # ....

   import pkgstruct
   import sshkeyring
   # ....

   def main():

       pkg_info=pkgstruct.PkgStruct(script_path=sys.argv[0])
       pkg_keydir_prefix=pkg_info.concat_path('pkg_statedatadir', 'pki')

       
       ......
       # Key is identified with the tuple '(key_id(i.e. key_name), key_type('rsa', ...) )'


       argpsr = argparse.ArgumentParser(description='SSH key utilities')
       ......
       argpsr.add_argument('-t', '--key-type', choices=sshkeyring.SSHKeyUtil.KEY_TYPES, default=None, help='Specify Key Type')
       argpsr.add_argument('-i', '--key-id',   default=None,
                           help=('Specify key id: Default is %s' % ( sshkeyring.SSHKeyUtil.Default_Key_Id(),) ))
       argpsr.add_argument('-U', '--use-openssh-keys', default=None, action='store_true',
                           help=( 'Use openssh keys (in %s)' % (sshkeyring.SSHKeyUtil.SEEK_OPENSSH_KEYDIR_DEFAULT,)))
       argpsr.add_argument('-p', '--passphrase', type=str, default=None, help='SSH key passphrase (common)')
       ......
       argpsr.add_argument('data', nargs='*', type=str, default=None,  help='Date to sign')
       opts = argpsr.parse_args()


       # Determine (key_id, key_type): CLI options or default name and type
       use_key_id   = opts.key_id   if isinstance(opts.key_id,   str) and opts.key_id   else sshkeyring.SSHKeyRing.Default_Key_Id()
       use_key_type = opts.key_type if isinstance(opts.key_type, str) and opts.key_type else sshkeyring.SSHKeyUtil.KEY_TYPE_DEFAULT

       # Initialize the SSHKeyring object
       skyrng = sshkeyring.SSHKeyRing(keyfile_basename_default = opts.keyfile_basename,
                                      seek_openssh_keydir_default = opts.use_openssh_keys,
                                      passphrase = opts.passphrase)

       # Scan ssh-keys in the ssh-agent and the local directories
       skyrng.refresh_keyinfo(use_local_key=True, # Scan local ssh-key files
                              seek_openssh_dir=opts.use_openssh_keys,
                              decode_private_key=False,
                              passphrase=opts.passphrase,
                              invoke_agent=True, # if no ssh-agent is running, new ssh-agent process is invoked.
                              ) 

       # Show the list of ssh-keys
       skyrng.dump()
       # Shoe the list of ssh-keys like `ssh-add -l/-L`
       skyrng.dump_agent_keys(key_name=opts.key_id, show_publickey=False)
       skyrng.dump_agent_keys(key_name=opts.key_id, show_publickey=True)

       # Pickup the SSHKeyInfo object to use from the stored list
       # if the specified key is not in the stored list, None is returned.
       picked_keyinfo = skyrng.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)

       if picked_keyinfo is None and opts.create_keys:
           # New key will be generated and registered to ssh-agent.
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
            # Pickup the new SSHKeyInfo object from the stored list 
            picked_keyinfo = skyrng.pickup_keyinfo(key_id=opts.key_id, key_type=opts.key_type)


        # Register private key to ssh-agent when it is not regeiterd yet 
        if not opts.disuse_ssh_agent:
           if picked_keyinfo.agent_key is None:
               # Decode from the encrypted private key
               picked_keyinfo.set_passphrase(passphrase=opts.passphrase, overwrite=False, min_passphrase_length=8, verbose=opts.verbose)
               picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)
               # register to ssh-agent
               skyrng.ssh_add_keyinfo(picked_keyinfo, verbose=opts.verbose)

        #
        # sample for ssh-key use
        #
        for data_idx, raw_data in enumerate(opts.data):
           # decode from the encrypted private key if necessary
           if opts.disuse_ssh_agent or opts.verify_sign:
               picked_keyinfo.load_local_key(passphrase=opts.passphrase, verbose=opts.verbose)

           # Sign the data bu using the selected SSH private key 
           bytes_signed = picked_keyinfo.sign_ssh_data(data=raw_data, algorithm=opts.sign_algorithm, 
                                                       use_local_key=opts.disuse_ssh_agent, verbose=opts.verbose)
           # Base-64 encoded signature 
           b64data_signed = base64.b64encode(bytes_signed).decode('utf-8')

       
           # Verify the signature and data by using public key.
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

Author
------

::

   Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
