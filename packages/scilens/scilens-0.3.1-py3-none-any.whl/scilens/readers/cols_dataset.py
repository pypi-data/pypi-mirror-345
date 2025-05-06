_E='charts'
_D='x_index'
_C='csv_col_index'
_B='curves'
_A=None
import logging
from dataclasses import dataclass,field
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
from scilens.config.models.reader_format_cols_curve import ReaderCurveParserNameConfig
@dataclass
class ColsDataset:cols_count:int=0;rows_count:int=0;names:list[str]=field(default_factory=lambda:[]);numeric_col_indexes:list[int]=field(default_factory=lambda:[]);data:list[list[float]]=field(default_factory=lambda:[]);origin_line_nb:list[int]=field(default_factory=lambda:[])
@dataclass
class ColsCurves:type:str;info:dict;curves:dict
def cols_dataset_get_curves_col_x(cols_dataset,col_x):
	I='title';B=col_x;A=cols_dataset;E={}
	if isinstance(B,int):
		C=B-1
		if C<0 or C>=A.cols_count:raise Exception('curve parser col_x: col_index is out of range.')
	if isinstance(B,str):B=[B]
	if isinstance(B,list):
		G=[A for(A,C)in enumerate(A.names)if C in B]
		if len(G)==0:return _A,E
		C=G[0]
	E[_D]=C;J=[B for(A,B)in enumerate(A.numeric_col_indexes)if A!=C];F=[];H=[]
	for D in J:B=A.data[C];K=A.data[D];L={I:A.names[D],'short_title':A.names[D],'series':[[B[A],K[A]]for A in range(A.rows_count)],_C:D};F+=[L];M={I:A.names[D],'type':'simple','xaxis':A.names[C],'yaxis':A.names[D],_B:[len(F)-1]};H+=[M]
	return{_B:F,_E:H},E
def compare(group,compare_floats,reader_test,reader_ref,cols_curve):
	L=compare_floats;K='Errors limit reached';G=reader_ref;E=group;C=cols_curve;A=reader_test;logging.debug(f"compare cols: {E.name}")
	if len(A.numeric_col_indexes)!=len(G.numeric_col_indexes):E.error=f"Number Float columns indexes are different: {len(A.numeric_col_indexes)} != {len(G.numeric_col_indexes)}";return
	D=[''for A in range(A.cols_count)];M=_A;H=_A
	if C and C.type==ReaderCurveParserNameConfig.COL_X:N=C.info[_D];M=A.data[N];H=A.names[N]
	I=False
	for B in range(A.cols_count):
		if B not in A.numeric_col_indexes:continue
		if I:D[B]=K;continue
		Q=A.data[B];R=G.data[B];U,F=L.compare_errors.add_group('vectors',A.names[B],parent=E,data={'info_prefix':H}if H else _A);logging.debug(f"compare cols: {F.name}");S,V=L.compare_vectors(Q,R,group_id=F.id,info_vector=M)
		if S:I=True;D[B]=K;continue
		if F.total_errors>0:D[B]=f"{F.total_errors} comparison errors"
	if C:
		for O in C.curves[_E]:
			P=0
			for T in O[_B]:
				J=C.curves[_B][T]
				if D[J[_C]]:J['comparison_error']=D[J[_C]];P+=1
			O['comparison']={'curves_nb_with_error':P}
	E.error=K if I else _A;E.info={'cols_has_error':D}