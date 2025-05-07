import logging,re
from scilens.readers.transform import string_2_float
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.cols_dataset import ColsDataset,ColsCurves,cols_dataset_get_curves_col_x,compare
from scilens.config.models import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_cols_curve import ReaderCurveParserNameConfig
from scilens.components.compare_floats import CompareFloats
class ReaderTxtFixedCols(ReaderInterface):
	configuration_type_code='txt_fixed_cols';category='datalines';extensions=[]
	def read(B,reader_options):
		A=reader_options;B.reader_options=A;J=open(B.origin.path,'r',encoding=B.encoding);K=A.column_widths;L=A.ignore_lines_patterns;E=len(K);C=ColsDataset(cols_count=E,names=[f"Column {A+1}"for A in range(E)],numeric_col_indexes=[A for A in range(E)],data=[[]for A in range(E)]);F=None;G=0
		for D in J:
			G+=1
			if L:
				M=False
				for P in L:
					if bool(re.match(P,D)):M=True;break
				if M:continue
			if A.has_header:
				if not F:
					F=D.strip();H=F
					if A.has_header_ignore:
						for Q in A.has_header_ignore:H=H.replace(Q,'')
					C.names=H.split();continue
				elif A.has_header_repetition and F==D.strip():continue
			if not D.strip():continue
			I=0;N=0
			for O in K:R=D[I:I+O].strip();S=string_2_float(R);C.data[N].append(S);I+=O;N+=1
			C.origin_line_nb.append(G)
		C.rows_count=len(C.origin_line_nb);J.close();B.cols_dataset=C;B.raw_lines_number=G;B.curves=None
		if A.curve_parser:
			if A.curve_parser.name==ReaderCurveParserNameConfig.COL_X:
				B.curves,T=cols_dataset_get_curves_col_x(C,A.curve_parser.parameters.x)
				if B.curves:B.cols_curve=ColsCurves(type=ReaderCurveParserNameConfig.COL_X,info=T,curves=B.curves)
			elif A.curve_parser.name==ReaderCurveParserNameConfig.COLS_COUPLE:raise NotImplementedError('cols_couple not implemented')
			else:raise Exception('Curve parser not supported.')
	def compare(A,compare_floats,param_reader,param_is_ref=True):D=param_is_ref;C=param_reader;B=compare_floats;E=A.cols_dataset if D else C.cols_dataset;F=A.cols_dataset if not D else C.cols_dataset;G=A.cols_curve;I,H=B.compare_errors.add_group('node','txt cols');return compare(H,B,E,F,G)
	def class_info(A):return{'cols':A.cols_dataset.names,'raw_lines_number':A.raw_lines_number,'curves':A.curves}