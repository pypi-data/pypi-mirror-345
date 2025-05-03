# PyHarmX

**Polyharmonic spline interpolation in PyTorch**

---
[![Documentation Status](https://readthedocs.org/projects/pyharmx/badge/?version=latest)](https://pyharmx.readthedocs.io/en/latest/?badge=latest)

PyHarmX is a PyTorch module designed for efficient [polyharmonic spline interpolation](https://en.wikipedia.org/wiki/Polyharmonic_spline). Leveraging GPU acceleration, this implementation excels in performance, making it well-suited for large-scale interpolation tasks.

## Installation

Install PyHarmX using the following command:

```bash
pip install pyharmx
```

PyHarmX has minimal dependencies, requiring only PyTorch and NumPy.

If you're interested in contributing or want to use PyHarmX in developer/editable mode with test dependencies, install it as follows:

```bash
pip install -e pyharmx[test]
```

To run the tests, simply execute:

```bash
pytest <path-to-pyharmx>
```

## Explore

Check out the [examples](https://github.com/ivanZanardi/pyharmx/tree/main/examples) provided in the repository to see PyHarmX in action. Please see the [documentation](https://pyharmx.readthedocs.io/en/latest/index.html) website for a detailed user guide.

## License

PyHarmX is distributed under the [NCSA Open Source License](https://github.com/ivanZanardi/pyharmx/blob/main/LICENSE). Feel free to use, modify, and contribute to this project within the terms of the license.
