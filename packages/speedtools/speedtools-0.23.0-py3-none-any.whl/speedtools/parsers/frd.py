# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Frd(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.unknown = self._io.read_bytes(28)
        self.num_segments = self._io.read_u4le()
        self.num_road_blocks = self._io.read_u4le()
        self.road_blocks = []
        for i in range(self.num_road_blocks):
            self.road_blocks.append(Frd.RoadBlock(self._io, self, self._root))

        self.segment_headers = []
        for i in range((self.num_segments + 1)):
            self.segment_headers.append(Frd.SegmentHeader(self._io, self, self._root))

        self.segment_data = []
        for i in range((self.num_segments + 1)):
            self.segment_data.append(Frd.SegmentData(self._io, self.segment_headers[i], self._root))

        self.global_objects = []
        for i in range(2):
            self.global_objects.append(Frd.GlobalObjectChunk(self._io, self, self._root))


    class ObjectHeader(KaitaiStruct):

        class ObjectType(Enum):
            billboard = 2
            animated = 3
            normal = 4
            special = 6
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = KaitaiStream.resolve_enum(Frd.ObjectHeader.ObjectType, self._io.read_u4le())
            self.attribute_index = self._io.read_u4le()
            self.unknown = self._io.read_bytes(4)
            self.location = Frd.Float3(self._io, self, self._root)
            self.specific_data_size = self._io.read_u4le()
            self.unused1 = self._io.read_bytes(4)
            self.num_vertices = self._io.read_u4le()
            self.unused2 = self._io.read_bytes(8)
            self.num_polygons = self._io.read_u4le()
            self.unused3 = self._io.read_bytes(4)


    class Keyframe(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Frd.Int3(self._io, self, self._root)
            self.quaternion = Frd.Short4(self._io, self, self._root)


    class Neighbor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.block = self._io.read_s2le()
            self.unknown = self._io.read_s2le()


    class GlobalObjectChunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_objects = self._io.read_u4le()
            self.chunk = Frd.ObjectChunk(self.num_objects, self._io, self, self._root)


    class Float4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


    class Polygon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.face = []
            for i in range(4):
                self.face.append(self._io.read_u2le())

            self.texture = self._io.read_u2le()
            self.flags = self._io.read_u2le()
            self.animation = self._io.read_u1()

        @property
        def invert(self):
            if hasattr(self, '_m_invert'):
                return self._m_invert

            self._m_invert = (self.flags & 8) != 0
            return getattr(self, '_m_invert', None)

        @property
        def mirror_y(self):
            if hasattr(self, '_m_mirror_y'):
                return self._m_mirror_y

            self._m_mirror_y = (self.flags & 32) != 0
            return getattr(self, '_m_mirror_y', None)

        @property
        def animate_uv(self):
            if hasattr(self, '_m_animate_uv'):
                return self._m_animate_uv

            self._m_animate_uv = (self.flags & 8192) != 0
            return getattr(self, '_m_animate_uv', None)

        @property
        def mirror_x(self):
            if hasattr(self, '_m_mirror_x'):
                return self._m_mirror_x

            self._m_mirror_x = (self.flags & 16) != 0
            return getattr(self, '_m_mirror_x', None)

        @property
        def rotate(self):
            if hasattr(self, '_m_rotate'):
                return self._m_rotate

            self._m_rotate = (self.flags & 4) != 0
            return getattr(self, '_m_rotate', None)

        @property
        def texture_count(self):
            if hasattr(self, '_m_texture_count'):
                return self._m_texture_count

            self._m_texture_count = (self.animation & 7)
            return getattr(self, '_m_texture_count', None)

        @property
        def texture_id(self):
            if hasattr(self, '_m_texture_id'):
                return self._m_texture_id

            self._m_texture_id = (self.texture & 2047)
            return getattr(self, '_m_texture_id', None)

        @property
        def lane(self):
            if hasattr(self, '_m_lane'):
                return self._m_lane

            self._m_lane = (self.texture & 2048) != 0
            return getattr(self, '_m_lane', None)

        @property
        def backface_culling(self):
            if hasattr(self, '_m_backface_culling'):
                return self._m_backface_culling

            self._m_backface_culling = (self.flags & 32768) == 0
            return getattr(self, '_m_backface_culling', None)

        @property
        def animation_ticks(self):
            if hasattr(self, '_m_animation_ticks'):
                return self._m_animation_ticks

            self._m_animation_ticks = (self.animation >> 3)
            return getattr(self, '_m_animation_ticks', None)


    class RoadBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Frd.Float3(self._io, self, self._root)
            self.normal = Frd.Float3(self._io, self, self._root)
            self.forward = Frd.Float3(self._io, self, self._root)
            self.right = Frd.Float3(self._io, self, self._root)
            self.left_wall = self._io.read_f4le()
            self.right_wall = self._io.read_f4le()
            self.unknown1 = self._io.read_bytes(8)
            self.neighbors = []
            for i in range(2):
                self.neighbors.append(self._io.read_u2le())

            self.unknown2 = self._io.read_bytes(16)


    class TrackPolygon(KaitaiStruct):
        def __init__(self, num_polygons, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.num_polygons = num_polygons
            self._read()

        def _read(self):
            self.polygons = []
            for i in range(self.num_polygons):
                self.polygons.append(Frd.Polygon(self._io, self, self._root))



    class SegmentData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertices = []
            for i in range(self._parent.num_vertices):
                self.vertices.append(Frd.Float3(self._io, self, self._root))

            self.vertex_shadings = []
            for i in range(self._parent.num_vertices):
                self.vertex_shadings.append(Frd.Color(self._io, self, self._root))

            self.driveable_polygons = []
            for i in range(self._parent.num_driveable_polygons):
                self.driveable_polygons.append(Frd.DriveablePolygon(self._io, self, self._root))

            self.object_attributes = []
            for i in range(self._parent.num_road_objects):
                self.object_attributes.append(Frd.ObjectAttribute(self._io, self, self._root))

            self._raw_second_object_attributes = self._io.read_bytes((20 * self._parent.num_polygon_objects))
            _io__raw_second_object_attributes = KaitaiStream(BytesIO(self._raw_second_object_attributes))
            self.second_object_attributes = Frd.ObjectAttribute2Padded(self._parent.num_polygon_objects, _io__raw_second_object_attributes, self, self._root)
            self.sound_sources = []
            for i in range(self._parent.num_sound_sources):
                self.sound_sources.append(Frd.SourceType(self._io, self, self._root))

            self.light_sources = []
            for i in range(self._parent.num_light_sources):
                self.light_sources.append(Frd.SourceType(self._io, self, self._root))

            self.chunks = []
            for i in range(11):
                self.chunks.append(Frd.TrackPolygon(self._parent.num_polygons[i], self._io, self, self._root))

            self.object_chunks = []
            for i in range(4):
                self.object_chunks.append(Frd.ObjectChunk(self._parent.num_objects_per_chunks[i].num_objects, self._io, self, self._root))



    class SegmentHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_polygons = []
            for i in range(11):
                self.num_polygons.append(self._io.read_u4le())

            self.unused1 = self._io.read_bytes(44)
            self.num_vertices = self._io.read_u4le()
            self.num_high_res_vertices = self._io.read_u4le()
            self.num_low_res_vertices = self._io.read_u4le()
            self.num_medium_res_vertices = self._io.read_u4le()
            self.num_vertices_dup = self._io.read_u4le()
            self.num_object_vertices = self._io.read_u4le()
            self.unused2 = self._io.read_bytes(8)
            self.location = Frd.Float3(self._io, self, self._root)
            self.bounding_points = []
            for i in range(4):
                self.bounding_points.append(Frd.Float3(self._io, self, self._root))

            self.neighbors = []
            for i in range(300):
                self.neighbors.append(Frd.Neighbor(self._io, self, self._root))

            self.num_objects_per_chunks = []
            for i in range(4):
                self.num_objects_per_chunks.append(Frd.NumObjectsPerChunk(self._io, self, self._root))

            self.num_driveable_polygons = self._io.read_u4le()
            self.min_point = Frd.Float3(self._io, self, self._root)
            self.max_point = Frd.Float3(self._io, self, self._root)
            self.unused3 = self._io.read_bytes(4)
            self.num_road_blocks = self._io.read_u4le()
            self.num_road_objects = self._io.read_u4le()
            self.unused4 = self._io.read_bytes(4)
            self.num_polygon_objects = self._io.read_u4le()
            self.unused5 = self._io.read_bytes(4)
            self.num_sound_sources = self._io.read_u4le()
            self.unused6 = self._io.read_bytes(4)
            self.num_light_sources = self._io.read_u4le()
            self.unused7 = self._io.read_bytes(4)
            self.neighbor_segments = []
            for i in range(8):
                self.neighbor_segments.append(self._io.read_u4le())



    class DriveablePolygon(KaitaiStruct):

        class RoadEffect(Enum):
            not_driveable = 0
            driveable1 = 1
            gravel = 2
            driveable2 = 3
            leaves1 = 4
            dust1 = 5
            driveable3 = 6
            driveable4 = 7
            driveable5 = 8
            snow1 = 9
            driveable6 = 10
            leaves2 = 11
            driveable7 = 12
            dust2 = 13
            driveable8 = 14
            snow2 = 15
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min_y = self._io.read_u1()
            self.max_y = self._io.read_u1()
            self.min_x = self._io.read_u1()
            self.max_x = self._io.read_u1()
            self.front_edge = self._io.read_u1()
            self.left_edge = self._io.read_u1()
            self.back_edge = self._io.read_u1()
            self.right_edge = self._io.read_u1()
            self.collision_flags = self._io.read_u1()
            self.unknown = self._io.read_bytes(1)
            self.polygon = self._io.read_u2le()
            self.normal = Frd.Short3(self._io, self, self._root)
            self.forward = Frd.Short3(self._io, self, self._root)

        @property
        def road_effect(self):
            if hasattr(self, '_m_road_effect'):
                return self._m_road_effect

            self._m_road_effect = KaitaiStream.resolve_enum(Frd.DriveablePolygon.RoadEffect, (self.collision_flags & 15))
            return getattr(self, '_m_road_effect', None)

        @property
        def has_finite_height(self):
            if hasattr(self, '_m_has_finite_height'):
                return self._m_has_finite_height

            self._m_has_finite_height = (self.collision_flags & 32) != 0
            return getattr(self, '_m_has_finite_height', None)

        @property
        def has_object_collision(self):
            if hasattr(self, '_m_has_object_collision'):
                return self._m_has_object_collision

            self._m_has_object_collision = (self.collision_flags & 64) != 0
            return getattr(self, '_m_has_object_collision', None)

        @property
        def has_wall_collision(self):
            if hasattr(self, '_m_has_wall_collision'):
                return self._m_has_wall_collision

            self._m_has_wall_collision = (self.collision_flags & 128) != 0
            return getattr(self, '_m_has_wall_collision', None)


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


    class Short3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()


    class SourceType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Frd.Int3(self._io, self, self._root)
            self.type = self._io.read_u4le()


    class Color(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.blue = self._io.read_u1()
            self.green = self._io.read_u1()
            self.red = self._io.read_u1()
            self.alpha = self._io.read_u1()


    class Int3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self.z = self._io.read_s4le()


    class ObjectAttribute(KaitaiStruct):

        class CollisionType(Enum):
            none = 0
            static = 1
            destructible = 2
            unknown = 3
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Frd.Int3(self._io, self, self._root)
            self.unknown1 = self._io.read_bytes(2)
            self.identifier = self._io.read_u2le()
            self.unknown2 = self._io.read_bytes(3)
            self.collision_type = KaitaiStream.resolve_enum(Frd.ObjectAttribute.CollisionType, self._io.read_u1())


    class Animation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.head = self._io.read_u2le()
            self.type = self._io.read_u1()
            self.identifier = self._io.read_u1()
            self.num_keyframes = self._io.read_u2le()
            self.delay = self._io.read_u2le()
            self.keyframes = []
            for i in range(self.num_keyframes):
                self.keyframes.append(Frd.Keyframe(self._io, self, self._root))



    class ObjectAttribute2(KaitaiStruct):

        class AttributeType(Enum):
            polygon_object = 1
            road_object1 = 2
            road_object2 = 3
            road_object3 = 4
            special = 6
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown1 = self._io.read_bytes(2)
            self.type = KaitaiStream.resolve_enum(Frd.ObjectAttribute2.AttributeType, self._io.read_u1())
            self.identifier = self._io.read_u1()
            self.location = Frd.Int3(self._io, self, self._root)
            if self.type != Frd.ObjectAttribute2.AttributeType.polygon_object:
                self.cross_index = self._io.read_u1()

            if self.type != Frd.ObjectAttribute2.AttributeType.polygon_object:
                self.unknown2 = self._io.read_bytes(3)



    class ObjectAttribute2Padded(KaitaiStruct):
        def __init__(self, num_attributes, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.num_attributes = num_attributes
            self._read()

        def _read(self):
            self.attributes = []
            for i in range(self.num_attributes):
                self.attributes.append(Frd.ObjectAttribute2(self._io, self, self._root))



    class Short4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.w = self._io.read_s2le()


    class ObjectChunk(KaitaiStruct):
        def __init__(self, num_objects, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.num_objects = num_objects
            self._read()

        def _read(self):
            self.objects = []
            for i in range(self.num_objects):
                self.objects.append(Frd.ObjectHeader(self._io, self, self._root))

            self.object_extras = []
            for i in range(len(self.objects)):
                self.object_extras.append(Frd.ObjectData(self._io, self.objects[i], self._root))



    class SpecialData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Frd.Float3(self._io, self, self._root)
            self.mass = self._io.read_f4le()
            self.transform = []
            for i in range(9):
                self.transform.append(self._io.read_f4le())

            self.dimensions = Frd.Float3(self._io, self, self._root)
            self.unknown3 = self._io.read_u4le()
            self.unknown4 = self._io.read_u2le()
            self.unknown5 = self._io.read_u2le()


    class ObjectData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._parent.type == Frd.ObjectHeader.ObjectType.animated:
                self._raw_animation = self._io.read_bytes(self._parent.specific_data_size)
                _io__raw_animation = KaitaiStream(BytesIO(self._raw_animation))
                self.animation = Frd.Animation(_io__raw_animation, self, self._root)

            if self._parent.type == Frd.ObjectHeader.ObjectType.special:
                self._raw_special = self._io.read_bytes(self._parent.specific_data_size)
                _io__raw_special = KaitaiStream(BytesIO(self._raw_special))
                self.special = Frd.SpecialData(_io__raw_special, self, self._root)

            self.vertices = []
            for i in range(self._parent.num_vertices):
                self.vertices.append(Frd.Float3(self._io, self, self._root))

            self.vertex_shadings = []
            for i in range(self._parent.num_vertices):
                self.vertex_shadings.append(Frd.Color(self._io, self, self._root))

            self.polygons = []
            for i in range(self._parent.num_polygons):
                self.polygons.append(Frd.Polygon(self._io, self, self._root))



    class NumObjectsPerChunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_objects = self._io.read_u4le()
            self.unknown = self._io.read_bytes(4)



