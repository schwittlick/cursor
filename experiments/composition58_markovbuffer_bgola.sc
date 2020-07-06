// reading in mono
~buf1 = Buffer.readChannel(s, "file.wav", 0, -1, [0]);
~buf2 = Buffer.readChannel(s, "anotherfile.wav",0, -1, [0]);


~buf1.loadToFloatArray(action: {|array| ~array1 = array})
~buf2.loadToFloatArray(action: {|array| ~array2 = array})

~array = ~array1 ++ ~array2;

~mkv = Dictionary.new;

// Number of frames to create the chain
~slices=3

// Generate markov chain
(~array.size/~slices).do {|idx|
	var i = (idx * ~slices).asInt;
	var v = ~array[i..i+~slices-1];
	~mkv[v] = ~mkv[v] ++ [~array[i+~slices..i+~slices+~slices-1]];
};


// New buffer to store generated frames
~gen.free; ~gen = Buffer.alloc(s, ~array.size, 1);

// Pick a random start
~last = ~mkv.keys.asArray.choose;

(~array.size/10).do{|i|
	~last.do {|j,c|
		~gen.set((i*~slices+c).asInt, j);
	};
	~last=~mkv[~last].choose;
};

// listen to generated buffer
~gen.play;