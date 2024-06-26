import psutil

class MemoryTracker:
    FIELDS = ['total', 'available', 'percent', 'used', 'free', 'active',
              'inactive', 'buffers', 'cached', 'shared', 'slab']
    def __init__(self, out_filepath):
        self.f = open(out_filepath, 'w')
        self.idx = 0
        print(','.join(['idx'] + self.FIELDS), file=self.f)
    def update(self):
        memprof = psutil.virtual_memory()
        numbers = [self.idx] + list(map(lambda x: getattr(memprof, x), self.FIELDS))
        print(','.join(map(str, numbers)), file=self.f)
        self.f.flush()
        self.idx += 1
