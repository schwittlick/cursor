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

OSCdef(\hello, { |msg|
	//"hello message received!".postln;
	//msg.postcs;
	msg[1].postln;
	//(instrument: \pandeiro1).play;
	(instrument: \kick_electro1).stop;
	(instrument: \kick_electro1, freq:msg[1] * 0.7, amp:1.0).play;
}, \hello);