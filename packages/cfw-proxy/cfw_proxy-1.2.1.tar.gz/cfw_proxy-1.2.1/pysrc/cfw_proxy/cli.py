import argparse
import sys
import os

from . import logconfig

def load_config(args: argparse.Namespace):
    if args.load:
        import json
        with open(args.config_file, "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    return config

def save_config(config, path):
    import json
    with open(path, "w") as f:
        json.dump(config, f, indent=4)
    os.chmod(path, 0o600)

def serve_proxy(args: argparse.Namespace):
    # priority: args > load > default
    
    config = load_config(args)
    config.update({
        "ca_cert": os.path.realpath(args.ca_cert or config.get("ca_cert", "./ca.crt")),
        "ca_key": os.path.realpath(args.ca_key or config.get("ca_key", "./ca.key")),
        "cert_cachedir": os.path.realpath(args.cert_cachedir or config.get("cert_cachedir", "./cert_cache")),
        "port": args.port if args.port else config.get("port", 8843),
        "bind": args.bind or config.get("bind", "127.0.0.1"),
        "auth": args.auth or config.get("auth"),
        "url": args.url or config.get("url")
    })
    if args.save: save_config(config, args.config_file)
    
    if not config["auth"]:
        print("auth token is required")
        sys.exit(1)
    if not config["url"]:
        print("cloudflare worker url is required")
        sys.exit(1)
    
    from .cf_proxy import CloudflareProxy
    from .certmgr import CertCache
    from .http_conn import HTTPServer
    
    cert_cache = CertCache(config["cert_cachedir"], config["ca_cert"], config["ca_key"])
    server = HTTPServer(CloudflareProxy, listen=(config["bind"], config["port"]), hdl_extra={
        "cert_cache": cert_cache,
        "cf_auth": config["auth"],
        "cf_url": config["url"]
    })
    server.serve_forever()


def cert_action(args: argparse.Namespace):
    config = load_config(args)
    config.update({
        "ca_cert": os.path.realpath(args.ca_cert or config.get("ca_cert", "./ca.crt")),
        "ca_key": os.path.realpath(args.ca_key or config.get("ca_key", "./ca.key")),
        "cert_cachedir": os.path.realpath(args.cert_cachedir or config.get("cert_cachedir", "./cert_cache")),
    })
    if args.save: save_config(config, args.config_file)
    
    
    from .certmgr import create_ca
    
    cafile = config["ca_cert"]
    cakey = config["ca_key"]
    cache_dir = config["cert_cachedir"]
    
    if args.action == "make-ca":
        create_ca(keyfile=cakey, cafile=cafile)
    elif args.action == "revoke-ca":
        os.remove(cafile)
        os.remove(cakey)
    elif args.action == "clear-cache":
        import shutil
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            os.mkdir(cache_dir)
    
    

def cli():
    argparser = argparse.ArgumentParser("cfw-proxy")
    argparser.add_argument("--ca-key")
    argparser.add_argument("--ca-cert")
    argparser.add_argument("--cert-cachedir")
    argparser.add_argument("-v", "--verbose", action="store_true")
    argparser.add_argument("-s", "--save", action="store_true", help="save config to file")
    argparser.add_argument("--config-file", default="~/.cfw-config.json", help="config file location")
    argparser.add_argument("-l", "--load", action="store_true", help="load config from file")
    argparser.set_defaults(func=lambda _: argparser.print_help())
    
    sub_parser = argparser.add_subparsers(title="action", dest="action")
    serve_cmd = sub_parser.add_parser("serve")
    serve_cmd.add_argument("-p", "--port", type=int)
    serve_cmd.add_argument("-b", "--bind", help="bind address")
    serve_cmd.add_argument("-a", "--auth", help="auth token for cloudflare worker")
    serve_cmd.add_argument("--url", help="cloudflare worker url")
    serve_cmd.set_defaults(func=serve_proxy)
    
    cert_cmd = sub_parser.add_parser("cert")
    cert_act = cert_cmd.add_argument("action", choices=["make-ca", "revoke-ca", "clear-cache"])
    cert_cmd.set_defaults(func=cert_action)
    
    args = argparser.parse_args()
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    
    args.config_file = os.path.expanduser(args.config_file)
    
    args.func(args)


if __name__ == "__main__":
    cli()