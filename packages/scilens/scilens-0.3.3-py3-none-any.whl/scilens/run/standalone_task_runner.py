import logging
from scilens.config.load import config_load
from scilens.run.task_context import TaskContext
from scilens.run.run_task import RunTask
from scilens.config.models import AppConfig
class StandaloneTaskRunner:
	config_path=None
	def __init__(A,config):A.config=config_load(config)
	def process(A,working_dir,origin_working_dir=None):B=TaskContext(config=A.config,config_file=A.config_path,working_dir=working_dir,origin_working_dir=origin_working_dir);C=RunTask(B);D=C.process();return D