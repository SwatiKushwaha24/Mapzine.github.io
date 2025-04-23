import folium
import pandas

# Load volcano data
data = pandas.read_csv("volcanoes.txt")
lat = list(data["LAT"])
lon = list(data["LON"])
elev = list(data["ELEV"])
name = list(data["NAME"])

# Optimized popup HTML (no scrollbars)
volcano_popup_html = """
<div style="
    font-family: Arial, sans-serif;
    width: 280px;
    padding: 10px;
    margin: 0;
    overflow: visible;
">
    <h3 style="
        margin: 0 0 8px 0;
        color: #c0392b;
        font-size: 18px;
        line-height: 1.3;
    ">
        🌋 {name}
    </h3>
    
    <div style="
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.5;
        color: #333;
    ">
        <div style="margin-bottom: 4px;">
            <strong>Elevation:</strong> <span style="color: #e74c3c;">{elev:,} m</span>
        </div>
        <div>
            <strong>Location:</strong> {lat:.2f}°N, {lon:.2f}°W
        </div>
    </div>
    
    <a href="https://www.google.com/search?q={name}+volcano" 
       target="_blank" 
       style="
            display: block;
            padding: 8px 12px;
            background: #4285F4;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            text-align: center;
            margin-top: 8px;
       ">
        🔍 Search on Google
    </a>
</div>
"""

def color_producer(elevation):
    if elevation < 1500:
        return "red"
    elif 1500 <= elevation < 2500:
        return "green"
    else:
        return "blue"

# Create map
m = folium.Map(
    location=[38.58, -99.09],
    zoom_start=5,
    tiles='CartoDB positron',
    attr='© OpenStreetMap contributors © CARTO',
    control_scale=True
)

# Volcano markers with enhanced popups
fg_volcanoes = folium.FeatureGroup(name='Volcanoes', show=True)
for lt, ln, el, nm in zip(lat, lon, elev, name):
    # Create the large popup
    popup = folium.Popup(
        folium.IFrame(
            html=volcano_popup_html.format(
                name=nm,
                elev=el,
                lat=lt,
                lon=abs(ln)  # Show as positive W longitude
            ),
            width=350,
            height=250
        ),
        max_width=400
    )
    
    # Add marker with the popup
    folium.Marker(
        location=[lt, ln],
        popup=popup,
        tooltip=f"🌋 {nm} ({el}m)",
        icon=folium.Icon(
            color=color_producer(el),
            icon='fire',
            prefix='fa',
            icon_color='white'
        )
    ).add_to(fg_volcanoes)

# Population layer
fg_population = folium.FeatureGroup(name='Population', show=True)
folium.GeoJson(
    data=open("world.json", "r", encoding="utf-8-sig").read(),
    style_function=lambda x: {
        'fillColor': '#fee5d9' if x['properties']['POP2005'] < 10000000 
                    else '#fcae91' if 10000000 <= x['properties']['POP2005'] < 20000000 
                    else '#fb6a4a',
        'color': '#636363',
        'weight': 0.5,
        'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['NAME', 'POP2005'],
        aliases=['Country:', 'Population:'],
        style=(
            "font-family: Arial; font-size: 14px; padding: 8px;"
            "background: white; border-radius: 4px;"
            "box-shadow: 0 2px 6px rgba(0,0,0,0.1);"
        )
    )
).add_to(fg_population)

# Add layers and controls
m.add_child(fg_volcanoes)
m.add_child(fg_population)
m.add_child(folium.LayerControl(position='topright'))

# Add a legend
legend_html = '''
<div style="
    position: fixed; 
    bottom: 50px; 
    left: 50px; 
    width: 240px;
    padding: 15px;
    background: white;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    font-family: Arial;
    z-index: 1000;
">
    <h4 style="margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
        Volcano Elevation
    </h4>
    <div style="margin-bottom: 8px;">
        <span style="display: inline-block; width: 20px; height: 20px; background: red; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>Low (<1,500m)</span>
    </div>
    <div style="margin-bottom: 8px;">
        <span style="display: inline-block; width: 20px; height: 20px; background: green; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>Medium (1,500-2,500m)</span>
    </div>
    <div style="margin-bottom: 15px;">
        <span style="display: inline-block; width: 20px; height: 20px; background: blue; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>High (>2,500m)</span>
    </div>
    
    <h4 style="margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
        Population Density
    </h4>
    <div style="margin-bottom: 8px;">
        <span style="display: inline-block; width: 20px; height: 20px; background: #fee5d9; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>Low (<10M)</span>
    </div>
    <div style="margin-bottom: 8px;">
        <span style="display: inline-block; width: 20px; height: 20px; background: #fcae91; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>Medium (10-20M)</span>
    </div>
    <div>
        <span style="display: inline-block; width: 20px; height: 20px; background: #fb6a4a; 
              margin-right: 10px; vertical-align: middle;"></span>
        <span>High (>20M)</span>
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
m.save("Mapzine.html")
print("Map successfully saved!!")