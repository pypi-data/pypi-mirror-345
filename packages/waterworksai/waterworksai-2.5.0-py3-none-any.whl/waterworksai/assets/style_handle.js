window.dashExtensions = window.dashExtensions || {};
window.dashExtensions.default = window.dashExtensions.default || {};
window.dashExtensions.default.styleHandle = function (feature, context) {
    const { classes, colorscale, style, colorProp } = context.hideout; // get props from hideout
    const value = feature.properties[colorProp]; // get value that determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.color = colorscale[i]; // set the fill color according to the class
        }
    }
    return style;
};
