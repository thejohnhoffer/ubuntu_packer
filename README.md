# Create the VM

- Install a packaged [virtualbox][virtualbox] on your Linux, MacOS, or Windows server.

- Enter `cd & cd VirtualBox\ Vms` in your interactive shell.

- Clone this into that folder with `git clone https://github.com/thejohnhoffer/ubuntu_packer`

Now, make an Ubuntu VM called 'butterfly0' with data from the 'huge' folder in your home directory. When everything's done, you'll be able to 'ssh' into 'butterfly0' on port '2424'. The name of the VM always ends with a number to ensure uniqueness.

```bash
python ubuntu_packer/configure.py butterfly ~/huge -s 2424
```

After _Downloading or copying ISO_, _Download progress: 100%_, _Executing custom VBoxManage commands..._, _Starting the virtual machine..._, _Waiting 10s for boot..._, and _Typing the boot command..._, you will see __Waiting for SSH to become available__ for roughly ten minutes while packer installs Ubuntu in the new VM.

Once you see the final message, __Build 'virtualbox-iso' finished__, you can start up the machine and connect to it with SSH.

```bash
VBoxHeadless --startvm butterfly0 &
ssh -p 2424 butterfly@localhost
```

The username and password default to the first word passed to `configure.py`, in this case `butterfly`. You can configure a different username with the `-u` flag or the password with the `-p` flag. The complete list of parameters is given below. You can even pass a filename (within the `ubuntu_packer` directory) to use as list of bash commands to run right after the creation of the VM.

Once you're in the home directory of the virtual machine, you should be able to type `ls data` to view and edit the contents of the given path (here, we use `~/huge`) on your host machine. 

## All parameters:

```
usage: python configure.py [-h] [-o OS] [-s SSH] [-r RAM] [-c CORES] [-b BASH]
                           [-p PASS] [-u USER]
                           vm_name data_path

Makes a VM with a shared path and ssh

positional arguments:
  vm_name               name for vm, username, password
  data_path             Share data with vm from host path

optional arguments:
  -h, --help            show this help message and exit
  -o OS, --os OS        Ubuntu or Ubuntu_64 (Ubuntu_64)
  -s SSH, --ssh SSH     port >1024 for ssh server (2222)
  -r RAM, --ram RAM     Total megabytes of RAM (1024)
  -c CORES, --cores CORES
                        Number of processor cores (1)
  -b BASH, --bash BASH  Path to bash script to run when made
  -p PASS, --pass PASS  password: overrides vm_name
  -u USER, --user USER  username: overrides vm_name
```

## Notes:

- Later, you can always reset the vm `VBoxManage controlvm $vm_name reset`

- Later, you can always power off the vm `VBoxManage controlvm $vm_name poweroff`

- If you need to start over, delete the vm `VBoxManage unregistervm vm_name --delete`

Where `vm_name` is the name of the VM including the number, ie `butterfly0`.

[virtualbox]: https://www.virtualbox.org/wiki/Downloads
