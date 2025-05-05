import logging,os
from scilens.processors.models.results import ProcessorResults
from scilens.run.task_context import TaskContext
from scilens.config.models import ExecuteConfig
from scilens.components.executor import Executor
from scilens.components.compare_folders import CompareFolders
class ExecuteAndCompare:
	def __init__(A,context):B=context;A.context=B;A.compare_folders=CompareFolders(B)
	def process(D):
		L='error';J='dir';I='label';B='config';H=ProcessorResults();E=D.context.config.execute;F=D.context.config.execute_and_compare;M=os.path.join(D.context.working_dir,F.test.working_dir)if F.test.working_dir else D.compare_folders.test_base;N=os.path.join(D.context.working_dir,F.reference.working_dir)if F.reference.working_dir else D.compare_folders.ref_base;G=[{I:'test',J:M,B:F.test}]
		if not F.test_only:G.append({I:'reference',J:N,B:F.reference})
		for A in G:
			if not A[B]:C=E
			else:C=ExecuteConfig();C.pre_folder_delete=A[B].pre_folder_delete or E.pre_folder_delete;C.pre_folder_creation=A[B].pre_folder_creation or E.pre_folder_creation;C.exe_path=A[B].exe_path or E.exe_path;C.exe_url=A[B].exe_url or E.exe_url;C.exe_url_headers=A[B].exe_url_headers or E.exe_url_headers;C.exe_unzip_and_use=A[B].exe_unzip_and_use or E.exe_unzip_and_use;C.exe_guess_os_extension=A[B].exe_guess_os_extension or E.exe_guess_os_extension;C.command_suffix=A[B].command_suffix or E.command_suffix
			logging.info(f"Execute {A[I]} Command")
			with Executor(A[J],C,alternative_working_dir=D.context.origin_working_dir)as O:O.process()
		G=D.compare_folders.compute_list_filenames();logging.info(f"Number files to compare: {len(G)}");K=D.compare_folders.compute_comparison(G);H.warnings=[A[L]for A in K if A.get(L)];H.data=K;return H