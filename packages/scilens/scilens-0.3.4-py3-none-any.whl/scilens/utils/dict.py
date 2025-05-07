from functools import reduce
def dict_path_set(obj,path,value):
	A=obj;B=path.split('.')
	for C in B[:-1]:A=A.setdefault(C,{})
	A[B[-1]]=value
def dict_path_get(obj,path):return reduce(dict.get,path.split('.'),obj)