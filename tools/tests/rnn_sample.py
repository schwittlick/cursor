import arcade
import tensorflow as tf

from cursor import misc
from cursor.data import DataDirHandler
from cursor.filter import MinPointCountFilter, MaxPointCountFilter
from cursor.load.loader import Loader
from cursor.path import Path
from cursor.renderer import RealtimeRenderer


def transform_path(path, bb, out):
    fn = misc.transformFn((bb.x, bb.y), (bb.x2, bb.y2), out[0], out[1])

    res = list(map(fn, path.generate))
    return Path.from_tuple_list(res)


if __name__ == "__main__":
    p = DataDirHandler().recordings()
    ll = Loader(directory=p, limit_files=10)
    c = ll.all_paths()

    min_filter = MinPointCountFilter(3)
    c.filter(min_filter)

    max_filter = MaxPointCountFilter(20)
    c.filter(max_filter)
    lines = []  # [[(x1, y1), (x2, y2), ..., (xn, yn)], [(x1, y1), (x2, y2), ..., (xm, ym)], ...]
    for pa in c:
        lines.append(pa.as_tuple_list())

    vocab = set()
    for sequence in lines:
        for point in sequence:
            vocab.add(point)

    # Assign unique indices to points in the vocabulary
    index_mapping = {point: idx for idx, point in enumerate(vocab)}
    inverted_mapping = {v: k for k, v in index_mapping.items()}

    p2 = c.random()
    print(len(p2))

    # Assuming you have loaded the trained model from a .h5 file
    model = tf.keras.models.load_model('trained_model4.h5')

    # Define the desired length of the generated sequence
    desired_length = len(p2)

    # Generate new sequences
    generated_sequences = []
    current_sequence = tf.constant([[0, 0]], dtype=tf.int32)  # Start with a single point (e.g., (0, 0))

    for _ in range(desired_length):
        current_sequence_padded = tf.pad(current_sequence,
                                         [[0, 0], [0, 19 - tf.shape(current_sequence)[1]]])  # Pad the sequence
        predictions = model(current_sequence_padded)  # Make predictions using the current sequence
        predicted_point = tf.random.categorical(predictions[:, -1, :], num_samples=1)  # Sample the next point

        predicted_point = tf.cast(predicted_point, dtype=tf.int32)  # Cast the predicted point to int32
        current_sequence = tf.concat([current_sequence, predicted_point], axis=1)  # Append the predicted point
        generated_sequences.append(predicted_point.numpy().tolist()[0][0])

    print(generated_sequences)

    points = [inverted_mapping[idx] for idx in generated_sequences]
    print(points)

    p = Path.from_tuple_list(points)
    # p.fit(BoundingBox(0, 0, 400, 400), padding=10)
    p = transform_path(p, p.bb(), ((0, 0), (400, 400)))

    p2 = transform_path(p2, p2.bb(), ((400, 0), (800, 400)))

    rr = RealtimeRenderer(800, 400, "projection")
    rr.background(arcade.color.WHITE)
    rr.add_path(p)
    rr.add_path(p2)
    rr.run()
