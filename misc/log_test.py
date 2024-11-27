import os
import logging
from datetime import datetime


def init_logger(log_dir,log_name,time_per_line=False):
     #Init Logger
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        print(e.message)
        return None

    try:
        LOG=os.environ.get('LOG')
    except:
        LOG=1

    if LOG is None or LOG==1:
        level=logging.INFO
    else:
        level=logging.WARNING

    today = datetime.today().strftime("%Y%m%d")
   
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module_name)s - %(message)s")
    console_formatter = logging.Formatter("%(asctime)s - %(module_name)s - %(message)s")

    
    fh = logging.FileHandler(filename=f"{log_dir}/{log_name}.log",mode='w')
    fh.setFormatter(log_formatter)
    fh.setLevel(level)

    logger.addHandler(fh)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(console_formatter)
    consoleHandler.setLevel(level)
    logger.addHandler(consoleHandler)
    return logger

logger=init_logger("logs_ast_app",f"logs_ast_app")