app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;

var outputPath = Folder.temp.fsName + "/font-image-text-replace-photoshop-smoke.json";
var result = {
    ok: false,
    photoshopVersion: app.version,
    textLayerCreated: false,
    fontReadable: false,
    error: null
};

var doc = null;
try {
    doc = app.documents.add(96, 96, 72, "font-image-text-replace-smoke", NewDocumentMode.RGB, DocumentFill.WHITE);
    var layer = doc.artLayers.add();
    layer.kind = LayerKind.TEXT;
    layer.name = "10-editable-smoke-test";
    layer.textItem.contents = "TEST";
    layer.textItem.size = UnitValue(24, "px");
    layer.textItem.position = [UnitValue(8, "px"), UnitValue(40, "px")];
    result.textLayerCreated = (layer.kind === LayerKind.TEXT);
    result.actualFont = layer.textItem.font;
    result.fontReadable = !!result.actualFont;
    result.ok = result.textLayerCreated && result.fontReadable;
} catch (e) {
    result.error = e.toString();
} finally {
    if (doc) {
        doc.close(SaveOptions.DONOTSAVECHANGES);
    }
}

var file = new File(outputPath);
file.encoding = "UTF8";
file.open("w");
file.write(JSON.stringify(result));
file.close();
