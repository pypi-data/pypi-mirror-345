import logging,os
from enum import Enum
from pydantic import BaseModel
from scilens.config.models import AppConfig
from scilens.run.models.task_results import TaskResults
from scilens.run.models.task_runtime import TaskRuntime
from scilens.run.task_context import TaskContext
from scilens.processors.models.results import ProcessorResults
from scilens.processors import Analyse,Compare,ExecuteAndCompare
from scilens.report.report import Report
from scilens.utils.system import info as system_info
from scilens.utils.time_tracker import TimeTracker
from scilens.utils.template import template_render_string
def var_render(value,runtime):return template_render_string(value,runtime.model_dump())
def runtime_process_vars(config):
	A=TaskRuntime(sys=system_info(),env=os.environ.copy(),vars={})
	for(B,C)in config.variables.items():A.vars[B]=var_render(C,A)
	return A
def runtime_apply_to_config(runtime,config_model):
	C=runtime;B=config_model
	for(D,J)in B.__class__.__pydantic_fields__.items():
		A=getattr(B,D);E=issubclass(A.__class__,BaseModel);F=isinstance(A.__class__,type)and issubclass(A.__class__,Enum);G=isinstance(A,str);H=isinstance(A,list)and all(isinstance(A,str)for A in A);I=isinstance(A,dict)and all(isinstance(A,str)and isinstance(B,str)for(A,B)in A.items())
		if E:runtime_apply_to_config(C,A)
		elif G and not F:setattr(B,D,var_render(A,C))
		elif H:setattr(B,D,[var_render(A,C)for A in A])
		elif I:setattr(B,D,{A:var_render(B,C)for(A,B)in A.items()})
class RunTask:
	def __init__(A,context):A.context=context
	def _get_processors(A):return{A.__name__:A for A in[Analyse,Compare,ExecuteAndCompare]}
	def process(A):
		logging.info(f"Running task");logging.info(f"Prepare runtime variables");H=runtime_process_vars(A.context.config);logging.info(f"Apply runtime variables to config");runtime_apply_to_config(H,A.context.config);logging.debug(f"on working_dir '{A.context.working_dir}'");logging.debug(f"with origin_working_dir '{A.context.origin_working_dir}'");logging.debug(f"with config {A.context.config.model_dump_json(indent=4)}");C=A.context.config.processor
		if not C:raise Exception('Processor not defined in config.')
		D=A._get_processors().get(C)
		if not D:raise Exception('Processor not found.')
		logging.info(f"Processor '{D.__name__}'")
		try:F=TimeTracker();G=D(A.context);E=G.process();F.stop();I=F.get_data()
		except Exception as B:logging.error(B);return TaskResults(error=str(B))
		finally:G=None
		try:J=Report(A.context.working_dir,[A.context.origin_working_dir],A.context.config.report,A.context.task_name).process({'meta':{'system_info':system_info(),'task_info':{'processor':C,'process_time':I}},'processor_results':E.data},C)
		except Exception as B:logging.error(B);return TaskResults(error=str(B),processor_results=E)
		return TaskResults(processor_results=E,report_results=J)