/** @module map */


window.searcharea = null;


/** status message div item */
const statusdiv = document.getElementById('status-div');


/* map objects */
let dragBox = null;
let draw = null;
let map = null;
let mapview = null;

/* map geometry layer sources */
let drawSource = null;
let heatSource = null;
let lineSource = null;
let polySource = null;

/* map layers */
let drawLayer = null;
let heatLayer = null;
let lineLayer = null;
let polyLayer = null;
let mapLayer = null;

/* processing functions for incoming websocket data */
let newHeatmapFeatures = null;
let newPolygonFeature = null;
let newTrackFeature = null;


/** set a search area bounding box as determined by the extent
 * of currently selected polygons
 */
async function setSearchAreaFromSelected() {
  for (let ft of polySource.getFeatures()) {
    if (ft.get('selected') === true) {
      if (window.searcharea === null) {
        window.searcharea = { minX: 180, maxX:-180, minY:90, maxY:-90 };
      }
      let coords = ft.getGeometry().clone()
        .transform('EPSG:3857', 'EPSG:4326').getCoordinates()[0];
      for (let point of coords) {
        if (point[0] < window.searcharea.minX) {
          window.searcharea.minX = point[0];
        }
        if (point[0] > window.searcharea.maxX) {
          window.searcharea.maxX = point[0];
        }
        if (point[1] < window.searcharea.minY) {
          window.searcharea.minY = point[1];
        }
        if (point[1] > window.searcharea.maxY) {
          window.searcharea.maxY = point[1];
        }
      }
    }
  }
}

/** initialize map layer and associated imports dynamically */
async function init_maplayers() {
  let [
    _css,
    { set_track_style },
    Feature,
    _Map,
    { default: View },
    GeoJSON,
    Point,
    { defaults },
    DragBox,
    Draw,
    { default: Heatmap },
    { default: TileLayer },
    { default: VectorLayer },
    proj,
    { default: VectorSource },
    { default: BingMaps },
  ] = await Promise.all([
    import('ol/ol.css'),
    import('./selectform'),
    import('ol/Feature'),
    import('ol/Map'),
    import('ol/View'),
    import('ol/format/GeoJSON'),
    import('ol/geom/Point'),
    import('ol/interaction'),
    import('ol/interaction/DragBox'),
    import('ol/interaction/Draw'),
    import('ol/layer/Heatmap'),
    import('ol/layer/Tile'),
    import('ol/layer/Vector'),
    import('ol/proj'),
    import('ol/source/Vector'),
    import('ol/source/BingMaps'),
  ]);

  let {
    dragBoxStyle,
    polyStyle,
    selectStyle,
    vesselStyles,
    vesseltypes,
  } = await import('./palette');

  /** contains geometry for map selection feature */
  drawSource = new VectorSource({ wrapX: false });
  /** contains drawSource for map selection layer */
  drawLayer = new VectorLayer({ source: drawSource, zIndex: 4 });

  /** contains geometry for map zone polygons */
  polySource = new VectorSource({});
  /** contains polySource for map zone polygons */
  polyLayer = new VectorLayer({
    source: polySource,
    style: polyStyle, zIndex: 1,
  });

  /** contains map vessel line geometries */
  lineSource = new VectorSource({});
  /** contains map lineSource layer */
  lineLayer = new VectorLayer({
    source: lineSource,
    style: vesselStyles.Unspecified,
    zIndex: 3,
  });


  /** map heatmap source */
  heatSource = new VectorSource({ });
  /** map heatmap layer */
  heatLayer = new Heatmap({
    source: heatSource,
    blur: 30,
    radius: 3,
    zIndex: 2,
  });


  /** default map position
   * @see module:url
   */
  mapview = new View({
    center: proj.fromLonLat([ -63.6, 44.0 ]), // east
    // center: proj.fromLonLat([-123.0, 49.2]), //west
    // center: proj.fromLonLat([ -100, 57 ]), // canada
    zoom: 7,
  });

  let mapSource = new BingMaps({
    key: import.meta.env.VITE_BINGMAPSKEY,
    imagerySet: 'Aerial',
    // use maxZoom 19 to see stretched tiles instead of the BingMaps
    // "no photos at this zoom level" tiles
    // maxZoom: 19
  });
  /** map window
   * @param {string} target target HTML item by ID
   * @param {Array} layers map layers to display
   * @param {ol/View) view default map view positioning
   */
  /** ol map TileLayer */
  mapLayer = new TileLayer({
    // visible: true,
    // preload: Infinity,
    source: mapSource,
    // zIndex: 0,
  });
  /*
  import OSM from 'ol/source/OSM';
  let mapLayer = new TileLayer({
    visible: true,
    source: new OSM(),
  });
  */

  let mapInteractions = defaults({ doubleClickZoom:false });
  map = new _Map.default({
    target: 'mapDiv', // div item in index.html
    layers: [ mapLayer, polyLayer, lineLayer, heatLayer, drawLayer ],
    view: mapview,
    interactions: mapInteractions,
  });


  /* map interactions */

  /* cursor styling: indicate to the user that we are selecting an area */
  // let draw = new Draw({
  draw = new Draw.default({
    type: 'Point',
  });

  // const Feature = await import('ol/Feature');
  dragBox = new DragBox.default({});
  dragBox.on('boxend', () => {
    window.geom = dragBox.getGeometry();
    let selectFeature = new Feature.default({
      geometry: dragBox.getGeometry(),
      name: 'selectionArea',
    });
    selectFeature.setStyle(dragBoxStyle);
    drawSource.addFeature(selectFeature);
    map.removeInteraction(dragBox);
  });

  /** draw layer addfeature event */
  drawSource.on('addfeature', async () => {
    let selectbox = drawSource.getFeatures()[0].getGeometry().clone()
      .transform('EPSG:3857', 'EPSG:4326').getCoordinates()[0];
    let minX = Math.min(selectbox[0][0], selectbox[1][0],
      selectbox[2][0], selectbox[3][0], selectbox[4][0]);
    let maxX = Math.max(selectbox[0][0], selectbox[1][0],
      selectbox[2][0], selectbox[3][0], selectbox[4][0]);
    let minY = Math.min(selectbox[0][1], selectbox[1][1],
      selectbox[2][1], selectbox[3][1], selectbox[4][1]);
    let maxY = Math.max(selectbox[0][1], selectbox[1][1],
      selectbox[2][1], selectbox[3][1], selectbox[4][1]);
    window.searcharea = { minX:minX, maxX:maxX, minY:minY, maxY:maxY };
    map.removeInteraction(draw);
    map.removeInteraction(dragBox);
  });

  /** callback for map pointermove event
   * @param {Vector} l ol VectorLayer
   * @returns {boolean}
   */
  function pointermoveLayerFilterCallback(l) {
    if (l === lineLayer || l === polyLayer) {
      return true;
    }
    return false;
  }

  /** callback for map click event
   * @param {Vector} l ol VectorLayer
   * @returns {boolean}
   */
  function clickLayerFilterCallback(l) {
    if (l === polyLayer) {
      return true;
    }
    return false;
  }

  /** new zone polygon feature
   * @param {Object} geojs GeoJSON Polygon object
   * @param {Object} meta geometry metadata
   */
  newPolygonFeature = function(geojs, meta) {
    const format = new GeoJSON.default();
    const feature = format.readFeature(geojs, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857',
    });
    feature.setProperties({ meta_str: meta.name });
    polySource.addFeature(feature);
  };

  /** add vessel points to overall heatmap
   * @param {Array} xy Coordinate tuples
   */
  newHeatmapFeatures = function(xy) {
    xy.forEach(async (p) => {
      let pt = new Feature.default({
        geometry: new Point(proj.fromLonLat(p)),
      });
      heatSource.addFeature(pt);
    });
  };

  /** new track geometry feature
   * @param {Object} geojs GeoJSON LineString object
   * @param {Object} meta geometry metadata
   */
  newTrackFeature = async function(geojs, meta) {
    const format = new GeoJSON.default();
    const feature = format.readFeature(geojs, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857',
    });
    let meta_str = '';
    if (meta.mmsi !== 'None') {
      meta_str = `${meta_str}MMSI: ${meta.mmsi}&emsp;`;
    }
    if (meta.imo !== 'None' && meta.imo !== 0) {
      meta_str = `${meta_str}IMO: ${meta.imo}&emsp;`;
    }
    if (meta.name !== 'None' && meta.name !== 0) {
      meta_str = `${meta_str}name: ${meta.name}&emsp;`;
    }
    if (meta.vesseltype_generic !== 'None') {
      meta_str = `${meta_str}type: ${meta.vesseltype_generic}&ensp;`;
    }
    if (
      meta.vesseltype_detailed !== 'None' &&
      meta.vesseltype_generic !== meta.vesseltype_detailed
    ) {
      meta_str = `${meta_str }(${meta.vesseltype_detailed})&emsp;`;
    }
    if (meta.flag !== 'None') {
      meta_str = `${meta_str }flag: ${meta.flag}  `;
    }
    feature.setProperties({
      meta: meta,
      meta_str: meta_str.replace(' ', '&nbsp;'),
    });
    await set_track_style(feature);
    feature.set('COLOR', vesseltypes[meta.vesseltype_generic]);
    lineSource.addFeature(feature);
  };


  let selected = null;
  let previous = null;
  map.on('pointermove', (e) => {
    if (selected !== null && selected.get('selected') !== true) {
      selected.setStyle(undefined);
      selected = null;
    } else
    if (selected !== null) {
      selected = null;
    }

    // reset track style to previous un-highlighted color
    if (previous !== null &&
      previous !== selected &&
      previous.get('meta') !== undefined) {
      set_track_style(previous);
    }

    // highlight feature at cursor
    map.forEachFeatureAtPixel(e.pixel, (f) => {
      selected = f;
      if (f.get('selected') !== true) {
        f.setStyle(selectStyle);
      }

      // keep track of last feature so that styles can be reset after moving mouse
      if (previous === null || previous.get('meta_str') !== f.get('meta_str')) {
        previous = f;
      }
      return true;
    }, { layerFilter: pointermoveLayerFilterCallback }
    );

    // show metadata for selected feature
    if (selected) {
      statusdiv.innerHTML = selected.get('meta_str');
    } else {
      statusdiv.innerHTML = window.statusmsg;
    }
  });

  map.on('click', async (e) => {
    map.forEachFeatureAtPixel(e.pixel, async (f) => {
      if (f.get('selected') !== true) {
        f.setStyle(selectStyle);
        f.set('selected', true);
      } else {
        f.setStyle(polyStyle);
        f.set('selected', false);
      }
      window.searcharea = null;
      await setSearchAreaFromSelected();
      return true;
    }, { layerFilter: clickLayerFilterCallback }
    );
  });
  /*
  map.on('prerender', async(e) => {
    mapLayer = new TileLayer({
      // visible: true,
      // preload: Infinity,
      source: new BingMaps({
        key: import.meta.env.VITE_BINGMAPSKEY,
        imagerySet: 'Aerial',
        // use maxZoom 19 to see stretched tiles instead of the BingMaps
        // "no photos at this zoom level" tiles
        // maxZoom: 19
      }),
      // zIndex: 0,
    });
  });
  */
}

(async () => {
  await init_maplayers();
})();


export {
  // addInteraction,
  // clearFeatures,
  dragBox,
  draw,
  drawSource,
  lineSource,
  map,
  mapview,
  newHeatmapFeatures,
  newPolygonFeature,
  newTrackFeature,
  polySource,
  setSearchAreaFromSelected,
};
