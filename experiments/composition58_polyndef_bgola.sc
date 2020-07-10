(
Ndef(\polysynth, {|t_gate, midinote=60|
	var n_voices = 10, max_voice_time=120;
	var times = LocalIn.kr(n_voices);
        // Latch returns 0 by default before the first trig, that is why we
        // sum 1 to the index and then subtract.
	var voice = (Latch.kr(ArrayMax.kr(times)[1] + 1, t_gate) - 1);
	var trigs = n_voices.collect {|idx|
		BinaryOpUGen('==', voice, idx);
	};

	var voices = n_voices.collect {|idx|
		SinOsc.ar(Latch.kr(midinote.midicps, trigs[idx])) * EnvGen.ar(
			Env.perc(0.01,3),
			trigs[idx];
		);
	};

	LocalOut.kr(
		n_voices.collect {|idx|
			EnvGen.kr(Env.new([1,0,1],[0,max_voice_time]), trigs[idx]);
	});
	Splay.ar(voices);
}).play;
)

(
Tdef(\melody, {
	var scale = Scale.choose;
	24.rand.do {
		Ndef(\polysynth).set(\t_gate, 1, \midinote, 60+scale.degrees.choose);
		2.0.rand.wait;
	}
}).play;
)

(
Tdef(\chord, {
	Ndef(\polysynth).set(\t_gate, 1, \midinote, 50);
	0.003.wait;
	Ndef(\polysynth).set(\t_gate, 1, \midinote, 60);
	0.003.wait;
	Ndef(\polysynth).set(\t_gate, 1, \midinote, 70);
}).play;
)