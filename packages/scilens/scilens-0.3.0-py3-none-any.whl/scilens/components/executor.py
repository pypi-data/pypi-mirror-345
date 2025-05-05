import logging,os,shutil,stat,subprocess,platform,tempfile,zipfile
from scilens.config.models import ExecuteConfig
from scilens.utils.file import dir_remove,dir_create
from scilens.utils.web import Web
def unzip_file(zip_file_path,extract_to_path):
	with zipfile.ZipFile(zip_file_path,'r')as A:A.extractall(extract_to_path)
def find_command(command_path,working_dirs,guess_os_extension=False):
	F='.bash';E='.sh';A=[]
	if guess_os_extension:
		B=platform.system().lower()
		if B=='windows':A=['.exe','.bat','.cmd']
		elif B=='linux':A=[E,F,'.bin']
		elif B=='darwin':A=[E,F]
		else:logging.warning(f"Unknown system {B}")
	for G in working_dirs:
		C=os.path.join(G,command_path)
		if os.path.exists(C):return C
		else:
			for H in A:
				D=C+H
				if os.path.exists(D):return D
class Executor:
	def __init__(A,absolute_working_dir,config,alternative_working_dir=None):
		B=config;A.working_dir=absolute_working_dir;A.config=B;A.alternative_working_dir=alternative_working_dir;A.command_path=None;A.temp_dir=None
		if B.exe_url and B.exe_path:raise ValueError('Executable URL and Path are defined. Only one can be defined.')
		if not B.exe_url and not B.exe_path:raise ValueError('Executable URL and Path are not defined. One must be defined.')
		if not os.path.exists(A.working_dir):logging.info(f"Creating working directory {A.working_dir}");dir_create(A.working_dir)
	def __enter__(A):return A
	def __exit__(A,exc_type,exc_value,traceback):A._cleanup()
	def _cleanup(A):0
	def _pre_operations(A):
		logging.info(f"Execute - Pre Operations");logging.info(f"Folders deletion")
		for dir in A.config.pre_folder_delete or[]:dir_remove(os.path.join(A.working_dir,dir))
		logging.info(f"Folders creation")
		for dir in A.config.pre_folder_creation or[]:dir_create(os.path.join(A.working_dir,dir))
		if A.config.exe_url:logging.info(f"Download executable {A.config.exe_url}");A.temp_dir=tempfile.mkdtemp();E='executable';B=os.path.join(A.temp_dir,E);Web().download_progress(A.config.exe_url,B,headers=A.config.exe_url_headers,callback100=lambda percentage:logging.info(f"Downloaded {percentage}%"));logging.info(f"Download completed")
		else:B=A.config.exe_path
		if A.config.exe_unzip_and_use:logging.info(f"Unzip archive");C=os.path.dirname(B);unzip_file(B,C);B=os.path.join(C,A.config.exe_unzip_and_use);print(f"executable_path {B}");logging.info(f"Unzip completed")
		if not os.path.exists(B):
			if not A.config.exe_guess_os_extension:raise FileNotFoundError(f"Command not found: {B}")
			else:
				logging.info(f"Guess OS extension");D=[A.working_dir]
				if A.alternative_working_dir:D.append(A.alternative_working_dir)
				B=find_command(B,D,guess_os_extension=True)
				if not B:raise FileNotFoundError(f"Command not found: {B}")
		logging.info(f"Add executable permissions");F=os.stat(B).st_mode;os.chmod(B,F|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH);A.command_path=B
	def _post_operations(A):logging.info(f"Execute - Post Operations")
	def _run_command(A):
		logging.info(f"Execute - Run Command");C=A.command_path;B=C
		if os.path.isabs(B):
			if not os.path.exists(B):raise FileNotFoundError(f"Command not found: {B}")
		else:
			D=[A.working_dir]
			if A.alternative_working_dir:D.append(A.alternative_working_dir)
			B=find_command(C,D,guess_os_extension=A.config.exe_guess_os_extension)
			if not B:raise FileNotFoundError(f"Command not found: {C}")
		E=f"{B}{A.config.command_suffix or''}";logging.info(f"RUN COMMAND {E} in {A.working_dir}");subprocess.run(E,shell=True,check=True,cwd=A.working_dir)
	def process(A):logging.info(f"Execute");A._pre_operations();A._run_command();A._post_operations();A._cleanup()