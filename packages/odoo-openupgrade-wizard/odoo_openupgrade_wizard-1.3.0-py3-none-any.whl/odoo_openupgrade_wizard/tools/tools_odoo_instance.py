import socket
import time

import odoorpc
from loguru import logger

# Wait for the launch of odoo instance 60 seconds
_ODOO_RPC_MAX_TRY = 60
_ODOO_RPC_URL = "0.0.0.0"


class OdooInstance:
    env = False
    version = False

    def __init__(self, ctx, database, alternative_xml_rpc_port=False):
        port = (
            alternative_xml_rpc_port
            and alternative_xml_rpc_port
            or ctx.obj["config"]["odoo_host_xmlrpc_port"]
        )
        logger.info(
            f"Connect to database {database} via odoorpc (Port {port})..."
        )

        for x in range(1, _ODOO_RPC_MAX_TRY + 1):
            # Connection
            try:
                rpc_connexion = odoorpc.ODOO(
                    _ODOO_RPC_URL,
                    "jsonrpc",
                    port=port,
                    timeout=ctx.obj["config"]["odoo_rpc_timeout"],
                )
                # connexion is OK
                break
            except (socket.gaierror, socket.error) as e:
                if x < _ODOO_RPC_MAX_TRY:
                    logger.debug(
                        f"{x}/{_ODOO_RPC_MAX_TRY}"
                        " Unable to connect to the server."
                        " Retrying in 1 second ..."
                    )
                    time.sleep(1)
                else:
                    logger.critical(
                        f"{x}/{_ODOO_RPC_MAX_TRY}"
                        " Unable to connect to the server."
                    )
                    raise e
        # Login
        try:
            rpc_connexion.login(database, "admin", "admin")
        except Exception as e:
            logger.error(
                f"Unable to connect to http://localhost:{port}"
                " with login 'admin' and password 'admin."
            )
            raise e

        self.env = rpc_connexion.env
        self.version = rpc_connexion.version

    def browse_by_search(
        self, model_name, domain=False, order=False, limit=False
    ):
        domain = domain or []
        model = self.env[model_name]
        return model.browse(model.search(domain, order=order, limit=limit))

    def browse_by_create(self, model_name, vals):
        model = self.env[model_name]
        return model.browse(model.create(vals))

    def install_modules(self, module_names):
        if type(module_names) is str:
            module_names = [module_names]
        installed_modules = []
        i = 0
        for module_name in module_names:
            i += 1
            log_prefix = f"{i}/{len(module_names)} - Module '{module_name}': "
            modules = self.browse_by_search(
                "ir.module.module", [("name", "=", module_name)]
            )
            if not len(modules):
                logger.error(f"{log_prefix}': Not found.")
                continue

            module = modules[0]
            if module.state == "installed":
                logger.info(f"{log_prefix}': still installed. Skipped.")
            elif module.state == "uninstalled":
                try_qty = 0
                installed = False
                while installed is False:
                    try_qty += 1
                    try_qty_text = f" (try #{try_qty})" if try_qty != 1 else ""
                    logger.info(f"{log_prefix}': Installing ...{try_qty_text}")
                    try:
                        module.button_immediate_install()
                        installed = True
                        installed_modules.append(module_name)
                        time.sleep(5)
                    except Exception as e:
                        if try_qty <= 5:
                            sleeping_time = 2 * try_qty * 60
                            logger.warning(
                                f"Error. Retrying in {sleeping_time} seconds."
                                f"\n{e}"
                            )
                            time.sleep(sleeping_time)
                        else:
                            logger.critical(
                                f"Error after {try_qty} try. Exiting." f"\n{e}"
                            )
                            raise e
            else:
                logger.error(
                    f"{log_prefix}': In the {module.state} state."
                    " (Unable to install)"
                )
        return installed_modules
