import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()

with tf.Session() as sess:
    model_filename = 'conv_actions_frozen.pb'
    with tf.gfile.GFile(model_filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        g_in = tf.import_graph_def(graph_def)
LOGDIR = 'content'
train_writer = tf.summary.FileWriter(LOGDIR)
train_writer.add_graph(sess.graph)
train_writer.flush()
train_writer.close()

constant_values = {}

with tf.Session() as sess:
    constant_ops = [op for op in sess.graph.get_operations() if op.type == "Const"]
    for constant_op in constant_ops:
        constant_values[constant_op.name] = sess.run(constant_op.outputs[0])
conv1_weights = constant_values.get('import/Variable')
print(conv1_weights)

# then run below
# % tensorboard --logdir /Users/zhangcheng/dev/educated_ai/try/content
