Shader "Chapter7/Ghost"
{
    Properties { _Color ("Color", Color) = (0.45, 0.48, 0.5, 0.18) }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Back
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct appdata { float4 vertex : POSITION; };
            struct v2f { float4 vertex : SV_POSITION; };
            CBUFFER_START(UnityPerMaterial)
            half4 _Color;
            CBUFFER_END
            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = TransformObjectToHClip(v.vertex.xyz);
                return o;
            }
            half4 frag(v2f i) : SV_Target { return _Color; }
            ENDHLSL
        }
    }
}
