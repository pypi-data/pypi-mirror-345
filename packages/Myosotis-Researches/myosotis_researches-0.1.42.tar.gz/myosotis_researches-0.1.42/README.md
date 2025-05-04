# Myosotis-Researches

## `CcGAN` (`myosotis_researches.CcGAN`)

### `visualize`

The visualize module can display datasets as a webpage

Import with code

```python
from myosotis_researches.CcGAN.visualize import *
```

Now we only have `visualize_datasets` function, defined as

```python
visualize_datasets(
  indexes,
  datasets_path,
  list_path,
  template_path = resources.files("myosotis_researches").joinpath("CcGAN", "visualize", "src", "template,html"),
  host = "127.0.0.1",
  port = 8000,
  debug = True,
  img_size = 64
)
```

### `internal`

The `internal` module is used for setting the local package itself, like installing datasets and so on.

Import with code

```python
from myosotis_researches.CcGAN.internal import *
```

| Function                          | Desctiption                                                          |
| --------------------------------- | -------------------------------------------------------------------- |
| `install_datasets(datasets_name)` | Install the datasets in `datasets_name` to the local python package. |
| `uninstall_datasets()`            | Remove all the datasets installed to the local python package.       |
| `show_datasets()`                 | Show all datasets installed.                                         |

**Note**:

1. The path of the installed datasets are

   `resources.files("myosotis_researches").join("CcGAN", "<datasets_name>")`

   To run this code, remember to add `from importlib import resources` at the beginning.

### `utils`

The `utils` module contains some basic functions and classes which are frequently used during the CcGAN research.

Import with code

```python
from myosotis_researches.CcGAN.utils import *
```

| Function                                                     | Description                               |
| ------------------------------------------------------------ | ----------------------------------------- |
| `concat_image(img_list, gap=2, direction="vertical")`        | Concat images vertically or horizontally. |
| `make_h5(old_datasets_name, size, new_datasets_path, image_indexes, train_indexes, val_indexes)` | Get piece of original HDF5 datasets.      |
| `parse_opts()`                                               | Parse arguments.                          |
| `print_hdf5(name, obj)`                                      | Print a basic structure of an HDF5 file.  |

| Class               | Description           |
| ------------------- | --------------------- |
| `IMGs_dataset`      | Images dataset.       |
| `SimpleProgressBar` | Simple progress bars. |

**Note**:

1. Function `print_hdf5` should be used within a `with` block:

   ```python
   import h5py
   
   with h5py.File(<HDF5_file_path>, "r") as f:
     f.visititems(print_hdf5)
   ```
