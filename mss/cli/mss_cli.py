from client import Client, ConnectionError
import argparse
import logging
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(h)


def wait_async_step(mytype, module="agent"):
    """ Poll every second if 'mytype' thread is finished """
    while True:
        a = client.call('get_state', mytype, module)
        print(type(a))
        code, output = a
        if code == 2000:
            pass
        else:
            break
        time.sleep(1)


def module(args):
    def exec_install_modules(modules):
        if modules is None:
            print('Enter some modules to install.')
            return
        for mod in modules:
            logger.debug(mod)
            slug = mod.split(',')[0]
            cfg = mod.split(',')[1:]
            client.install_module(slug, sync=True)
            # Configure module
            config = {}
            for i in cfg:
                ik, iv = i.split('=', 1)
                config.update({slug + '_' + ik: iv})
            client.configure_module(slug, config)

    if client.authenticate(args.login, args.password):
        logger.debug("Authentication successful")
        if args.list:
            mods = []
            for mod in client.call('get_modules'):
                mods.append((mod['slug'],
                             mod['installed'],
                             mod['configured']))

            for mod in sorted(mods, key=lambda t: t[0]):
                print('%12s\t is installed: %5s, is configured: %s'
                      % (mod[0],
                         mod[1],
                         mod[2]))
            return
        if args.detail:
            print(args.detail)
            for mod in args.detail:
                detail = client.call('get_module_details', mod)
                print('%s:' % mod)
                for key in detail:
                    print('  %20s: %s' % (key, detail[key]))
            return
        if args.config:
            details = client.call('get_config', args.config)
            for d in details:
                print('Configuration for module %s:' % d['slug'])
                count = 0
                for conf in d['config']:
                    del conf['slug']
                    if 'type' in conf and conf['type'] == 'subtitle':
                        continue
                    count += 1
                    print('  Param %s:' % count)
                    for k in ['name', 'type', 'default', 'label', 'help']:
                        if k in conf:
                            print('    %10s: %s' % (k, conf[k]))
                            del conf[k]
                    if len(conf) > 0:
                        print('    %s' % conf)
            return
        if args.modules:
            print args.modules
            exec_install_modules(args.modules)
    else:
        logger.debug("Authentication failed")
        raise ConnectionError()


def status(args):
    print client.call('get_state', args.process)


def get_option(args):
    print client.call('get_option', args.option)
#################### ARGUMENTS PARSING ####################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='mss_cli')
    subparsers = parser.add_subparsers(help='command help')

    parser.add_argument('--port',
                        '-p',
                        type=int,
                        default=8001,
                        help='agent port')
    parser.add_argument('--host',
                        '-H',
                        type=str,
                        default='127.0.0.1',
                        help='agent url')
    parser.add_argument('--password',
                        '-P',
                        dest='password',
                        type=str,
                        help='agent password')
    parser.add_argument('--login',
                        '-l',
                        dest='login',
                        type=str,
                        default='root',
                        help='agent login')
    parser.add_argument('--debug',
                        '-d',
                        default=False,
                        action='store_true',
                        dest='debug',
                        help="Set verbosity to debug")

    parser_module = subparsers.add_parser('module', help='module commands')
    parser_module.add_argument('--list',
                               '-l',
                               action='store_true',
                               help='list available modules')
    parser_module.add_argument('--detail',
                               '-d',
                               nargs="*",
                               dest='detail',
                               help='print details for module list')
    parser_module.add_argument('--config-info',
                               '-c',
                               nargs="*",
                               dest='config',
                               help='print config details for module list')

    parser_module.add_argument('--install',
                               '-i',
                               nargs="*",
                               dest='modules',
                               help="List of modules to install <slug1>,<name1=value2>,<name2=value2> <slug2>,<name=value1>...");
    parser_module.set_defaults(func=module)

    parser_status = subparsers.add_parser('status', help='test commands')
    parser_status.add_argument('process',
                               choices=["load",
                                        "install",
                                        "update",
                                        "media",
                                        "config",
                                        "net",
                                        "reboot"])
    parser_status.set_defaults(func=status)

    parser_option = subparsers.add_parser('get_option', help='test commands')
    parser_option.add_argument('option',
                               choices=["first-time"])
    parser_option.set_defaults(func=get_option)

    # Parse arguments
    arguments = parser.parse_args()

    # Declare a MSS client
    client = Client(host=arguments.host, port=arguments.port)
    if arguments.debug:
        logger.setLevel(logging.DEBUG)
        client.debug()

    arguments.func(arguments)
