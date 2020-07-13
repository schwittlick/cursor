
NetAddr.langPort;

(

SynthDef("kick_electro1", {
	arg freq=60, amp=1, pan=0, out=0;
	var x, env1, env2, env3, mod, noise;
	env1 = Env.perc(0.001,0.15,1,-4);
	env2 = Env.perc(0.001,0.01,1,-4);
	env3 = Env.perc(0.0001,0.01,0.2,-10);
	mod = EnvGen.ar(env2, 1) * 1000;
	noise = EnvGen.ar(env3, 1);
	x = SinOsc.ar(freq + mod);
	x = EnvGen.ar(env1, 1, doneAction: 2) * x - noise;
	OffsetOut.ar(out, Pan2.ar(x,pan, amp));
}).add;

SynthDef(\ImpulseTest, { arg outbus=0, effectbus, freq=0.5, phase=0.25, attack=0.01, decay=0.2, direct=0.5, amp=1.0;
	var source;
	//MouseX.kr(1, 20, 1).poll;
	source = Impulse.ar(freq, phase);
	source = Decay2.ar(source, attack, decay, SinOsc.ar);
	Out.ar(outbus, (source * direct) * amp);
	Out.ar(outbus + 1, (source * direct) * amp);
	Out.ar(effectbus, (source * (1 - direct)));
}).add;

SynthDef(\ImpulseMod, { arg outbus=0, inbus, amp=1.0;
	var input;
	input = In.ar(inbus, 1);
	16.do({ input = AllpassC.ar(input, 0.04, { Rand(0.001,0.04) }.dup, 3)});
	Out.ar(outbus, input * amp);
}).add;

b = Bus.audio(s,1); // effects bus
//b.index.postln;
//b.numChannels.postln;
)

(
x = Synth.new(\ImpulseTest, [\effectbus, b.index]);
y = Synth.after(x, \ImpulseMod, [\inbus, b.index, \outbus, 0]);
)

x.set(\freq, 0.5);
x.set(\attack, 0.005);
x.set(\decay, 0.2);
x.set(\direct, 0);
x.set(\amp, 1);
y.set(\amp, 1);
x.free; y.free;

(
OSCdef(\keyboard_keys_ascii, { arg msg;
	var freq, direct;
	freq = msg[1] / 10;
	direct = (freq / 12);
	//"msg: ".post;
	//msg[1].postln;
	//"freq: ".post;
	//freq.postln;
	//"direct: ".post;
	//direct.postln;

	x.set(\freq, freq);
	x.set(\direct, direct);
	x.set(\attack, 0.0005);
}, \keyboard_keys_ascii);



OSCdef(\keyboard_keys_ascii_special, { arg msg;
	var backspace, shift;
	msg[1].postln;

	backspace = (msg[1].asString == "BACKSPACE");

	if(backspace, {
		(instrument: \kick_electro1, freq:50, amp:1.0).play;
	},{});

	shift = (msg[1].asString == "SHIFT");

	if(shift, {
		(instrument: \kick_electro1, freq:10000, amp:1.0).play;
	},{});
}, \keyboard_keys_ascii_special);
)