import os
import unittest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

class TestExamples(unittest.TestCase):

    # Directory containing the notebooks, relative to the root of the project
    notebooks_dir = '../examples'

    def run_notebook(self, filename):
        filepath = os.path.join(self.notebooks_dir, filename)
        print(f'Running notebook: {filename}', flush=True)

        with open(filepath) as f:
            nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            try:
                ep.preprocess(nb, {'metadata': {'path': self.notebooks_dir}})
                print(f'Finished running notebook: {filename}', flush=True)
            except Exception as e:
                print(f"Notebook {filename} failed with error: {e}", flush=True)

    def test_example_classSwitch_1(self):
        self.run_notebook("example_classSwitch_1.ipynb")

    def test_example_closedModel_1(self):
        self.run_notebook("example_closedModel_1.ipynb")

    def test_example_closedModel_4(self):
        self.run_notebook("example_closedModel_4.ipynb")

    def test_example_forkJoin_1(self):
        self.run_notebook("example_forkJoin_1.ipynb")

    def test_example_initState_1(self):
        self.run_notebook("example_initState_1.ipynb")

    def test_example_layeredModel_1(self):
        self.run_notebook("example_layeredModel_1.ipynb")

    def test_example_loadDependent_1(self):
        self.run_notebook("example_loadDependent_1.ipynb")

    def test_example_mixedModel_1(self):
        self.run_notebook("example_mixedModel_1.ipynb")

    def test_example_openModel_1(self):
        self.run_notebook("example_openModel_1.ipynb")

    def test_example_prio_1(self):
        self.run_notebook("example_prio_1.ipynb")

    def test_example_randomEnvironment_1(self):
        self.run_notebook("example_randomEnvironment_1.ipynb")

    def test_example_stateDependentRouting_2(self):
        self.run_notebook("example_stateDependentRouting_2.ipynb")

if __name__ == '__main__':
    unittest.main(verbosity=2)
