# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Can(KaitaiStruct):
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
            self.keyframes.append(Can.Keyframe(self._io, self, self._root))


    class Keyframe(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.location = Can.Int3(self._io, self, self._root)
            self.quaternion = Can.Short4(self._io, self, self._root)


    class Int3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ix = self._io.read_s4le()
            self.iy = self._io.read_s4le()
            self.iz = self._io.read_s4le()

        @property
        def x(self):
            if hasattr(self, '_m_x'):
                return self._m_x

            self._m_x = ((self.ix * 0.7692307692307693) / 65536)
            return getattr(self, '_m_x', None)

        @property
        def y(self):
            if hasattr(self, '_m_y'):
                return self._m_y

            self._m_y = ((self.iy * 0.7692307692307693) / 65536)
            return getattr(self, '_m_y', None)

        @property
        def z(self):
            if hasattr(self, '_m_z'):
                return self._m_z

            self._m_z = ((self.iz * 0.7692307692307693) / 65536)
            return getattr(self, '_m_z', None)


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



