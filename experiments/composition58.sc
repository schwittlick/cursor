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

(
OSCdef(\hello, { |msg|
	msg[1].postln;
	//(instrument: \kick_electro1).stop;
	//(instrument: \kick_electro1, freq:msg[1] * 0.7, amp:1.0).play;
	Synth(\drum1, [\freq, msg[1]*100, \freqMul, 500, \decay, 20.2, \fdecay, 20.5, \amp, 5.0]);
}, \hello);
)

SynthDef(\drum1, {|out=0, t_trig=1, freq, freqMul=4, decay=0.1, fdecay=0.02, rq=0.2, amp=0.7, pan=0|
	var snd, fenv, env = EnvGen.ar(Env.perc(1e-5, decay, curve:-8), t_trig, doneAction:2);
	fenv = EnvGen.ar(Env.perc(1e-5, fdecay, curve:-4), t_trig, doneAction:0);
	snd = BPF.ar( WhiteNoise.ar(10), freq * freqMul * fenv + 100, rq);
	OffsetOut.ar(out, Pan2.ar(snd.softclip * amp * env, pan));
}).add;

SynthDef(\drum2, {|out=0, t_trig=1,freq, freqMul=4, decay=0.1, ffreq=1000, rq=0.3, amp=0.4, pan=0|
	var snd, env = EnvGen.ar(Env.perc(1e-9, decay, curve:-8), t_trig, doneAction:2);
	snd = BPF.ar( WhiteNoise.ar(10), freq * freqMul + 100, rq)
	+ SinOsc.ar(freq/2)!2;
	OffsetOut.ar(out, Pan2.ar(LPF.ar(snd, ffreq, amp * env * 0.5), pan));
}).add;

Synth(\drum1, [\freq, 2000, \freqMul, 5, \decay, 10, \fdecay, 0.1, \amp, 1]);
Synth(\drum2, [\freq, 500, \freqMul, 5, \decay, 10, \fdecay, 0.1, \amp, 1]);


Synth(q.tonalDefs[15]).stop;
a = Synth(q.tonalDefs[15], [\freq, 500, \freqMul, 5, \decay, 1, \fdecay, 0.1, \amp, 1]);

