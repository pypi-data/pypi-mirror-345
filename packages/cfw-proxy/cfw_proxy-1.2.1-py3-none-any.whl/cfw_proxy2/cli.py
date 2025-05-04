import argparse
import sys
import os
from loguru import logger
import json

def load_config(args: argparse.Namespace):
    if args.load:
        with open(args.config_file, "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    return config

def save_config(config, path):
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
        "cfw_host": args.cfw_host or config.get("cfw_host"),
        "timeout": args.timeout or config.get("timeout", 10),
        "client_idle_timeout": args.client_idle_timeout or config.get("client_idle_timeout", 60),
        "worker_count": args.worker_count or config.get("worker_count", 10),
        "cfw_pool_size": args.cfw_pool_size or config.get("cfw_pool_size", 20),
    })
    if args.save: 
        save_config(config, args.config_file)

    if not config["auth"]:
        logger.error("auth token is required")
        sys.exit(1)

    if not config["cfw_host"]:
        logger.error("cloudflare worker hostname (--cfw-host) is required")
        sys.exit(1)

    from .cfw_proxy import CFWProxyServer, CFWProxyConfig

    try:
        config = CFWProxyConfig(
            listen_addr=(config["bind"], config["port"]),
            timeout=config["timeout"],
            client_idle_timeout=config["client_idle_timeout"],
            cfw_pool_size=config["cfw_pool_size"],
            worker_count=config["worker_count"],
            ca_cert=config["ca_cert"],
            ca_key=config["ca_key"],
            cert_cachedir=config["cert_cachedir"],
            cfw_host=config["cfw_host"],
            cfw_key=config["auth"],
        )
    except Exception as e:
        logger.error(f"Failed to create CFWProxyConfig: {e}")
        sys.exit(1)

    logger.debug(f"Config: {config.model_dump_json(indent=2)}")

    server = CFWProxyServer(config)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


def cert_action(args: argparse.Namespace):
    config = load_config(args)
    config.update({
        "ca_cert": os.path.realpath(args.ca_cert or config.get("ca_cert", "./ca.crt")),
        "ca_key": os.path.realpath(args.ca_key or config.get("ca_key", "./ca.key")),
        "cert_cachedir": os.path.realpath(args.cert_cachedir or config.get("cert_cachedir", "./cert_cache")),
    })
    if args.save: 
        save_config(config, args.config_file)

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


def main():
    import importlib.metadata
    version = importlib.metadata.version("cfw-proxy")

    argparser = argparse.ArgumentParser("cfw-proxy")
    argparser.add_argument("--version", action="version", version=f"%(prog)s {version}")
    argparser.add_argument("--ca-key")
    argparser.add_argument("--ca-cert")
    argparser.add_argument("--cert-cachedir")
    argparser.add_argument("-v", "--verbose", action="store_true")
    argparser.add_argument("-vv", "--trace", action="store_true", help="enable trace logging")
    argparser.add_argument("-s", "--save", action="store_true", help="save config to file")
    argparser.add_argument("--config-file", default="~/.cfw-config.json", help="config file location")
    argparser.add_argument("-l", "--load", action="store_true", help="load config from file")
    argparser.set_defaults(func=lambda _: argparser.print_help())

    sub_parser = argparser.add_subparsers(title="action", dest="action")
    serve_cmd = sub_parser.add_parser("serve")
    serve_cmd.add_argument("-p", "--port", type=int)
    serve_cmd.add_argument("-b", "--bind", help="bind address")
    serve_cmd.add_argument("-a", "--auth", help="auth token for cloudflare worker")
    serve_cmd.add_argument("--cfw-host", help="cloudflare worker hostname")
    serve_cmd.add_argument("--timeout", type=float, help="general timeout")
    serve_cmd.add_argument("--client-idle-timeout", type=float, help="close idle client connection after this time")
    serve_cmd.add_argument("--worker-count", type=int, default=10, help="number of worker threads to serve the clients")
    serve_cmd.add_argument("--cfw-pool-size", type=int, default=20, help="number of maximum connections to cloudflare worker")
    serve_cmd.set_defaults(func=serve_proxy)

    cert_cmd = sub_parser.add_parser("cert")
    cert_act = cert_cmd.add_argument("action", choices=["make-ca", "revoke-ca", "clear-cache"])  # noqa: F841
    cert_cmd.set_defaults(func=cert_action)

    args = argparser.parse_args()

    brief_log_fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " + 
        "<lvl><b>{level: <7}</b></lvl> | " +
        "{thread.name}({thread.id}) <lvl><n>{message}</n></lvl>"
    )
    full_log_fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " + 
        "<lvl><b>{level: <7}</b></lvl> | " +
        "<lvl><n>{module}:{function}:{line}</n></lvl> | " +
        "<lvl><n>{thread.name}({thread.id}) {message}</n></lvl>"
    )
    if args.trace:
        logger.remove()
        logger.add(
            sys.stderr, level="TRACE", enqueue=True,
            format=full_log_fmt
        )
    elif args.verbose:
        logger.remove()
        logger.add(
            sys.stderr, level="DEBUG", enqueue=True,
            format=brief_log_fmt
        )
    else:
        logger.remove()
        logger.add(
            sys.stderr, level="INFO", enqueue=True,
            format=brief_log_fmt,
        )
    logger.level("INFO", color="<blue>")
    logger.level("DEBUG", color="<fg 255>")
    logger.level("TRACE", color="<fg 128>")
    
    args.config_file = os.path.expanduser(args.config_file)
    args.func(args)