_B='netcdf'
_A='txt_fixed_cols'
from typing import Literal
from pydantic import BaseModel,Field,model_validator
from scilens.config.models.reader_format_txt import ReaderTxtConfig
from scilens.config.models.reader_format_csv import ReaderCsvConfig
from scilens.config.models.reader_format_txt_fixed_cols import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_netcdf import ReaderNetcdfConfig
TYPE_PARAMETERS_CLASS={'txt':ReaderTxtConfig,'csv':ReaderCsvConfig,_A:ReaderTxtFixedColsConfig,_B:ReaderNetcdfConfig}
class ReaderConfig(BaseModel):
	type:Literal['txt','csv',_A,_B]=Field(description='Type du reader. Les paramètres `parameters` dépendent de ce type.');parameters:ReaderTxtConfig|ReaderCsvConfig|ReaderTxtFixedColsConfig|ReaderNetcdfConfig=Field(description='Paramètres du reader')
	@model_validator(mode='after')
	def validate_model(cls,model):
		A=model
		if not isinstance(A.parameters,TYPE_PARAMETERS_CLASS[A.type]):raise ValueError(f"Reader Type {A.type} Parameters are not correct")
		return A
class ReadersConfig(BaseModel):txt:ReaderTxtConfig=Field(default=ReaderTxtConfig(),description='Configuration des readers txt.');csv:ReaderCsvConfig=Field(default=ReaderCsvConfig(),description='Configuration des readers csv.');txt_fixed_cols:ReaderTxtFixedColsConfig=Field(default=ReaderTxtFixedColsConfig(),description='Configuration des readers txt avec colonnes fixes.');netcdf:ReaderNetcdfConfig=Field(default=ReaderNetcdfConfig(),description='Configuration des readers NetCDF.');catalog:dict[str,ReaderConfig]|None=Field(default=None,description="Catalogue de configuration de readers par clé. Ex: `{'csv_comma': {'type': 'csv', 'parameters': {'delimiter': ','}}, 'csv_semicolon': {'type': 'csv', 'parameters': {'delimiter': ';'}}}`")