import subprocess
import argparse
import inspect
import json
import sys
import os

def configure(argv,os_types):
    """Makes two config files, then makes a virtual machine.
    Args
    -------
    argv : list
	parsed as sys.argv by argparse
    """

    helps = {
	'configure': 'Makes a VM with a shared path and ssh',
	'data_path': 'Share data with vm from host path',
	'ssh': 'port >1024 for ssh server (2222)',
	'vm_name': 'name for vm, username, password',
        'user': 'username: overrides vm_name',
        'pass': 'password: overrides vm_name',
        'os': 'Ubuntu or Ubuntu_64 (Ubuntu_64)',
        'bash': 'Path to bash script to run when made',
        'cores': 'Number of processor cores (1)',
        'ram': 'Total megabytes of RAM (1024)',
    }

    parser = argparse.ArgumentParser(prog= 'python configure.py',
			description= helps['configure'])
    parser.add_argument('vm_name', help= helps['vm_name'])
    parser.add_argument('data_path', help= helps['data_path'])
    parser.add_argument('-o','--os', default='Ubuntu_64', help= helps['os'])
    parser.add_argument('-s','--ssh', default='2222', help= helps['ssh'])
    parser.add_argument('-r','--ram', default='1024', help= helps['ram'])
    parser.add_argument('-c','--cores', default='1', help= helps['cores'])
    parser.add_argument('-b','--bash', default='', help= helps['bash'])

    # Set the default name for user and password
    parser.add_argument('-p','--pass', help= helps['pass'])
    parser.add_argument('-u','--user',  help= helps['user'])

    # Actually parse the arguments 
    parsed = parser.parse_args(argv[1:])

    # Set pass and user defaults
    if getattr(parsed, 'pass') == None:
        setattr(parsed, 'pass', parsed.vm_name)
    if getattr(parsed, 'user') == None:
        setattr(parsed, 'user', parsed.vm_name)

    # Restrict the os type to Ubuntu or Ubuntu_64
    parsed.os = parsed.os if parsed.os in os_types else os_types[0]
    # Expand to the full path from relative or user paths
    def clean_path(path):
        if not path:
            return False
        relative = os.path.expanduser(path)
        return os.path.abspath(relative).replace(' ','\ ')
    # Clean the data and the command paths
    parsed.data_path = clean_path(parsed.data_path)
    parsed.bash = clean_path(parsed.bash)
    return vars(parsed)

if __name__ == "__main__":
    # Map os type arguments
    os_types = {
        'Ubuntu_64': {
            'host': 'releases.ubuntu.com/16.04.2',
            'iso': 'ubuntu-16.04.2-server-amd64.iso',
            'sum': '2bce60d18248df9980612619ff0b34e6',
        },
        'Ubuntu': {
            'host': 'releases.ubuntu.com/16.04.2',
            'iso': 'ubuntu-16.04.2-server-i386.iso',
            'sum': 'c32ba78bf6bdae6627b1e717d33eb7ae',
        },
    }
    count = 0
    vm_name = '.'

    # Get the parse command line arguments
    arg_dict = configure(sys.argv, os_types.keys())

    ####
    # Go to the parent path of this script
    ####
    stack_path = inspect.stack()[0][1]
    script_path = os.path.dirname(os.path.abspath(stack_path))
    parent_path = os.path.abspath(os.path.join(script_path, '..'))
    root_path = os.path.basename(script_path)
    # move to parent of this script
    os.chdir(parent_path)

    ####
    # dependent on os type
    ####
    os_type = os_types[arg_dict['os']]
    arg_dict['iso_host'] = os_type['host']
    arg_dict['iso_file'] = os_type['iso']
    arg_dict['iso_sum'] = os_type['sum']

    #### 
    # many backspaces
    ####
    arg_dict['del'] = '<bs>'*84

    ####
    # dependent on existing folders
    ####
    hostname = arg_dict['vm_name']
    # Increas the count while project exists
    while os.path.exists(vm_name):
       vm_name = '{}{:d}'.format(hostname, count)
       count += 1
    # Set the project files
    arg_dict['vm_name'] = vm_name
    arg_dict['ovf_name'] = os.path.join(vm_name,'ovf')

    ####
    # get all the path values needed for configuration 
    ####
    config_file = os.path.join(root_path, 'template.cfg')
    template_file = os.path.join(root_path, 'template.json')
    pack_file = os.path.join(root_path, hostname + '_pack.json')
    seed_file = os.path.join(root_path, hostname + '_seed.cfg')

    # Store the root path in template
    arg_dict['seed_cfg'] = seed_file

    # Format with the arguments
    def arg_format(placeholder):
        return placeholder.format(**arg_dict)

    # Append extra bash commands:
    def add_bash(d_template, bash_path):
        # Get all the commands run on creation
        all_bash = d_template['provisioners'][0]['inline']
        # Load bash file
        with open(bash_path, 'r') as f_bash:
            # Add bash file to all bash commands
            all_bash += f_bash.read().splitlines()

    ####
    # write a new json package from template
    ####

    # Read the template file
    with open(template_file, 'r') as f_template:
        # Create the new pack file
        with open(pack_file, 'w') as f_pack:
            # Load template as object
            d_template = json.load(f_template)
            # Load and format variables as string
            pre_var_str = json.dumps(d_template['variables'])
            new_var_str = arg_format(pre_var_str[1:-1])
            new_var_str = '{{{}}}'.format(new_var_str)
            ####
            # If extra bash commands given
            ####
            bash_path = arg_dict['bash']
            if bash_path and os.path.exists(bash_path):
                # Add the commands to the template
                add_bash(d_template, bash_path)
            # Store variables in new template
            new_vars = json.loads(new_var_str)
            d_template['variables'].update(new_vars)
            # Write new template to pack file
            json.dump(d_template, f_pack, indent=4)

    ####
    # write a new seed from template
    ####
    # Read the config file
    with open(config_file, 'r') as f_config:
        # Create the new seed file
        with open(seed_file, 'w') as f_seed:
            # Format the config file
            f_seed.write(f_config.read().format(**arg_dict))

    ####
    # Create the virutal environment
    ####
    # Get the packer shell command
    packer_sh = os.path.join(root_path, 'packer')
    command = '{} build {}'.format(packer_sh, pack_file)
    # Run the command in the current directory
    p = subprocess.Popen(command.split(), cwd= os.getcwd())
    p.wait()
