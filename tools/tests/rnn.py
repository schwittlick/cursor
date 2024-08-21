from cursor.data import DataDirHandler
from cursor.filter import MaxPointCountFilter, MinPointCountFilter
from cursor.load.loader import Loader

import tensorflow as tf

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

    # print(index_mapping)

    encoded_sequences = []
    for sequence in lines:
        encoded_sequence = [index_mapping[point] for point in sequence]
        encoded_sequences.append(encoded_sequence)

    # print(encoded_sequences)

    max_length = max(len(seq) for seq in encoded_sequences)
    print(max_length)

    # Pad the sequences to the maximum length
    padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(encoded_sequences, maxlen=max_length)

    print(padded_sequences)

    input_sequences = padded_sequences[:, :-1]  # All but the last element of each sequence
    target_sequences = padded_sequences[:, 1:]  # All but the first element of each sequence

    vocab_size = len(index_mapping)
    embedding_dim = 128
    num_epochs = 10
    batch_size = 128

    model = tf.keras.models.Sequential([
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length - 1),
        tf.keras.layers.GRU(units=64, return_sequences=True),
        tf.keras.layers.Dense(units=vocab_size, activation='softmax')
    ])

    # Compile the model
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    model.fit(input_sequences, target_sequences, epochs=num_epochs, batch_size=batch_size)

    # Save the trained model
    model.save('trained_model4.h5')
