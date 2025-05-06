import os
from scilens.run.task_context import TaskContext
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.file_reader import FileReader
from scilens.components.compare_models import SEVERITY_ERROR
from scilens.components.compare_errors import CompareErrors
from scilens.components.compare_floats import CompareFloats
class Compare2Files:
	def __init__(A,context):A.context=context
	def compare(B,path_test,path_ref):
		R='comparison_errors';Q='comparison';N='reader';L='error';K='ref';J='test';F='path';A={J:{},K:{},Q:None,R:None};D={J:{F:path_test},K:{F:path_ref}}
		for(M,G)in D.items():
			if not G.get(F)or not os.path.exists(G[F]):A[L]=f"file {M} does not exist";return A
		S=FileReader(B.context.working_dir,B.context.config.file_reader,B.context.config.readers,config_alternate_path=B.context.origin_working_dir)
		for(M,G)in D.items():D[M][N]=S.read(G[F])
		C=D[J][N];H=D[K][N]
		if not C or not H:A['skipped']=True;return A
		A[J]=C.info();A[K]=H.info()
		if C.read_error:A[L]=C.read_error;return A
		I=CompareErrors(B.context.config.compare.errors_limit,B.context.config.compare.ignore_warnings);T=CompareFloats(I,B.context.config.compare.float_thresholds);C.compare(T,H,param_is_ref=True);E=I.root_group;O={'total_diffs':E.total_diffs}
		if E.info:O.update(E.info)
		A[Q]=O;A[R]=I.get_data()
		if E.error:A[L]=E.error;return A
		C.close();H.close();P=len(I.errors[SEVERITY_ERROR])
		if P>0:U=f"{P} comparison errors";A[L]=U
		return A