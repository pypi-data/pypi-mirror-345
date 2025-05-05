import pytest
import numpy as np
from rcoredepai_sdk.training import infer, load_model

def test_load_model_fail():
    with pytest.raises(Exception):
        load_model('nonexistent.onnx')

def test_infer_shape():
    # Dummy session
    class DummySession:
        def get_inputs(self):
            return [type('i',(object,),{'name':'input'})()]
        def get_outputs(self):
            return [type('o',(object,),{'name':'output'})()]
        def run(self, outputs, feeds):
            return [np.array([[1,2,3]])]
    sess = DummySession()
    out = infer(sess, np.zeros((1,3)))
    assert isinstance(out, np.ndarray)
