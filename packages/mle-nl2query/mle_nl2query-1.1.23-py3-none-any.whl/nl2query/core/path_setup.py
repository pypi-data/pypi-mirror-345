import os

file_path = __file__

work_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
data_dir = os.path.join(work_dir, "data")
input_dir = os.path.join(data_dir, "input")
