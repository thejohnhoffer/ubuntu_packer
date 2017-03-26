import subprocess
import argparse
import inspect
import json
import sys
import os

def configure(argv,os_types):
    """Set environment variables with defaults.
    Args
    -------
    argv : list
	parsed as sys.argv by argparse
    """

    helps = {
	'configure': 'Set environment variables',
	'data_path': 'Share data with vm from host path',
	'ssh': 'port >1024 for ssh server (2222)',
	'vm_name': 'name for vm, username, password (vm)',
        'user': 'username: overrides the name (vm)',
        'pass': 'password: overrides the name (vm)',
        'os': 'Ubuntu or Ubuntu_64 (Ubuntu_64)',
        'cores': 'Number of processor cores (1)',
        'ram': 'Total megabytes of RAM (1024)',
    }

    parser = argparse.ArgumentParser(prog= 'python configure.py',
			description= helps['configure'])
    parser.add_argument('vm_name', help= helps['vm_name'])
    parser.add_argument('data_path', help= helps['data_path'])
    parser.add_argument('-s','--ssh', default='2222', help= helps['ssh'])
    parser.add_argument('-r','--ram', default='1024', help= helps['ram'])
    parser.add_argument('-c','--cores', default='1', help= helps['cores'])
    parser.add_argument('-o','--os', default='Ubuntu_64', help= helps['os'])

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
    parsed.data_path = os.path.expanduser(parsed.data_path)
    parsed.data_apth = parsed.data_path.replace(' ','\ ')
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
    # dependent on existing folders
    ####
    hostname = arg_dict['vm_name']
    # Increas the count while project exists
    while os.path.exists(vm_name):
       vm_name = '{}{:d}'.format(hostname, count)
       count += 1
    # Set the project file
    arg_dict['vm_name'] = vm_name

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
    # Go to the parent path of this script
    ####
    script_path = os.path.dirname(inspect.stack()[0][1])
    parent_path = os.path.abspath(os.path.join(script_path, '..'))
    root_path = os.path.basename(script_path)
    # move to parent of this script
    os.chdir(parent_path)
    ####
    # get all the path values needed for configuration 
    ####
    config_file = os.path.join(root_path, 'template.cfg')
    template_file = os.path.join(root_path, 'template.json')
    pack_file = os.path.join(root_path, hostname + '_pack.json')
    seed_file = os.path.join(root_path, hostname + '_seed.cfg')
    ####
    # write a new json package from template
    ####
    # Store the root path in template
    arg_dict['seed_cfg'] = seed_file
    print parent_path
    # Read the template file
    with open(template_file, 'r') as f_template:
        # Create the new pack file
        with open(pack_file, 'w') as f_pack:
            # Load template as object
            d_template = json.load(f_template)
            # Load and format variables as string
            pre_var_str = json.dumps(d_template['variables'])
            new_var_str = pre_var_str[1:-1].format(**arg_dict)
            new_var_str = '{{{}}}'.format(new_var_str)
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
