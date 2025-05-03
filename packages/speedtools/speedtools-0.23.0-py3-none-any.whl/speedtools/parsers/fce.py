# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Fce(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x14\x10\x10\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x14\x10\x10\x00", self.magic, self._io, u"/seq/0")
        self.unknown = self._io.read_bytes(4)
        self.num_polygons = self._io.read_u4le()
        self.num_vertices = self._io.read_u4le()
        self.num_arts = self._io.read_u4le()
        self.vertice_table_offset = self._io.read_u4le()
        self.normals_table_offset = self._io.read_u4le()
        self.polygon_table_offset = self._io.read_u4le()
        self.unknown2 = self._io.read_bytes(12)
        self.undamaged_vertices_offset = self._io.read_u4le()
        self.undamaged_normals_offset = self._io.read_u4le()
        self.damaged_vertices_offset = self._io.read_u4le()
        self.damaged_normals_offset = self._io.read_u4le()
        self.damage_weights_offset = self._io.read_u4le()
        self.driver_movement_offset = self._io.read_u4le()
        self.unknown4 = self._io.read_bytes(8)
        self.half_sizes = Fce.Float3(self._io, self, self._root)
        self.num_light_sources = self._io.read_u4le()
        self.light_sources = []
        for i in range(self.num_light_sources):
            self.light_sources.append(Fce.Float3(self._io, self, self._root))

        self.unused_light_sources = []
        for i in range((16 - self.num_light_sources)):
            self.unused_light_sources.append(Fce.Float3(self._io, self, self._root))

        self.num_car_parts = self._io.read_u4le()
        self.part_locations = []
        for i in range(self.num_car_parts):
            self.part_locations.append(Fce.Float3(self._io, self, self._root))

        self.unused_parts = []
        for i in range((64 - self.num_car_parts)):
            self.unused_parts.append(Fce.Float3(self._io, self, self._root))

        self.part_vertex_index = []
        for i in range(self.num_car_parts):
            self.part_vertex_index.append(self._io.read_u4le())

        self.unused_part_vertex_index = []
        for i in range((64 - self.num_car_parts)):
            self.unused_part_vertex_index.append(self._io.read_u4le())

        self.part_num_vertices = []
        for i in range(self.num_car_parts):
            self.part_num_vertices.append(self._io.read_u4le())

        self.unused_part_num_vertices = []
        for i in range((64 - self.num_car_parts)):
            self.unused_part_num_vertices.append(self._io.read_u4le())

        self.part_polygon_index = []
        for i in range(self.num_car_parts):
            self.part_polygon_index.append(self._io.read_u4le())

        self.unused_part_polygon_index = []
        for i in range((64 - self.num_car_parts)):
            self.unused_part_polygon_index.append(self._io.read_u4le())

        self.part_num_polygons = []
        for i in range(self.num_car_parts):
            self.part_num_polygons.append(self._io.read_u4le())

        self.unused_part_num_polygons = []
        for i in range((64 - self.num_car_parts)):
            self.unused_part_num_polygons.append(self._io.read_u4le())

        self.num_colors = self._io.read_u4le()
        self.primary_colors = []
        for i in range(self.num_colors):
            self.primary_colors.append(Fce.Color(self._io, self, self._root))

        self.unused_primary_colors = []
        for i in range((16 - self.num_colors)):
            self.unused_primary_colors.append(Fce.Color(self._io, self, self._root))

        self.interior_colors = []
        for i in range(self.num_colors):
            self.interior_colors.append(Fce.Color(self._io, self, self._root))

        self.unused_interior_colors = []
        for i in range((16 - self.num_colors)):
            self.unused_interior_colors.append(Fce.Color(self._io, self, self._root))

        self.secondary_colors = []
        for i in range(self.num_colors):
            self.secondary_colors.append(Fce.Color(self._io, self, self._root))

        self.unused_secondary_colors = []
        for i in range((16 - self.num_colors)):
            self.unused_secondary_colors.append(Fce.Color(self._io, self, self._root))

        self.driver_colors = []
        for i in range(self.num_colors):
            self.driver_colors.append(Fce.Color(self._io, self, self._root))

        self.unused_driver_colors = []
        for i in range((16 - self.num_colors)):
            self.unused_driver_colors.append(Fce.Color(self._io, self, self._root))

        self.unknown5 = self._io.read_bytes(260)
        self._raw_dummies = []
        self.dummies = []
        for i in range(16):
            self._raw_dummies.append(self._io.read_bytes(64))
            _io__raw_dummies = KaitaiStream(BytesIO(self._raw_dummies[i]))
            self.dummies.append(Fce.Dummy(_io__raw_dummies, self, self._root))

        self._raw_part_strings = []
        self.part_strings = []
        for i in range(self.num_car_parts):
            self._raw_part_strings.append(self._io.read_bytes(64))
            _io__raw_part_strings = KaitaiStream(BytesIO(self._raw_part_strings[i]))
            self.part_strings.append(Fce.Part(_io__raw_part_strings, self, self._root))

        self._raw_unused_part_strings = []
        self.unused_part_strings = []
        for i in range((64 - self.num_car_parts)):
            self._raw_unused_part_strings.append(self._io.read_bytes(64))
            _io__raw_unused_part_strings = KaitaiStream(BytesIO(self._raw_unused_part_strings[i]))
            self.unused_part_strings.append(Fce.Part(_io__raw_unused_part_strings, self, self._root))

        self.unknown8 = self._io.read_bytes(528)

    class Polygon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.texture = self._io.read_u4le()
            self.face = []
            for i in range(3):
                self.face.append(self._io.read_u4le())

            self.unknown = []
            for i in range(6):
                self.unknown.append(self._io.read_bytes(2))

            self.flags = self._io.read_u4le()
            self.u = []
            for i in range(3):
                self.u.append(self._io.read_f4le())

            self.v = []
            for i in range(3):
                self.v.append(self._io.read_f4le())


        @property
        def non_reflective(self):
            if hasattr(self, '_m_non_reflective'):
                return self._m_non_reflective

            self._m_non_reflective = (self.flags & 1) != 0
            return getattr(self, '_m_non_reflective', None)

        @property
        def highly_reflective(self):
            if hasattr(self, '_m_highly_reflective'):
                return self._m_highly_reflective

            self._m_highly_reflective = (self.flags & 2) != 0
            return getattr(self, '_m_highly_reflective', None)

        @property
        def backface_culling(self):
            if hasattr(self, '_m_backface_culling'):
                return self._m_backface_culling

            self._m_backface_culling = (self.flags & 4) == 0
            return getattr(self, '_m_backface_culling', None)

        @property
        def transparent(self):
            if hasattr(self, '_m_transparent'):
                return self._m_transparent

            self._m_transparent = (self.flags & 8) != 0
            return getattr(self, '_m_transparent', None)


    class Float3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class Color(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hue = self._io.read_u1()
            self.saturation = self._io.read_u1()
            self.brightness = self._io.read_u1()
            self.unknown = self._io.read_bytes(1)


    class Dummy(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = (self._io.read_bytes(1)).decode(u"ASCII")
            self.color = (self._io.read_bytes(1)).decode(u"ASCII")
            self.type = (self._io.read_bytes(1)).decode(u"ASCII")
            self.breakable = (self._io.read_bytes(1)).decode(u"ASCII")
            self.flashing = (self._io.read_bytes(1)).decode(u"ASCII")
            self.intensity = (self._io.read_bytes(1)).decode(u"ASCII")
            self.time_on = (self._io.read_bytes(1)).decode(u"ASCII")
            self.time_off = (self._io.read_bytes(1)).decode(u"ASCII")


    class Part(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = []
            i = 0
            while not self._io.is_eof():
                self.value.append((self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII"))
                i += 1



    @property
    def damaged_normals(self):
        """Damaged normal table."""
        if hasattr(self, '_m_damaged_normals'):
            return self._m_damaged_normals

        _pos = self._io.pos()
        self._io.seek((8248 + self.damaged_normals_offset))
        self._m_damaged_normals = []
        for i in range(self.num_vertices):
            self._m_damaged_normals.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_damaged_normals', None)

    @property
    def polygons(self):
        """Polygon table."""
        if hasattr(self, '_m_polygons'):
            return self._m_polygons

        _pos = self._io.pos()
        self._io.seek((8248 + self.polygon_table_offset))
        self._m_polygons = []
        for i in range(self.num_polygons):
            self._m_polygons.append(Fce.Polygon(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_polygons', None)

    @property
    def damaged_vertices(self):
        """Damaged vertice table."""
        if hasattr(self, '_m_damaged_vertices'):
            return self._m_damaged_vertices

        _pos = self._io.pos()
        self._io.seek((8248 + self.damaged_vertices_offset))
        self._m_damaged_vertices = []
        for i in range(self.num_vertices):
            self._m_damaged_vertices.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_damaged_vertices', None)

    @property
    def undamaged_vertices(self):
        """Undamaged vertice table."""
        if hasattr(self, '_m_undamaged_vertices'):
            return self._m_undamaged_vertices

        _pos = self._io.pos()
        self._io.seek((8248 + self.undamaged_vertices_offset))
        self._m_undamaged_vertices = []
        for i in range(self.num_vertices):
            self._m_undamaged_vertices.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_undamaged_vertices', None)

    @property
    def vertex_damage_weights(self):
        """Vertex damage weights."""
        if hasattr(self, '_m_vertex_damage_weights'):
            return self._m_vertex_damage_weights

        _pos = self._io.pos()
        self._io.seek((8248 + self.damage_weights_offset))
        self._m_vertex_damage_weights = []
        for i in range(self.num_vertices):
            self._m_vertex_damage_weights.append(self._io.read_f4le())

        self._io.seek(_pos)
        return getattr(self, '_m_vertex_damage_weights', None)

    @property
    def vertices(self):
        """Vertice table."""
        if hasattr(self, '_m_vertices'):
            return self._m_vertices

        _pos = self._io.pos()
        self._io.seek((8248 + self.vertice_table_offset))
        self._m_vertices = []
        for i in range(self.num_vertices):
            self._m_vertices.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_vertices', None)

    @property
    def movement_data(self):
        """Vertex movement data."""
        if hasattr(self, '_m_movement_data'):
            return self._m_movement_data

        _pos = self._io.pos()
        self._io.seek((8248 + self.driver_movement_offset))
        self._m_movement_data = []
        for i in range(self.num_vertices):
            self._m_movement_data.append(self._io.read_u4le())

        self._io.seek(_pos)
        return getattr(self, '_m_movement_data', None)

    @property
    def undamaged_normals(self):
        """Undamaged normal table."""
        if hasattr(self, '_m_undamaged_normals'):
            return self._m_undamaged_normals

        _pos = self._io.pos()
        self._io.seek((8248 + self.undamaged_normals_offset))
        self._m_undamaged_normals = []
        for i in range(self.num_vertices):
            self._m_undamaged_normals.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_undamaged_normals', None)

    @property
    def normals(self):
        """Normal table."""
        if hasattr(self, '_m_normals'):
            return self._m_normals

        _pos = self._io.pos()
        self._io.seek((8248 + self.normals_table_offset))
        self._m_normals = []
        for i in range(self.num_vertices):
            self._m_normals.append(Fce.Float3(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_normals', None)


