# Create the VM

- Install a packaged [virtualbox][virtualbox] on your Linux, MacOS, or Windows server.

Go to the right directory and unpack this code:

```baah
cd
cd VirtualBox\ VMs
git clone https://github.com/thejohnhoffer/ubuntu_packer
```

## Running configure.py

In the code block below, we'll make an example Ubuntu VM called _butterfly0_ with data from the __~/huge__ folder on our host machine. When it's all done, we can _ssh_ into __butterfly0__ on port __2424__. Just replace _butterfly_ with the base name for your VM, and replace _~/huge_ with the path to the folder you want to share with your VM.

```bash
python ubuntu_packer/configure.py butterfly ~/huge -s 2424
```

Packer tells you it's _Downloading or copying ISO_, _Download progress: 100%_, _Executing custom VBoxManage commands..._, _Starting the virtual machine..._, _Waiting 10s for boot..._, and _Typing the boot command..._. It will only tell you it's __Waiting for SSH to become available__ for roughly ten minutes while packer installs Ubuntu in the new VM.

Once you see the final message, __Build 'virtualbox-iso' finished__, power up the machine and connect to it with SSH.

```bash
VBoxHeadless --startvm butterfly0 &
ssh -p 2424 butterfly@localhost
```

The username and password default to the first word passed to `configure.py`, in this case `butterfly`. You can configure a different username with the `-u` flag or the password with the `-p` flag. The complete list of parameters is given below. You _can even pass a filename_ with __a list of bash commands__ to _run right after_ the creation of the VM.

Once in the new VM, mount the shared folder once and for all
```bash
sudo mount -t vboxsf data ~/data
```

In the new VM, `ls ~/data` to view and edit the contents of the given path (here, we use `~/huge`) on your host machine. 

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
