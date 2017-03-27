# Create the VM

- Install a packaged [virtualbox][virtualbox] on your Linux, MacOS, or Windows server.

Go to the right directory and unpack this code:

```baah
cd
cd VirtualBox\ VMs
git clone https://github.com/thejohnhoffer/ubuntu_packer
```

## Running configure.py

The code block below makes an example Ubuntu VM sharing data from the __~/huge__ folder on our host machine.

### Option 1: forward ssh port

This machine will be accessible from anywhere with a custom password.

```bash
cd ubuntu_packer
python configure.py butterfly ~/huge -f 2424,22 -p mySecret1
```

|                      |            |                                |
|----------------------|------------|--------------------------------|
| host ssh port        | 2424       | Routes to guest ssh port (22)  |
| host ipv4 address    | N/A        | This example gives no ipv4     |
| virtual machine name | butterfly0 | Number added to `vm_name`      |
| username             | butterfly  | Defaults to `vm_name`          |
| password             | mySecret1  | The password is set by -p flag |

### Option 2: local ip address

This machine will be accessible from the host machine.

```bash
cd ubuntu_packer
python configure.py butterfly ~/huge -i 192.168.133.7
```

|                      |               |                            |
|----------------------|---------------|----------------------------|
| host ssh port        | N/A           | This example gives no port |
| host ipv4 address    | 192.168.133.7 | Must start with 192.168    |
| virtual machine name | butterfly0    | Number added to `vm_name`  |
| username             | butterfly     | Defaults to `vm_name`      |
| password             | butterfly     | Defaults to `vm_name`      |

## After running configure.py

Packer tells you it's _Downloading or copying ISO_, _Download progress: 100%_, _Executing custom VBoxManage commands..._, _Starting the virtual machine..._, _Waiting 10s for boot..._, and _Typing the boot command..._. It will only tell you it's __Waiting for SSH to become available__ for roughly ten minutes while packer installs Ubuntu in the new VM.

Once you see the final message, __Build 'virtualbox-iso' finished__,  connect to it with SSH.


- If you used `-f 2424,22` for port forwarding, use `ssh -p 2424 butterfly@localhost`
- If you used `-i 192.168.133.7` for a local ip, use `ssh butterfly@192.168.133.7`

Then enter the password which is given by `-p` or defaults to the username.

The first time on the new VM, mount the shared folder exactly like this.

```bash
sudo mount -t vboxsf data ~/data
```

In the new VM, `ls ~/data` shows the shared contents from the host machine path. 

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
  -f HOST,GUEST, --fwd HOST,GUEST
                        use once for each pair of host,guest ports
  -r RAM, --ram RAM     Total megabytes of RAM (1024)
  -c CORES, --cores CORES
                        Number of processor cores (1)
  -b BASH, --bash BASH  Path to bash script to run when made
  -i IP, --ip IP        Local IPV4 address, if any
  -p PASS, --pass PASS  password: overrides vm_name
  -u USER, --user USER  username: overrides vm_name
```

## Notes:

- Later, you can always reset the vm `VBoxManage controlvm $vm_name reset`

- Later, you can always power off the vm `VBoxManage controlvm $vm_name poweroff`

- If you need to start over, delete the vm `VBoxManage unregistervm $vm_name --delete`
    - And, delete the exported vm with `rm -rf ~/VirtualBox\ VMs/$(vm_name)_ovf`

Where `$vm_name` is the name of the VM including the number, ie `butterfly0`.

[virtualbox]: https://www.virtualbox.org/wiki/Downloads
