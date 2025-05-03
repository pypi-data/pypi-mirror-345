import os
import pandas as pd
import xgboost as xgb
from pathlib import Path

from ..utils.helpers import get_current_file_location


def is_model_available(iqi_name: str, src_res: int, dst_res: int):
	return os.path.exists(str(Path(str(get_current_file_location()), 'models/resolution_cast/', f'model_{iqi_name}_{src_res}p_{dst_res}p.xgb').resolve()))


def cast(iqi_vector: pd.Series, iqi_name: str, src_res: int, dst_res: int):
	if is_model_available(iqi_name, src_res, dst_res):
		model = xgb.XGBRegressor()
		model.load_model(str(Path(str(get_current_file_location()), 'models/resolution_cast/', f'model_{iqi_name}_{src_res}p_{dst_res}p.xgb').resolve()))
		y_pred = model.predict(iqi_vector)
		return y_pred
	else:
		return None
