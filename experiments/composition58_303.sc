(
SynthDef(\impulseSync, {
	|rate=1, bpm=135, barLengthInBeats=4, resetLength=1|
	var reso = 96;
	var clockFreqFull = bpm / 60 / barLengthInBeats * rate;
	var clockFreq = clockFreqFull / resetLength;
	var impSubDivs = Impulse.ar(clockFreqFull * barLengthInBeats * reso, 0);
	var imp = PulseDivider.ar(impSubDivs, (barLengthInBeats * reso * resetLength).floor, barLengthInBeats * reso);
	var clockPos = Phasor.ar(imp, clockFreqFull / SampleRate.ir, 0, 1, 0); 	var barCounter = PulseCount.ar(imp);
	Out.ar(30, barCounter);
	Out.ar(31, imp);
	Out.ar(32, clockPos);
	Out.ar(33, impSubDivs);
}).store;

~pulsePattern = {
	|pat|
	var clock, seq;
	clock = In.ar(33,1);
	seq = {Dseq(pat,inf)};
	Demand.ar(clock, In.ar(31,1), seq) * clock;
};

~every = {
	|x|
	~pulsePattern.([1] ++ (0!(x-1)));
};

~seq = {|pulse, pattern, barreset=1, noreset=0|
	var isBarZero = InRange.ar(In.ar(30) % barreset,0,0.99999);
	Demand.ar(pulse, In.ar(31) * isBarZero * (1-noreset), {Dseq(pattern, inf)})
};


~imp = Synth.before(1, \impulseSync);
{
	var w, p4, nt, ds,fr, lagfr, fenv, et,ac, acInt,gt;
	var wv=0.1; //0-1, mix between saw and pulse
	var ampComp, cutoff, accMod=1;
	nt = ~every.(24);
	Poll.ar(nt, nt, \tr);
	fr = ~seq.(nt, [100,100,400,200,100,100,800,050] *0.5); //freq
	et = ~seq.(nt, [001,001,001,001,001,001,000,001]) * nt; //env trig
	ac = ~seq.(nt, [001,000,000,001,000,000,001,000]) * nt; //accent
	gt = ~seq.(nt, [001,001,001,001,001,001,000,001]); //gate
	lagfr = LagUD.ar(fr,0.39, 0.09);
	lagfr = lagfr * LFDNoise3.ar(0.3,0.0156,1);
	w = DPW4Saw.ar(lagfr, 0.5 + (wv ** 4 * 550)).softclip;
	ampComp = (1.05-wv) ** 6 + 1;
	w = w * 0.9* ampComp * LFDNoise3.ar(0.5,0.04,1);
	acInt = LPF.ar(ac*12, 1);
	fenv = Decay2.ar(et*0.16 + (acInt * 0.02 * accMod) , 0.01, 0.12)  * LFDNoise3.ar(0.2,0.003,1);
	cutoff = MouseX.kr(20,10000,1);
	w = RLPFD.ar(w, cutoff + (15000-cutoff * fenv), 0.6 + (acInt * 1.2 * accMod), 0.5) * 2;
	w = LeakDC.ar(w, 0.995);
	w = w + (HPF.ar(w,400,10).softclip * 0.04);
	w = w * Lag.ar(gt, 0.001);
	Out.ar(0,w.dup);
	w.poll;
}.play;

)