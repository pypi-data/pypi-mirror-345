EVALSCRIPTS = {
    "true_color": """
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B03", "B02", "dataMask"],
            output: { bands: 4 }
        };
    }
    const maxR = 3.0; const midR = 0.13; const sat = 1.2; const gamma = 1.8;
    function evaluatePixel(smp) {
        const rgbLin = satEnh(sAdj(smp.B04), sAdj(smp.B03), sAdj(smp.B02));
        return [sRGB(rgbLin[0]), sRGB(rgbLin[1]), sRGB(rgbLin[2]), smp.dataMask];
    }
    function sAdj(a) {
        return adjGamma(adj(a, midR, 1, maxR));
    }
    const gOff = 0.01;
    const gOffPow = Math.pow(gOff, gamma);
    const gOffRange = Math.pow(1 + gOff, gamma) - gOffPow;
    function adjGamma(b) {
        return (Math.pow((b + gOff), gamma) - gOffPow)/gOffRange;
    }
    function satEnh(r, g, b) {
        const avgS = (r + g + b) / 3.0 * (1 - sat);
        return [clip(avgS + r * sat), clip(avgS + g * sat), clip(avgS + b * sat)];
    }
    function clip(s) {
        return s < 0 ? 0 : s > 1 ? 1 : s;
    }
    function adj(a, tx, ty, maxC) {
        var ar = clip(a / maxC, 0, 1);
        return ar * (ar * (tx/maxC + ty -1) - ty) / (ar * (2 * tx/maxC - 1) - tx/maxC);
    }
    const sRGB = (c) => c <= 0.0031308 ? (12.92 * c) : (1.055 * Math.pow(c, 0.41666666666) - 0.055);
    """,

    "false_color": """
    //VERSION=3
    let minVal = 0.0;
    let maxVal = 0.4;
    let viz = new HighlightCompressVisualizer(minVal, maxVal);
    function setup(ds) {
        return {
            input: ["B03", "B04", "B08", "dataMask"],
            output: { bands: 4 }
        };
    }
    function evaluatePixel(samples) {
        let val = [samples.B08, samples.B04, samples.B03, samples.dataMask];
        return viz.processList(val);
    }
    """,

    "ndvi": """
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B08", "SCL", "dataMask"],
            output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 }
            ]
        };
    }
    function evaluatePixel(samples) {
        let val = index(samples.B08, samples.B04);
        let imgVals = null;
        const indexVal = samples.dataMask === 1 ? val : NaN;
        if (val < -0.5) imgVals = [0.05, 0.05, 0.05, samples.dataMask];
        else if (val < -0.2) imgVals = [0.75, 0.75, 0.75, samples.dataMask];
        else if (val < -0.1) imgVals = [0.86, 0.86, 0.86, samples.dataMask];
        else if (val < 0) imgVals = [0.92, 0.92, 0.92, samples.dataMask];
        else if (val < 0.025) imgVals = [1, 0.98, 0.8, samples.dataMask];
        else if (val < 0.05) imgVals = [0.93, 0.91, 0.71, samples.dataMask];
        else if (val < 0.075) imgVals = [0.87, 0.85, 0.61, samples.dataMask];
        else if (val < 0.1) imgVals = [0.8, 0.78, 0.51, samples.dataMask];
        else if (val < 0.125) imgVals = [0.74, 0.72, 0.42, samples.dataMask];
        else if (val < 0.15) imgVals = [0.69, 0.76, 0.38, samples.dataMask];
        else if (val < 0.175) imgVals = [0.64, 0.8, 0.35, samples.dataMask];
        else if (val < 0.2) imgVals = [0.57, 0.75, 0.32, samples.dataMask];
        else if (val < 0.25) imgVals = [0.5, 0.7, 0.28, samples.dataMask];
        else if (val < 0.3) imgVals = [0.44, 0.64, 0.25, samples.dataMask];
        else if (val < 0.35) imgVals = [0.38, 0.59, 0.21, samples.dataMask];
        else if (val < 0.4) imgVals = [0.31, 0.54, 0.18, samples.dataMask];
        else if (val < 0.45) imgVals = [0.25, 0.49, 0.14, samples.dataMask];
        else if (val < 0.5) imgVals = [0.19, 0.43, 0.11, samples.dataMask];
        else if (val < 0.55) imgVals = [0.13, 0.38, 0.07, samples.dataMask];
        else if (val < 0.6) imgVals = [0.06, 0.33, 0.04, samples.dataMask];
        else imgVals = [0, 0.27, 0, samples.dataMask];
        return {
            default: imgVals,
            index: [indexVal],
            eobrowserStats: [val, isCloud(samples.SCL) ? 1 : 0],
            dataMask: [samples.dataMask]
        };
    }
    function isCloud(scl) {
        return scl === 9 || scl === 8 || scl === 10;
    }
    """,

    "ndwi": """
    //VERSION=3
    const colorRamp1 = [[0, 0xFFFFFF], [1, 0x008000]];
    const colorRamp2 = [[0, 0xFFFFFF], [1, 0x0000CC]];
    let viz1 = new ColorRampVisualizer(colorRamp1);
    let viz2 = new ColorRampVisualizer(colorRamp2);
    function setup() {
        return {
            input: ["B03", "B08", "SCL", "dataMask"],
            output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 }
            ]
        };
    }
    function evaluatePixel(samples) {
        let val = index(samples.B03, samples.B08);
        let imgVals = null;
        const indexVal = samples.dataMask === 1 ? val : NaN;
        if (val < -0) imgVals = [...viz1.process(-val), samples.dataMask];
        else imgVals = [...viz2.process(Math.sqrt(Math.sqrt(val))), samples.dataMask];
        return {
            default: imgVals,
            index: [indexVal],
            eobrowserStats: [val, isCloud(samples.SCL) ? 1 : 0],
            dataMask: [samples.dataMask]
        };
    }
    function isCloud(scl) {
        return scl === 9 || scl === 8 || scl === 10;
    }
    """,

    "rvi": """
    //VERSION=3
    function setup() {
        return {
            input: ["VV", "VH", "dataMask"],
            output: { bands: 4 }
        };
    }
    function evaluatePixel(samples) {
        let VV = samples.VV;
        let VH = samples.VH;
        let RVI = (4 * VH) / (VV + VH);
        return [RVI, RVI, RVI, samples.dataMask];
    }
    """
}

def get_band_evalscript_s2(band):
    return f"""
            //VERSION=3
            function setup() {{
                return {{
                    input: ['{band}', 'dataMask'],
                    output: {{ bands: 1, sampleType: 'FLOAT32' }}
                }};
            }}

            function evaluatePixel(sample) {{
                if (sample.dataMask === 1) {{
                    return [sample.{band}];
                }} else {{
                    return [0];
                }}
            }}
            """

def get_band_evalscript_s1(band):
    return f"""
            //VERSION=3
            function setup() {{
                return {{
                    input: ['{band}', 'dataMask'],
                    output: {{ bands: 1, sampleType: 'FLOAT32' }}
                }};
            }}

            function evaluatePixel(sample) {{
                if (sample.dataMask === 1) {{
                    return [sample.{band}];
                }} else {{
                    return [0];
                }}
            }}
            """