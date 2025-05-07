import os
import pytest
import sys
from unittest import mock
import importlib


examples_path = os.path.dirname(__file__) + "/../examples/"


@pytest.mark.parametrize("example_file", os.listdir(examples_path))
def test_examples(example_file):
    if example_file.startswith('_'):
        return
    name = f"examples.{example_file[:-3]}"
    # check that all main module examples run without errors

    import matplotlib.pyplot as plt

    def no_show(*args, **kwargs):
        pass
    plt.show = no_show  # disable plt show that requires the user to close the plot

    def no_print(*_):
        pass

    try:
        spec = importlib.util.spec_from_file_location(name, examples_path + example_file)
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)
        with mock.patch.object(module, "print", no_print):  # @UndefinedVariable
            # To count 'if __name__=="__main__": main()' in cov
            with mock.patch.object(module, "__name__", "__main__"):  # @UndefinedVariable

                getattr(module, 'main')()

    except Exception as e:
        raise type(e)(str(e) +
                      ' in %s.main' % name).with_traceback(sys.exc_info()[2])
    finally:
        plt.close('all')
