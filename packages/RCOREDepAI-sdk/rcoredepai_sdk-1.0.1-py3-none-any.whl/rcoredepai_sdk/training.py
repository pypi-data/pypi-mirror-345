import onnxruntime as rt
import numpy as np

def load_model(onnx_path: str):
    return rt.InferenceSession(onnx_path)

def infer(sess, input_tensor: np.ndarray):
    inp_name  = sess.get_inputs()[0].name
    out_name  = sess.get_outputs()[0].name
    return sess.run([out_name], {inp_name: input_tensor})[0]
