# pi-geig
A program written in Python 3 to interface a geiger counter and a webserver.

Make sure to change the text on the webpage to something you want.



How to hook up a geiger counter;

Your counter should have an output jack similar to what headphones use. Sarcrifice a pair of old headphones or something and strip the cable of its insulation. The outermost band on the jack is often the ground, connect that to the Pi's ground. Connect the signal wire to the base of an NPN transistor. Connect 5v to the collector with 1K, the emitter to the Pi's input pin, and input pin to ground with 2k2.
