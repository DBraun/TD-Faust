import("stdfaust.lib");
mix = hslider("v:[0] JPrev/h:[0] Mix/wet [style:knob]", 1., 0, 1, .01) : si.smoo;
process = ef.dryWetMixer(mix, dm.jprev_demo);