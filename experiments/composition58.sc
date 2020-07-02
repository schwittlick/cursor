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


SynthDef(\tb101, {|out=0, freq=100, filt_freq=15000, atk=0.001, rel=0.2, rq=1, filt_atk=0.001, filt_rel=0.2, sub_amt=0.4, fdbk=0.2, dly=0.2, dlytime=0.4, amp=0.1|
	var sub = SinOscFB.ar(freq*0.5, fdbk);
	var snd = Mix.ar([LFSaw.ar(freq), LFPulse.ar(freq*1.002)*0.5, sub*sub_amt]);
	snd = snd * EnvGen.ar(Env.perc(atk,rel), doneAction: Done.freeSelf);
	snd = RLPF.ar(snd, EnvGen.ar(Env.new([filt_freq, filt_freq, filt_freq*0.25], [filt_atk,filt_rel], \exp)), rq);
	snd = snd*amp;
	Out.ar(out, Mix.ar([Pan2.ar(snd), AllpassC.ar(snd*dly, 1.5, [dlytime,dlytime * 1.02], 5.0)]));
}).add;

(instrument: \tb101, freq:1000, filt_freq:2000, atk:0.001, rel:0.1, rq:0.1, filt_atk:0.001, filt_rel:0.2, sub_amt:0.4, fdbk:0.1, dly:0.1, dlytime:0.01, amp:1.0).play;

NetAddr.langPort;

(
OSCdef(\hello, { |msg|
	//msg[1].postln;
	if(msg[1] == 32)
	{
		// extra bassy kick for space key
		(instrument: \kick_electro1, freq:50, amp:1.0).play;
		//(instrument: \kick_electro1, freq:msg[1] * 1.0, amp:1.0).play;
	}{
		//(instrument: \tb101, freq:msg[1] * 20.0, filt_freq:2000, atk:0.001, rel:0.1, rq:0.1, filt_atk:0.001, filt_rel:0.2, sub_amt:0.4, fdbk:0.1, dly:0.1, dlytime:0.01, amp:1.0).play;
		(instrument: \kick_electro1, freq:msg[1] * 1.0, amp:1.0).play;
	};


	(instrument: \tb101, freq:msg[1] * 20.0, filt_freq:2000, atk:0.001, rel:0.1, rq:0.1, filt_atk:0.001, filt_rel:0.2, sub_amt:0.4, fdbk:0.1, dly:0.1, dlytime:0.01, amp:1.0).play;

	// hyperdisko history extra stuff
	// escape synth names with double backslash
	// and format strings via % and .format(replacement)
	//MFdef('historyForward').value("(instrument: \\tb101, freq:% * 0.7, amp:1.0).play;".format(msg[1]));
	//History.enter("(instrument: \\tb, freq101:% * 0.7, amp:1.0).play;".format(msg[1]), q.myID);
}, \hello);
)

(instrument: \kick_electro1, freq:50, amp:1.0).play;

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

