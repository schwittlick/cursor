#version 330

uniform sampler2D texture0;
uniform vec2 target_size;

in vec2 v_uv;
out vec4 outColor;

void main()
{
    float Pi = 6.28318530718; // Pi*2

    // GAUSSIAN BLUR SETTINGS {{{
    float Directions = 32.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
    float Quality = 2.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
    float Size = 3.0; // BLUR SIZE (Radius)
    // GAUSSIAN BLUR SETTINGS }}}

    vec2 Radius = Size/target_size;

    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = v_uv;
    // Pixel colour
    vec4 Color = texture(texture0, uv);

    // Blur calculations
    for( float d=0.0; d<Pi; d+=Pi/Directions)
    {
		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality)
        {
			Color += texture( texture0, uv+vec2(cos(d),sin(d))*Radius*i);
        }
    }

    // Output to screen
    Color /= Quality * Directions - 15.0;
    outColor =  Color;
}