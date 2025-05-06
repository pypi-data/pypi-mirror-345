_B=False
_A=None
from dataclasses import asdict
from.compare_models import SEVERITY_ERROR,SEVERITY_WARNING,COMPARE_GROUP_TYPE,CompareGroup,CompareFloatsErr,CompareErr,Compare2ValuesResults
class CompareErrors:
	def __init__(A,nb_max,ignore_warnings=_B):A.nb_max=nb_max;A.ignore_warnings=ignore_warnings;A.errors={SEVERITY_ERROR:[],SEVERITY_WARNING:[]};A.count=0;A.limit_reached=_B;A.root_group=_A;A.messages=[];A._messages_map={};A.groups=[]
	def add_group(A,type,name,parent=_A,data=_A):
		B=parent
		if not A.root_group and B:raise Exception('No root group defined')
		id=len(A.groups);C=CompareGroup(id=id,type=type,name=name,parent=B,data=data)
		if not B:A.root_group=C
		A.groups.append(C);return id,C
	def add(A,group,comp_res,info=_A):
		F=group;C=comp_res;D=C.severity;E=C.message;G=C.comp_err
		if A.ignore_warnings and D==SEVERITY_WARNING:return _B
		A.count+=1;B=A._messages_map.get(E)
		if B is _A:B=len(A.messages);A.messages.append(E);A._messages_map[E]=B
		A.errors[D].append(CompareErr(err=G,msg=B,group=F.id,info=info));F.incr(D)
		if A.count>=A.nb_max:A.limit_reached=True;return True
	def get_data(B):
		D=[{'id':A.id,'type':A.type,'name':A.name,'error':A.error,'total_diffs':A.total_diffs,'total_warnings':A.total_warnings,'total_errors':A.total_errors,'data':A.data,'info':A.info,'parent_id':A.parent.id if A.parent else _A}for A in B.groups];A={'messages':B.messages,'groups':D}
		for(C,E)in B.errors.items():A[C]=[A.model_dump()for A in E];A[C+'_nb']=len(A[C])
		return A