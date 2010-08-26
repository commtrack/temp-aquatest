from django.forms import ModelForm
#from django import forms
from django.contrib.gis import forms
from django.contrib.admin import widgets
from django.forms.fields import CharField
from django.contrib.gis.admin.options import GeoModelAdmin

from wqm.admin import PointWidget

from wqm.models import *

class DateForm(forms.Form):
    startdate = forms.DateField(widget = widgets.AdminDateWidget())
    enddate = forms.DateField(widget = widgets.AdminDateWidget())
    failure = forms.BooleanField(help_text='Show failures only')

#geomodeladmin =  GeoModelAdmin(SamplingPoint, google_admin)
#db_field = SamplingPoint._meta.get_field('point')
 

 
class SamplingPointForm(ModelForm):
    point = forms.CharField(widget=PointWidget())
    
    class Meta:
        model = SamplingPoint
        exclude = ('longitude','latitude','modified','created','type','parent')
    
    class Media:
                js = ("http://openlayers.org/api/2.6/OpenLayers.js",)
 
#class GMapInput(Input):
#    """
#        Widget parameter selector for google maps
#    """
# 
#    def render(self, name, value, attrs=None):
#        """
#            Atributos extras:
#             - width: ancho del mapa en pixeles
#             - height: alto del mapa en pixeles
#             - center: latitud,longitud del punto central del mapa
#             - zoom: zoom inicial del mapa, 1 - 17
#        """
# 
#        final_attrs = self.build_attrs(attrs)
#        width = final_attrs['width'] if 'width' in final_attrs else '500'
#        height = final_attrs['height'] if 'height' in final_attrs else '300'
#        center = final_attrs['center'] if 'center' in final_attrs else '21.983801,-100.964355' 
#        zoom = final_attrs['zoom'] if 'zoom' in final_attrs else '4' #
# 
#        widget = u'''<div style="margin-left:7em; padding-left:30px;">
#                    <input type="hidden" value="%(value)s" name="%(name)s" id="%(id)s" />
#                    <div id="%(id)s_map" style="width: %(width)spx; height: %(height)spx"></div></div>
#                    <script type="text/javascript">
#                        var %(id)s_map = new GMap2(document.getElementById("%(id)s_map"));
#                        %(id)s_map.addControl(new GLargeMapControl3D());
# 
#                        var %(id)s_marker;
#                        function %(id)s_updateField() {
#                            document.getElementById("%(id)s").value = %(id)s_marker.getLatLng().toUrlValue() + "|" + %(id)s_map.getZoom();
#                            %(id)s_map.panTo(%(id)s_marker.getLatLng(), true);
#                        }
#                    ''' % { 'value': value, 'name': name, 'id': final_attrs['id'], 'width': width, 'height': height }
# 
#        if value is None or value == '':
#            widget = widget + u'''
#                        %(id)s_map.setCenter(new GLatLng(%(center)s), %(zoom)s);
#                        var %(id)s_clickListener = GEvent.addListener(%(id)s_map, "click", function(overlay, latlng) {
#                            if(latlng) {
#                                %(id)s_marker = new GMarker(latlng, {draggable: true});
#                                %(id)s_map.addOverlay(%(id)s_marker);
#                                %(id)s_updateField();
# 
#                                GEvent.addListener(%(id)s_marker, "dragend", %(id)s_updateField);
#                                GEvent.addListener(%(id)s_map, "zoomend", %(id)s_updateField);
#                                GEvent.addListener(%(id)s_map, "dblclick", function (overlay, latlng) { %(id)s_marker.setLatLng(latlng); %(id)s_updateField(); });
#                                GEvent.removeListener(%(id)s_clickListener);
#                            }
#                        });
#                    </script>''' % { 'id': final_attrs['id'], 'center': center, 'zoom': zoom }
#        else:
#            values = value.partition('|')
# 
#            widget = widget + u'''
#                        %(id)s_map.setCenter(new GLatLng(%(coords)s), %(zoom)s);
#                        %(id)s_marker = new GMarker(new GLatLng(%(coords)s), {draggable: true});
#                        %(id)s_map.addOverlay(%(id)s_marker);
# 
#                        GEvent.addListener(%(id)s_marker, "dragend", %(id)s_updateField);
#                        GEvent.addListener(%(id)s_map, "zoomend", %(id)s_updateField);
#                        GEvent.addListener(%(id)s_map, "dblclick", function (overlay, latlng) { %(id)s_marker.setLatLng(latlng); %(id)s_updateField(); });
#                    ''' % { 'id': final_attrs['id'], 'coords': values[0], 'zoom': values[2] }
# 
#        return mark_safe(widget)
