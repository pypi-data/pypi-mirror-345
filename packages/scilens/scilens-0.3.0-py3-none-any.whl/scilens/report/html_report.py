import logging,os
from mimetypes import MimeTypes
from scilens.app import pkg_name,pkg_version,pkg_homepage,product_name,powered_by
from scilens.config.models import ReportConfig
from scilens.report.template import template_render_infolder
from scilens.report.assets import get_image_base64,get_image_base64_local,get_logo_image_src
from scilens.utils.time_tracker import TimeTracker
class HtmlReport:
	def __init__(A,config,alt_config_dirs,working_dir=None):A.config=config;A.alt_config_dirs=alt_config_dirs;A.working_dir=working_dir
	def process(A,processor,data,task_name):
		G='meta';F='date';logging.info(f"Processing html report");H=TimeTracker();C=H.get_data()['start']
		if A.config.logo and A.config.logo_file:raise ValueError('logo and logo_file are exclusive.')
		I=A.config.logo;B=None
		if A.config.logo_file:
			D=A.config.logo_file
			if os.path.isabs(D):B=D
			else:
				B=os.path.join(A.working_dir,D)
				if not os.path.isfile(B):
					for J in A.alt_config_dirs:
						B=os.path.join(J,D)
						if os.path.isfile(B):break
			if not os.path.isfile(B):raise FileNotFoundError(f"Derived Logo file '{A.config.logo_file}' not found.")
		K=A.config.title if A.config.title else A.config.title_prefix+' '+task_name;L={'app_name':product_name,'app_version':pkg_version,'app_homepage':pkg_homepage,'app_copyright':f"© {C[F][:4]} {powered_by['name']}. All rights reserved",'app_powered_by':powered_by,'execution_utc_datetime':C['datetime'],'execution_utc_date':C[F],'execution_utc_time':C['time'],'execution_dir':A.working_dir,'title':K,'image':I or get_logo_image_src(B),'config':A.config.html,'config_json':A.config.html.model_dump_json()};E=None
		if A.config.debug:E=A.config.model_dump_json(indent=4)
		return template_render_infolder('index.html',{G:L,'task':data.get(G),'data':{'files':data.get('processor_results')},'debug':E})