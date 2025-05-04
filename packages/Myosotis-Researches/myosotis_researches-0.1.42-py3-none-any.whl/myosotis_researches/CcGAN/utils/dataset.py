import base64
from flask import Flask, send_file
import gdown
import getpass
import h5py
import h5py
import humanize
from importlib import resources
from io import BytesIO
from jinja2 import Template
import numpy as np
import os
from PIL import Image
import subprocess
import time


# view_dataset
def _print_hdf5(name, obj):
    indent = "  " * name.count("/")
    if isinstance(obj, h5py.Dataset):
        print(f"{indent}[Dataset] {name} shape={obj.shape} dtype={obj.dtype}")
    elif isinstance(obj, h5py.Group):
        print(f"{indent}[Group]   {name}")


def view_dataset(dataset_path):
    with h5py.File(dataset_path, "r") as f:
        f.visititems(_print_hdf5)


# visualize_dataset
def _nparray_to_Base64(nparray):
    nparray = np.transpose(nparray, (1, 2, 0))
    image = Image.fromarray(nparray)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


def visualize_dataset(dataset_path, indexes):
    keys = []
    _data = {}
    with h5py.File(dataset_path, "r") as f:
        for key in f.keys():
            keys.append(key)
            _data[key] = f[key][:]
            if _data[key].dtype.kind == "O":
                _data[key] = _data[key].astype("str")
    keys.append("original_indexes")
    N = len(_data["images"])
    data = []
    for i in indexes:
        item = {}
        for key in keys:
            if key == "images":
                item[key] = _nparray_to_Base64(_data[key][i])
            elif key in ["index_train", "index_valid"]:
                continue
            elif key == "original_indexes":
                item[key] = i
            else:
                item[key] = _data[key][i]
        data.append(item)
    hyperinfo = {
        "template_path": resources.files("myosotis_researches").joinpath(
            "CcGAN", "utils", "src", "template.html"
        ),
        "style_path": resources.files("myosotis_researches").joinpath(
            "CcGAN", "utils", "src", "style.css"
        ),
        "server_path": os.path.abspath(__file__),
        "host": "0.0.0.0",
        "port": "8000",
        "debug": True,
    }
    info = {
        "file": {
            "size": humanize.naturalsize(os.path.getsize(dataset_path), binary=True),
            "created_date": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(dataset_path))
            ),
            "last_edited_date": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(dataset_path))
            ),
            "path": dataset_path,
            "name": os.path.basename(dataset_path),
        },
        "rows": {"num": N},
        "columns": {"num": len(keys), "list": keys},
        "indexes": indexes,
    }
    all_data = data

    # Local server
    app = Flask(__name__)

    @app.route("/")
    def index():
        with open(hyperinfo["template_path"], "r") as f:
            template = Template(f.read())
        return template.render(hyperinfo=hyperinfo, info=info, datas=all_data)

    @app.route("/style.css")
    def style():
        return send_file(hyperinfo["style_path"])

    app.run(host=hyperinfo["host"], port=hyperinfo["port"], debug=hyperinfo["debug"])


# download_datasets
_file_id_dict = {
    "Ra": "1YVLFAaQ1ldre0ASLSRdV_kPIcAMkwGqO",
    "MNIST": "18249ryrDPsznWWtOkJuALZWCVoZqfibC",
}


def download_datasets(datasets_name, datasets_dir):
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir, exist_ok=True)
    zipped_datasets_path = os.path.join(datasets_dir, f"{datasets_name}.rar")
    file_id = _file_id_dict[datasets_name]
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, zipped_datasets_path, quiet=False, use_cookies=False)
    unzip_password = getpass.getpass("Please input the zipped file's password:")
    try:
        cmd = ["unrar", "x", f"-p{unzip_password}", zipped_datasets_path, datasets_dir]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
    os.remove(zipped_datasets_path)


__all__ = ["view_dataset", "visualize_dataset", "download_datasets"]
