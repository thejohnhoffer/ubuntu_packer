# Create the VM

- Install a packaged [virtualbox][virtualbox] on your Linux, MacOS, or Windows server.

- Enter `cd & cd VirtualBox\ Vms` in your interactive shell.

- Enter all the `code blocks` that follow.

Now, Download the Ubuntu iso and install it in a VM with packer:

```bash
ubuntu_packer/packer build ubuntu_packer/build.json
```

After _Downloading or copying ISO_, _Download progress: 100%_, _Executing custom VBoxManage commands..._, _Starting the virtual machine..._, _Waiting 10s for boot..._, and _Typing the boot command..._, you will see __Waiting for SSH to become available__ for roughly ten minutes while packer installs Ubuntu in the new VM. 


[virtualbox]: https://www.virtualbox.org/wiki/Downloads
